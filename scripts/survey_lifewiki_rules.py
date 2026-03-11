#!/usr/bin/env python3
"""Survey all 106 Life-like rules from the LifeWiki using period-first NML selection.

For each rule:
1. Simulate on a 64x64 torus for 100 steps
2. Run period-first selection (periods 1-8, shifts -2..2)
3. Record: selected period, shift, NML score, defect rate, margin, status

Rules with B0 are strobing (every dead cell with 0 neighbors is born),
which means the entire grid oscillates. We include them but flag them.

Output: outputs/lifewiki_survey.csv
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from relative_symmetry_repair.ca2d import (
    random_initial_grid,
    simulate_2d_general,
    parse_rulestring,
)
from relative_symmetry_repair.selection import select_period_nd, selection_summary


def is_trivial(spacetime: np.ndarray) -> str:
    """Check if a spacetime is trivially dead, all-ones, or static."""
    if spacetime[-1].sum() == 0:
        return "dead"
    if spacetime[-1].sum() == spacetime[-1].size:
        return "all_ones"
    if np.array_equal(spacetime[0], spacetime[-1]):
        # Could be static or low-period
        if np.array_equal(spacetime[0], spacetime[1]):
            return "static"
    return "nontrivial"


def survey_rule(
    rulestring: str,
    name: str,
    width: int = 64,
    height: int = 64,
    steps: int = 100,
    density: float = 0.5,
    seed: int = 42,
    max_period: int = 8,
    shift_radius: int = 2,
) -> dict:
    """Run period-first selection on a single Life-like rule."""
    birth, survive = parse_rulestring(rulestring)
    has_b0 = 0 in birth

    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d_general(initial, steps=steps, birth=birth, survive=survive)

    triviality = is_trivial(spacetime)

    # Compute density at last step
    final_density = float(spacetime[-1].mean())

    # If dead or all-ones, skip full analysis
    if triviality in ("dead", "all_ones", "static"):
        return {
            "rulestring": rulestring,
            "name": name,
            "has_b0": has_b0,
            "triviality": triviality,
            "final_density": final_density,
            "selected_period": 1,
            "selected_shift": "(0, 0)",
            "nml_bits": 0.0,
            "nll_bits": 0.0,
            "complexity_bits": 0.0,
            "defect_rate": 0.0,
            "margin_bits": float("inf"),
            "status": "trivial",
            "runner_up_period": None,
        }

    shift_range = range(-shift_radius, shift_radius + 1)
    result = select_period_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
    )
    summary = selection_summary(result)

    return {
        "rulestring": rulestring,
        "name": name,
        "has_b0": has_b0,
        "triviality": triviality,
        "final_density": final_density,
        "selected_period": summary["selected_period"],
        "selected_shift": str(summary["selected_shift"]),
        "nml_bits": summary["selected_nml_bits"],
        "nll_bits": summary["selected_nll_bits"],
        "complexity_bits": summary["selected_complexity"],
        "defect_rate": summary["selected_defect_rate"],
        "margin_bits": summary["margin_bits"],
        "status": summary["status"],
        "runner_up_period": summary.get("runner_up_period"),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--max-period", type=int, default=8)
    parser.add_argument("--shift-radius", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-suffix", type=str, default="")
    args = parser.parse_args()

    data_path = Path(__file__).resolve().parent.parent / "data" / "lifewiki_rules.json"
    output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(data_path) as f:
        rules = json.load(f)

    print(f"Surveying {len(rules)} Life-like rules from LifeWiki")
    print(f"Grid: {args.width}x{args.height}, steps: {args.steps}, periods: 1-{args.max_period}, shifts: -{args.shift_radius}..{args.shift_radius}")
    print()

    records = []
    t0 = time.time()

    for i, rule in enumerate(rules):
        rulestring = rule["rulestring"]
        name = rule["name"]
        try:
            rec = survey_rule(rulestring, name, width=args.width, height=args.height,
                              steps=args.steps, seed=args.seed,
                              max_period=args.max_period, shift_radius=args.shift_radius)
            records.append(rec)
            status_icon = {
                "stable_winner": "+",
                "near_tie": "~",
                "unresolved": "?",
                "trivial": ".",
            }.get(rec["status"], " ")
            print(f"  [{status_icon}] {i+1:3d}/{len(rules)} {rulestring:20s} "
                  f"p={rec['selected_period']} s={rec['selected_shift']:12s} "
                  f"d={rec['defect_rate']:.3f} m={rec['margin_bits']:8.1f}  {name}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  [!] {i+1:3d}/{len(rules)} {rulestring:20s} ERROR: {e}")
            records.append({
                "rulestring": rulestring,
                "name": name,
                "has_b0": 0 in rule.get("birth", []),
                "triviality": "error",
                "final_density": None,
                "selected_period": None,
                "selected_shift": None,
                "nml_bits": None,
                "nll_bits": None,
                "complexity_bits": None,
                "defect_rate": None,
                "margin_bits": None,
                "status": f"error: {e}",
                "runner_up_period": None,
            })

    elapsed = time.time() - t0
    df = pd.DataFrame.from_records(records)
    suffix = args.output_suffix or f"_T{args.steps}"
    csv_path = output_dir / f"lifewiki_survey{suffix}.csv"
    df.to_csv(csv_path, index=False)

    print(f"\nDone in {elapsed:.1f}s")
    print(f"Saved to {csv_path}")

    # Summary
    nontrivial = df[df["triviality"] == "nontrivial"]
    print(f"\nSummary:")
    print(f"  Total rules: {len(df)}")
    print(f"  Trivial (dead/static/all_ones): {len(df) - len(nontrivial)}")
    print(f"  Nontrivial: {len(nontrivial)}")
    if len(nontrivial) > 0:
        print(f"  Period distribution:")
        for p, count in nontrivial["selected_period"].value_counts().sort_index().items():
            print(f"    p={p}: {count} rules")
        print(f"  Status distribution:")
        for s, count in nontrivial["status"].value_counts().items():
            print(f"    {s}: {count}")
        print(f"\n  Rules with period > 1:")
        higher = nontrivial[nontrivial["selected_period"] > 1].sort_values("selected_period")
        for _, row in higher.iterrows():
            print(f"    {row['rulestring']:20s} p={row['selected_period']} "
                  f"d={row['defect_rate']:.3f} m={row['margin_bits']:.1f}  {row['name']}")


if __name__ == "__main__":
    main()
