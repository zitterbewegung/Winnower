"""Strengthening experiments v2 — addresses all Codex review critiques.

1. Re-run 2D survey with MDL scoring
2. 400-step verification of persistent defects
3. Multi-seed size scaling
4. Autocorrelation baseline with MDL
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d, rule_consistency_rate_2d
from relative_symmetry_repair.repair_nd import (
    fit_relative_periodic_background_nd,
    scan_relative_periodicity_nd,
)

SEEDS = [11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]

PERSISTENT_RULES = [
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
]

TOP_RULES = [
    ("S14_B11", (1, 4), (1, 1)),
    ("S25_B12", (2, 5), (1, 2)),
    ("S66_B36", (6, 6), (3, 6)),
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
]


# ── Experiment 1: 400-step verification ──────────────────────────────────────

def experiment_400step(width=64, height=64, steps=400):
    """Verify that persistent defects stabilize at 400 steps."""
    print("\n" + "=" * 70)
    print("EXPERIMENT: 400-step verification")
    print("=" * 70)

    results = []
    for name, survive, birth in PERSISTENT_RULES:
        initial = random_initial_grid(width=width, height=height, density=0.5, seed=11)
        spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

        # Find best MDL period
        best_mdl = float("inf")
        best_p = 1
        for p in range(1, 9):
            fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
            if fit.mdl_bits < best_mdl:
                best_mdl = fit.mdl_bits
                best_p = p

        fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=best_p)
        defects_per_t = fit.defect_mask.sum(axis=(1, 2))

        # Measure defect counts in windows
        windows = [
            ("t=50-100", 50, 100),
            ("t=100-200", 100, 200),
            ("t=200-300", 200, 300),
            ("t=300-400", 300, 400),
        ]
        print(f"\n  {name} (MDL period={best_p}, mdl={best_mdl}):")
        for label, t0, t1 in windows:
            segment = defects_per_t[t0:t1]
            result = {
                "rule": name,
                "window": label,
                "period": best_p,
                "mdl_bits": best_mdl,
                "mean_defects": round(float(segment.mean()), 1),
                "std_defects": round(float(segment.std()), 1),
                "min_defects": int(segment.min()),
                "max_defects": int(segment.max()),
            }
            results.append(result)
            print(f"    {label}: {result['mean_defects']} ± {result['std_defects']} "
                  f"[{result['min_defects']}, {result['max_defects']}]")

    return pd.DataFrame.from_records(results)


# ── Experiment 2: Multi-seed size scaling ─────────────────────────────────

GRID_SIZES = [32, 64, 96, 128, 192]


def experiment_multiseed_scaling(steps=100, n_seeds=5):
    """Multi-seed size-scaling experiment."""
    print("\n" + "=" * 70)
    print("EXPERIMENT: Multi-seed size scaling")
    print("=" * 70)

    results = []
    seeds_to_use = SEEDS[:n_seeds]

    for name, survive, birth in PERSISTENT_RULES:
        print(f"\n  {name}:")
        for size in GRID_SIZES:
            rates = []
            defect_counts = []
            periods = []
            for seed in seeds_to_use:
                initial = random_initial_grid(width=size, height=size, density=0.5, seed=seed)
                spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

                end_density = float(spacetime[-10:].mean())
                if end_density < 0.02 or end_density > 0.98:
                    continue

                # Find best MDL period
                best_mdl = float("inf")
                best_p = 1
                for p in range(1, 9):
                    fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
                    if fit.mdl_bits < best_mdl:
                        best_mdl = fit.mdl_bits
                        best_p = p

                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=best_p)
                rates.append(fit.defect_rate)
                mid = len(fit.defect_mask) // 2
                late = fit.defect_mask[mid:].sum(axis=(1, 2))
                defect_counts.append(float(late.mean()))
                periods.append(best_p)

            if not rates:
                continue

            rates_arr = np.array(rates)
            defects_arr = np.array(defect_counts)
            result = {
                "rule": name,
                "grid_size": size,
                "n_seeds": len(rates),
                "mean_rate": round(float(rates_arr.mean()), 5),
                "std_rate": round(float(rates_arr.std()), 5),
                "mean_late_defects": round(float(defects_arr.mean()), 1),
                "std_late_defects": round(float(defects_arr.std()), 1),
                "defect_density": round(float(defects_arr.mean()) / (size * size), 6),
                "modal_period": int(np.median(periods)),
            }
            results.append(result)
            print(f"    {size}x{size}: rate={result['mean_rate']:.4f}±{result['std_rate']:.4f}, "
                  f"defects={result['mean_late_defects']:.1f}±{result['std_late_defects']:.1f}, "
                  f"density={result['defect_density']:.6f} (n={result['n_seeds']})")

    return pd.DataFrame.from_records(results)


# ── Experiment 3: Multi-seed robustness with MDL ─────────────────────────────

def experiment_multi_seed_mdl(width=64, height=64, steps=60):
    """Multi-seed robustness with MDL-based period selection."""
    print("\n" + "=" * 70)
    print("EXPERIMENT: Multi-seed robustness (MDL)")
    print("=" * 70)

    results = []
    for name, survive, birth in TOP_RULES:
        defect_rates = []
        mdl_values = []
        periods = []
        for seed in SEEDS:
            initial = random_initial_grid(width=width, height=height, density=0.5, seed=seed)
            spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

            end_density = float(spacetime[-10:].mean())
            if end_density < 0.02 or end_density > 0.98:
                continue

            best_mdl = float("inf")
            best_p = 1
            best_rate = 1.0
            for p in range(1, 9):
                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
                if fit.mdl_bits < best_mdl:
                    best_mdl = fit.mdl_bits
                    best_p = p
                    best_rate = fit.defect_rate

            defect_rates.append(best_rate)
            mdl_values.append(best_mdl)
            periods.append(best_p)

        rates_arr = np.array(defect_rates)
        periods_arr = np.array(periods)
        mdl_arr = np.array(mdl_values)
        result = {
            "rule": name,
            "mean_defect_rate": float(rates_arr.mean()),
            "std_defect_rate": float(rates_arr.std()),
            "mean_mdl_bits": int(mdl_arr.mean()),
            "n_valid_seeds": len(rates_arr),
            "modal_period": int(np.median(periods_arr)),
            "period_consistent": len(set(periods_arr)) == 1,
        }
        results.append(result)
        print(f"  {name}: rate={result['mean_defect_rate']:.4f} ± {result['std_defect_rate']:.4f}, "
              f"MDL period={result['modal_period']}, consistent={result['period_consistent']}")

    return pd.DataFrame.from_records(results)


# ── Experiment 4: Autocorrelation baseline with MDL ──────────────────────────

def autocorrelation_period_detect(spacetime, max_period=10):
    """Detect dominant temporal period via autocorrelation."""
    T = spacetime.shape[0]
    flat = spacetime.reshape(T, -1).astype(np.float64)
    mean = flat.mean(axis=1)
    centered = flat - mean[:, None]
    autocorrs = []
    for lag in range(1, min(max_period + 1, T)):
        num = (centered[:T - lag] * centered[lag:]).sum()
        den = np.sqrt((centered[:T - lag] ** 2).sum() * (centered[lag:] ** 2).sum())
        autocorrs.append(num / den if den > 0 else 0.0)
    return int(np.argmax(autocorrs)) + 1, np.array(autocorrs)


def experiment_autocorrelation_mdl(width=64, height=64, steps=60):
    """Compare MDL-selected period vs autocorrelation."""
    print("\n" + "=" * 70)
    print("EXPERIMENT: Autocorrelation vs MDL baseline")
    print("=" * 70)

    results = []
    for name, survive, birth in TOP_RULES:
        initial = random_initial_grid(width=width, height=height, density=0.5, seed=11)
        spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

        # Autocorrelation baseline
        ac_period, _ = autocorrelation_period_detect(spacetime)
        ac_fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=ac_period)

        # MDL-optimal
        best_mdl = float("inf")
        best_p = 1
        for p in range(1, 9):
            fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
            if fit.mdl_bits < best_mdl:
                best_mdl = fit.mdl_bits
                best_p = p

        mdl_fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=best_p)

        result = {
            "rule": name,
            "ac_period": ac_period,
            "ac_defect_rate": round(ac_fit.defect_rate, 5),
            "ac_mdl_bits": ac_fit.mdl_bits,
            "mdl_period": best_p,
            "mdl_defect_rate": round(mdl_fit.defect_rate, 5),
            "mdl_bits": best_mdl,
            "period_agrees": ac_period == best_p,
            "mdl_improvement": round(ac_fit.mdl_bits - best_mdl),
        }
        results.append(result)
        print(f"  {name}: AC p={ac_period} mdl={ac_fit.mdl_bits} | "
              f"MDL p={best_p} mdl={best_mdl} | "
              f"improvement={result['mdl_improvement']} bits")

    return pd.DataFrame.from_records(results)


def main():
    out_dir = Path("outputs/strengthening_v2")
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    df_400 = experiment_400step()
    df_400.to_csv(out_dir / "verification_400step.csv", index=False)

    df_mseed = experiment_multi_seed_mdl()
    df_mseed.to_csv(out_dir / "multi_seed_mdl.csv", index=False)

    df_ac = experiment_autocorrelation_mdl()
    df_ac.to_csv(out_dir / "autocorrelation_mdl.csv", index=False)

    df_scale = experiment_multiseed_scaling(n_seeds=5)
    df_scale.to_csv(out_dir / "multiseed_scaling.csv", index=False)

    elapsed = time.time() - t0
    print(f"\nAll experiments completed in {elapsed:.1f}s")
    print(f"Results saved to {out_dir}")

    print("\n=== 400-STEP VERIFICATION ===")
    print(df_400.to_string(index=False))
    print("\n=== MULTI-SEED MDL ===")
    print(df_mseed.to_string(index=False))
    print("\n=== AUTOCORRELATION vs MDL ===")
    print(df_ac.to_string(index=False))
    print("\n=== MULTI-SEED SCALING ===")
    print(df_scale.to_string(index=False))


if __name__ == "__main__":
    main()
