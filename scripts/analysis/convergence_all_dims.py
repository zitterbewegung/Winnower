"""Cross-dimensional NML convergence study (1D, 2D, 3D).

Validates the NML consistency theorem: for each rule, the NML-selected
period stabilizes as T grows, with margins increasing monotonically
once stabilized.  Uses exact Bernoulli NML on orbit classes.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.eca import random_initial_state, simulate_eca
from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d
from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d
from relative_symmetry_repair.repair import fit_relative_periodic_background
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

# ── 1D Rules ─────────────────────────────────────────────────────────────────
RULES_1D = [
    ("ECA-54", 54),
    ("ECA-110", 110),
    ("ECA-30", 30),
]
T_VALUES_1D = [50, 100, 200, 400, 600, 800]

# ── 2D Rules ─────────────────────────────────────────────────────────────────
RULES_2D = [
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
]
T_VALUES_2D = [60, 100, 200, 400, 600, 800]

# ── 3D Rules ─────────────────────────────────────────────────────────────────
RULES_3D = [
    ("3d-life", (4, 5), (5, 5)),
    ("diamoeba3d", (5, 8), (5, 8)),
]
T_VALUES_3D = [10, 20, 40, 60, 80]


def convergence_1d(max_period=10):
    """1D ECA convergence: sweep T, find NML-optimal period."""
    print("\n" + "=" * 70)
    print("1D ECA CONVERGENCE")
    print("=" * 70)

    results = []
    for name, rule_num in RULES_1D:
        print(f"\n  {name}:")
        max_T = max(T_VALUES_1D)
        initial = random_initial_state(width=192, density=0.5, seed=11)
        spacetime_full = simulate_eca(rule=rule_num, initial=initial, steps=max_T)

        for T in T_VALUES_1D:
            spacetime = spacetime_full[:T + 1]
            best_nml = float("inf")
            best_p = 1
            all_scores = {}
            for p in range(1, max_period + 1):
                fit = fit_relative_periodic_background(spacetime, shift=0, period=p)
                all_scores[p] = fit.nml_bits
                if fit.nml_bits < best_nml:
                    best_nml = fit.nml_bits
                    best_p = p

            runner_up = min(v for k, v in all_scores.items() if k != best_p)
            margin = runner_up - best_nml

            results.append({
                "dim": 1, "rule": name, "T": T,
                "best_period": best_p, "best_nml": round(best_nml, 1),
                "runner_up_nml": round(runner_up, 1), "margin": round(margin, 1),
            })
            print(f"    T={T}: period={best_p}, nml={best_nml:.0f}, margin={margin:.0f}")

    return pd.DataFrame.from_records(results)


def convergence_2d(max_period=8):
    """2D totalistic convergence: sweep T, find NML-optimal period."""
    print("\n" + "=" * 70)
    print("2D TOTALISTIC CONVERGENCE")
    print("=" * 70)

    results = []
    for name, survive, birth in RULES_2D:
        print(f"\n  {name}:")
        max_T = max(T_VALUES_2D)
        initial = random_initial_grid(width=64, height=64, density=0.5, seed=11)
        spacetime_full = simulate_2d(initial, steps=max_T, rule="custom",
                                     survive=survive, birth=birth)

        for T in T_VALUES_2D:
            spacetime = spacetime_full[:T + 1]
            best_nml = float("inf")
            best_p = 1
            all_scores = {}
            for p in range(1, max_period + 1):
                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
                all_scores[p] = fit.nml_bits
                if fit.nml_bits < best_nml:
                    best_nml = fit.nml_bits
                    best_p = p

            runner_up = min(v for k, v in all_scores.items() if k != best_p)
            margin = runner_up - best_nml

            results.append({
                "dim": 2, "rule": name, "T": T,
                "best_period": best_p, "best_nml": round(best_nml, 1),
                "runner_up_nml": round(runner_up, 1), "margin": round(margin, 1),
            })
            print(f"    T={T}: period={best_p}, nml={best_nml:.0f}, margin={margin:.0f}")

    return pd.DataFrame.from_records(results)


def convergence_3d(max_period=6):
    """3D totalistic convergence: sweep T, find NML-optimal period."""
    print("\n" + "=" * 70)
    print("3D TOTALISTIC CONVERGENCE")
    print("=" * 70)

    results = []
    for name, survive, birth in RULES_3D:
        print(f"\n  {name}:")
        max_T = max(T_VALUES_3D)
        initial = random_initial_volume(sx=16, sy=16, sz=16, density=0.3, seed=11)
        spacetime_full = simulate_3d(initial, steps=max_T, rule="custom",
                                     survive=survive, birth=birth)

        # Check for trivial outcome
        end_density = float(spacetime_full[-5:].mean())
        if end_density < 0.02 or end_density > 0.98:
            print(f"    TRIVIAL (density={end_density:.3f}), skipping")
            continue

        for T in T_VALUES_3D:
            spacetime = spacetime_full[:T + 1]
            best_nml = float("inf")
            best_p = 1
            all_scores = {}
            for p in range(1, max_period + 1):
                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0, 0), period=p)
                all_scores[p] = fit.nml_bits
                if fit.nml_bits < best_nml:
                    best_nml = fit.nml_bits
                    best_p = p

            runner_up = min(v for k, v in all_scores.items() if k != best_p)
            margin = runner_up - best_nml

            results.append({
                "dim": 3, "rule": name, "T": T,
                "best_period": best_p, "best_nml": round(best_nml, 1),
                "runner_up_nml": round(runner_up, 1), "margin": round(margin, 1),
            })
            print(f"    T={T}: period={best_p}, nml={best_nml:.0f}, margin={margin:.0f}")

    return pd.DataFrame.from_records(results)


def main():
    out_dir = Path("outputs/convergence")
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    df_1d = convergence_1d()
    df_2d = convergence_2d()
    df_3d = convergence_3d()

    df_all = pd.concat([df_1d, df_2d, df_3d], ignore_index=True)

    df_all.to_csv(out_dir / "convergence_all_dims.csv", index=False)
    df_1d.to_csv(out_dir / "convergence_1d.csv", index=False)
    df_2d.to_csv(out_dir / "convergence_2d.csv", index=False)
    df_3d.to_csv(out_dir / "convergence_3d.csv", index=False)

    elapsed = time.time() - t0
    print(f"\nAll convergence experiments completed in {elapsed:.1f}s")
    print(f"Results saved to {out_dir}")

    # Summary: show stabilization
    print("\n=== CONVERGENCE SUMMARY ===")
    for dim in [1, 2, 3]:
        subset = df_all[df_all["dim"] == dim]
        if subset.empty:
            continue
        print(f"\n  {dim}D rules:")
        for rule in subset["rule"].unique():
            rule_data = subset[subset["rule"] == rule]
            periods = rule_data["best_period"].tolist()
            margins = rule_data["margin"].tolist()
            T_vals = rule_data["T"].tolist()
            print(f"    {rule}: periods={dict(zip(T_vals, periods))}")
            print(f"           margins={dict(zip(T_vals, [int(m) for m in margins]))}")


if __name__ == "__main__":
    main()
