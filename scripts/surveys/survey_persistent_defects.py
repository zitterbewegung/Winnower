"""Search for 2D rules with persistent, STRUCTURED defects — the 2D analogue of Rule 54."""
from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd


def analyze_defect_persistence(spacetime, shift, period):
    """Measure defect count at each time step to check for persistence."""
    fit = fit_relative_periodic_background_nd(spacetime, shift=shift, period=period)
    mask = fit.defect_mask

    # Defects per time step
    defects_per_t = mask.sum(axis=(1, 2))

    # Split into early (transient) and late (steady state)
    mid = len(defects_per_t) // 2
    early_defects = defects_per_t[:mid].mean()
    late_defects = defects_per_t[mid:].mean()
    late_std = defects_per_t[mid:].std()

    return fit, {
        "early_defects_mean": float(early_defects),
        "late_defects_mean": float(late_defects),
        "late_defects_std": float(late_std),
        "late_defects_min": int(defects_per_t[mid:].min()),
        "late_defects_max": int(defects_per_t[mid:].max()),
        "defects_persistent": float(late_defects) > 10,  # not just transient
        "defects_declining": float(late_defects) < float(early_defects) * 0.8,
    }


def quick_scan_best_fit(spacetime, shift_radius=3, max_period=6):
    """Quick scan to find best (shift, period), return it."""
    best_rate = 1.0
    best_shift = (0, 0)
    best_period = 1

    shift_range = range(-shift_radius, shift_radius + 1)
    for period in range(1, max_period + 1):
        for s0 in shift_range:
            for s1 in shift_range:
                fit = fit_relative_periodic_background_nd(
                    spacetime, shift=(s0, s1), period=period
                )
                if fit.defect_rate < best_rate:
                    best_rate = fit.defect_rate
                    best_shift = (s0, s1)
                    best_period = period

    return best_shift, best_period, best_rate


def survey_rule(survive, birth, width=64, height=64, steps=100, density=0.5, seed=11):
    """Analyze one rule for persistent structured defects."""
    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

    # Check trivial outcomes
    end_density = float(spacetime[-10:].mean())
    if end_density < 0.02 or end_density > 0.98:
        return None

    # Quick scan for best fit
    best_shift, best_period, best_rate = quick_scan_best_fit(spacetime)

    # Too high or too low defect rate isn't interesting
    if best_rate > 0.30 or best_rate < 0.005:
        return None

    # Analyze persistence
    fit, persistence = analyze_defect_persistence(spacetime, best_shift, best_period)

    # Not interesting if defects are just transient
    if not persistence["defects_persistent"]:
        return None

    # Compute structure ratio: run_length_bits per defect site
    # Lower = more structured (defects are clustered, not scattered)
    rl_per_defect = fit.run_length_bits / max(fit.defect_sites, 1)

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
        "defect_rate": round(best_rate, 5),
        "run_length_bits": fit.run_length_bits,
        "lz4_bits": fit.lz4_bits,
        "defect_sites": fit.defect_sites,
        "rl_per_defect": round(rl_per_defect, 3),
        "has_nonzero_shift": best_shift != (0, 0),
        **{k: round(v, 2) if isinstance(v, float) else v for k, v in persistence.items()},
    }


def main():
    candidates = []
    for s_lo in range(0, 8):
        for s_hi in range(s_lo, min(s_lo + 5, 9)):
            for b_lo in range(1, 8):
                for b_hi in range(b_lo, min(b_lo + 5, 9)):
                    candidates.append(((s_lo, s_hi), (b_lo, b_hi)))

    print(f"Surveying {len(candidates)} rules for persistent structured defects...")
    results = []
    t0 = time.time()

    for i, (survive, birth) in enumerate(candidates):
        if (i + 1) % 100 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(candidates) - i - 1) / rate
            print(f"  [{i+1}/{len(candidates)}] {elapsed:.0f}s elapsed, ~{eta:.0f}s remaining, "
                  f"{len(results)} candidates so far")

        try:
            result = survey_rule(survive, birth)
            if result is not None:
                results.append(result)
        except Exception as e:
            pass

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s. Found {len(results)} rules with persistent defects.")

    if not results:
        print("No candidates found!")
        return

    df = pd.DataFrame.from_records(results)

    # Sort by structure quality: low defect rate AND low rl_per_defect
    # (persistent, structured, sparse defects)
    df["score"] = df["defect_rate"] * df["rl_per_defect"]
    df = df.sort_values("score").reset_index(drop=True)

    out_path = Path("outputs/survey_persistent_defects.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")

    print("\n=== TOP 30 BY COMBINED SCORE (low = good) ===")
    cols = ["rule_name", "end_density", "best_shift_0", "best_shift_1", "best_period",
            "defect_rate", "rl_per_defect", "late_defects_mean", "late_defects_std",
            "has_nonzero_shift", "score"]
    print(df[cols].head(30).to_string(index=False))

    shifted = df[df["has_nonzero_shift"]].head(15)
    if len(shifted) > 0:
        print("\n=== TOP 15 WITH NONZERO SHIFT ===")
        print(shifted[cols].to_string(index=False))


if __name__ == "__main__":
    main()
