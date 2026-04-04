from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import ndimage

from ._orbit_scoring import (
    RelativePeriodicOrbitWorkspace,
    class_sizes_1d,
    reduce_binary_spacetime_by_orbits,
)
from .coding import (
    combinatorial_repair_bits, lz4_mask_bits, nml_score_bits,
    run_length_bits, template_bits_nml, template_bits_raw,
)
from .eca import rule_consistency_rate


@dataclass(slots=True)
class RelativePeriodicFit:
    shift: int
    period: int
    background: np.ndarray
    defect_mask: np.ndarray
    defect_sites: int
    total_sites: int
    defect_rate: float
    combinatorial_bits: float
    run_length_bits: int
    lz4_bits: int
    template_bits: int = 0
    mdl_bits: float = 0.0       # legacy: template_bits_nml + run_length_bits
    nll_bits: float = 0.0       # Bernoulli NLL over orbit classes
    nml_complexity: float = 0.0 # Bernoulli NML complexity under the configured mode
    nml_bits: float = 0.0       # Bernoulli NML score under the configured mode
    nml_mode: str = "hybrid"
    rule_error: float | None = None

    def to_record(self) -> dict[str, float | int | None]:
        return {
            "shift": self.shift,
            "period": self.period,
            "defect_sites": self.defect_sites,
            "total_sites": self.total_sites,
            "defect_rate": self.defect_rate,
            "combinatorial_bits": self.combinatorial_bits,
            "run_length_bits": self.run_length_bits,
            "lz4_bits": self.lz4_bits,
            "template_bits": self.template_bits,
            "mdl_bits": self.mdl_bits,
            "nll_bits": self.nll_bits,
            "nml_complexity": self.nml_complexity,
            "nml_bits": self.nml_bits,
            "nml_mode": self.nml_mode,
            "rule_error": self.rule_error,
        }


@dataclass(slots=True)
class ReflectionFit:
    target: np.ndarray
    defect_mask: np.ndarray
    defect_sites: int
    total_sites: int
    defect_rate: float
    combinatorial_bits: float
    run_length_bits: int
    lz4_bits: int

    def to_record(self) -> dict[str, float | int]:
        return {
            "defect_sites": self.defect_sites,
            "total_sites": self.total_sites,
            "defect_rate": self.defect_rate,
            "combinatorial_bits": self.combinatorial_bits,
            "run_length_bits": self.run_length_bits,
            "lz4_bits": self.lz4_bits,
        }


def component_labels(shape: tuple[int, int], shift: int, period: int) -> np.ndarray:
    """Label each spacetime site by its relative-periodic orbit class.

    The exact relative-periodic constraint is:
        B[t + period, (x + shift) mod width] = B[t, x]
    on all valid time slices.
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    steps, width = shape
    t = np.arange(steps, dtype=np.int64)[:, None]
    x = np.arange(width, dtype=np.int64)[None, :]
    residue = t % int(period)
    orbit_step = t // int(period)
    start_x = (x - orbit_step * int(shift)) % width
    labels = residue * width + start_x
    return labels.astype(np.int32)


def _majority_binary_by_labels(spacetime: np.ndarray, labels: np.ndarray, period: int) -> np.ndarray:
    steps, width = spacetime.shape
    n_labels = int(period) * width
    flat_labels = labels.ravel()
    flat_values = spacetime.ravel().astype(np.int64)
    totals = np.bincount(flat_labels, minlength=n_labels)
    ones = np.bincount(flat_labels, weights=flat_values, minlength=n_labels)
    majority_values = (2 * ones >= totals).astype(np.uint8)
    return majority_values[labels]


def _fit_relative_periodic_background_reference(
    spacetime: np.ndarray,
    shift: int,
    period: int,
    *,
    rule: int | None = None,
    nml_mode: str = "hybrid",
) -> RelativePeriodicFit:
    """Reference implementation retained for correctness tests and benchmarks."""
    labels = component_labels(spacetime.shape, shift=shift, period=period)
    background = _majority_binary_by_labels(
        spacetime.astype(np.uint8),
        labels,
        int(period),
    )
    defect_mask = spacetime.astype(np.uint8) != background
    defect_sites = int(defect_mask.sum())
    total_sites = int(defect_mask.size)
    rule_error = None if rule is None else rule_consistency_rate(background, int(rule))

    steps, width = spacetime.shape
    n_labels = int(period) * width
    rl_bits = run_length_bits(defect_mask)
    t_bits_raw = template_bits_raw(period, (width,))
    t_bits_nml = template_bits_nml(period, (width,), steps)
    mdl = t_bits_nml + rl_bits
    nll, nml_comp, nml_total = nml_score_bits(
        spacetime.astype(np.uint8),
        labels,
        n_labels,
        mode=nml_mode,
    )

    return RelativePeriodicFit(
        shift=int(shift),
        period=int(period),
        background=background.astype(np.uint8),
        defect_mask=defect_mask,
        defect_sites=defect_sites,
        total_sites=total_sites,
        defect_rate=defect_sites / total_sites,
        combinatorial_bits=combinatorial_repair_bits(total_sites, defect_sites, alphabet_size=2),
        run_length_bits=rl_bits,
        lz4_bits=lz4_mask_bits(defect_mask),
        template_bits=t_bits_raw,
        mdl_bits=mdl,
        nll_bits=nll,
        nml_complexity=nml_comp,
        nml_bits=nml_total,
        nml_mode=nml_mode,
        rule_error=rule_error,
    )


def _fit_relative_periodic_background_from_workspace(
    workspace: RelativePeriodicOrbitWorkspace,
    spacetime: np.ndarray,
    shift: int,
    period: int,
    *,
    rule: int | None = None,
    nml_mode: str = "hybrid",
) -> RelativePeriodicFit:
    """Optimized grouped-reduction path for a single 1D candidate."""
    reduction = workspace.evaluate_candidate((int(shift),), int(period), nml_mode=nml_mode)
    background = reduction.background_flat.reshape(spacetime.shape).copy()
    defect_mask = reduction.defect_flat.reshape(spacetime.shape).astype(bool, copy=True)
    total_sites = int(defect_mask.size)
    rule_error = None if rule is None else rule_consistency_rate(background, int(rule))

    steps, width = spacetime.shape
    rl_bits = run_length_bits(defect_mask)
    t_bits_raw = template_bits_raw(period, (width,))
    t_bits_nml = template_bits_nml(period, (width,), steps)
    mdl = t_bits_nml + rl_bits

    return RelativePeriodicFit(
        shift=int(shift),
        period=int(period),
        background=background.astype(np.uint8, copy=False),
        defect_mask=defect_mask,
        defect_sites=reduction.defect_sites,
        total_sites=total_sites,
        defect_rate=reduction.defect_sites / total_sites,
        combinatorial_bits=combinatorial_repair_bits(total_sites, reduction.defect_sites, alphabet_size=2),
        run_length_bits=rl_bits,
        lz4_bits=lz4_mask_bits(defect_mask),
        template_bits=t_bits_raw,
        mdl_bits=mdl,
        nll_bits=reduction.nll_bits,
        nml_complexity=reduction.nml_complexity,
        nml_bits=reduction.nml_bits,
        nml_mode=nml_mode,
        rule_error=rule_error,
    )


def fit_relative_periodic_background(
    spacetime: np.ndarray,
    shift: int,
    period: int,
    *,
    rule: int | None = None,
    nml_mode: str = "hybrid",
) -> RelativePeriodicFit:
    """Project a binary spacetime field onto the nearest relative-periodic background."""
    if spacetime.ndim != 2:
        raise ValueError("spacetime must be a 2D array")
    if np.any((spacetime != 0) & (spacetime != 1)):
        raise ValueError("spacetime must be binary")
    workspace = RelativePeriodicOrbitWorkspace(spacetime, residue_major=True)
    return _fit_relative_periodic_background_from_workspace(
        workspace,
        np.asarray(spacetime, dtype=np.uint8),
        shift,
        period,
        rule=rule,
        nml_mode=nml_mode,
    )


def _scan_relative_periodicity_reference(
    spacetime: np.ndarray,
    shifts: Iterable[int],
    periods: Iterable[int],
    *,
    rule: int | None = None,
    nml_mode: str = "hybrid",
) -> tuple[pd.DataFrame, dict[tuple[int, int], RelativePeriodicFit]]:
    """Reference candidate scan retained for benchmarks and regression tests."""
    fits: dict[tuple[int, int], RelativePeriodicFit] = {}
    records: list[dict[str, float | int | None]] = []
    for period in periods:
        for shift in shifts:
            fit = _fit_relative_periodic_background_reference(
                spacetime,
                shift=shift,
                period=period,
                rule=rule,
                nml_mode=nml_mode,
            )
            fits[(int(shift), int(period))] = fit
            records.append(fit.to_record())
    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        return frame, fits
    if rule is not None:
        frame["composite_score"] = frame["defect_rate"] + frame["rule_error"].fillna(0.0)
    return frame.sort_values(["period", "shift"]).reset_index(drop=True), fits


def scan_relative_periodicity(
    spacetime: np.ndarray,
    shifts: Iterable[int],
    periods: Iterable[int],
    *,
    rule: int | None = None,
    nml_mode: str = "hybrid",
) -> tuple[pd.DataFrame, dict[tuple[int, int], RelativePeriodicFit]]:
    """Scan a spacetime field across a grid of relative-periodic background models."""
    if spacetime.ndim != 2:
        raise ValueError("spacetime must be a 2D array")
    if np.any((spacetime != 0) & (spacetime != 1)):
        raise ValueError("spacetime must be binary")

    binary = np.ascontiguousarray(spacetime, dtype=np.uint8)
    workspace = RelativePeriodicOrbitWorkspace(binary, residue_major=True)
    fits: dict[tuple[int, int], RelativePeriodicFit] = {}
    records: list[dict[str, float | int | None]] = []
    for period in periods:
        for shift in shifts:
            fit = _fit_relative_periodic_background_from_workspace(
                workspace,
                binary,
                shift=shift,
                period=period,
                rule=rule,
                nml_mode=nml_mode,
            )
            fits[(int(shift), int(period))] = fit
            records.append(fit.to_record())
    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        return frame, fits
    if rule is not None:
        frame["composite_score"] = frame["defect_rate"] + frame["rule_error"].fillna(0.0)
    return frame.sort_values(["period", "shift"]).reset_index(drop=True), fits


def fit_reflection_symmetric_state(state: np.ndarray) -> ReflectionFit:
    """Nearest mirror-symmetric binary state (minimum Hamming distance, 0-bias on ties)."""
    if state.ndim != 1:
        raise ValueError("state must be 1D")
    if state.size == 0:
        raise ValueError("state must be non-empty")
    if np.any((state != 0) & (state != 1)):
        raise ValueError("state must be binary")

    state = state.astype(np.uint8)
    flipped = state[::-1]
    # Pairwise majority: agree → keep value; disagree → 0 (minimum-defect tie-break)
    target = np.where(state == flipped, state, (state & flipped)).astype(np.uint8)
    defect_mask = state != target
    defect_sites = int(defect_mask.sum())
    total_sites = int(state.size)

    return ReflectionFit(
        target=target,
        defect_mask=defect_mask,
        defect_sites=defect_sites,
        total_sites=total_sites,
        defect_rate=defect_sites / total_sites,
        combinatorial_bits=combinatorial_repair_bits(total_sites, defect_sites, alphabet_size=2),
        run_length_bits=run_length_bits(defect_mask),
        lz4_bits=lz4_mask_bits(defect_mask),
    )


def extract_components(defect_mask: np.ndarray, *, min_size: int = 1) -> tuple[np.ndarray, int]:
    """Label connected defect components with 8-neighborhood connectivity."""
    structure = np.ones((3, 3), dtype=np.uint8)
    labels, num_labels = ndimage.label(defect_mask.astype(np.uint8), structure=structure)
    if min_size <= 1:
        return labels, int(num_labels)

    counts = np.bincount(labels.ravel())
    keep = {label for label, count in enumerate(counts) if label != 0 and count >= min_size}
    filtered = np.where(np.isin(labels, list(keep)), labels, 0)
    return filtered, len(keep)


def summarise_components(labels: np.ndarray) -> pd.DataFrame:
    """Summarise connected components extracted from a defect mask."""
    rows: list[dict[str, int]] = []
    for label in np.unique(labels):
        if label == 0:
            continue
        coords = np.argwhere(labels == label)
        if coords.size == 0:
            continue
        t_min, x_min = coords.min(axis=0)
        t_max, x_max = coords.max(axis=0)
        rows.append(
            {
                "label": int(label),
                "size": int(coords.shape[0]),
                "t_min": int(t_min),
                "t_max": int(t_max),
                "time_span": int(t_max - t_min + 1),
                "x_min": int(x_min),
                "x_max": int(x_max),
                "x_span": int(x_max - x_min + 1),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["label", "size", "t_min", "t_max", "time_span", "x_min", "x_max", "x_span"])
    return pd.DataFrame.from_records(rows).sort_values(["time_span", "size"], ascending=False).reset_index(drop=True)
