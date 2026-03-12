#!/usr/bin/env python3
"""Generate detailed candidate score tables for benchmark rules."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from relative_symmetry_repair.ca2d import parse_rulestring, random_initial_grid, simulate_2d_general
from relative_symmetry_repair.eca import random_initial_state, simulate_eca
from relative_symmetry_repair.repair import scan_relative_periodicity
from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd
from relative_symmetry_repair.selector_tools import ranked_candidates, write_metadata_sidecar


@dataclass(frozen=True, slots=True)
class DumpCase1D:
    slug: str
    rule: int
    steps: int
    width: int = 192
    density: float = 0.5
    seed: int = 11
    shift_radius: int = 6
    max_period: int = 10


@dataclass(frozen=True, slots=True)
class DumpCase2D:
    slug: str
    rulestring: str
    steps: int
    width: int = 64
    height: int = 64
    density: float = 0.5
    seed: int = 42
    shift_radius: int = 2
    max_period: int = 8


CASES_1D = [
    DumpCase1D(slug="eca54_T200", rule=54, steps=200),
    DumpCase1D(slug="eca110_T200", rule=110, steps=200),
]

CASES_2D = [
    DumpCase2D(slug="fredkin_T100", rulestring="B1357/S02468", steps=100),
    DumpCase2D(slug="diamoeba_T100", rulestring="B35678/S5678", steps=100),
    DumpCase2D(slug="diamoeba_T400", rulestring="B35678/S5678", steps=400),
    DumpCase2D(slug="serviettes_T100", rulestring="B234/S", steps=100),
    DumpCase2D(slug="serviettes_T400", rulestring="B234/S", steps=400),
]


def _merge_score_modes(
    hybrid_frame: pd.DataFrame,
    asym_frame: pd.DataFrame,
) -> pd.DataFrame:
    key_cols = ["period"] + [col for col in hybrid_frame.columns if col == "shift" or col.startswith("shift_")]
    keep_common = ["defect_sites", "defect_rate", "nll_bits"]
    merged = hybrid_frame[key_cols + keep_common + ["nml_complexity", "nml_bits"]].rename(
        columns={
            "nml_complexity": "nml_complexity_hybrid",
            "nml_bits": "nml_bits_hybrid",
        }
    )
    merged = merged.merge(
        asym_frame[key_cols + ["nml_complexity", "nml_bits"]].rename(
            columns={
                "nml_complexity": "nml_complexity_asymptotic",
                "nml_bits": "nml_bits_asymptotic",
            }
        ),
        on=key_cols,
        how="inner",
    )
    return merged


def _annotate_ranks(frame: pd.DataFrame) -> pd.DataFrame:
    annotated = frame.reset_index(drop=True).copy()
    annotated["candidate_id"] = np.arange(len(annotated), dtype=np.int64)
    for column, rank_name in [
        ("defect_rate", "defect_rank"),
        ("nll_bits", "nll_rank"),
        ("nml_bits_hybrid", "hybrid_rank"),
        ("nml_bits_asymptotic", "asymptotic_rank"),
    ]:
        ranked = ranked_candidates(annotated, column, rank_column=rank_name)[
            ["candidate_id", rank_name]
        ]
        annotated = annotated.merge(ranked, on="candidate_id", how="left", sort=False)
    return annotated.drop(columns=["candidate_id"]).sort_values(
        ["hybrid_rank", "asymptotic_rank", "defect_rank", "period"]
    ).reset_index(drop=True)


def dump_case_1d(case: DumpCase1D, output_dir: Path) -> Path:
    initial = random_initial_state(width=case.width, density=case.density, seed=case.seed)
    spacetime = simulate_eca(case.rule, initial, case.steps)
    shifts = list(range(-case.shift_radius, case.shift_radius + 1))
    periods = list(range(1, case.max_period + 1))

    hybrid_frame, _ = scan_relative_periodicity(
        spacetime,
        shifts=shifts,
        periods=periods,
        nml_mode="hybrid",
    )
    asym_frame, _ = scan_relative_periodicity(
        spacetime,
        shifts=shifts,
        periods=periods,
        nml_mode="asymptotic",
    )
    dump = _annotate_ranks(_merge_score_modes(hybrid_frame, asym_frame))
    dump["rule"] = f"ECA-{case.rule}"
    dump["steps"] = case.steps
    csv_path = output_dir / f"{case.slug}.csv"
    dump.to_csv(csv_path, index=False)
    write_metadata_sidecar(
        csv_path,
        {
            "case": case.slug,
            "rule": f"ECA-{case.rule}",
            "grid_size": case.width,
            "steps": case.steps,
            "density": case.density,
            "seed": case.seed,
            "period_range": periods,
            "shift_range": shifts,
            "boundary_condition": "periodic",
            "score_columns": [
                "defect_rate",
                "nll_bits",
                "nml_bits_hybrid",
                "nml_bits_asymptotic",
            ],
        },
    )
    return csv_path


def dump_case_2d(case: DumpCase2D, output_dir: Path) -> Path:
    birth, survive = parse_rulestring(case.rulestring)
    initial = random_initial_grid(
        width=case.width,
        height=case.height,
        density=case.density,
        seed=case.seed,
    )
    spacetime = simulate_2d_general(initial, steps=case.steps, birth=birth, survive=survive)
    shift_values = list(range(-case.shift_radius, case.shift_radius + 1))
    periods = list(range(1, case.max_period + 1))

    hybrid_frame, _ = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_values, shift_values],
        periods=periods,
        nml_mode="hybrid",
    )
    asym_frame, _ = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_values, shift_values],
        periods=periods,
        nml_mode="asymptotic",
    )
    dump = _annotate_ranks(_merge_score_modes(hybrid_frame, asym_frame))
    dump["rulestring"] = case.rulestring
    dump["steps"] = case.steps
    csv_path = output_dir / f"{case.slug}.csv"
    dump.to_csv(csv_path, index=False)
    write_metadata_sidecar(
        csv_path,
        {
            "case": case.slug,
            "rulestring": case.rulestring,
            "grid_size": [case.width, case.height],
            "steps": case.steps,
            "density": case.density,
            "seed": case.seed,
            "period_range": periods,
            "shift_range": shift_values,
            "boundary_condition": "periodic",
            "score_columns": [
                "defect_rate",
                "nll_bits",
                "nml_bits_hybrid",
                "nml_bits_asymptotic",
            ],
        },
    )
    return csv_path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    output_dir = root / "results" / "selector_score_dumps"
    output_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for case in CASES_1D:
        path = dump_case_1d(case, output_dir)
        written.append(path.relative_to(root))
        print(f"Wrote {path.relative_to(root)}")
    for case in CASES_2D:
        path = dump_case_2d(case, output_dir)
        written.append(path.relative_to(root))
        print(f"Wrote {path.relative_to(root)}")

    print("\nDetailed selector score dumps:")
    for path in written:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
