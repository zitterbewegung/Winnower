"""Strengthening experiments for paper:
1. Multi-seed robustness of top 2D rules
2. Autocorrelation baseline comparison
3. Size-scaling of persistent defect rules
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
from relative_symmetry_repair.coding import run_length_bits


# ── Experiment 1: Multi-seed robustness ──────────────────────────────────────

TOP_RULES = [
    ("S14_B11", (1, 4), (1, 1)),
    ("S25_B12", (2, 5), (1, 2)),
    ("S66_B36", (6, 6), (3, 6)),
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
]

SEEDS = [11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]


def experiment_multi_seed(width=64, height=64, steps=60):
    """Test whether top rules' rankings are stable across 10 random seeds."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 1: Multi-seed robustness")
    print("=" * 70)

    results = []
    for name, survive, birth in TOP_RULES:
        defect_rates = []
        periods = []
        for seed in SEEDS:
            initial = random_initial_grid(width=width, height=height, density=0.5, seed=seed)
            spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

            end_density = float(spacetime[-10:].mean())
            if end_density < 0.02 or end_density > 0.98:
                defect_rates.append(np.nan)
                periods.append(np.nan)
                continue

            # Quick scan: just test the best-known shift (0,0) with periods 1-8
            best_rate = 1.0
            best_p = 1
            for p in range(1, 9):
                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
                if fit.defect_rate < best_rate:
                    best_rate = fit.defect_rate
                    best_p = p
            defect_rates.append(best_rate)
            periods.append(best_p)

        rates_arr = np.array([r for r in defect_rates if not np.isnan(r)])
        periods_arr = np.array([p for p in periods if not np.isnan(p)])
        result = {
            "rule": name,
            "mean_defect_rate": float(rates_arr.mean()) if len(rates_arr) > 0 else np.nan,
            "std_defect_rate": float(rates_arr.std()) if len(rates_arr) > 0 else np.nan,
            "min_defect_rate": float(rates_arr.min()) if len(rates_arr) > 0 else np.nan,
            "max_defect_rate": float(rates_arr.max()) if len(rates_arr) > 0 else np.nan,
            "n_valid_seeds": len(rates_arr),
            "modal_period": int(np.median(periods_arr)) if len(periods_arr) > 0 else 0,
            "period_consistent": len(set(periods_arr)) == 1 if len(periods_arr) > 0 else False,
        }
        results.append(result)
        print(f"  {name}: rate={result['mean_defect_rate']:.4f} ± {result['std_defect_rate']:.4f}, "
              f"period consistent={result['period_consistent']}, seeds={result['n_valid_seeds']}/10")

    return pd.DataFrame.from_records(results)


# ── Experiment 2: Autocorrelation baseline ───────────────────────────────────

def autocorrelation_period_detect(spacetime, max_period=10):
    """Detect dominant temporal period via autocorrelation (baseline method)."""
    T = spacetime.shape[0]
    flat = spacetime.reshape(T, -1).astype(np.float64)
    mean = flat.mean(axis=1)
    centered = flat - mean[:, None]

    # Temporal autocorrelation averaged over all spatial sites
    norms = np.sqrt((centered ** 2).sum(axis=1))
    autocorrs = []
    for lag in range(1, min(max_period + 1, T)):
        # correlation between t and t+lag, averaged
        num = (centered[:T - lag] * centered[lag:]).sum()
        den = np.sqrt((centered[:T - lag] ** 2).sum() * (centered[lag:] ** 2).sum())
        autocorrs.append(num / den if den > 0 else 0.0)

    autocorrs = np.array(autocorrs)
    # Best period = lag with highest autocorrelation
    best_lag = int(np.argmax(autocorrs)) + 1
    return best_lag, autocorrs


def autocorrelation_defect_rate(spacetime, period):
    """Compute 'defect rate' using simple periodic (no-shift) tiling as baseline."""
    T = spacetime.shape[0]
    # Tile: B[t] = majority of {U[t], U[t+p], U[t+2p], ...}
    # This is equivalent to our method with shift=(0,...,0)
    fit = fit_relative_periodic_background_nd(spacetime, shift=(0,) * (spacetime.ndim - 1), period=period)
    return fit.defect_rate, fit.run_length_bits


def experiment_autocorrelation_baseline(width=64, height=64, steps=60):
    """Compare our method's period detection vs autocorrelation baseline."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Autocorrelation baseline comparison")
    print("=" * 70)

    results = []
    for name, survive, birth in TOP_RULES:
        initial = random_initial_grid(width=width, height=height, density=0.5, seed=11)
        spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

        # Autocorrelation baseline
        ac_period, ac_values = autocorrelation_period_detect(spacetime, max_period=10)
        ac_defect_rate, ac_rl_bits = autocorrelation_defect_rate(spacetime, ac_period)

        # Our method: scan shifts too
        def rule_error_fn(bg):
            return rule_consistency_rate_2d(bg, survive, birth)

        shift_range = range(-3, 4)
        frame, fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=[shift_range, shift_range],
            periods=range(1, 9),
            rule_error_fn=rule_error_fn,
        )
        best = frame.sort_values(["defect_rate", "run_length_bits"]).iloc[0]
        our_shift = (int(best["shift_0"]), int(best["shift_1"]))
        our_period = int(best["period"])
        our_defect = float(best["defect_rate"])
        our_rl = int(best["run_length_bits"])

        result = {
            "rule": name,
            "ac_period": ac_period,
            "ac_defect_rate": round(ac_defect_rate, 5),
            "ac_rl_bits": ac_rl_bits,
            "our_shift": str(our_shift),
            "our_period": our_period,
            "our_defect_rate": round(our_defect, 5),
            "our_rl_bits": our_rl,
            "period_agrees": ac_period == our_period,
            "improvement_pct": round(100 * (ac_defect_rate - our_defect) / ac_defect_rate, 1) if ac_defect_rate > 0 else 0,
        }
        results.append(result)
        print(f"  {name}: AC period={ac_period} rate={ac_defect_rate:.4f} | "
              f"Ours shift={our_shift} p={our_period} rate={our_defect:.4f} | "
              f"improvement={result['improvement_pct']}%")

    return pd.DataFrame.from_records(results)


# ── Experiment 3: Size scaling of persistent defects ─────────────────────────

PERSISTENT_RULES = [
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
]

GRID_SIZES = [32, 64, 96, 128, 192]


def experiment_size_scaling(steps=100):
    """Test whether persistent defects survive at larger grid sizes."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Size scaling of persistent defects")
    print("=" * 70)

    results = []
    for name, survive, birth in PERSISTENT_RULES:
        print(f"\n  {name}:")
        for size in GRID_SIZES:
            initial = random_initial_grid(width=size, height=size, density=0.5, seed=11)
            spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

            end_density = float(spacetime[-10:].mean())

            # Find best fit
            best_rate = 1.0
            best_p = 1
            for p in range(1, 9):
                fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=p)
                if fit.defect_rate < best_rate:
                    best_rate = fit.defect_rate
                    best_p = p

            # Get full fit for defect analysis
            fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=best_p)
            defects_per_t = fit.defect_mask.sum(axis=(1, 2))
            mid = len(defects_per_t) // 2
            late_mean = float(defects_per_t[mid:].mean())
            late_std = float(defects_per_t[mid:].std())
            # Normalize by grid area
            late_density = late_mean / (size * size)

            result = {
                "rule": name,
                "grid_size": size,
                "grid_area": size * size,
                "end_density": round(end_density, 4),
                "defect_rate": round(best_rate, 5),
                "best_period": best_p,
                "late_defects_mean": round(late_mean, 1),
                "late_defects_std": round(late_std, 1),
                "late_defect_density": round(late_density, 6),
                "defects_persist": late_mean > 5,
            }
            results.append(result)
            print(f"    {size}x{size}: rate={best_rate:.4f}, late={late_mean:.1f}±{late_std:.1f}, "
                  f"density={late_density:.6f}, persist={result['defects_persist']}")

    return pd.DataFrame.from_records(results)


def main():
    out_dir = Path("outputs/strengthening")
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    # Run all three experiments
    df_seeds = experiment_multi_seed()
    df_seeds.to_csv(out_dir / "multi_seed_robustness.csv", index=False)

    df_baseline = experiment_autocorrelation_baseline()
    df_baseline.to_csv(out_dir / "autocorrelation_baseline.csv", index=False)

    df_scaling = experiment_size_scaling()
    df_scaling.to_csv(out_dir / "size_scaling.csv", index=False)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"All experiments completed in {elapsed:.1f}s")
    print(f"Results saved to {out_dir}")
    print(f"{'=' * 70}")

    # Summary
    print("\n=== MULTI-SEED ROBUSTNESS ===")
    print(df_seeds.to_string(index=False))
    print("\n=== AUTOCORRELATION BASELINE ===")
    print(df_baseline.to_string(index=False))
    print("\n=== SIZE SCALING ===")
    print(df_scaling.to_string(index=False))


if __name__ == "__main__":
    main()
