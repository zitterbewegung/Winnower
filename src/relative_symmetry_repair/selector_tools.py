from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from .coding import resolve_nml_mode

TIE_BREAK_RULE = "score asc, period asc, shift lex asc"


@dataclass(frozen=True, slots=True)
class SelectorVariant:
    """Explicit selector definition for experiment metadata and validation."""

    name: str
    selector_type: str
    score_type: str
    score_column: str
    shift_handling: str
    tie_break_rule: str = TIE_BREAK_RULE
    nml_mode: str | None = None

    def to_metadata(self) -> dict[str, object]:
        metadata = asdict(self)
        if metadata["nml_mode"] is not None:
            metadata["nml_mode"] = resolve_nml_mode(mode=str(metadata["nml_mode"]))
        return metadata


def shift_columns(frame: pd.DataFrame) -> list[str]:
    cols = []
    if "shift" in frame.columns:
        cols.append("shift")
    cols.extend(sorted(c for c in frame.columns if c.startswith("shift_")))
    return cols


def deterministic_sort_columns(
    frame: pd.DataFrame,
    score_column: str,
) -> list[str]:
    cols = [score_column]
    if "period" in frame.columns:
        cols.append("period")
    cols.extend(shift_columns(frame))
    return cols


def sort_candidates(
    frame: pd.DataFrame,
    score_column: str,
) -> pd.DataFrame:
    sort_cols = deterministic_sort_columns(frame, score_column)
    return frame.sort_values(sort_cols, kind="mergesort").reset_index(drop=True)


def ranked_candidates(
    frame: pd.DataFrame,
    score_column: str,
    *,
    rank_column: str = "rank",
) -> pd.DataFrame:
    ranked = sort_candidates(frame, score_column).copy()
    ranked[rank_column] = np.arange(1, len(ranked) + 1, dtype=np.int64)
    return ranked


def select_best_candidate(frame: pd.DataFrame, score_column: str) -> pd.Series:
    if frame.empty:
        raise ValueError("No candidates available")
    return sort_candidates(frame, score_column).iloc[0]


def shift_handling_from_1d(shifts: Iterable[int]) -> str:
    shift_list = [int(s) for s in shifts]
    if len(shift_list) == 1 and shift_list[0] == 0:
        return "shift_zero_only"
    if len(shift_list) == 1:
        return "fixed_shift"
    return "joint_shift_optimization"


def shift_handling_from_nd(shift_ranges: Sequence[Iterable[int]]) -> str:
    shift_lists = [[int(s) for s in axis] for axis in shift_ranges]
    if all(len(axis) == 1 and axis[0] == 0 for axis in shift_lists):
        return "shift_zero_only"
    if all(len(axis) == 1 for axis in shift_lists):
        return "fixed_shift"
    return "joint_shift_optimization"


def serialize_jsonable(value):
    if isinstance(value, dict):
        return {str(k): serialize_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_jsonable(v) for v in value]
    if isinstance(value, range):
        return list(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def write_metadata_sidecar(csv_path: Path, metadata: dict[str, object]) -> Path:
    metadata_path = Path(f"{csv_path}.metadata.json")
    metadata_path.write_text(
        json.dumps(serialize_jsonable(metadata), indent=2, sort_keys=True) + "\n"
    )
    return metadata_path
