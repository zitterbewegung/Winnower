#!/usr/bin/env python3
"""Experiment 1: baseline selector comparison.

Compares three explicit candidate-level selectors on each rule:
  1. Residual minimization: argmin defect_rate
  2. Bernoulli NLL: argmin nll_bits
  3. Bernoulli NML (hybrid exact/asymptotic): argmin nml_bits

The script writes:
  - rule-level selections
  - candidate-level score tables with ranks and selected flags
  - summary counts
  - a metadata sidecar describing selector definitions and defaults
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from relative_symmetry_repair.ca2d import (
    parse_rulestring,
    random_initial_grid,
    simulate_2d_general,
)
from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d
from relative_symmetry_repair.eca import simulate_eca
from relative_symmetry_repair.repair import scan_relative_periodicity
from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd
from relative_symmetry_repair.selector_tools import (
    SelectorVariant,
    ranked_candidates,
    select_best_candidate,
    shift_columns,
    shift_handling_from_1d,
    shift_handling_from_nd,
    write_metadata_sidecar,
)

NML_MODE = "hybrid"

SELECTORS: dict[str, SelectorVariant] = {
    "resid": SelectorVariant(
        name="candidate_residual_joint",
        selector_type="candidate_scan",
        score_type="residual_defect_rate",
        score_column="defect_rate",
        shift_handling="joint_shift_optimization",
    ),
    "nll": SelectorVariant(
        name="candidate_nll_joint",
        selector_type="candidate_scan",
        score_type="bernoulli_nll",
        score_column="nll_bits",
        shift_handling="joint_shift_optimization",
    ),
    "nml": SelectorVariant(
        name="candidate_nml_joint_hybrid",
        selector_type="candidate_scan",
        score_type="bernoulli_nml",
        score_column="nml_bits",
        shift_handling="joint_shift_optimization",
        nml_mode=NML_MODE,
    ),
}


def _stringify_shift(row: pd.Series) -> str:
    if "shift" in row:
        return str(int(row["shift"]))
    shifts = tuple(int(row[col]) for col in shift_columns(pd.DataFrame([row])))
    return str(shifts)


def _selected_record(frame: pd.DataFrame, prefix: str) -> dict[str, object]:
    variant = SELECTORS[prefix]
    best = select_best_candidate(frame, variant.score_column)
    return {
        f"{prefix}_selector": variant.name,
        f"{prefix}_score_type": variant.score_type,
        f"{prefix}_period": int(best["period"]),
        f"{prefix}_shift": _stringify_shift(best),
        f"{prefix}_score": float(best[variant.score_column]),
    }


def _annotate_candidates(frame: pd.DataFrame) -> pd.DataFrame:
    annotated = frame.reset_index(drop=True).copy()
    annotated["candidate_id"] = np.arange(len(annotated), dtype=np.int64)
    for prefix, variant in SELECTORS.items():
        ranked = ranked_candidates(
            annotated,
            variant.score_column,
            rank_column=f"{prefix}_rank",
        )[["candidate_id", f"{prefix}_rank"]]
        annotated = annotated.merge(ranked, on="candidate_id", how="left", sort=False)
        annotated[f"{prefix}_selected"] = annotated[f"{prefix}_rank"] == 1
    return annotated


def _summarize_rule(frame: pd.DataFrame, *, rule: str) -> dict[str, object]:
    record: dict[str, object] = {"rule": rule}
    for prefix in SELECTORS:
        record.update(_selected_record(frame, prefix))
    return record


def analyze_rule_2d(
    spacetime: np.ndarray,
    *,
    dataset: str,
    rule_id: str,
    periods,
    shift_range,
) -> tuple[dict[str, object], pd.DataFrame]:
    frame, _ = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=periods,
        nml_mode=NML_MODE,
    )
    annotated = _annotate_candidates(frame)
    annotated["dataset"] = dataset
    annotated["rule"] = rule_id
    return _summarize_rule(annotated, rule=rule_id), annotated


def run_lifewiki_survey(
    data_path: Path,
    *,
    steps: int = 100,
    width: int = 64,
    height: int = 64,
    max_period: int = 8,
    shift_radius: int = 2,
    density: float = 0.5,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run baseline comparison on all 106 LifeWiki rules."""
    with data_path.open() as f:
        rules = json.load(f)

    records = []
    candidate_frames = []
    periods = range(1, max_period + 1)
    shift_range = range(-shift_radius, shift_radius + 1)

    for i, rule in enumerate(rules):
        rulestring = rule["rulestring"]
        name = rule["name"]
        birth, survive = parse_rulestring(rulestring)
        initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
        spacetime = simulate_2d_general(initial, steps=steps, birth=birth, survive=survive)

        if spacetime[-1].sum() == 0 or spacetime[-1].sum() == spacetime[-1].size:
            trivial_record = {
                "rule": rulestring,
                "name": name,
                "dataset": "LifeWiki_T100",
                "trivial": True,
            }
            for prefix, variant in SELECTORS.items():
                trivial_record.update(
                    {
                        f"{prefix}_selector": variant.name,
                        f"{prefix}_score_type": variant.score_type,
                        f"{prefix}_period": 1,
                        f"{prefix}_shift": "(0, 0)",
                        f"{prefix}_score": 0.0,
                    }
                )
            records.append(trivial_record)
            print(f"  [{i+1:3d}/{len(rules)}] {rulestring:20s} trivial")
            continue

        try:
            rec, candidate_frame = analyze_rule_2d(
                spacetime,
                dataset="LifeWiki_T100",
                rule_id=rulestring,
                periods=periods,
                shift_range=shift_range,
            )
            rec["name"] = name
            rec["dataset"] = "LifeWiki_T100"
            rec["trivial"] = False
            candidate_frame["name"] = name
            candidate_frames.append(candidate_frame)
            records.append(rec)
            print(
                f"  [{i+1:3d}/{len(rules)}] {rulestring:20s} "
                f"resid=p{rec['resid_period']} nll=p{rec['nll_period']} nml=p{rec['nml_period']}"
            )
        except Exception as exc:
            print(f"  [{i+1:3d}/{len(rules)}] {rulestring:20s} ERROR: {exc}")
            error_record = {
                "rule": rulestring,
                "name": name,
                "dataset": "LifeWiki_T100",
                "trivial": True,
            }
            for prefix, variant in SELECTORS.items():
                error_record.update(
                    {
                        f"{prefix}_selector": variant.name,
                        f"{prefix}_score_type": variant.score_type,
                        f"{prefix}_period": None,
                        f"{prefix}_shift": None,
                        f"{prefix}_score": None,
                    }
                )
            records.append(error_record)

    return (
        pd.DataFrame.from_records(records).sort_values(["dataset", "rule"]).reset_index(drop=True),
        pd.concat(candidate_frames, ignore_index=True)
        if candidate_frames
        else pd.DataFrame(),
    )


def run_1d_eca(
    rules_shifts,
    *,
    width: int = 192,
    steps: int = 144,
    max_period: int = 10,
    density: float = 0.5,
    seed: int = 11,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run baseline comparison on 1D ECA rules."""
    records = []
    candidate_frames = []
    periods = range(1, max_period + 1)

    for rule_num, shift_radius in rules_shifts:
        rng = np.random.default_rng(seed)
        initial = (rng.random(width) < density).astype(np.uint8)
        spacetime = simulate_eca(rule_num, initial, steps)

        shifts = range(-shift_radius, shift_radius + 1)
        frame, _ = scan_relative_periodicity(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode=NML_MODE,
        )
        annotated = _annotate_candidates(frame)
        annotated["dataset"] = "1D_ECA"
        annotated["rule"] = f"ECA-{rule_num}"
        candidate_frames.append(annotated)

        rec = _summarize_rule(annotated, rule=f"ECA-{rule_num}")
        rec["dataset"] = "1D_ECA"
        records.append(rec)
        print(
            f"  ECA-{rule_num}: resid=p{rec['resid_period']} "
            f"nll=p{rec['nll_period']} nml=p{rec['nml_period']}"
        )

    return (
        pd.DataFrame.from_records(records).sort_values(["dataset", "rule"]).reset_index(drop=True),
        pd.concat(candidate_frames, ignore_index=True).sort_values(
            ["dataset", "rule", "period", "shift"]
        ).reset_index(drop=True),
    )


def run_3d(
    survive,
    birth,
    *,
    size: int = 16,
    steps: int = 80,
    max_period: int = 6,
    density: float = 0.5,
    seed: int = 11,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run baseline comparison on a 3D rule."""
    initial = random_initial_volume(size, size, size, density=density, seed=seed)
    spacetime = simulate_3d(initial, steps=steps, survive=survive, birth=birth)

    periods = range(1, max_period + 1)
    shift_range = range(-1, 2)
    frame, _ = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range, shift_range],
        periods=periods,
        nml_mode=NML_MODE,
    )
    annotated = _annotate_candidates(frame)
    annotated["dataset"] = "3D"
    annotated["rule"] = "diamoeba3d"

    rec = _summarize_rule(annotated, rule="diamoeba3d")
    rec["dataset"] = "3D"
    print(
        f"  3D diamoeba: resid=p{rec['resid_period']} "
        f"nll=p{rec['nll_period']} nml=p{rec['nml_period']}"
    )
    return (
        pd.DataFrame.from_records([rec]),
        annotated.sort_values(
            ["dataset", "rule", "period", "shift_0", "shift_1", "shift_2"]
        ).reset_index(drop=True),
    )


def summary_table(df: pd.DataFrame, label: str) -> None:
    """Print summary distribution table."""
    nt = df[df.get("trivial", False) != True] if "trivial" in df.columns else df
    print(f"\n=== {label} ({len(nt)} nontrivial rules) ===")
    print(f"{'Selector':<12} {'p=1':>6} {'p=2':>6} {'p=3':>6} {'p=4+':>6} {'max_p':>6}")
    for prefix, name in [("resid", "Residual"), ("nll", "NLL"), ("nml", "NML")]:
        vals = nt[f"{prefix}_period"].dropna()
        p1 = (vals == 1).sum()
        p2 = (vals == 2).sum()
        p3 = (vals == 3).sum()
        p4plus = (vals >= 4).sum()
        max_p = int(vals.max()) if len(vals) > 0 else 0
        print(f"{name:<12} {p1:>6} {p2:>6} {p3:>6} {p4plus:>6} {max_p:>6}")


def _summary_records(combined: pd.DataFrame) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for ds, label in [("1D_ECA", "1D ECA"), ("LifeWiki_T100", "LifeWiki"), ("3D", "3D")]:
        subset = combined[combined["dataset"] == ds]
        nt = subset[subset.get("trivial", False) != True] if "trivial" in subset.columns else subset
        for prefix, sel_name in [("resid", "Residual"), ("nll", "NLL"), ("nml", "NML")]:
            vals = nt[f"{prefix}_period"].dropna()
            records.append(
                {
                    "dataset": label,
                    "selector": sel_name,
                    "selector_variant": SELECTORS[prefix].name,
                    "score_type": SELECTORS[prefix].score_type,
                    "p1": int((vals == 1).sum()),
                    "p2": int((vals == 2).sum()),
                    "p3": int((vals == 3).sum()),
                    "p4plus": int((vals >= 4).sum()),
                    "max_period": int(vals.max()) if len(vals) > 0 else 0,
                    "n_rules": int(len(vals)),
                }
            )
    return records


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "data" / "lifewiki_rules.json"
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    all_records = []
    candidate_tables = []

    print("\n### 1D ECA ###")
    df_1d, candidates_1d = run_1d_eca([(30, 6), (54, 6), (110, 6)])
    summary_table(df_1d, "1D ECA")
    all_records.append(df_1d)
    candidate_tables.append(candidates_1d)

    print("\n### LifeWiki (T=100) ###")
    df_lw, candidates_lw = run_lifewiki_survey(data_path)
    summary_table(df_lw, "LifeWiki T=100")
    all_records.append(df_lw)
    if not candidates_lw.empty:
        candidate_tables.append(candidates_lw.sort_values(["dataset", "rule", "period", "shift_0", "shift_1"]))

    print("\n### 3D Diamoeba ###")
    df_3d, candidates_3d = run_3d(survive=(5, 8), birth=(5, 8))
    summary_table(df_3d, "3D Diamoeba")
    all_records.append(df_3d)
    candidate_tables.append(candidates_3d)

    combined = pd.concat(all_records, ignore_index=True).sort_values(
        ["dataset", "rule"]
    ).reset_index(drop=True)
    candidates = pd.concat(candidate_tables, ignore_index=True).sort_values(
        ["dataset", "rule", "period", *shift_columns(pd.concat(candidate_tables, ignore_index=True))]
    ).reset_index(drop=True)

    rule_level_path = results_dir / "baseline_selector_rule_level.csv"
    summary_path = results_dir / "baseline_selector_summary.csv"
    candidates_path = results_dir / "baseline_selector_candidates.csv"

    combined.to_csv(rule_level_path, index=False)
    pd.DataFrame.from_records(_summary_records(combined)).to_csv(summary_path, index=False)
    candidates.to_csv(candidates_path, index=False)

    metadata = {
        "experiment": "baseline_selector_comparison",
        "boundary_condition": "periodic",
        "selector_variants": [variant.to_metadata() for variant in SELECTORS.values()],
        "datasets": {
            "1D_ECA": {
                "width": 192,
                "steps": 144,
                "density": 0.5,
                "seed": 11,
                "period_range": list(range(1, 11)),
                "shift_range": list(range(-6, 7)),
                "shift_handling": shift_handling_from_1d(range(-6, 7)),
                "rules": ["ECA-30", "ECA-54", "ECA-110"],
            },
            "LifeWiki_T100": {
                "grid_size": [64, 64],
                "steps": 100,
                "density": 0.5,
                "seed": 42,
                "period_range": list(range(1, 9)),
                "shift_range": list(range(-2, 3)),
                "shift_handling": shift_handling_from_nd([range(-2, 3), range(-2, 3)]),
                "n_rules": 106,
            },
            "3D": {
                "grid_size": [16, 16, 16],
                "steps": 80,
                "density": 0.5,
                "seed": 11,
                "period_range": list(range(1, 7)),
                "shift_range": list(range(-1, 2)),
                "shift_handling": shift_handling_from_nd([range(-1, 2)] * 3),
                "rule": "diamoeba3d",
            },
        },
        "outputs": {
            "rule_level": str(rule_level_path.relative_to(root)),
            "summary": str(summary_path.relative_to(root)),
            "candidates": str(candidates_path.relative_to(root)),
        },
    }
    write_metadata_sidecar(rule_level_path, metadata)
    write_metadata_sidecar(summary_path, metadata)
    write_metadata_sidecar(candidates_path, metadata)

    print(f"\nSaved to {results_dir}")


if __name__ == "__main__":
    main()
