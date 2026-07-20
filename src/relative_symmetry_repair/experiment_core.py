"""Plotting-free core of the ALIFE experiment suite.

Cases, search configs, simulation drivers, candidate scanning, and
period-first selection -- everything needed to regenerate the run-level
numbers in ``outputs/alife_2026`` without importing matplotlib. Extracted
from ``experiment_suite`` so lightweight environments (e.g. the in-browser
Pyodide reproduction demo) can import it.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import time
from typing import Any, Iterable, Literal, Sequence

import numpy as np
import pandas as pd

from .ca2d import parse_rulestring, random_initial_grid, simulate_2d, simulate_2d_general
from .ca3d import (
    RULES_3D,
    RULES_3D_DENSITY,
    parse_rulestring_3d,
    random_initial_volume,
    simulate_3d,
    simulate_3d_general,
)
from .eca import random_initial_state, simulate_eca
from .repair import RelativePeriodicFit, scan_relative_periodicity
from .repair_nd import RelativePeriodicFitND, scan_relative_periodicity_nd

ALIFE_OUTPUT_ROOT = Path("outputs/alife_2026")

DEFAULT_HORIZONS_1D_2D = (50, 100, 200, 400, 600, 800)
DEFAULT_HORIZONS_3D = (10, 20, 40, 60, 80)
DEFAULT_LIFEWIKI_HORIZONS = (100, 200, 400, 800)
DEFAULT_ECA_ATLAS_HORIZONS = (50, 100, 200, 400, 800)

NEAR_TIE_THRESHOLD_BITS = 2.0
VERY_SMALL_MARGIN_BITS = 0.5
TIE_TOLERANCE_BITS = 1e-9


CONTROL_ORDER = ["original", "time_shuffled", "space_shuffled", "bernoulli_iid"]
CONTROL_LABELS = {
    "original": "Original",
    "time_shuffled": "Time shuffled",
    "space_shuffled": "Space shuffled",
    "bernoulli_iid": "Bernoulli i.i.d.",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _lifewiki_rules_path() -> Path:
    return _repo_root() / "data" / "lifewiki_rules.json"


def _serialize_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _serialize_jsonable(inner) for key, inner in value.items()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_serialize_jsonable(inner) for inner in value]
    if isinstance(value, range):
        return list(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "to_manifest"):
        return _serialize_jsonable(value.to_manifest())
    return value


def _slugify(value: str) -> str:
    normalized = [
        char.lower() if char.isalnum() else "_"
        for char in value.strip()
    ]
    slug = "".join(normalized)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def _classify_margin(margin_bits: float) -> str:
    if margin_bits <= 0.0:
        return "unresolved"
    if margin_bits < NEAR_TIE_THRESHOLD_BITS:
        return "near_tie"
    return "stable_winner"


def iter_deterministic_seeds(base_seed: int, count: int) -> list[int]:
    if count < 1:
        raise ValueError("count must be >= 1")
    return [int(base_seed + index) for index in range(count)]


def ensure_output_dir(path: Path | str) -> Path:
    directory = Path(path)
    if directory.exists() and not directory.is_dir():
        raise NotADirectoryError(f"{directory} exists and is not a directory")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_summary_csv(frame: pd.DataFrame, path: Path | str) -> Path:
    csv_path = Path(path)
    ensure_output_dir(csv_path.parent)
    frame.to_csv(csv_path, index=False)
    return csv_path


def write_json_manifest(path: Path | str, payload: dict[str, Any]) -> Path:
    manifest_path = Path(path)
    ensure_output_dir(manifest_path.parent)
    manifest_path.write_text(
        json.dumps(_serialize_jsonable(payload), indent=2, sort_keys=True) + "\n"
    )
    return manifest_path


@dataclass(frozen=True, slots=True)
class SearchConfig:
    label: str
    periods: tuple[int, ...]
    shift_ranges: tuple[tuple[int, ...], ...]

    @property
    def dimension(self) -> int:
        return len(self.shift_ranges)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "periods": list(self.periods),
            "shift_ranges": [list(values) for values in self.shift_ranges],
        }


def make_search_config(
    dimension: int,
    *,
    shift_radius: int,
    max_period: int,
    label: str,
) -> SearchConfig:
    shifts = tuple(range(-int(shift_radius), int(shift_radius) + 1))
    return SearchConfig(
        label=label,
        periods=tuple(range(1, int(max_period) + 1)),
        shift_ranges=tuple(shifts for _ in range(int(dimension))),
    )


DEFAULT_SEARCH_1D = make_search_config(1, shift_radius=6, max_period=10, label="default_1d")
DEFAULT_SEARCH_2D = make_search_config(2, shift_radius=2, max_period=8, label="default_2d")
DEFAULT_SEARCH_3D = make_search_config(3, shift_radius=2, max_period=4, label="default_3d")

ROBUSTNESS_SEARCH_RANGES: dict[int, tuple[SearchConfig, ...]] = {
    1: (
        make_search_config(1, shift_radius=3, max_period=6, label="small"),
        DEFAULT_SEARCH_1D,
        make_search_config(1, shift_radius=10, max_period=16, label="large"),
    ),
    2: (
        make_search_config(2, shift_radius=1, max_period=4, label="small"),
        DEFAULT_SEARCH_2D,
        make_search_config(2, shift_radius=3, max_period=10, label="large"),
    ),
    3: (
        make_search_config(3, shift_radius=1, max_period=3, label="small"),
        DEFAULT_SEARCH_3D,
        make_search_config(3, shift_radius=2, max_period=6, label="large"),
    ),
}


@dataclass(frozen=True, slots=True)
class ALifeCase:
    slug: str
    name: str
    dimension: int
    family: Literal["eca", "life_range", "life_rulestring", "rule3d", "rule3d_general"]
    size: tuple[int, ...]
    density: float
    search: SearchConfig
    horizons: tuple[int, ...]
    rule_number: int | None = None
    rulestring: str | None = None
    survive: tuple[int, int] | None = None
    birth: tuple[int, int] | None = None

    def to_manifest(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["search"] = self.search.to_manifest()
        return payload


def eca_case(
    rule: int,
    *,
    width: int = 192,
    density: float = 0.5,
    horizons: Sequence[int] = DEFAULT_HORIZONS_1D_2D,
    search: SearchConfig = DEFAULT_SEARCH_1D,
) -> ALifeCase:
    return ALifeCase(
        slug=f"eca_{rule}",
        name=f"ECA-{rule}",
        dimension=1,
        family="eca",
        size=(int(width),),
        density=float(density),
        search=search,
        horizons=tuple(int(value) for value in horizons),
        rule_number=int(rule),
    )


def life_range_case(
    name: str,
    *,
    survive: tuple[int, int],
    birth: tuple[int, int],
    width: int = 64,
    height: int = 64,
    density: float = 0.5,
    horizons: Sequence[int] = DEFAULT_HORIZONS_1D_2D,
    search: SearchConfig = DEFAULT_SEARCH_2D,
) -> ALifeCase:
    return ALifeCase(
        slug=_slugify(name),
        name=name,
        dimension=2,
        family="life_range",
        size=(int(width), int(height)),
        density=float(density),
        search=search,
        horizons=tuple(int(value) for value in horizons),
        survive=(int(survive[0]), int(survive[1])),
        birth=(int(birth[0]), int(birth[1])),
    )


def life_rulestring_case(
    name: str,
    *,
    rulestring: str,
    width: int = 64,
    height: int = 64,
    density: float = 0.5,
    horizons: Sequence[int] = DEFAULT_HORIZONS_1D_2D,
    search: SearchConfig = DEFAULT_SEARCH_2D,
) -> ALifeCase:
    return ALifeCase(
        slug=_slugify(name),
        name=name,
        dimension=2,
        family="life_rulestring",
        size=(int(width), int(height)),
        density=float(density),
        search=search,
        horizons=tuple(int(value) for value in horizons),
        rulestring=rulestring,
    )


def rule3d_case(
    name: str,
    *,
    survive: tuple[int, int],
    birth: tuple[int, int],
    size: int = 16,
    density: float = 0.5,
    horizons: Sequence[int] = DEFAULT_HORIZONS_3D,
    search: SearchConfig = DEFAULT_SEARCH_3D,
) -> ALifeCase:
    return ALifeCase(
        slug=_slugify(name),
        name=name,
        dimension=3,
        family="rule3d",
        size=(int(size), int(size), int(size)),
        density=float(density),
        search=search,
        horizons=tuple(int(value) for value in horizons),
        survive=(int(survive[0]), int(survive[1])),
        birth=(int(birth[0]), int(birth[1])),
    )


def rule3d_general_case(
    name: str,
    *,
    rulestring: str,
    size: int = 16,
    density: float = 0.5,
    horizons: Sequence[int] = DEFAULT_HORIZONS_3D,
    search: SearchConfig = DEFAULT_SEARCH_3D,
) -> ALifeCase:
    """3D case with arbitrary birth/survive count sets, e.g. 'B5-7,9/S4,6-8'."""
    parse_rulestring_3d(rulestring)  # validate eagerly
    return ALifeCase(
        slug=_slugify(name),
        name=name,
        dimension=3,
        family="rule3d_general",
        size=(int(size), int(size), int(size)),
        density=float(density),
        search=search,
        horizons=tuple(int(value) for value in horizons),
        rulestring=rulestring,
    )


REPRESENTATIVE_CASES_1D = (
    eca_case(30),
    eca_case(54),
    eca_case(110),
)

REPRESENTATIVE_CASES_2D = (
    life_rulestring_case("Diamoeba", rulestring="B35678/S5678"),
    life_rulestring_case("Maze with Mice", rulestring="B37/S12345"),
    life_range_case("S24/B11", survive=(2, 4), birth=(1, 1)),
    life_range_case("S11/B37", survive=(1, 1), birth=(3, 7)),
    life_range_case("S37/B11", survive=(3, 7), birth=(1, 1)),
)

REPRESENTATIVE_CASES_3D = tuple(
    rule3d_case(
        name,
        survive=(values[0], values[1]),
        birth=(values[2], values[3]),
        density=RULES_3D_DENSITY.get(name, 0.5),
    )
    for name, values in RULES_3D.items()
)

REPRESENTATIVE_PANEL = (
    *REPRESENTATIVE_CASES_1D,
    *REPRESENTATIVE_CASES_2D,
    *REPRESENTATIVE_CASES_3D,
)


def all_3d_cases() -> tuple[ALifeCase, ...]:
    return REPRESENTATIVE_CASES_3D


def load_lifewiki_rules(limit: int | None = None) -> list[dict[str, Any]]:
    with open(_lifewiki_rules_path()) as handle:
        rules = json.load(handle)
    if limit is not None:
        rules = rules[: int(limit)]
    return list(rules)


def eca_atlas_cases(limit: int | None = None) -> tuple[ALifeCase, ...]:
    rules = list(range(256))
    if limit is not None:
        rules = rules[: int(limit)]
    return tuple(
        eca_case(rule, horizons=DEFAULT_ECA_ATLAS_HORIZONS)
        for rule in rules
    )


def shift_columns(frame: pd.DataFrame) -> list[str]:
    columns: list[str] = []
    if "shift" in frame.columns:
        columns.append("shift")
    columns.extend(sorted(column for column in frame.columns if column.startswith("shift_")))
    return columns


def shift_from_row(row: pd.Series | dict[str, Any], columns: Sequence[str]) -> int | tuple[int, ...]:
    if columns == ["shift"]:
        return int(row["shift"])
    return tuple(int(row[column]) for column in columns)


def shift_to_string(value: int | tuple[int, ...]) -> str:
    if isinstance(value, tuple):
        return str(tuple(int(inner) for inner in value))
    return str(int(value))


@dataclass(slots=True)
class FrameSelectionResult:
    selected_period: int
    selected_shift: int | tuple[int, ...]
    selected_nml_bits: float
    selected_nll_bits: float
    selected_complexity: float
    selected_defect_rate: float
    runner_up_period: int | None
    runner_up_nml_bits: float | None
    margin_bits: float
    status: str
    period_tie_count: int
    selected_shift_tie_count: int
    period_summary: pd.DataFrame
    selected_candidate: dict[str, Any]

    def to_record(self) -> dict[str, Any]:
        payload = {
            "selected_period": self.selected_period,
            "selected_shift_str": shift_to_string(self.selected_shift),
            "selected_nml_bits": self.selected_nml_bits,
            "selected_nll_bits": self.selected_nll_bits,
            "selected_complexity": self.selected_complexity,
            "selected_defect_rate": self.selected_defect_rate,
            "runner_up_period": self.runner_up_period,
            "runner_up_nml_bits": self.runner_up_nml_bits,
            "margin_bits": self.margin_bits,
            "status": self.status,
            "period_tie_count": self.period_tie_count,
            "selected_shift_tie_count": self.selected_shift_tie_count,
        }
        return payload


def period_first_selection_from_frame(
    frame: pd.DataFrame,
    *,
    score_column: str = "nml_bits",
    atol: float = TIE_TOLERANCE_BITS,
) -> FrameSelectionResult:
    if frame.empty:
        raise ValueError("No candidate rows available")
    if "period" not in frame.columns:
        raise ValueError("frame must include a 'period' column")
    if score_column not in frame.columns:
        raise ValueError(f"frame must include a '{score_column}' column")

    sh_columns = shift_columns(frame)
    period_rows: list[dict[str, Any]] = []

    for period, group in frame.groupby("period", sort=True):
        ordered = group.sort_values([score_column, *sh_columns], kind="mergesort").reset_index(drop=True)
        best = ordered.iloc[0]
        best_score = float(best[score_column])
        tie_count = int(
            np.isclose(
                ordered[score_column].to_numpy(dtype=float),
                best_score,
                atol=atol,
                rtol=0.0,
            ).sum()
        )
        period_row: dict[str, Any] = {
            "period": int(period),
            "nml_bits": float(best["nml_bits"]),
            "nll_bits": float(best["nll_bits"]),
            "nml_complexity": float(best["nml_complexity"]),
            "defect_rate": float(best["defect_rate"]),
            "n_shifts_scanned": int(len(group)),
            "shift_tie_count": tie_count,
        }
        for column in sh_columns:
            period_row[column] = int(best[column])
        period_rows.append(period_row)

    period_summary = pd.DataFrame.from_records(period_rows).sort_values(
        [score_column, "period", *sh_columns],
        kind="mergesort",
    ).reset_index(drop=True)
    period_summary["period_rank"] = np.arange(1, len(period_summary) + 1, dtype=np.int64)
    period_summary["best_shift_str"] = period_summary.apply(
        lambda row: shift_to_string(shift_from_row(row, sh_columns)),
        axis=1,
    )

    selected_row = period_summary.iloc[0]
    selected_score = float(selected_row[score_column])
    period_tie_count = int(
        np.isclose(
            period_summary[score_column].to_numpy(dtype=float),
            selected_score,
            atol=atol,
            rtol=0.0,
        ).sum()
    )
    runner_up = period_summary.iloc[1] if len(period_summary) > 1 else None
    margin_bits = (
        float(runner_up[score_column] - selected_score)
        if runner_up is not None
        else float("inf")
    )

    selected_period = int(selected_row["period"])
    selected_shift = shift_from_row(selected_row, sh_columns)
    candidate_frame = frame[frame["period"] == selected_period].sort_values(
        [score_column, *sh_columns],
        kind="mergesort",
    )
    selected_candidate = candidate_frame.iloc[0].to_dict()

    return FrameSelectionResult(
        selected_period=selected_period,
        selected_shift=selected_shift,
        selected_nml_bits=float(selected_row["nml_bits"]),
        selected_nll_bits=float(selected_row["nll_bits"]),
        selected_complexity=float(selected_row["nml_complexity"]),
        selected_defect_rate=float(selected_row["defect_rate"]),
        runner_up_period=int(runner_up["period"]) if runner_up is not None else None,
        runner_up_nml_bits=float(runner_up["nml_bits"]) if runner_up is not None else None,
        margin_bits=margin_bits,
        status=_classify_margin(margin_bits),
        period_tie_count=period_tie_count,
        selected_shift_tie_count=int(selected_row["shift_tie_count"]),
        period_summary=period_summary,
        selected_candidate=selected_candidate,
    )


@dataclass(slots=True)
class ScanOutcome:
    frame: pd.DataFrame
    fits: dict[Any, RelativePeriodicFit | RelativePeriodicFitND]
    selection: FrameSelectionResult
    best_fit: RelativePeriodicFit | RelativePeriodicFitND


def simulate_case(case: ALifeCase, *, steps: int, seed: int) -> np.ndarray:
    if case.family == "eca":
        initial = random_initial_state(case.size[0], density=case.density, seed=seed)
        return simulate_eca(int(case.rule_number), initial, int(steps))

    if case.family == "life_range":
        initial = random_initial_grid(case.size[0], case.size[1], density=case.density, seed=seed)
        return simulate_2d(
            initial,
            steps=int(steps),
            rule="custom",
            survive=case.survive,
            birth=case.birth,
        )

    if case.family == "life_rulestring":
        birth_counts, survive_counts = parse_rulestring(str(case.rulestring))
        initial = random_initial_grid(case.size[0], case.size[1], density=case.density, seed=seed)
        return simulate_2d_general(
            initial,
            steps=int(steps),
            birth=birth_counts,
            survive=survive_counts,
        )

    if case.family == "rule3d":
        initial = random_initial_volume(
            sx=case.size[0],
            sy=case.size[1],
            sz=case.size[2],
            density=case.density,
            seed=seed,
        )
        return simulate_3d(
            initial,
            steps=int(steps),
            rule="custom",
            survive=case.survive,
            birth=case.birth,
        )

    if case.family == "rule3d_general":
        birth_counts, survive_counts = parse_rulestring_3d(str(case.rulestring))
        initial = random_initial_volume(
            sx=case.size[0],
            sy=case.size[1],
            sz=case.size[2],
            density=case.density,
            seed=seed,
        )
        return simulate_3d_general(
            initial,
            steps=int(steps),
            birth=birth_counts,
            survive=survive_counts,
        )

    raise ValueError(f"Unsupported family: {case.family}")


def scan_case_spacetime(
    case: ALifeCase,
    spacetime: np.ndarray,
    *,
    search: SearchConfig | None = None,
    nml_mode: str = "hybrid",
) -> ScanOutcome:
    active_search = search or case.search
    if case.dimension == 1:
        frame, fits = scan_relative_periodicity(
            spacetime,
            shifts=active_search.shift_ranges[0],
            periods=active_search.periods,
            rule=case.rule_number,
            nml_mode=nml_mode,
        )
        selection = period_first_selection_from_frame(frame)
        key = (int(selection.selected_shift), int(selection.selected_period))
    else:
        frame, fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=active_search.shift_ranges,
            periods=active_search.periods,
            nml_mode=nml_mode,
        )
        selection = period_first_selection_from_frame(frame)
        key = (tuple(int(value) for value in selection.selected_shift), int(selection.selected_period))
    best_fit = fits[key]
    return ScanOutcome(frame=frame, fits=fits, selection=selection, best_fit=best_fit)


def time_shuffled_control(spacetime: np.ndarray, *, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    order = rng.permutation(spacetime.shape[0])
    return spacetime[order].astype(np.uint8, copy=False)


def space_shuffled_control(spacetime: np.ndarray, *, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    control = np.empty_like(spacetime, dtype=np.uint8)
    flat_size = int(np.prod(spacetime.shape[1:]))
    for time_index in range(spacetime.shape[0]):
        flattened = spacetime[time_index].reshape(flat_size).copy()
        rng.shuffle(flattened)
        control[time_index] = flattened.reshape(spacetime.shape[1:]).astype(np.uint8, copy=False)
    return control


def bernoulli_iid_control(spacetime: np.ndarray, *, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    density = float(spacetime.mean())
    return (rng.random(spacetime.shape) < density).astype(np.uint8)


def make_null_controls(spacetime: np.ndarray, *, seed: int) -> dict[str, np.ndarray]:
    return {
        "original": spacetime.astype(np.uint8, copy=False),
        "time_shuffled": time_shuffled_control(spacetime, seed=seed + 101),
        "space_shuffled": space_shuffled_control(spacetime, seed=seed + 202),
        "bernoulli_iid": bernoulli_iid_control(spacetime, seed=seed + 303),
    }


class ResumeTable:
    def __init__(
        self,
        path: Path | str,
        *,
        key_columns: Sequence[str],
        sort_columns: Sequence[str] | None = None,
        resume: bool = True,
    ) -> None:
        self.path = Path(path)
        self.key_columns = tuple(key_columns)
        self.sort_columns = tuple(sort_columns or key_columns)
        self.resume = bool(resume)
        self._pending: list[dict[str, Any]] = []

        if self.resume and self.path.exists():
            self._frame = pd.read_csv(self.path)
        else:
            self._frame = pd.DataFrame()
        self._keys = self._build_keys(self._frame)

    def _build_keys(self, frame: pd.DataFrame) -> set[tuple[Any, ...]]:
        if frame.empty:
            return set()
        missing = [column for column in self.key_columns if column not in frame.columns]
        if missing:
            return set()
        keys: set[tuple[Any, ...]] = set()
        for row in frame[list(self.key_columns)].itertuples(index=False, name=None):
            keys.add(tuple(row))
        return keys

    def has_key(self, record: dict[str, Any]) -> bool:
        return tuple(record[column] for column in self.key_columns) in self._keys

    def add(self, record: dict[str, Any]) -> bool:
        key = tuple(record[column] for column in self.key_columns)
        if key in self._keys:
            return False
        self._keys.add(key)
        self._pending.append(record)
        return True

    def extend(self, records: Iterable[dict[str, Any]]) -> int:
        added = 0
        for record in records:
            added += int(self.add(record))
        return added

    def dataframe(self) -> pd.DataFrame:
        if not self._pending:
            return self._frame.copy()
        pending_frame = pd.DataFrame.from_records(self._pending)
        if self._frame.empty:
            combined = pending_frame
        else:
            combined = pd.concat([self._frame, pending_frame], ignore_index=True)
        if self.sort_columns:
            combined = combined.sort_values(list(self.sort_columns), kind="mergesort").reset_index(drop=True)
        return combined

    def flush(self) -> pd.DataFrame:
        frame = self.dataframe()
        if not frame.empty:
            write_summary_csv(frame, self.path)
        self._frame = frame
        self._pending = []
        return frame


def _record_base(case: ALifeCase, *, seed: int, horizon: int | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "rule": case.name,
        "rule_slug": case.slug,
        "dimension": case.dimension,
        "family": case.family,
        "seed": int(seed),
        "density": float(case.density),
    }
    if horizon is not None:
        payload["horizon"] = int(horizon)
    return payload


def _add_selection_metrics(
    payload: dict[str, Any],
    selection: FrameSelectionResult,
) -> dict[str, Any]:
    payload.update(selection.to_record())
    return payload


def _grouped_summary(
    frame: pd.DataFrame,
    *,
    group_columns: Sequence[str],
    margin_column: str = "margin_bits",
) -> pd.DataFrame:
    grouped = frame.groupby(list(group_columns), dropna=False)
    summary = grouped.agg(
        runs=("rule", "size"),
        mean_selected_period=("selected_period", "mean"),
        median_selected_period=("selected_period", "median"),
        mean_margin_bits=(margin_column, "mean"),
        median_margin_bits=(margin_column, "median"),
        mean_defect_rate=("selected_defect_rate", "mean"),
        median_defect_rate=("selected_defect_rate", "median"),
        stable_winner_fraction=("status", lambda values: float((pd.Series(values) == "stable_winner").mean())),
        nonunique_period_fraction=("period_tie_count", lambda values: float((pd.Series(values) > 1).mean())),
        nonunique_shift_fraction=("selected_shift_tie_count", lambda values: float((pd.Series(values) > 1).mean())),
    ).reset_index()
    return summary.sort_values(list(group_columns), kind="mergesort").reset_index(drop=True)


