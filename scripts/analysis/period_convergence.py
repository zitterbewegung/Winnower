"""Period convergence study — generates backing data for Section 5.3."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

RULES = [
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
]

T_VALUES = [60, 100, 200, 400, 600, 800]
MAX_PERIOD = 8


def main():
    out_dir = Path("outputs/strengthening_v2")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    t0 = time.time()

    for name, survive, birth in RULES:
        print(f"\n{name}:")
        # Generate spacetime at max T, then slice for shorter windows
        max_T = max(T_VALUES)
        initial = random_initial_grid(width=64, height=64, density=0.5, seed=11)
        spacetime_full = simulate_2d(initial, steps=max_T, rule="custom", survive=survive, birth=birth)

        for T in T_VALUES:
            spacetime = spacetime_full[:T + 1]  # T steps = T+1 frames

            best_mdl = float("inf")
            best_p = 1
            all_scores = {}
            for p in range(1, MAX_PERIOD + 1):
                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
                all_scores[p] = fit.mdl_bits
                if fit.mdl_bits < best_mdl:
                    best_mdl = fit.mdl_bits
                    best_p = p

            # Find runner-up
            runner_up_mdl = min(v for k, v in all_scores.items() if k != best_p)
            margin = runner_up_mdl - best_mdl

            result = {
                "rule": name,
                "T": T,
                "best_period": best_p,
                "best_mdl": round(best_mdl, 1),
                "runner_up_mdl": round(runner_up_mdl, 1),
                "margin": round(margin, 1),
            }
            results.append(result)
            print(f"  T={T}: period={best_p}, mdl={best_mdl:.0f}, margin={margin:.0f}")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")

    df = pd.DataFrame.from_records(results)
    out_path = out_dir / "period_convergence.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
