"""Structured reading of a selected relative-periodic template.

The in-browser reproduction demo (``webdemo/reproduce.html``) answers two
questions. "Did this browser regenerate the committed row?" is a
column-by-column comparison. "What does the selected template actually say
about this run?" is an *interpretation* -- and an interpretation that lives
only in page JavaScript is a second implementation of the pipeline's own
thresholds: one that no test covers, and one that silently disagrees with
:mod:`relative_symmetry_repair.experiment_core` the moment a threshold there
changes.

This module is that interpretation, in Python, next to the code it reads:

- every threshold is *imported* from :mod:`experiment_core` rather than
  restated, so there is exactly one definition of "near tie" in the project;
- every decision is a pure function of the run-level record, the period
  summary, and the per-frame defect counts -- no arrays, no pandas, no
  plotting, so it imports cleanly under WebAssembly Python and is trivially
  testable;
- the page is left with rendering. ``webdemo/bootstrap.py`` calls
  :func:`build_reading` and ships the result in the ``run_repro`` payload;
  ``reproduce.html`` reads decisions and numbers off that payload.

The payload crosses into the page as ``json.dumps`` -> ``JSON.parse``, which
rejects the bare ``Infinity`` that Python's ``json`` emits for a non-finite
float. :func:`build_reading` therefore returns a strictly JSON-safe payload:
non-finite floats become ``None``, and callers branch on the ``kind`` fields
rather than re-testing finiteness themselves.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any, Literal, Mapping, Sequence

from .experiment_core import (
    NEAR_TIE_THRESHOLD_BITS,
    TIE_TOLERANCE_BITS,
    VERY_SMALL_MARGIN_BITS,
    _classify_margin,
)

__all__ = [
    "DEFECT_RATE_TOLERANCE",
    "DENSE_MASK_SHARE",
    "MIN_TREND_FRAMES",
    "NEAR_EXACT_SITES_PER_FRAME",
    "TREND_BAND",
    "ConsistencyCheck",
    "CostReading",
    "ComplexityReading",
    "ConfidenceReading",
    "DefectDynamics",
    "TemplateReading",
    "build_reading",
    "classify_defect_dynamics",
    "parse_shift",
    "read_complexity",
    "read_confidence",
    "read_cost",
    "read_template",
    "thresholds",
]


# --- Thresholds owned by this module -----------------------------------------
#
# The tie thresholds above are imported, not redefined. The four below are
# genuinely about *reading a mask over time* -- the selector has no opinion on
# them -- so they are defined here and exported to the page rather than being
# spelled into prose at two sites.

#: Above this share of a frame, a steady mask is dense rather than a sparse
#: set of localized departures from the domain.
DENSE_MASK_SHARE = 0.10

#: A monotone move across the trend window is only called a trend when the
#: end-to-end change exceeds this fraction of the opening block mean.
TREND_BAND = 0.25

#: Fewer frames than this in the trend window cannot separate a trend from
#: fluctuation, so no direction is claimed at all.
MIN_TREND_FRAMES = 9

#: Mean defect sites per frame below which the closing window counts as
#: "all but empty" rather than as a surviving defect population.
NEAR_EXACT_SITES_PER_FRAME = 0.5

#: The rendered mask must carry exactly the defect rate that was scored.
DEFECT_RATE_TOLERANCE = 1e-9


TemplateKind = Literal[
    "static_period_1", "rigid_drift", "static_periodic", "drifting_periodic"
]
ConfidenceKind = Literal["no_alternative", "stable_winner", "near_tie", "unresolved"]
GainKind = Literal["clear", "thin", "negative"]
DefectKind = Literal[
    "no_series",
    "exact",
    "transient",
    "near_exact",
    "growing",
    "decaying",
    "too_short",
    "dense",
    "persistent",
]

#: Bootstrap badge class and label for each defect-dynamics kind. Kept beside
#: the classifier so a new kind cannot reach the page without a badge.
DEFECT_BADGES: dict[str, tuple[str, str]] = {
    "no_series": ("text-bg-secondary", "NO DEFECT SERIES"),
    "exact": ("text-bg-success", "EXACT DOMAIN"),
    "transient": ("text-bg-success", "EXACT DOMAIN"),
    "near_exact": ("text-bg-success", "NEAR-EXACT DOMAIN"),
    "growing": ("text-bg-warning", "DEFECTS GROWING"),
    "decaying": ("text-bg-secondary", "STILL RELAXING"),
    "too_short": ("text-bg-primary", "DEFECTS PRESENT"),
    "dense": ("text-bg-warning", "DENSE DEFECT MASK"),
    "persistent": ("text-bg-primary", "PERSISTENT DEFECTS"),
}


def thresholds() -> dict[str, float]:
    """Every threshold the page quotes, from the modules that own them."""
    return {
        "near_tie_bits": float(NEAR_TIE_THRESHOLD_BITS),
        "very_small_margin_bits": float(VERY_SMALL_MARGIN_BITS),
        "tie_tolerance_bits": float(TIE_TOLERANCE_BITS),
        "dense_mask_share": float(DENSE_MASK_SHARE),
        "trend_band": float(TREND_BAND),
        "min_trend_frames": int(MIN_TREND_FRAMES),
        "near_exact_sites_per_frame": float(NEAR_EXACT_SITES_PER_FRAME),
        "defect_rate_tolerance": float(DEFECT_RATE_TOLERANCE),
    }


def _finite(value: Any) -> float | None:
    """A float that survives ``json.dumps`` -> ``JSON.parse``, else ``None``."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _mean(values: Sequence[float]) -> float:
    return (sum(values) / len(values)) if len(values) else 0.0


def parse_shift(value: Any) -> tuple[int, ...]:
    """Read a displacement out of a ``selected_shift_str`` cell.

    Accepts both the 1D scalar form (``"-3"``) and the ND tuple form
    (``"(-1, 2)"``), matching how the selection record is written to CSV.
    """
    if isinstance(value, (list, tuple)):
        return tuple(int(component) for component in value)
    return tuple(int(match) for match in re.findall(r"-?\d+", str(value)))


# --- Which template won -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TemplateReading:
    kind: TemplateKind
    period: int
    shift: tuple[int, ...]
    shift_tie_count: int
    shift_identified: bool
    moving: bool
    velocity: tuple[float, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "period": self.period,
            "shift": list(self.shift),
            "shift_tie_count": self.shift_tie_count,
            "shift_identified": self.shift_identified,
            "moving": self.moving,
            "velocity": [_finite(v) for v in self.velocity],
        }


def read_template(record: Mapping[str, Any]) -> TemplateReading:
    """Classify the winning candidate as a kind of domain.

    A displacement that only won a tie-break carries no information: several
    displacements scored identically and one was picked by scan order, so a
    non-zero ``s`` must not be read as motion unless it is identified.
    """
    period = int(record["selected_period"])
    shift = parse_shift(record.get("selected_shift_str", record.get("selected_shift", ())))
    shift_tie_count = int(record.get("selected_shift_tie_count", 1))
    identified = shift_tie_count <= 1
    moving = identified and any(component != 0 for component in shift)

    if period == 1 and not moving:
        kind: TemplateKind = "static_period_1"
    elif period == 1:
        kind = "rigid_drift"
    elif not moving:
        kind = "static_periodic"
    else:
        kind = "drifting_periodic"

    velocity = tuple(component / period for component in shift) if period else ()
    return TemplateReading(
        kind=kind,
        period=period,
        shift=shift,
        shift_tie_count=shift_tie_count,
        shift_identified=identified,
        moving=moving,
        velocity=velocity,
    )


# --- How much the selection is worth ------------------------------------------


@dataclass(frozen=True, slots=True)
class ConfidenceReading:
    kind: ConfidenceKind
    margin_bits: float
    runner_up_period: int | None
    period_tie_count: int
    shift_tie_count: int
    shift_identified: bool
    below_very_small_margin: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "margin_bits": _finite(self.margin_bits),
            "runner_up_period": self.runner_up_period,
            "period_tie_count": self.period_tie_count,
            "shift_tie_count": self.shift_tie_count,
            "shift_identified": self.shift_identified,
            "below_very_small_margin": self.below_very_small_margin,
        }


def read_confidence(record: Mapping[str, Any]) -> ConfidenceReading:
    """Grade the margin between the winner and the best alternative.

    The ``status`` already on the record is authoritative when present -- it is
    what the suite wrote to CSV -- and is otherwise recomputed with
    ``experiment_core``'s own classifier, never with a restated threshold.
    """
    raw_margin = record.get("margin_bits")
    try:
        margin = float(raw_margin)
    except (TypeError, ValueError):
        margin = float("nan")
    runner_up = record.get("runner_up_period")
    runner_up = None if runner_up is None or (isinstance(runner_up, float) and math.isnan(runner_up)) else int(runner_up)

    if runner_up is None or not math.isfinite(margin):
        kind: ConfidenceKind = "no_alternative"
    else:
        status = record.get("status") or _classify_margin(margin)
        kind = {
            "stable_winner": "stable_winner",
            "near_tie": "near_tie",
            "unresolved": "unresolved",
        }.get(str(status), "unresolved")

    return ConfidenceReading(
        kind=kind,
        margin_bits=margin,
        runner_up_period=runner_up,
        period_tie_count=int(record.get("period_tie_count", 1)),
        shift_tie_count=int(record.get("selected_shift_tie_count", 1)),
        shift_identified=int(record.get("selected_shift_tie_count", 1)) <= 1,
        below_very_small_margin=math.isfinite(margin) and margin < VERY_SMALL_MARGIN_BITS,
    )


# --- What the template cost ---------------------------------------------------


@dataclass(frozen=True, slots=True)
class CostReading:
    frames: int
    cells_per_frame: int
    n_sites: int
    defect_sites: int
    defect_rate: float
    coverage: float
    nml_bits: float
    nll_bits: float
    complexity_bits: float
    n_candidates: int
    index_bits: float
    bits_per_site: float
    compresses: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "frames": self.frames,
            "cells_per_frame": self.cells_per_frame,
            "n_sites": self.n_sites,
            "defect_sites": self.defect_sites,
            "defect_rate": _finite(self.defect_rate),
            "coverage": _finite(self.coverage),
            "nml_bits": _finite(self.nml_bits),
            "nll_bits": _finite(self.nll_bits),
            "complexity_bits": _finite(self.complexity_bits),
            "n_candidates": self.n_candidates,
            "index_bits": _finite(self.index_bits),
            "bits_per_site": _finite(self.bits_per_site),
            "compresses": self.compresses,
        }


def read_cost(
    record: Mapping[str, Any],
    *,
    n_sites: int,
    frames: int,
    defect_sites: int,
    n_candidates: int,
) -> CostReading:
    """Total description length per site, against the 1 bit/site raw baseline.

    The NML score is conditional on the winning candidate, so a fair comparison
    against raw storage also pays ``log2(n_candidates)`` bits to name which
    candidate the search chose.
    """
    n_sites = int(n_sites)
    frames = int(frames)
    n_candidates = max(1, int(n_candidates))
    index_bits = math.log2(n_candidates)
    nml_bits = float(record["selected_nml_bits"])
    bits_per_site = (nml_bits + index_bits) / n_sites if n_sites else float("inf")
    defect_rate = float(record["selected_defect_rate"])
    return CostReading(
        frames=frames,
        cells_per_frame=(n_sites // frames) if frames else 0,
        n_sites=n_sites,
        defect_sites=int(defect_sites),
        defect_rate=defect_rate,
        coverage=1.0 - defect_rate,
        nml_bits=nml_bits,
        nll_bits=float(record["selected_nll_bits"]),
        complexity_bits=float(record["selected_complexity"]),
        n_candidates=n_candidates,
        index_bits=index_bits,
        bits_per_site=bits_per_site,
        compresses=bits_per_site < 1.0,
    )


# --- What the complexity term bought ------------------------------------------


@dataclass(frozen=True, slots=True)
class ComplexityReading:
    selected_period: int
    best_nll_period: int
    max_period: int
    best_nll_is_max_period: bool
    fit_agrees: bool
    period_1_gain_bits: float | None
    period_1_shift_str: str | None
    gain_kind: GainKind | None
    runner_up_period: int | None
    margin_bits: float

    def to_payload(self) -> dict[str, Any]:
        return {
            "selected_period": self.selected_period,
            "best_nll_period": self.best_nll_period,
            "max_period": self.max_period,
            "best_nll_is_max_period": self.best_nll_is_max_period,
            "fit_agrees": self.fit_agrees,
            "period_1_gain_bits": _finite(self.period_1_gain_bits)
            if self.period_1_gain_bits is not None
            else None,
            "period_1_shift_str": self.period_1_shift_str,
            "gain_kind": self.gain_kind,
            "runner_up_period": self.runner_up_period,
            "margin_bits": _finite(self.margin_bits),
        }


def read_complexity(
    record: Mapping[str, Any],
    period_summary: Sequence[Mapping[str, Any]],
) -> ComplexityReading | None:
    """Contrast the NLL-only ranking with the penalized (NML) ranking.

    Returns ``None`` when there is no period summary to rank, which is the one
    case where nothing can be said about what the penalty did.
    """
    rows = list(period_summary)
    if not rows:
        return None

    selected_period = int(record["selected_period"])
    best_nll_row = min(rows, key=lambda row: float(row["nll_bits"]))
    max_period = max(int(row["period"]) for row in rows)
    period_1 = next((row for row in rows if int(row["period"]) == 1), None)

    gain: float | None = None
    gain_kind: GainKind | None = None
    if selected_period > 1 and period_1 is not None:
        gain = float(period_1["nml_bits"]) - float(record["selected_nml_bits"])
        if gain > NEAR_TIE_THRESHOLD_BITS:
            gain_kind = "clear"
        elif gain > 0:
            gain_kind = "thin"
        else:
            gain_kind = "negative"

    runner_up = record.get("runner_up_period")
    runner_up = None if runner_up is None or (isinstance(runner_up, float) and math.isnan(runner_up)) else int(runner_up)
    try:
        margin = float(record.get("margin_bits"))
    except (TypeError, ValueError):
        margin = float("nan")

    best_nll_period = int(best_nll_row["period"])
    return ComplexityReading(
        selected_period=selected_period,
        best_nll_period=best_nll_period,
        max_period=max_period,
        best_nll_is_max_period=best_nll_period == max_period and max_period > 1,
        fit_agrees=best_nll_period == selected_period,
        period_1_gain_bits=gain,
        period_1_shift_str=str(period_1["best_shift_str"]) if period_1 is not None else None,
        gain_kind=gain_kind,
        runner_up_period=runner_up,
        margin_bits=margin,
    )


# --- What the mask did over time ----------------------------------------------


@dataclass(frozen=True, slots=True)
class DefectDynamics:
    kind: DefectKind
    badge_class: str
    badge_label: str
    frames: int
    window_frames: int
    thirds: tuple[float, float, float]
    level: float
    end_level: float
    end_frames: int
    empty_end_frames: int
    change: float
    rising: bool
    falling: bool
    enough_frames: bool
    tail_share: float
    peak: int
    peak_at: int
    final_count: int
    last_defect_index: int | None
    settled: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "badge_class": self.badge_class,
            "badge_label": self.badge_label,
            "frames": self.frames,
            "window_frames": self.window_frames,
            "thirds": [_finite(v) for v in self.thirds],
            "level": _finite(self.level),
            "end_level": _finite(self.end_level),
            "end_frames": self.end_frames,
            "empty_end_frames": self.empty_end_frames,
            # ``change`` is unbounded when the window opens empty; the page
            # renders ">999%" for a null rather than parsing an Infinity.
            "change": _finite(self.change),
            "rising": self.rising,
            "falling": self.falling,
            "enough_frames": self.enough_frames,
            "tail_share": _finite(self.tail_share),
            "peak": self.peak,
            "peak_at": self.peak_at,
            "final_count": self.final_count,
            "last_defect_index": self.last_defect_index,
            "settled": self.settled,
        }


def classify_defect_dynamics(
    series: Sequence[int],
    cells_per_frame: int | float,
) -> DefectDynamics:
    """Classify a per-frame defect count series.

    The trend is read off the second half of the run only -- the first half is
    where the transient lives -- split into thirds. A direction is claimed only
    when the thirds are monotone *and* the end-to-end change exceeds
    :data:`TREND_BAND`; a single quarter-vs-quarter comparison flags noise as
    trend. Windows shorter than :data:`MIN_TREND_FRAMES` get no trend claim.
    """
    counts = [int(value) for value in series]
    frames = len(counts)
    if not frames:
        badge_class, badge_label = DEFECT_BADGES["no_series"]
        return DefectDynamics(
            kind="no_series",
            badge_class=badge_class,
            badge_label=badge_label,
            frames=0,
            window_frames=0,
            thirds=(0.0, 0.0, 0.0),
            level=0.0,
            end_level=0.0,
            end_frames=0,
            empty_end_frames=0,
            change=0.0,
            rising=False,
            falling=False,
            enough_frames=False,
            tail_share=0.0,
            peak=0,
            peak_at=-1,
            final_count=0,
            last_defect_index=None,
            settled=False,
        )

    quarter = max(1, frames // 4)
    tail = counts[frames - quarter :]
    window = counts[frames // 2 :]
    block = len(window) // 3
    if block >= 1:
        thirds = (
            _mean(window[:block]),
            _mean(window[block : 2 * block]),
            _mean(window[2 * block :]),
        )
        end_frames = len(window) - 2 * block
    else:
        window_mean = _mean(window)
        thirds = (window_mean, window_mean, window_mean)
        end_frames = len(window)

    level = _mean(window)
    end_level = thirds[2]
    enough = len(window) >= MIN_TREND_FRAMES
    if thirds[0] > 0:
        change = (thirds[2] - thirds[0]) / thirds[0]
    else:
        change = math.inf if thirds[2] > 0 else 0.0
    rising = thirds[0] <= thirds[1] <= thirds[2]
    falling = thirds[0] >= thirds[1] >= thirds[2]
    tail_share = (level / cells_per_frame) if cells_per_frame else 0.0
    peak = max(counts)
    peak_at = counts.index(peak)
    end_window = counts[frames - end_frames :] if end_frames else []
    empty_end_frames = sum(1 for value in end_window if value == 0)
    last_defect_index = next(
        (index for index in range(frames - 1, -1, -1) if counts[index] > 0), None
    )
    settled = thirds[0] >= 1 and end_level < thirds[0] / 2

    if all(value == 0 for value in tail):
        kind: DefectKind = "exact" if last_defect_index is None else "transient"
    elif end_level < NEAR_EXACT_SITES_PER_FRAME:
        kind = "near_exact"
    elif enough and rising and change > TREND_BAND:
        kind = "growing"
    elif enough and falling and change < -TREND_BAND:
        kind = "decaying"
    elif not enough:
        kind = "too_short"
    elif tail_share >= DENSE_MASK_SHARE:
        kind = "dense"
    else:
        kind = "persistent"

    badge_class, badge_label = DEFECT_BADGES[kind]
    return DefectDynamics(
        kind=kind,
        badge_class=badge_class,
        badge_label=badge_label,
        frames=frames,
        window_frames=len(window),
        thirds=thirds,
        level=level,
        end_level=end_level,
        end_frames=end_frames,
        empty_end_frames=empty_end_frames,
        change=change,
        rising=rising,
        falling=falling,
        enough_frames=enough,
        tail_share=tail_share,
        peak=peak,
        peak_at=peak_at,
        final_count=counts[-1],
        last_defect_index=last_defect_index,
        settled=settled,
    )


# --- The mask on the page must be the mask that was scored --------------------


@dataclass(frozen=True, slots=True)
class ConsistencyCheck:
    defect_sites: int
    n_sites: int
    implied_rate: float
    recorded_rate: float
    ok: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "defect_sites": self.defect_sites,
            "n_sites": self.n_sites,
            "implied_rate": _finite(self.implied_rate),
            "recorded_rate": _finite(self.recorded_rate),
            "ok": self.ok,
        }


def check_defect_rate(
    record: Mapping[str, Any], *, defect_sites: int, n_sites: int
) -> ConsistencyCheck:
    """Invariant: the mask shipped to the page carries the rate that was scored.

    Any disagreement means the rendered fields and the selection record came
    from different fits, which is a bug worth surfacing on the page rather than
    rounding away.
    """
    implied = (defect_sites / n_sites) if n_sites else 0.0
    recorded = float(record["selected_defect_rate"])
    return ConsistencyCheck(
        defect_sites=int(defect_sites),
        n_sites=int(n_sites),
        implied_rate=implied,
        recorded_rate=recorded,
        ok=abs(implied - recorded) <= DEFECT_RATE_TOLERANCE,
    )


# --- The whole reading --------------------------------------------------------


def build_reading(
    *,
    record: Mapping[str, Any],
    period_summary: Sequence[Mapping[str, Any]],
    defects_per_frame: Sequence[int],
    shape: Sequence[int],
    n_candidates: int,
    dimension: int,
) -> dict[str, Any]:
    """Assemble the JSON-safe reading payload the demo page renders.

    ``shape`` is the observed space-time shape ``(T, ...)``; ``n_sites`` is its
    product, so coverage is quoted over every observed site including the
    transient, matching ``selected_defect_rate``.
    """
    dims = [int(value) for value in shape]
    n_sites = math.prod(dims) if dims else 0
    frames = dims[0] if dims else 0
    defect_sites = int(sum(int(value) for value in defects_per_frame))
    cells_per_frame = (n_sites // frames) if frames else 0

    template = read_template(record)
    confidence = read_confidence(record)
    cost = read_cost(
        record,
        n_sites=n_sites,
        frames=frames,
        defect_sites=defect_sites,
        n_candidates=n_candidates,
    )
    complexity = read_complexity(record, period_summary)
    dynamics = classify_defect_dynamics(defects_per_frame, cells_per_frame)
    consistency = check_defect_rate(record, defect_sites=defect_sites, n_sites=n_sites)

    periods = [int(row["period"]) for row in period_summary]
    return {
        "dimension": int(dimension),
        "template": template.to_payload(),
        "confidence": confidence.to_payload(),
        "cost": cost.to_payload(),
        "complexity": complexity.to_payload() if complexity is not None else None,
        "defects": dynamics.to_payload(),
        "consistency": consistency.to_payload(),
        "grid": {
            "min_period": min(periods) if periods else None,
            "max_period": max(periods) if periods else None,
            "n_candidates": int(n_candidates),
        },
        "thresholds": thresholds(),
    }
