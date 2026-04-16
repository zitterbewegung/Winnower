from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import time
from typing import Any, Iterable, Literal, Sequence

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import numpy as np
import pandas as pd

from .alife_style import BACKGROUND_COLOR, TEXT_COLOR
from .ca2d import parse_rulestring, random_initial_grid, simulate_2d, simulate_2d_general
from .ca3d import RULES_3D, RULES_3D_DENSITY, random_initial_volume, simulate_3d
from .eca import random_initial_state, simulate_eca
from .plotting import plot_decomposition, save_figure
from .plotting_nd import (
    plot_2d_decomposition,
    plot_3d_decomposition,
    plot_3d_volume_decomposition,
    plot_3d_volume_montage,
)
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

PLOT_RC = {
    "font.family": "DejaVu Serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": BACKGROUND_COLOR,
    "figure.facecolor": BACKGROUND_COLOR,
    "savefig.facecolor": BACKGROUND_COLOR,
    "savefig.edgecolor": BACKGROUND_COLOR,
    "text.color": TEXT_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "axes.titlecolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
}

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
    family: Literal["eca", "life_range", "life_rulestring", "rule3d"]
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


def _save_decomposition(
    case: ALifeCase,
    spacetime: np.ndarray,
    fit: RelativePeriodicFit | RelativePeriodicFitND,
    path: Path,
) -> None:
    if case.dimension == 1:
        fig, _ = plot_decomposition(fit, source=spacetime, title_prefix=f"{case.name} ")
    elif case.dimension == 2:
        fig, _ = plot_2d_decomposition(fit, source=spacetime, title_prefix=f"{case.name} ")
    else:
        fig, _ = plot_3d_decomposition(fit, source=spacetime, title_prefix=f"{case.name} ")
    save_figure(fig, path)
    plt.close(fig)


def _plot_grouped_bars(
    frame: pd.DataFrame,
    *,
    value_column: str,
    title: str,
    ylabel: str,
    path: Path,
) -> None:
    with plt.rc_context(PLOT_RC):
        dimensions = sorted(frame["dimension"].unique())
        controls = [control for control in CONTROL_ORDER if control in set(frame["control_type"])]
        x = np.arange(len(dimensions))
        width = 0.18
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        for index, control in enumerate(controls):
            subset = frame[frame["control_type"] == control]
            values = []
            for dimension in dimensions:
                match = subset[subset["dimension"] == dimension]
                values.append(float(match[value_column].iloc[0]) if not match.empty else np.nan)
            ax.bar(
                x + (index - (len(controls) - 1) / 2.0) * width,
                values,
                width=width,
                label=CONTROL_LABELS[control],
            )
        ax.set_xticks(x)
        ax.set_xticklabels([f"{dimension}D" for dimension in dimensions])
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(frameon=False, ncol=2)
        fig.tight_layout()
        save_figure(fig, path)
        plt.close(fig)


def run_null_controls_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    cases: Sequence[ALifeCase] | None = None,
    base_seed: int = 11,
    n_seeds: int = 1,
    resume: bool = True,
    save_decompositions: bool = False,
    max_decompositions: int = 6,
    nml_mode: str = "hybrid",
) -> dict[str, Any]:
    started = time.time()
    cases = tuple(cases or REPRESENTATIVE_PANEL)
    output_dir = ensure_output_dir(Path(output_root) / "null_controls")
    decomposition_dir = ensure_output_dir(output_dir / "decompositions") if save_decompositions else None
    seed_values = iter_deterministic_seeds(base_seed, n_seeds)

    rule_level_path = output_dir / "null_controls_rule_level.csv"
    table = ResumeTable(
        rule_level_path,
        key_columns=("rule", "seed", "control_type"),
        sort_columns=("dimension", "rule", "seed", "control_type"),
        resume=resume,
    )

    saved_decompositions = 0
    for case in cases:
        horizon = int(max(case.horizons))
        for seed in seed_values:
            if all(
                table.has_key({"rule": case.name, "seed": seed, "control_type": control})
                for control in CONTROL_ORDER
            ):
                continue
            spacetime = simulate_case(case, steps=horizon, seed=seed)
            controls = make_null_controls(spacetime, seed=seed)
            batch: list[dict[str, Any]] = []
            for control_index, control_name in enumerate(CONTROL_ORDER):
                control_spacetime = controls[control_name]
                outcome = scan_case_spacetime(case, control_spacetime, search=case.search, nml_mode=nml_mode)
                record = _record_base(case, seed=seed, horizon=horizon)
                record["control_type"] = control_name
                record["control_label"] = CONTROL_LABELS[control_name]
                record["control_seed"] = int(seed + control_index * 101) if control_index > 0 else None
                record["observed_density"] = float(control_spacetime.mean())
                _add_selection_metrics(record, outcome.selection)
                batch.append(record)

                if save_decompositions and decomposition_dir is not None and saved_decompositions < max_decompositions:
                    filename = f"{case.slug}_seed{seed}_{control_name}.png"
                    _save_decomposition(case, control_spacetime, outcome.best_fit, decomposition_dir / filename)
                    saved_decompositions += 1
            table.extend(batch)
            table.flush()

    rule_level = table.flush()
    summary = _grouped_summary(rule_level, group_columns=("dimension", "control_type", "control_label"))
    summary_path = write_summary_csv(summary, output_dir / "null_controls_summary.csv")

    margin_plot_path = output_dir / "null_controls_margin.png"
    defect_plot_path = output_dir / "null_controls_defect_rate.png"
    _plot_grouped_bars(
        summary,
        value_column="mean_margin_bits",
        title="Null controls: mean winner margin",
        ylabel="Mean winner margin (bits)",
        path=margin_plot_path,
    )
    _plot_grouped_bars(
        summary,
        value_column="mean_defect_rate",
        title="Null controls: mean defect rate",
        ylabel="Mean defect rate",
        path=defect_plot_path,
    )

    manifest = {
        "experiment": "alife_null_controls",
        "output_dir": output_dir,
        "cases": cases,
        "base_seed": base_seed,
        "n_seeds": n_seeds,
        "resume": resume,
        "nml_mode": nml_mode,
        "files": {
            "rule_level_csv": rule_level_path,
            "summary_csv": summary_path,
            "margin_plot": margin_plot_path,
            "defect_rate_plot": defect_plot_path,
            "decomposition_dir": decomposition_dir,
        },
        "counts": {
            "rule_level_rows": int(len(rule_level)),
            "summary_rows": int(len(summary)),
        },
        "runtime_seconds": time.time() - started,
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def _count_transitions(periods: Sequence[int]) -> int:
    return sum(1 for index in range(1, len(periods)) if periods[index] != periods[index - 1])


def _mode_and_frequency(values: Sequence[int]) -> tuple[int | None, float]:
    if not values:
        return None, math.nan
    series = pd.Series(values)
    counts = series.value_counts().sort_index()
    mode = int(counts.idxmax())
    frequency = float(counts.max() / len(series))
    return mode, frequency


def _coefficient_of_variation(values: Sequence[float]) -> float:
    series = pd.Series(values, dtype=float)
    mean = float(series.mean())
    if mean == 0.0 or series.empty:
        return 0.0
    return float(series.std(ddof=0) / mean)


def _plot_seed_stability_summary(summary: pd.DataFrame, path: Path) -> None:
    with plt.rc_context(PLOT_RC):
        labels = summary["rule"].tolist()
        y = np.arange(len(labels))
        fig, axes = plt.subplots(1, 3, figsize=(13.5, max(4.2, 0.45 * len(labels) + 1.2)))

        axes[0].barh(y, summary["final_modal_period_frequency"], color="#375a7f")
        axes[0].set_xlabel("Final modal frequency")
        axes[0].set_xlim(0.0, 1.05)
        axes[0].set_yticks(y)
        axes[0].set_yticklabels(labels)
        axes[0].set_title("Seed agreement")

        axes[1].barh(y, summary["mean_transitions_per_seed"], color="#c1742a")
        axes[1].set_xlabel("Mean transitions / seed")
        axes[1].set_yticks(y)
        axes[1].set_yticklabels([])
        axes[1].set_title("Stabilization churn")

        axes[2].barh(y, summary["final_defect_rate_cv"], color="#5b8c5a")
        axes[2].set_xlabel("Final defect-rate CV")
        axes[2].set_yticks(y)
        axes[2].set_yticklabels([])
        axes[2].set_title("Residual variability")

        fig.suptitle("ALIFE seed stability summary")
        fig.tight_layout()
        save_figure(fig, path)
        plt.close(fig)


def run_seed_stability_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    cases: Sequence[ALifeCase] | None = None,
    base_seed: int = 11,
    n_seeds: int = 10,
    resume: bool = True,
    nml_mode: str = "hybrid",
) -> dict[str, Any]:
    started = time.time()
    cases = tuple(cases or REPRESENTATIVE_PANEL)
    output_dir = ensure_output_dir(Path(output_root) / "seed_stability")
    seed_values = iter_deterministic_seeds(base_seed, n_seeds)

    runs_path = output_dir / "seed_stability_runs.csv"
    table = ResumeTable(
        runs_path,
        key_columns=("rule", "seed", "horizon"),
        sort_columns=("dimension", "rule", "seed", "horizon"),
        resume=resume,
    )

    for case in cases:
        max_horizon = int(max(case.horizons))
        for seed in seed_values:
            pending_horizons = [
                horizon
                for horizon in case.horizons
                if not table.has_key({"rule": case.name, "seed": seed, "horizon": int(horizon)})
            ]
            if not pending_horizons:
                continue
            spacetime = simulate_case(case, steps=max_horizon, seed=seed)
            batch: list[dict[str, Any]] = []
            for horizon in case.horizons:
                horizon = int(horizon)
                if horizon not in pending_horizons:
                    continue
                outcome = scan_case_spacetime(case, spacetime[:horizon], search=case.search, nml_mode=nml_mode)
                record = _record_base(case, seed=seed, horizon=horizon)
                _add_selection_metrics(record, outcome.selection)
                batch.append(record)
            table.extend(batch)
            table.flush()

    runs = table.flush()
    final_horizon_by_rule = runs.groupby("rule")["horizon"].max().to_dict()
    summary_rows: list[dict[str, Any]] = []
    for rule, group in runs.groupby("rule"):
        group = group.sort_values(["seed", "horizon"], kind="mergesort")
        final_horizon = int(final_horizon_by_rule[rule])
        final_group = group[group["horizon"] == final_horizon]
        final_periods = final_group["selected_period"].astype(int).tolist()
        final_mode, final_freq = _mode_and_frequency(final_periods)
        transition_counts = [
            _count_transitions(seed_group.sort_values("horizon")["selected_period"].astype(int).tolist())
            for _, seed_group in group.groupby("seed")
        ]
        summary_rows.append(
            {
                "rule": rule,
                "dimension": int(group["dimension"].iloc[0]),
                "n_seeds": int(group["seed"].nunique()),
                "n_horizons": int(group["horizon"].nunique()),
                "final_horizon": final_horizon,
                "final_modal_period": final_mode,
                "final_modal_period_frequency": final_freq,
                "mean_transitions_per_seed": float(np.mean(transition_counts)) if transition_counts else 0.0,
                "max_transitions_per_seed": int(max(transition_counts)) if transition_counts else 0,
                "mean_margin_bits": float(group["margin_bits"].mean()),
                "median_margin_bits": float(group["margin_bits"].median()),
                "final_mean_margin_bits": float(final_group["margin_bits"].mean()),
                "final_median_margin_bits": float(final_group["margin_bits"].median()),
                "final_defect_rate_cv": _coefficient_of_variation(final_group["selected_defect_rate"].tolist()),
                "nonunique_final_fraction": float((final_group["period_tie_count"] > 1).mean()),
            }
        )

    summary = pd.DataFrame.from_records(summary_rows).sort_values(
        ["dimension", "rule"],
        kind="mergesort",
    ).reset_index(drop=True)
    summary_path = write_summary_csv(summary, output_dir / "seed_stability_summary.csv")
    figure_path = output_dir / "seed_stability_summary.png"
    _plot_seed_stability_summary(summary, figure_path)

    manifest = {
        "experiment": "alife_seed_stability",
        "output_dir": output_dir,
        "cases": cases,
        "base_seed": base_seed,
        "n_seeds": n_seeds,
        "resume": resume,
        "nml_mode": nml_mode,
        "files": {
            "runs_csv": runs_path,
            "summary_csv": summary_path,
            "summary_figure": figure_path,
        },
        "counts": {
            "run_rows": int(len(runs)),
            "summary_rows": int(len(summary)),
        },
        "runtime_seconds": time.time() - started,
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def _plot_candidate_range_summary(summary: pd.DataFrame, path: Path) -> None:
    with plt.rc_context(PLOT_RC):
        labels = summary["rule"].tolist()
        y = np.arange(len(labels))
        fig, axes = plt.subplots(1, 2, figsize=(11.5, max(4.0, 0.42 * len(labels) + 1.0)))

        axes[0].barh(y, summary["period_change_rate"], color="#8c5a5a")
        axes[0].set_xlim(0.0, 1.05)
        axes[0].set_xlabel("Period-change rate")
        axes[0].set_yticks(y)
        axes[0].set_yticklabels(labels)
        axes[0].set_title("Winner period instability")

        axes[1].barh(y, summary["shift_change_rate"], color="#4e7f5f")
        axes[1].set_xlim(0.0, 1.05)
        axes[1].set_xlabel("Shift-change rate")
        axes[1].set_yticks(y)
        axes[1].set_yticklabels([])
        axes[1].set_title("Winner shift instability")

        fig.suptitle("Candidate-range robustness")
        fig.tight_layout()
        save_figure(fig, path)
        plt.close(fig)


def run_candidate_range_robustness_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    cases: Sequence[ALifeCase] | None = None,
    base_seed: int = 11,
    n_seeds: int = 5,
    resume: bool = True,
    nml_mode: str = "hybrid",
) -> dict[str, Any]:
    started = time.time()
    cases = tuple(cases or REPRESENTATIVE_PANEL)
    output_dir = ensure_output_dir(Path(output_root) / "candidate_range_robustness")
    seed_values = iter_deterministic_seeds(base_seed, n_seeds)

    runs_path = output_dir / "candidate_range_robustness_runs.csv"
    table = ResumeTable(
        runs_path,
        key_columns=("rule", "seed", "range_label"),
        sort_columns=("dimension", "rule", "seed", "range_label"),
        resume=resume,
    )

    for case in cases:
        horizon = int(max(case.horizons))
        search_ranges = ROBUSTNESS_SEARCH_RANGES[case.dimension]
        for seed in seed_values:
            pending = [
                search.label
                for search in search_ranges
                if not table.has_key({"rule": case.name, "seed": seed, "range_label": search.label})
            ]
            if not pending:
                continue
            spacetime = simulate_case(case, steps=horizon, seed=seed)
            batch: list[dict[str, Any]] = []
            for search in search_ranges:
                if search.label not in pending:
                    continue
                outcome = scan_case_spacetime(case, spacetime, search=search, nml_mode=nml_mode)
                record = _record_base(case, seed=seed, horizon=horizon)
                record["range_label"] = search.label
                record["range_periods"] = f"{min(search.periods)}..{max(search.periods)}"
                record["range_shift_radius"] = int(max(abs(value) for value in search.shift_ranges[0]))
                _add_selection_metrics(record, outcome.selection)
                batch.append(record)
            table.extend(batch)
            table.flush()

    runs = table.flush()
    summary_rows: list[dict[str, Any]] = []
    for rule, group in runs.groupby("rule"):
        group = group.sort_values(["seed", "range_label"], kind="mergesort")
        baseline = group[group["range_label"] == "small"].sort_values("seed")
        largest = group[group["range_label"] == "large"].sort_values("seed")
        merged = baseline.merge(
            largest,
            on=["rule", "seed"],
            suffixes=("_small", "_large"),
            how="inner",
        )
        period_change_rate = float((merged["selected_period_small"] != merged["selected_period_large"]).mean()) if not merged.empty else 0.0
        shift_change_rate = float((merged["selected_shift_str_small"] != merged["selected_shift_str_large"]).mean()) if not merged.empty else 0.0
        summary_row: dict[str, Any] = {
            "rule": rule,
            "dimension": int(group["dimension"].iloc[0]),
            "n_seeds": int(group["seed"].nunique()),
            "period_change_rate": period_change_rate,
            "shift_change_rate": shift_change_rate,
        }
        for range_label, range_group in group.groupby("range_label"):
            summary_row[f"mean_margin_bits_{range_label}"] = float(range_group["margin_bits"].mean())
            modal_period, modal_frequency = _mode_and_frequency(range_group["selected_period"].astype(int).tolist())
            summary_row[f"modal_period_{range_label}"] = modal_period
            summary_row[f"modal_period_frequency_{range_label}"] = modal_frequency
        summary_rows.append(summary_row)

    summary = pd.DataFrame.from_records(summary_rows).sort_values(
        ["dimension", "rule"],
        kind="mergesort",
    ).reset_index(drop=True)
    summary_path = write_summary_csv(summary, output_dir / "candidate_range_robustness_summary.csv")
    figure_path = output_dir / "candidate_range_robustness.png"
    _plot_candidate_range_summary(summary, figure_path)

    manifest = {
        "experiment": "alife_candidate_range_robustness",
        "output_dir": output_dir,
        "cases": cases,
        "base_seed": base_seed,
        "n_seeds": n_seeds,
        "resume": resume,
        "nml_mode": nml_mode,
        "files": {
            "runs_csv": runs_path,
            "summary_csv": summary_path,
            "summary_figure": figure_path,
        },
        "counts": {
            "run_rows": int(len(runs)),
            "summary_rows": int(len(summary)),
        },
        "runtime_seconds": time.time() - started,
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def _rulestring_case_from_lifewiki(rule_entry: dict[str, Any]) -> ALifeCase:
    return life_rulestring_case(
        rule_entry["name"],
        rulestring=rule_entry["rulestring"],
        horizons=DEFAULT_LIFEWIKI_HORIZONS,
    )


def _discrete_period_heatmap(
    matrix: np.ndarray,
    *,
    x_labels: Sequence[str],
    y_labels: Sequence[str],
    title: str,
    path: Path,
    y_label: str,
) -> None:
    with plt.rc_context(PLOT_RC):
        finite = matrix[np.isfinite(matrix)]
        max_period = int(finite.max()) if finite.size else 1
        cmap = plt.get_cmap("Blues", max_period + 1)
        boundaries = np.arange(-0.5, max_period + 1.5, 1.0)
        norm = BoundaryNorm(boundaries, cmap.N)
        fig, ax = plt.subplots(figsize=(9.0, max(4.8, 0.22 * matrix.shape[0] + 1.0)))
        image = ax.imshow(matrix, aspect="auto", interpolation="nearest", cmap=cmap, norm=norm)
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(list(x_labels))
        if len(y_labels) <= 30:
            ax.set_yticks(np.arange(len(y_labels)))
            ax.set_yticklabels(list(y_labels))
        else:
            tick_positions = np.linspace(0, len(y_labels) - 1, min(12, len(y_labels)), dtype=int)
            ax.set_yticks(tick_positions)
            ax.set_yticklabels([y_labels[index] for index in tick_positions])
        ax.set_xlabel("Horizon")
        ax.set_ylabel(y_label)
        ax.set_title(title)
        colorbar = fig.colorbar(image, ax=ax)
        colorbar.set_label("Modal selected period")
        fig.tight_layout()
        save_figure(fig, path)
        plt.close(fig)


def run_lifewiki_horizon_sweep_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    base_seed: int = 11,
    n_seeds: int = 5,
    horizons: Sequence[int] = DEFAULT_LIFEWIKI_HORIZONS,
    limit_rules: int | None = None,
    resume: bool = True,
    nml_mode: str = "hybrid",
) -> dict[str, Any]:
    started = time.time()
    output_dir = ensure_output_dir(Path(output_root) / "lifewiki_horizon_sweep")
    rules = load_lifewiki_rules(limit_rules)
    seed_values = iter_deterministic_seeds(base_seed, n_seeds)
    horizon_values = tuple(int(value) for value in horizons)
    max_horizon = int(max(horizon_values))

    runs_path = output_dir / "lifewiki_horizon_runs.csv"
    table = ResumeTable(
        runs_path,
        key_columns=("rule", "seed", "horizon"),
        sort_columns=("rule", "seed", "horizon"),
        resume=resume,
    )

    for rule_entry in rules:
        case = _rulestring_case_from_lifewiki(rule_entry)
        for seed in seed_values:
            pending_horizons = [
                horizon
                for horizon in horizon_values
                if not table.has_key({"rule": case.name, "seed": seed, "horizon": int(horizon)})
            ]
            if not pending_horizons:
                continue
            spacetime = simulate_case(case, steps=max_horizon, seed=seed)
            batch: list[dict[str, Any]] = []
            for horizon in pending_horizons:
                outcome = scan_case_spacetime(case, spacetime[: int(horizon)], search=case.search, nml_mode=nml_mode)
                record = _record_base(case, seed=seed, horizon=int(horizon))
                record["rulestring"] = rule_entry["rulestring"]
                _add_selection_metrics(record, outcome.selection)
                batch.append(record)
            table.extend(batch)
            table.flush()

    runs = table.flush()

    transition_rows: list[dict[str, Any]] = []
    for rule, group in runs.groupby("rule"):
        group = group.sort_values(["seed", "horizon"], kind="mergesort")
        final_horizon = int(group["horizon"].max())
        final_group = group[group["horizon"] == final_horizon]
        final_mode, final_frequency = _mode_and_frequency(final_group["selected_period"].astype(int).tolist())
        transitions_per_seed = [
            _count_transitions(seed_group.sort_values("horizon")["selected_period"].astype(int).tolist())
            for _, seed_group in group.groupby("seed")
        ]
        transition_rows.append(
            {
                "rule": rule,
                "dimension": 2,
                "n_seeds": int(group["seed"].nunique()),
                "final_horizon": final_horizon,
                "final_modal_period": final_mode,
                "final_modal_period_frequency": final_frequency,
                "mean_transitions_per_seed": float(np.mean(transitions_per_seed)) if transitions_per_seed else 0.0,
                "max_transitions_per_seed": int(max(transitions_per_seed)) if transitions_per_seed else 0,
                "mean_margin_bits": float(group["margin_bits"].mean()),
                "final_mean_margin_bits": float(final_group["margin_bits"].mean()),
            }
        )
    transition_summary = pd.DataFrame.from_records(transition_rows).sort_values("rule").reset_index(drop=True)
    transition_summary_path = write_summary_csv(
        transition_summary,
        output_dir / "lifewiki_horizon_transition_summary.csv",
    )

    final_horizon = int(max(horizon_values))
    final_distribution = (
        runs[runs["horizon"] == final_horizon]
        .groupby("selected_period")
        .size()
        .reset_index(name="count_runs")
        .sort_values("selected_period")
        .reset_index(drop=True)
    )
    final_distribution["horizon"] = final_horizon
    final_distribution_path = write_summary_csv(
        final_distribution,
        output_dir / "lifewiki_horizon_final_period_distribution.csv",
    )

    modal_heatmap = (
        runs.groupby(["rule", "horizon"])["selected_period"]
        .agg(lambda values: pd.Series(values).value_counts().sort_index().idxmax())
        .unstack("horizon")
        .sort_index()
    )
    heatmap_path = output_dir / "lifewiki_horizon_heatmap.png"
    _discrete_period_heatmap(
        modal_heatmap.to_numpy(dtype=float),
        x_labels=[str(value) for value in modal_heatmap.columns.tolist()],
        y_labels=modal_heatmap.index.tolist(),
        title="LifeWiki survey: modal selected period by horizon",
        path=heatmap_path,
        y_label="Rule",
    )

    manifest = {
        "experiment": "alife_lifewiki_horizon_sweep",
        "output_dir": output_dir,
        "base_seed": base_seed,
        "n_seeds": n_seeds,
        "horizons": list(horizon_values),
        "limit_rules": limit_rules,
        "resume": resume,
        "nml_mode": nml_mode,
        "files": {
            "runs_csv": runs_path,
            "transition_summary_csv": transition_summary_path,
            "final_distribution_csv": final_distribution_path,
            "heatmap_png": heatmap_path,
        },
        "counts": {
            "run_rows": int(len(runs)),
            "transition_rows": int(len(transition_summary)),
            "period_distribution_rows": int(len(final_distribution)),
        },
        "runtime_seconds": time.time() - started,
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def _plot_eca_atlas_stability(matrix: np.ndarray, *, x_labels: Sequence[str], path: Path) -> None:
    with plt.rc_context(PLOT_RC):
        fig, ax = plt.subplots(figsize=(9.0, 9.6))
        image = ax.imshow(matrix, aspect="auto", interpolation="nearest", vmin=0.0, vmax=1.0, cmap="Greys")
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(list(x_labels))
        ax.set_yticks(np.linspace(0, matrix.shape[0] - 1, 16, dtype=int))
        ax.set_yticklabels([str(value) for value in np.linspace(0, 255, 16, dtype=int)])
        ax.set_xlabel("Horizon")
        ax.set_ylabel("ECA rule")
        ax.set_title("ECA atlas: modal period frequency by horizon")
        colorbar = fig.colorbar(image, ax=ax)
        colorbar.set_label("Modal frequency across seeds")
        fig.tight_layout()
        save_figure(fig, path)
        plt.close(fig)


def run_eca_atlas_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    base_seed: int = 11,
    n_seeds: int = 5,
    horizons: Sequence[int] = DEFAULT_ECA_ATLAS_HORIZONS,
    limit_rules: int | None = None,
    resume: bool = True,
    nml_mode: str = "hybrid",
    search: SearchConfig = DEFAULT_SEARCH_1D,
) -> dict[str, Any]:
    started = time.time()
    output_dir = ensure_output_dir(Path(output_root) / "eca_atlas")
    seed_values = iter_deterministic_seeds(base_seed, n_seeds)
    horizon_values = tuple(int(value) for value in horizons)
    max_horizon = int(max(horizon_values))
    cases = eca_atlas_cases(limit_rules)

    runs_path = output_dir / "eca_atlas_runs.csv"
    table = ResumeTable(
        runs_path,
        key_columns=("rule", "seed", "horizon"),
        sort_columns=("rule", "seed", "horizon"),
        resume=resume,
    )

    for case in cases:
        for seed in seed_values:
            pending_horizons = [
                horizon
                for horizon in horizon_values
                if not table.has_key({"rule": case.name, "seed": seed, "horizon": int(horizon)})
            ]
            if not pending_horizons:
                continue
            spacetime = simulate_case(case, steps=max_horizon, seed=seed)
            batch: list[dict[str, Any]] = []
            for horizon in pending_horizons:
                outcome = scan_case_spacetime(case, spacetime[: int(horizon)], search=search, nml_mode=nml_mode)
                record = _record_base(case, seed=seed, horizon=int(horizon))
                _add_selection_metrics(record, outcome.selection)
                batch.append(record)
            table.extend(batch)
            table.flush()

    runs = table.flush()

    summary_rows: list[dict[str, Any]] = []
    for rule, group in runs.groupby("rule"):
        group = group.sort_values(["seed", "horizon"], kind="mergesort")
        final_horizon = int(group["horizon"].max())
        final_group = group[group["horizon"] == final_horizon]
        final_mode, final_frequency = _mode_and_frequency(final_group["selected_period"].astype(int).tolist())
        transitions_per_seed = [
            _count_transitions(seed_group.sort_values("horizon")["selected_period"].astype(int).tolist())
            for _, seed_group in group.groupby("seed")
        ]
        summary_rows.append(
            {
                "rule": rule,
                "rule_number": int(rule.split("-")[-1]),
                "final_modal_period": final_mode,
                "final_modal_period_frequency": final_frequency,
                "mean_transitions_per_seed": float(np.mean(transitions_per_seed)) if transitions_per_seed else 0.0,
                "mean_margin_bits": float(group["margin_bits"].mean()),
                "final_mean_margin_bits": float(final_group["margin_bits"].mean()),
                "final_mean_defect_rate": float(final_group["selected_defect_rate"].mean()),
            }
        )
    summary = pd.DataFrame.from_records(summary_rows).sort_values("rule_number").reset_index(drop=True)
    summary_path = write_summary_csv(summary, output_dir / "eca_atlas_summary.csv")

    modal_period_heatmap = (
        runs.groupby(["rule", "horizon"])["selected_period"]
        .agg(lambda values: pd.Series(values).value_counts().sort_index().idxmax())
        .unstack("horizon")
        .sort_index(key=lambda index: index.map(lambda item: int(str(item).split("-")[-1])))
    )
    period_plot_path = output_dir / "eca_atlas_periods.png"
    _discrete_period_heatmap(
        modal_period_heatmap.to_numpy(dtype=float),
        x_labels=[str(value) for value in modal_period_heatmap.columns.tolist()],
        y_labels=modal_period_heatmap.index.tolist(),
        title="ECA atlas: modal selected period",
        path=period_plot_path,
        y_label="ECA rule",
    )

    modal_frequency_heatmap = (
        runs.groupby(["rule", "horizon"])["selected_period"]
        .agg(lambda values: float(pd.Series(values).value_counts().max() / len(values)))
        .unstack("horizon")
        .sort_index(key=lambda index: index.map(lambda item: int(str(item).split("-")[-1])))
    )
    stability_plot_path = output_dir / "eca_atlas_stability.png"
    _plot_eca_atlas_stability(
        modal_frequency_heatmap.to_numpy(dtype=float),
        x_labels=[str(value) for value in modal_frequency_heatmap.columns.tolist()],
        path=stability_plot_path,
    )

    manifest = {
        "experiment": "alife_eca_atlas",
        "output_dir": output_dir,
        "base_seed": base_seed,
        "n_seeds": n_seeds,
        "horizons": list(horizon_values),
        "limit_rules": limit_rules,
        "resume": resume,
        "nml_mode": nml_mode,
        "search": search,
        "files": {
            "runs_csv": runs_path,
            "summary_csv": summary_path,
            "period_plot": period_plot_path,
            "stability_plot": stability_plot_path,
        },
        "counts": {
            "run_rows": int(len(runs)),
            "summary_rows": int(len(summary)),
        },
        "runtime_seconds": time.time() - started,
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def _plot_3d_survey_summary(summary: pd.DataFrame, path: Path) -> None:
    with plt.rc_context(PLOT_RC):
        labels = summary["rule"].tolist()
        y = np.arange(len(labels))
        fig, axes = plt.subplots(1, 2, figsize=(10.8, max(4.0, 0.6 * len(labels) + 1.0)))

        axes[0].barh(y, summary["modal_period"], color="#486581")
        axes[0].set_xlabel("Modal selected period")
        axes[0].set_yticks(y)
        axes[0].set_yticklabels(labels)
        axes[0].set_title("3D rule survey: modal period")

        axes[1].barh(y, summary["mean_margin_bits"], color="#b36a3c")
        axes[1].set_xlabel("Mean winner margin (bits)")
        axes[1].set_yticks(y)
        axes[1].set_yticklabels([])
        axes[1].set_title("3D rule survey: margin")

        fig.tight_layout()
        save_figure(fig, path)
        plt.close(fig)


def run_3d_survey_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    cases: Sequence[ALifeCase] | None = None,
    base_seed: int = 11,
    n_seeds: int = 5,
    resume: bool = True,
    nml_mode: str = "hybrid",
    search: SearchConfig = DEFAULT_SEARCH_3D,
) -> dict[str, Any]:
    started = time.time()
    cases = tuple(cases or all_3d_cases())
    output_dir = ensure_output_dir(Path(output_root) / "survey_3d")
    seed_values = iter_deterministic_seeds(base_seed, n_seeds)

    runs_path = output_dir / "alife_3d_survey_runs.csv"
    table = ResumeTable(
        runs_path,
        key_columns=("rule", "seed"),
        sort_columns=("rule", "seed"),
        resume=resume,
    )

    for case in cases:
        horizon = int(max(case.horizons))
        for seed in seed_values:
            if table.has_key({"rule": case.name, "seed": seed}):
                continue
            spacetime = simulate_case(case, steps=horizon, seed=seed)
            outcome = scan_case_spacetime(case, spacetime, search=search, nml_mode=nml_mode)
            record = _record_base(case, seed=seed, horizon=horizon)
            _add_selection_metrics(record, outcome.selection)
            table.add(record)
        table.flush()

    runs = table.flush()
    summary_rows: list[dict[str, Any]] = []
    for rule, group in runs.groupby("rule"):
        modal_period, modal_frequency = _mode_and_frequency(group["selected_period"].astype(int).tolist())
        summary_rows.append(
            {
                "rule": rule,
                "dimension": 3,
                "n_seeds": int(group["seed"].nunique()),
                "horizon": int(group["horizon"].max()),
                "modal_period": modal_period,
                "modal_period_frequency": modal_frequency,
                "mean_margin_bits": float(group["margin_bits"].mean()),
                "mean_defect_rate": float(group["selected_defect_rate"].mean()),
                "nonunique_fraction": float((group["period_tie_count"] > 1).mean()),
            }
        )
    summary = pd.DataFrame.from_records(summary_rows).sort_values("rule").reset_index(drop=True)
    summary_path = write_summary_csv(summary, output_dir / "alife_3d_survey_summary.csv")
    figure_path = output_dir / "alife_3d_survey.png"
    _plot_3d_survey_summary(summary, figure_path)

    manifest = {
        "experiment": "alife_3d_survey",
        "output_dir": output_dir,
        "cases": cases,
        "base_seed": base_seed,
        "n_seeds": n_seeds,
        "resume": resume,
        "nml_mode": nml_mode,
        "search": search,
        "files": {
            "runs_csv": runs_path,
            "summary_csv": summary_path,
            "summary_plot": figure_path,
        },
        "counts": {
            "run_rows": int(len(runs)),
            "summary_rows": int(len(summary)),
        },
        "runtime_seconds": time.time() - started,
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def _safe_read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def _markdown_table(frame: pd.DataFrame, *, index: bool = False, max_rows: int | None = None) -> str:
    if frame.empty:
        return "_No rows._"
    display = frame.copy()
    if max_rows is not None:
        display = display.head(max_rows)
    if not index:
        display = display.reset_index(drop=True)
    headers = list(display.columns)
    rows = [[str(value) for value in headers], ["---" for _ in headers]]
    for row in display.itertuples(index=False):
        rows.append([str(value) for value in row])
    return "\n".join(f"| {' | '.join(row)} |" for row in rows)


def generate_paper_reports(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    paper_dir: Path | str = Path("paper"),
) -> dict[str, Any]:
    output_root = Path(output_root)
    paper_dir = ensure_output_dir(Path(paper_dir))

    null_summary = _safe_read_csv(output_root / "null_controls" / "null_controls_summary.csv")
    seed_summary = _safe_read_csv(output_root / "seed_stability" / "seed_stability_summary.csv")
    range_summary = _safe_read_csv(output_root / "candidate_range_robustness" / "candidate_range_robustness_summary.csv")
    lifewiki_distribution = _safe_read_csv(output_root / "lifewiki_horizon_sweep" / "lifewiki_horizon_final_period_distribution.csv")
    lifewiki_transition = _safe_read_csv(output_root / "lifewiki_horizon_sweep" / "lifewiki_horizon_transition_summary.csv")
    eca_summary = _safe_read_csv(output_root / "eca_atlas" / "eca_atlas_summary.csv")
    survey_3d_summary = _safe_read_csv(output_root / "survey_3d" / "alife_3d_survey_summary.csv")
    counterexample_report_path = output_root / "counterexample_stress" / "counterexample_stress_report.json"
    counterexample_report = json.loads(counterexample_report_path.read_text()) if counterexample_report_path.exists() else None

    narrative_lines = ["# ALIFE experiment summary", ""]
    table_lines = ["# ALIFE table snippets", ""]

    if null_summary is not None:
        narrative_lines.extend(
            [
                "## Null controls",
                "",
                "The null-control panel compares original spacetimes against time-shuffled, space-shuffled, and density-matched Bernoulli controls using the same period-first Bernoulli-NML selector.",
                "",
                _markdown_table(
                    null_summary[
                        [
                            "dimension",
                            "control_label",
                            "runs",
                            "mean_margin_bits",
                            "mean_defect_rate",
                            "stable_winner_fraction",
                        ]
                    ]
                ),
                "",
            ]
        )
        table_lines.extend(
            [
                "## Null controls",
                "",
                _markdown_table(
                    null_summary[
                        [
                            "dimension",
                            "control_label",
                            "mean_margin_bits",
                            "mean_defect_rate",
                        ]
                    ]
                ),
                "",
            ]
        )

    if seed_summary is not None:
        narrative_lines.extend(
            [
                "## Seed stability",
                "",
                "Representative rules were re-run across multiple deterministic seeds and stabilization horizons. The table below reports agreement on the final selected period, transition counts, and residual variability.",
                "",
                _markdown_table(
                    seed_summary[
                        [
                            "rule",
                            "final_modal_period",
                            "final_modal_period_frequency",
                            "mean_transitions_per_seed",
                            "final_mean_margin_bits",
                            "final_defect_rate_cv",
                        ]
                    ]
                ),
                "",
            ]
        )
        table_lines.extend(
            [
                "## Seed stability",
                "",
                _markdown_table(
                    seed_summary[
                        [
                            "rule",
                            "final_modal_period",
                            "final_modal_period_frequency",
                            "mean_transitions_per_seed",
                        ]
                    ]
                ),
                "",
            ]
        )

    if range_summary is not None:
        unstable = range_summary[
            (range_summary["period_change_rate"] > 0.0) | (range_summary["shift_change_rate"] > 0.0)
        ]
        narrative_lines.extend(
            [
                "## Candidate-range robustness",
                "",
                f"Across the tested nested search ranges, {len(unstable)} rules showed at least one winner change between the smallest and largest candidate sets.",
                "",
                _markdown_table(
                    range_summary[
                        [
                            "rule",
                            "period_change_rate",
                            "shift_change_rate",
                            "modal_period_small",
                            "modal_period_large",
                        ]
                    ]
                ),
                "",
            ]
        )
        table_lines.extend(
            [
                "## Candidate-range robustness",
                "",
                _markdown_table(
                    range_summary[
                        [
                            "rule",
                            "period_change_rate",
                            "shift_change_rate",
                        ]
                    ]
                ),
                "",
            ]
        )

    if lifewiki_distribution is not None:
        narrative_lines.extend(
            [
                "## LifeWiki horizon sweep",
                "",
                "The named Life-like survey tracks how the selected period distribution evolves as the observation horizon grows.",
                "",
                _markdown_table(lifewiki_distribution),
                "",
            ]
        )
        if lifewiki_transition is not None:
            table_lines.extend(
                [
                    "## LifeWiki transition summary",
                    "",
                    _markdown_table(
                        lifewiki_transition[
                            [
                                "rule",
                                "final_modal_period",
                                "final_modal_period_frequency",
                                "mean_transitions_per_seed",
                            ]
                        ],
                        max_rows=20,
                    ),
                    "",
                ]
            )

    if eca_summary is not None:
        period_counts = (
            eca_summary.groupby("final_modal_period").size().reset_index(name="count_rules")
            .sort_values("final_modal_period")
            .reset_index(drop=True)
        )
        narrative_lines.extend(
            [
                "## ECA atlas",
                "",
                "The complete ECA atlas reports the modal selected period for each rule across five horizons and five seeds.",
                "",
                _markdown_table(period_counts),
                "",
            ]
        )
        table_lines.extend(
            [
                "## ECA atlas sample",
                "",
                _markdown_table(
                    eca_summary[
                        [
                            "rule",
                            "final_modal_period",
                            "final_modal_period_frequency",
                            "mean_transitions_per_seed",
                        ]
                    ],
                    max_rows=20,
                ),
                "",
            ]
        )

    if survey_3d_summary is not None:
        narrative_lines.extend(
            [
                "## 3D survey",
                "",
                _markdown_table(survey_3d_summary),
                "",
            ]
        )

    if counterexample_report is not None:
        narrative_lines.extend(
            [
                "## Counterexample stress",
                "",
                f"Observed issues: {counterexample_report['counts']}",
                "",
            ]
        )
        table_lines.extend(
            [
                "## Counterexample stress counts",
                "",
                _markdown_table(pd.DataFrame([counterexample_report["counts"]])),
                "",
            ]
        )

    summary_path = paper_dir / "alife_experiment_summary.md"
    table_path = paper_dir / "alife_table_snippets.md"
    summary_path.write_text("\n".join(narrative_lines).strip() + "\n")
    table_path.write_text("\n".join(table_lines).strip() + "\n")

    manifest = {
        "paper_summary": summary_path,
        "paper_tables": table_path,
    }
    return manifest


def run_counterexample_stress_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    very_small_margin_bits: float = VERY_SMALL_MARGIN_BITS,
    repeated_tie_threshold: int = 3,
) -> dict[str, Any]:
    started = time.time()
    output_dir = ensure_output_dir(Path(output_root) / "counterexample_stress")

    seed_runs = _safe_read_csv(Path(output_root) / "seed_stability" / "seed_stability_runs.csv")
    range_runs = _safe_read_csv(Path(output_root) / "candidate_range_robustness" / "candidate_range_robustness_runs.csv")
    null_runs = _safe_read_csv(Path(output_root) / "null_controls" / "null_controls_rule_level.csv")
    atlas_runs = _safe_read_csv(Path(output_root) / "eca_atlas" / "eca_atlas_runs.csv")
    lifewiki_runs = _safe_read_csv(Path(output_root) / "lifewiki_horizon_sweep" / "lifewiki_horizon_runs.csv")
    survey_3d_runs = _safe_read_csv(Path(output_root) / "survey_3d" / "alife_3d_survey_runs.csv")

    all_runs = [
        frame
        for frame in [seed_runs, atlas_runs, lifewiki_runs, survey_3d_runs]
        if frame is not None
    ]
    combined = pd.concat(all_runs, ignore_index=True) if all_runs else pd.DataFrame()

    nonunique = (
        combined[(combined["period_tie_count"] > 1) | (combined["selected_shift_tie_count"] > 1)]
        if not combined.empty
        else pd.DataFrame()
    )
    small_margins = (
        combined[combined["margin_bits"] <= very_small_margin_bits]
        if not combined.empty
        else pd.DataFrame()
    )

    if range_runs is not None and not range_runs.empty:
        baseline = range_runs[range_runs["range_label"] == "small"]
        largest = range_runs[range_runs["range_label"] == "large"]
        candidate_instability = baseline.merge(
            largest,
            on=["rule", "seed"],
            suffixes=("_small", "_large"),
        )
        candidate_instability = candidate_instability[
            (candidate_instability["selected_period_small"] != candidate_instability["selected_period_large"])
            | (candidate_instability["selected_shift_str_small"] != candidate_instability["selected_shift_str_large"])
        ]
    else:
        candidate_instability = pd.DataFrame()

    null_false_positives = (
        null_runs[
            (null_runs["control_type"] != "original")
            & (null_runs["selected_period"] > 1)
            & (null_runs["status"] == "stable_winner")
        ]
        if null_runs is not None and not null_runs.empty
        else pd.DataFrame()
    )

    if not combined.empty:
        repeated_ties = (
            combined.assign(has_tie=(combined["period_tie_count"] > 1) | (combined["selected_shift_tie_count"] > 1))
            .groupby("rule")["has_tie"]
            .sum()
            .reset_index(name="tie_runs")
        )
        repeated_ties = repeated_ties[repeated_ties["tie_runs"] >= int(repeated_tie_threshold)]
    else:
        repeated_ties = pd.DataFrame()

    report = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "counts": {
            "nonunique_winners": int(len(nonunique)),
            "very_small_margins": int(len(small_margins)),
            "candidate_range_instability": int(len(candidate_instability)),
            "null_control_false_positives": int(len(null_false_positives)),
            "suspicious_repeated_ties": int(len(repeated_ties)),
        },
        "cases": {
            "nonunique_winners": nonunique.head(50).to_dict(orient="records") if not nonunique.empty else [],
            "very_small_margins": small_margins.head(50).to_dict(orient="records") if not small_margins.empty else [],
            "candidate_range_instability": candidate_instability.head(50).to_dict(orient="records") if not candidate_instability.empty else [],
            "null_control_false_positives": null_false_positives.head(50).to_dict(orient="records") if not null_false_positives.empty else [],
            "suspicious_repeated_ties": repeated_ties.head(50).to_dict(orient="records") if not repeated_ties.empty else [],
        },
        "runtime_seconds": time.time() - started,
    }
    report_path = write_json_manifest(output_dir / "counterexample_stress_report.json", report)

    markdown_lines = [
        "# Counterexample stress summary",
        "",
        "This report lists only observed cases from the generated experiment outputs.",
        "",
        f"- Non-unique winners: {report['counts']['nonunique_winners']}",
        f"- Very small margins (<= {very_small_margin_bits:.3f} bits): {report['counts']['very_small_margins']}",
        f"- Candidate-range instability cases: {report['counts']['candidate_range_instability']}",
        f"- Null-control false positives: {report['counts']['null_control_false_positives']}",
        f"- Suspicious repeated ties: {report['counts']['suspicious_repeated_ties']}",
        "",
    ]

    def _append_section(title: str, frame: pd.DataFrame) -> None:
        markdown_lines.append(f"## {title}")
        markdown_lines.append("")
        if frame.empty:
            markdown_lines.append("_No observed cases._")
            markdown_lines.append("")
            return
        markdown_lines.append(_markdown_table(frame.head(20)))
        markdown_lines.append("")

    _append_section("Non-unique winners", nonunique)
    _append_section("Very small margins", small_margins)
    _append_section("Candidate-range instability", candidate_instability)
    _append_section("Null-control false positives", null_false_positives)
    _append_section("Suspicious repeated ties", repeated_ties)

    markdown_path = output_dir / "counterexample_stress_summary.md"
    markdown_path.write_text("\n".join(markdown_lines).strip() + "\n")

    manifest = {
        "experiment": "alife_counterexample_stress",
        "output_dir": output_dir,
        "files": {
            "report_json": report_path,
            "summary_markdown": markdown_path,
        },
        "counts": report["counts"],
        "runtime_seconds": report["runtime_seconds"],
    }
    manifest_path = write_json_manifest(output_dir / "manifest.json", manifest)
    manifest["manifest_path"] = manifest_path
    return manifest


def run_all_suite(
    *,
    output_root: Path | str = ALIFE_OUTPUT_ROOT,
    paper_dir: Path | str = Path("paper"),
    base_seed: int = 11,
    resume: bool = True,
    run_null_controls: bool = True,
    run_seed_stability: bool = True,
    run_candidate_range_robustness: bool = True,
    run_lifewiki_horizon_sweep: bool = True,
    run_eca_atlas: bool = True,
    run_3d_survey: bool = True,
    run_counterexample_stress: bool = True,
    generate_paper_markdown: bool = True,
    lifewiki_limit: int | None = None,
    eca_limit: int | None = None,
) -> dict[str, Any]:
    started = time.time()
    output_root = ensure_output_dir(Path(output_root))

    manifests: dict[str, Any] = {}
    if run_null_controls:
        manifests["null_controls"] = run_null_controls_suite(
            output_root=output_root,
            base_seed=base_seed,
            resume=resume,
        )
    if run_seed_stability:
        manifests["seed_stability"] = run_seed_stability_suite(
            output_root=output_root,
            base_seed=base_seed,
            resume=resume,
        )
    if run_candidate_range_robustness:
        manifests["candidate_range_robustness"] = run_candidate_range_robustness_suite(
            output_root=output_root,
            base_seed=base_seed,
            resume=resume,
        )
    if run_lifewiki_horizon_sweep:
        manifests["lifewiki_horizon_sweep"] = run_lifewiki_horizon_sweep_suite(
            output_root=output_root,
            base_seed=base_seed,
            resume=resume,
            limit_rules=lifewiki_limit,
        )
    if run_eca_atlas:
        manifests["eca_atlas"] = run_eca_atlas_suite(
            output_root=output_root,
            base_seed=base_seed,
            resume=resume,
            limit_rules=eca_limit,
        )
    if run_3d_survey:
        manifests["survey_3d"] = run_3d_survey_suite(
            output_root=output_root,
            base_seed=base_seed,
            resume=resume,
        )
    if run_counterexample_stress:
        manifests["counterexample_stress"] = run_counterexample_stress_suite(
            output_root=output_root,
        )
    if generate_paper_markdown:
        manifests["paper_reports"] = generate_paper_reports(
            output_root=output_root,
            paper_dir=paper_dir,
        )

    root_manifest = {
        "experiment": "alife_run_all",
        "output_root": output_root,
        "base_seed": base_seed,
        "resume": resume,
        "flags": {
            "run_null_controls": run_null_controls,
            "run_seed_stability": run_seed_stability,
            "run_candidate_range_robustness": run_candidate_range_robustness,
            "run_lifewiki_horizon_sweep": run_lifewiki_horizon_sweep,
            "run_eca_atlas": run_eca_atlas,
            "run_3d_survey": run_3d_survey,
            "run_counterexample_stress": run_counterexample_stress,
            "generate_paper_markdown": generate_paper_markdown,
        },
        "limits": {
            "lifewiki_limit": lifewiki_limit,
            "eca_limit": eca_limit,
        },
        "manifests": manifests,
        "runtime_seconds": time.time() - started,
    }
    root_manifest_path = write_json_manifest(output_root / "results_manifest.json", root_manifest)
    root_manifest["manifest_path"] = root_manifest_path
    return root_manifest
