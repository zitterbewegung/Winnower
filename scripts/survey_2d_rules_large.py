"""Large-scale survey of 2D totalistic rules (1000+ candidates).

Expands the candidate space to range widths ≤ 4 and uses multiprocessing
for speed. Primary selector: exact Bernoulli NML on orbit classes.
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d, rule_consistency_rate_2d
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd, scan_relative_periodicity_nd


def density_at_end(spacetime: np.ndarray, last_n: int = 5) -> float:
    return float(spacetime[-last_n:].mean())


def survey_rule(args: tuple) -> dict | None:
    """Run a quick analysis for one (survive, birth) rule. Returns None if trivial."""
    survive, birth = args
    width, height, steps = 48, 48, 40
    density, seed = 0.5, 11
    shift_radius, max_period = 2, 6  # 5x5 shifts, periods 1-6

    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

    end_density = density_at_end(spacetime)
    if end_density < 0.02 or end_density > 0.98:
        return None

    def rule_error_fn(bg):
        return rule_consistency_rate_2d(bg, survive, birth)

    shift_range = range(-shift_radius, shift_radius + 1)
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    best = frame.sort_values(["nml_bits", "defect_rate"]).iloc[0]
    best_shift = (int(best["shift_0"]), int(best["shift_1"]))
    best_period = int(best["period"])
    best_fit = fits[(best_shift, best_period)]

    return {
        "survive_lo": survive[0],
        "survive_hi": survive[1],
        "birth_lo": birth[0],
        "birth_hi": birth[1],
        "rule_name": f"S{survive[0]}{survive[1]}/B{birth[0]}{birth[1]}",
        "end_density": round(end_density, 4),
        "best_shift_0": best_shift[0],
        "best_shift_1": best_shift[1],
        "best_period": best_period,
        "defect_rate": round(best_fit.defect_rate, 5),
        "run_length_bits": best_fit.run_length_bits,
        "lz4_bits": best_fit.lz4_bits,
        "template_bits": best_fit.template_bits,
        "mdl_bits": round(best_fit.mdl_bits, 1),
        "nll_bits": round(best_fit.nll_bits, 1),
        "nml_complexity": round(best_fit.nml_complexity, 1),
        "nml_bits": round(best_fit.nml_bits, 1),
        "rule_error": round(best_fit.rule_error, 5) if best_fit.rule_error is not None else None,
        "has_nonzero_shift": best_shift != (0, 0),
        "total_sites": best_fit.total_sites,
        "defect_sites": best_fit.defect_sites,
    }


def generate_candidates() -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Generate (survive, birth) range pairs with range width <= 4."""
    candidates = []
    for s_lo in range(0, 9):
        for s_hi in range(s_lo, min(s_lo + 5, 9)):  # range width <= 4
            for b_lo in range(1, 9):  # birth needs at least 1 neighbor
                for b_hi in range(b_lo, min(b_lo + 5, 9)):
                    candidates.append(((s_lo, s_hi), (b_lo, b_hi)))
    return candidates


def main():
    candidates = generate_candidates()
    print(f"Surveying {len(candidates)} rule candidates using {cpu_count()} cores...")
    t0 = time.time()

    # Use multiprocessing for speed
    n_workers = min(cpu_count(), 8)
    with Pool(n_workers) as pool:
        raw_results = pool.map(survey_rule, candidates, chunksize=4)

    results = [r for r in raw_results if r is not None]
    trivial_count = sum(1 for r in raw_results if r is None)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s. {len(results)} non-trivial rules, {trivial_count} trivial.")

    df = pd.DataFrame.from_records(results)
    df = df.sort_values("nml_bits").reset_index(drop=True)

    out_path = Path("outputs/survey_2d_rules_large.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")

    print(f"\n=== SUMMARY ===")
    print(f"Total non-trivial: {len(results)}")
    print(f"With nonzero shift: {df['has_nonzero_shift'].sum()}")
    print(f"Period distribution:")
    print(df["best_period"].value_counts().sort_index().to_string())

    print(f"\n=== TOP 30 BY NML BITS ===")
    cols = ["rule_name", "best_period", "best_shift_0", "best_shift_1",
            "defect_rate", "nml_bits", "nll_bits", "nml_complexity", "rule_error"]
    print(df[cols].head(30).to_string(index=False))

    shifted = df[df["has_nonzero_shift"]].head(20)
    if len(shifted) > 0:
        print(f"\n=== TOP 20 WITH NONZERO SHIFT ===")
        print(shifted[cols].to_string(index=False))


if __name__ == "__main__":
    main()
