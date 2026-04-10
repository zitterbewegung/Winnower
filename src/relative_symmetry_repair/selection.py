"""Period-first model selection and two-stage pipeline.

Stage A: Select the best period (and its best shift) using Bernoulli NML.
Stage B: Analyze the residual mask of the selected model.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from .coding import lz4_mask_bits, nml_score_bits, resolve_nml_mode, run_length_bits
from .repair import (
    RelativePeriodicFit,
    fit_relative_periodic_background,
    scan_relative_periodicity,
    extract_components,
    summarise_components,
)
from .repair_nd import (
    RelativePeriodicFitND,
    fit_relative_periodic_background_nd,
    scan_relative_periodicity_nd,
    extract_components_nd,
    summarise_components_nd,
)
from .selector_tools import (
    TIE_BREAK_RULE,
    shift_columns,
    shift_handling_from_1d,
    shift_handling_from_nd,
    sort_candidates,
)


# ── Data structures ───────────────────────────────────────────────────────────


class SelectionStatus(enum.Enum):
    """Confidence level of period selection."""
    STABLE_WINNER = "stable_winner"
    NEAR_TIE = "near_tie"
    UNRESOLVED = "unresolved"


@dataclass(slots=True)
class PeriodScore:
    """NML score for a single period, minimized over shifts."""
    period: int
    best_shift: int | tuple[int, ...]  # scalar for 1D, tuple for ND
    nml_bits: float
    nll_bits: float
    nml_complexity: float
    defect_rate: float
    n_shifts_scanned: int


@dataclass(slots=True)
class ResidualDiagnostics:
    """Stage B: residual mask diagnostics, separate from selection."""
    run_length_bits: int
    lz4_bits: int
    n_components: int
    component_summary: pd.DataFrame | None = None
    defect_rate: float = 0.0


@dataclass(slots=True)
class SelectionResult:
    """Complete result of period-first model selection."""
    # Stage A: selection
    selected: PeriodScore
    runner_up: PeriodScore | None
    margin: float  # NML gap between selected and runner-up (bits)
    status: SelectionStatus
    all_periods: list[PeriodScore]

    # Stage B: residual diagnostics (populated by analyze_residual)
    residual: ResidualDiagnostics | None = None

    # The underlying fit object for the selected model
    best_fit: RelativePeriodicFit | RelativePeriodicFitND | None = None

    # Selector metadata for traceability
    selector_type: str = "period_first"
    score_type: str = "bernoulli_nml"
    nml_mode: str = "hybrid"
    shift_handling: str = "joint_shift_optimization"
    tie_break_rule: str = TIE_BREAK_RULE
    majority_tie_break: str = "ones"
    candidate_margin_bits: float = float("inf")
    candidate_runner_up_period: int | None = None
    candidate_runner_up_shift: int | tuple[int, ...] | None = None
    candidate_runner_up_nml_bits: float | None = None


# ── Margin thresholds ─────────────────────────────────────────────────────────
# These are in bits. A margin < NEAR_TIE_THRESHOLD means selection is fragile.
# A margin < 0 (impossible by construction) or exactly 0 means unresolved.

NEAR_TIE_THRESHOLD = 2.0  # bits — below this, report near_tie


def _classify_status(margin: float) -> SelectionStatus:
    if margin <= 0.0:
        return SelectionStatus.UNRESOLVED
    if margin < NEAR_TIE_THRESHOLD:
        return SelectionStatus.NEAR_TIE
    return SelectionStatus.STABLE_WINNER


# ── Stage A: Period-first selection ───────────────────────────────────────────


def _group_by_period(
    frame: pd.DataFrame,
    fits: dict,
    *,
    nd: bool = False,
) -> list[PeriodScore]:
    """Group scan results by period, taking min NML over shifts."""
    if frame.empty or "period" not in frame.columns:
        return []
    scores = []
    for period, group in frame.groupby("period"):
        best_row = sort_candidates(group, "nml_bits").iloc[0]
        if nd:
            shift_cols = [c for c in group.columns if c.startswith("shift_")]
            best_shift = tuple(int(best_row[c]) for c in shift_cols)
        else:
            best_shift = int(best_row["shift"])
        scores.append(PeriodScore(
            period=int(period),
            best_shift=best_shift,
            nml_bits=float(best_row["nml_bits"]),
            nll_bits=float(best_row["nll_bits"]),
            nml_complexity=float(best_row["nml_complexity"]),
            defect_rate=float(best_row["defect_rate"]),
            n_shifts_scanned=len(group),
        ))
    scores.sort(key=lambda s: (s.nml_bits, s.period))
    return scores


def _shift_from_row(frame: pd.DataFrame, row: pd.Series) -> int | tuple[int, ...]:
    cols = shift_columns(frame)
    if not cols:
        raise KeyError("Candidate frame is missing shift columns")
    if cols == ["shift"]:
        return int(row["shift"])
    return tuple(int(row[c]) for c in cols)


def _candidate_margin_from_frame(
    frame: pd.DataFrame,
) -> tuple[float, int | None, int | tuple[int, ...] | None, float | None]:
    ranked = sort_candidates(frame, "nml_bits")
    if len(ranked) <= 1:
        return float("inf"), None, None, None
    runner_up = ranked.iloc[1]
    return (
        float(runner_up["nml_bits"] - ranked.iloc[0]["nml_bits"]),
        int(runner_up["period"]),
        _shift_from_row(ranked, runner_up),
        float(runner_up["nml_bits"]),
    )


def select_period(
    spacetime: np.ndarray,
    shifts: Iterable[int],
    periods: Iterable[int],
    *,
    rule: int | None = None,
    min_component_size: int = 6,
    nml_mode: str = "hybrid",
    majority_tie_break: str = "ones",
) -> SelectionResult:
    """Period-first selection for 1D spacetimes.

    Stage A: scan all (period, shift) pairs, group by period, select
    the period with lowest NML (min over shifts).

    Returns a SelectionResult with the selected period, runner-up,
    margin, and status. Call analyze_residual() to populate Stage B.
    """
    shift_list = [int(shift) for shift in shifts]
    period_list = [int(period) for period in periods]
    frame, fits = scan_relative_periodicity(
        spacetime,
        shifts=shift_list,
        periods=period_list,
        rule=rule,
        nml_mode=nml_mode,
        majority_tie_break=majority_tie_break,
    )
    return select_period_from_scan(
        frame,
        fits,
        min_component_size=min_component_size,
        nml_mode=nml_mode,
        shift_handling=shift_handling_from_1d(shift_list),
        majority_tie_break=majority_tie_break,
    )


def select_period_from_scan(
    frame: pd.DataFrame,
    fits: dict[tuple[int, int], RelativePeriodicFit],
    *,
    min_component_size: int = 6,
    nml_mode: str = "hybrid",
    shift_handling: str = "joint_shift_optimization",
    majority_tie_break: str = "ones",
) -> SelectionResult:
    """Build a period-first selection result from a precomputed 1D scan."""
    period_scores = _group_by_period(frame, fits, nd=False)
    if not period_scores:
        raise ValueError("No candidates scanned")

    selected = period_scores[0]
    runner_up = period_scores[1] if len(period_scores) > 1 else None
    margin = (runner_up.nml_bits - selected.nml_bits) if runner_up else float("inf")
    (
        candidate_margin_bits,
        candidate_runner_up_period,
        candidate_runner_up_shift,
        candidate_runner_up_nml_bits,
    ) = _candidate_margin_from_frame(frame)

    # Retrieve the best fit object
    best_key = (selected.best_shift, selected.period)
    best_fit = fits.get(best_key)
    if best_fit is None and fits:
        raise KeyError(
            f"Best-fit key {best_key!r} not found in fits dict "
            f"(available keys: {list(fits.keys())[:5]}...)"
        )
    result_majority_tie_break = (
        best_fit.majority_tie_break if best_fit is not None else majority_tie_break
    )

    result = SelectionResult(
        selected=selected,
        runner_up=runner_up,
        margin=margin,
        status=_classify_status(margin),
        all_periods=period_scores,
        best_fit=best_fit,
        nml_mode=nml_mode,
        shift_handling=shift_handling,
        majority_tie_break=result_majority_tie_break,
        candidate_margin_bits=candidate_margin_bits,
        candidate_runner_up_period=candidate_runner_up_period,
        candidate_runner_up_shift=candidate_runner_up_shift,
        candidate_runner_up_nml_bits=candidate_runner_up_nml_bits,
    )

    # Auto-populate residual diagnostics
    if best_fit is not None:
        result.residual = _compute_residual_1d(best_fit, min_component_size)

    return result


def select_period_nd(
    spacetime: np.ndarray,
    shift_ranges: Sequence[Iterable[int]],
    periods: Iterable[int],
    *,
    rule_error_fn=None,
    min_component_size: int = 4,
    nml_mode: str = "hybrid",
    majority_tie_break: str = "ones",
) -> SelectionResult:
    """Period-first selection for N-dimensional spacetimes.

    Stage A: scan all (period, shift_vector) pairs, group by period,
    select the period with lowest NML (min over shifts).
    """
    shift_lists = [[int(shift) for shift in axis] for axis in shift_ranges]
    period_list = [int(period) for period in periods]
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=shift_lists,
        periods=period_list,
        rule_error_fn=rule_error_fn,
        nml_mode=nml_mode,
        majority_tie_break=majority_tie_break,
    )
    return select_period_nd_from_scan(
        frame,
        fits,
        min_component_size=min_component_size,
        nml_mode=nml_mode,
        shift_handling=shift_handling_from_nd(shift_lists),
        majority_tie_break=majority_tie_break,
    )


def select_period_nd_from_scan(
    frame: pd.DataFrame,
    fits: dict[tuple[tuple[int, ...], int], RelativePeriodicFitND],
    *,
    min_component_size: int = 4,
    nml_mode: str = "hybrid",
    shift_handling: str = "joint_shift_optimization",
    majority_tie_break: str = "ones",
) -> SelectionResult:
    """Build a period-first selection result from a precomputed N-D scan."""
    period_scores = _group_by_period(frame, fits, nd=True)
    if not period_scores:
        raise ValueError("No candidates scanned")

    selected = period_scores[0]
    runner_up = period_scores[1] if len(period_scores) > 1 else None
    margin = (runner_up.nml_bits - selected.nml_bits) if runner_up else float("inf")
    (
        candidate_margin_bits,
        candidate_runner_up_period,
        candidate_runner_up_shift,
        candidate_runner_up_nml_bits,
    ) = _candidate_margin_from_frame(frame)

    # Retrieve the best fit object
    best_key = (selected.best_shift, selected.period)
    best_fit = fits.get(best_key)
    if best_fit is None and fits:
        raise KeyError(
            f"Best-fit key {best_key!r} not found in fits dict "
            f"(available keys: {list(fits.keys())[:5]}...)"
        )
    result_majority_tie_break = (
        best_fit.majority_tie_break if best_fit is not None else majority_tie_break
    )

    result = SelectionResult(
        selected=selected,
        runner_up=runner_up,
        margin=margin,
        status=_classify_status(margin),
        all_periods=period_scores,
        best_fit=best_fit,
        nml_mode=nml_mode,
        shift_handling=shift_handling,
        majority_tie_break=result_majority_tie_break,
        candidate_margin_bits=candidate_margin_bits,
        candidate_runner_up_period=candidate_runner_up_period,
        candidate_runner_up_shift=candidate_runner_up_shift,
        candidate_runner_up_nml_bits=candidate_runner_up_nml_bits,
    )

    if best_fit is not None:
        result.residual = _compute_residual_nd(best_fit, min_component_size)

    return result


# ── Stage B: Residual diagnostics ─────────────────────────────────────────────


def _compute_residual_1d(
    fit: RelativePeriodicFit,
    min_component_size: int = 6,
) -> ResidualDiagnostics:
    """Compute residual diagnostics for a 1D fit."""
    labels, n_comp = extract_components(fit.defect_mask, min_size=min_component_size)
    comp_df = summarise_components(labels) if n_comp > 0 else None
    return ResidualDiagnostics(
        run_length_bits=fit.run_length_bits,
        lz4_bits=fit.lz4_bits,
        n_components=n_comp,
        component_summary=comp_df,
        defect_rate=fit.defect_rate,
    )


def _compute_residual_nd(
    fit: RelativePeriodicFitND,
    min_component_size: int = 4,
) -> ResidualDiagnostics:
    """Compute residual diagnostics for an N-D fit."""
    labels, n_comp = extract_components_nd(fit.defect_mask, min_size=min_component_size)
    comp_df = summarise_components_nd(labels) if n_comp > 0 else None
    return ResidualDiagnostics(
        run_length_bits=fit.run_length_bits,
        lz4_bits=fit.lz4_bits,
        n_components=n_comp,
        component_summary=comp_df,
        defect_rate=fit.defect_rate,
    )


def analyze_residual(
    result: SelectionResult,
    *,
    min_component_size: int = 6,
) -> ResidualDiagnostics:
    """Explicitly run Stage B residual analysis on a SelectionResult.

    Usually called automatically by select_period / select_period_nd,
    but can be called again with different parameters.
    """
    fit = result.best_fit
    if fit is None:
        raise ValueError("No fit object available")
    if isinstance(fit, RelativePeriodicFitND):
        diag = _compute_residual_nd(fit, min_component_size)
    else:
        diag = _compute_residual_1d(fit, min_component_size)
    result.residual = diag
    return diag


# ── Convenience: structured output ────────────────────────────────────────────


def selection_summary(result: SelectionResult) -> dict:
    """Return a flat dict summarizing the selection for structured output."""
    d = {
        "selected_period": result.selected.period,
        "selected_shift": result.selected.best_shift,
        "selected_nml_bits": result.selected.nml_bits,
        "selected_nll_bits": result.selected.nll_bits,
        "selected_complexity": result.selected.nml_complexity,
        "selected_defect_rate": result.selected.defect_rate,
        "status": result.status.value,
        "margin_bits": result.margin,
        "period_margin_bits": result.margin,
        "candidate_margin_bits": result.candidate_margin_bits,
        "n_periods_scanned": len(result.all_periods),
        "selector_type": result.selector_type,
        "score_type": result.score_type,
        "nml_mode": result.nml_mode,
        "resolved_nml_mode": resolve_nml_mode(mode=result.nml_mode),
        "shift_handling": result.shift_handling,
        "tie_break_rule": result.tie_break_rule,
        "majority_tie_break": result.majority_tie_break,
    }
    if result.runner_up:
        d["runner_up_period"] = result.runner_up.period
        d["runner_up_nml_bits"] = result.runner_up.nml_bits
    if result.candidate_runner_up_period is not None:
        d["candidate_runner_up_period"] = result.candidate_runner_up_period
        d["candidate_runner_up_shift"] = result.candidate_runner_up_shift
        d["candidate_runner_up_nml_bits"] = result.candidate_runner_up_nml_bits
    if result.residual is not None:
        d["residual_rl_bits"] = result.residual.run_length_bits
        d["residual_lz4_bits"] = result.residual.lz4_bits
        d["residual_n_components"] = result.residual.n_components
    return d
