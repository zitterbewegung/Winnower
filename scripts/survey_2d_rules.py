"""Survey 2D totalistic rules to find ones with strong relative-periodic structure."""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d, rule_consistency_rate_2d
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd, scan_relative_periodicity_nd


def density_at_end(spacetime: np.ndarray, last_n: int = 5) -> float:
    """Average density over the last N time steps."""
    return float(spacetime[-last_n:].mean())


def survey_rule(
    survive: tuple[int, int],
    birth: tuple[int, int],
    width: int = 48,
    height: int = 48,
    steps: int = 40,
    density: float = 0.5,
    seed: int = 11,
    shift_radius: int = 3,
    max_period: int = 6,
) -> dict | None:
    """Run a quick analysis for one (survive, birth) rule. Returns None if trivial."""
    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

    # Check for trivial outcomes
    end_density = density_at_end(spacetime)
    if end_density < 0.02 or end_density > 0.98:
        return None  # died out or filled up

    # Check that there's actual temporal change in the last portion
    last_slice = spacetime[-10:]
    if np.all(last_slice == last_slice[0:1]):
        # Completely static — still interesting if we find period=1 shift!=0,
        # but let's skip pure fixed points
        pass

    def rule_error_fn(bg):
        return rule_consistency_rate_2d(bg, survive, birth)

    shift_range = range(-shift_radius, shift_radius + 1)
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    best = frame.sort_values(["mdl_bits", "defect_rate"]).iloc[0]
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
        "rule_error": round(best_fit.rule_error, 5) if best_fit.rule_error is not None else None,
        "has_nonzero_shift": best_shift != (0, 0),
        "total_sites": best_fit.total_sites,
        "defect_sites": best_fit.defect_sites,
    }


def main():
    # Generate candidate (survive, birth) range pairs
    # Survival range: (lo, hi) where 0 <= lo <= hi <= 8
    # Birth range: (lo, hi) where 0 <= lo <= hi <= 8
    # Focus on ranges that are likely to produce interesting dynamics:
    # - Not too permissive (everything lives) or too restrictive (everything dies)

    candidates = []
    for s_lo in range(0, 7):
        for s_hi in range(s_lo, min(s_lo + 4, 9)):  # keep range width <= 3
            for b_lo in range(1, 7):  # birth needs at least 1 neighbor
                for b_hi in range(b_lo, min(b_lo + 4, 9)):
                    candidates.append(((s_lo, s_hi), (b_lo, b_hi)))

    print(f"Surveying {len(candidates)} rule candidates...")
    results = []
    trivial_count = 0
    t0 = time.time()

    for i, (survive, birth) in enumerate(candidates):
        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(candidates) - i - 1) / rate
            print(f"  [{i+1}/{len(candidates)}] {elapsed:.0f}s elapsed, ~{eta:.0f}s remaining, "
                  f"{len(results)} non-trivial so far, {trivial_count} trivial")

        try:
            result = survey_rule(survive, birth)
            if result is None:
                trivial_count += 1
            else:
                results.append(result)
        except Exception as e:
            print(f"  Error on S{survive}/B{birth}: {e}")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s. {len(results)} non-trivial rules, {trivial_count} trivial (died/filled).")

    df = pd.DataFrame.from_records(results)
    df = df.sort_values("defect_rate").reset_index(drop=True)

    out_path = Path("outputs/survey_2d_rules.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")

    # Print top 30
    print("\n=== TOP 30 BY DEFECT RATE ===")
    print(df.head(30).to_string(index=False))

    # Print top rules with nonzero shift (most interesting)
    shifted = df[df["has_nonzero_shift"]].head(20)
    if len(shifted) > 0:
        print("\n=== TOP 20 WITH NONZERO SHIFT (drifting periodic structure) ===")
        print(shifted.to_string(index=False))


if __name__ == "__main__":
    main()
