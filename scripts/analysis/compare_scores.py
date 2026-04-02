#!/usr/bin/env python3
"""Compare scoring methods for model selection.

Compares:
1. Current MDL score: BIC-type penalty + run-length defect encoding
2. Bernoulli NML score: NLL + asymptotic NML complexity
3. Two-part combinatorial score: raw template bits + log2(binom(N,w))
4. RL and LZ4 as secondary diagnostics

Tests whether the winner changes under different scores,
especially for cases with small reported margins.
"""

import math

import numpy as np
import pandas as pd

from relative_symmetry_repair.coding import (
    combinatorial_repair_bits,
    log2_binomial,
    run_length_bits,
    lz4_mask_bits,
    template_bits_raw,
    template_bits_nml,
)
from relative_symmetry_repair.repair import fit_relative_periodic_background
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd
from relative_symmetry_repair.eca import random_initial_state, simulate_eca


def combinatorial_two_part_score(fit) -> float:
    """Exact two-part code: raw template bits + combinatorial residual."""
    return fit.template_bits + fit.combinatorial_bits


def compare_scores_1d(rule: int, width: int, T: int, seed: int = 11):
    """Compare scores for a 1D ECA rule."""
    initial = random_initial_state(width=width, density=0.5, seed=seed)
    spacetime = simulate_eca(rule=rule, initial=initial, steps=T)

    rows = []
    for p in range(1, 11):
        for s in range(-3, 4):
            fit = fit_relative_periodic_background(spacetime, shift=s, period=p, rule=rule)
            comb_score = combinatorial_two_part_score(fit)
            rows.append({
                "shift": s,
                "period": p,
                "defect_rate": fit.defect_rate,
                "defect_sites": fit.defect_sites,
                "mdl_bits": fit.mdl_bits,
                "nml_bits": fit.nml_bits,
                "comb_score": comb_score,
                "rl_bits": fit.run_length_bits,
                "lz4_bits": fit.lz4_bits,
                "template_raw": fit.template_bits,
                "nll_bits": fit.nll_bits,
                "nml_complexity": fit.nml_complexity,
            })

    df = pd.DataFrame(rows)
    return df


def winner_comparison(df: pd.DataFrame) -> dict:
    """Find the winner under each scoring method."""
    scores = {
        "mdl_bits": "MDL (BIC + RL)",
        "nml_bits": "NML (NLL + complexity)",
        "comb_score": "Combinatorial (raw template + binom)",
        "defect_rate": "Defect rate (no penalty)",
    }
    results = {}
    for col, name in scores.items():
        best = df.sort_values([col, "defect_rate"]).iloc[0]
        results[name] = {
            "shift": int(best["shift"]),
            "period": int(best["period"]),
            "score": float(best[col]),
            "defect_rate": float(best["defect_rate"]),
        }
    return results


def test_flattening_order_sensitivity():
    """Test whether RL codelength changes with flattening order."""
    print("\n" + "=" * 70)
    print("TEST: Flattening-order sensitivity of RL codelength")
    print("=" * 70)

    # Create a 2D defect mask with structure along one axis
    mask = np.zeros((20, 20), dtype=np.uint8)
    # Vertical stripe of defects
    mask[:, 5] = 1
    mask[:, 15] = 1

    # Row-major (C order) vs column-major (F order)
    rl_row = run_length_bits(mask.ravel(order="C").reshape(mask.shape))
    rl_col = run_length_bits(mask.T)  # transpose effectively swaps order

    print(f"Row-major RL: {rl_row} bits")
    print(f"Column-major RL: {rl_col} bits")
    print(f"Ratio: {max(rl_row, rl_col) / max(min(rl_row, rl_col), 1):.2f}")

    # Diagonal defects (should be very different between orderings)
    mask2 = np.zeros((20, 20), dtype=np.uint8)
    for i in range(20):
        mask2[i, i] = 1

    rl_row2 = run_length_bits(mask2)
    rl_col2 = run_length_bits(mask2.T)

    print(f"\nDiagonal mask:")
    print(f"Row-major RL: {rl_row2} bits")
    print(f"Column-major RL: {rl_col2} bits")
    print(f"(Same because diagonal is symmetric under transpose)")


def main():
    print("=" * 70)
    print("SCORE COMPARISON: MDL vs NML vs Combinatorial")
    print("=" * 70)

    # Test standard 1D rules
    for rule in [30, 54, 110]:
        print(f"\n{'=' * 70}")
        print(f"Rule {rule}")
        print(f"{'=' * 70}")

        winners_by_T = {}
        for T in [50, 100, 200, 400]:
            df = compare_scores_1d(rule, width=192, T=T)
            winners = winner_comparison(df)
            winners_by_T[T] = winners

            print(f"\n  T={T}:")
            for name, w in winners.items():
                print(f"    {name:40s}: s={w['shift']}, p={w['period']}, "
                      f"score={w['score']:.1f}, defect_rate={w['defect_rate']:.4f}")

        # Check stability
        print(f"\n  Winner stability across T:")
        for name in winners_by_T[50]:
            periods = [winners_by_T[T][name]["period"] for T in winners_by_T]
            shifts = [winners_by_T[T][name]["shift"] for T in winners_by_T]
            stable = len(set(periods)) == 1 and len(set(shifts)) == 1
            print(f"    {name:40s}: periods={periods}, stable={stable}")

    # Check score agreement
    print(f"\n{'=' * 70}")
    print("SCORE AGREEMENT SUMMARY")
    print(f"{'=' * 70}")

    agree_count = 0
    disagree_count = 0
    for rule in [30, 54, 110]:
        for T in [100, 200, 400]:
            df = compare_scores_1d(rule, width=192, T=T)
            winners = winner_comparison(df)
            mdl_period = winners["MDL (BIC + RL)"]["period"]
            nml_period = winners["NML (NLL + complexity)"]["period"]
            comb_period = winners["Combinatorial (raw template + binom)"]["period"]

            if mdl_period == nml_period == comb_period:
                agree_count += 1
            else:
                disagree_count += 1
                print(f"  DISAGREE: Rule {rule}, T={T}: "
                      f"MDL=p{mdl_period}, NML=p{nml_period}, Comb=p{comb_period}")

    print(f"\n  Agreement: {agree_count}/{agree_count + disagree_count}")
    if disagree_count > 0:
        print(f"  Disagreement: {disagree_count} cases — scores select different periods!")

    # Combinatorial score overcapacity test
    print(f"\n{'=' * 70}")
    print("OVERCAPACITY TEST: Does combinatorial score prevent it?")
    print(f"{'=' * 70}")

    df = compare_scores_1d(30, width=192, T=200)
    best_comb = df.sort_values(["comb_score"]).iloc[0]
    best_defect = df.sort_values(["defect_rate"]).iloc[0]
    print(f"  Combinatorial winner: p={int(best_comb['period'])}, "
          f"defect_rate={best_comb['defect_rate']:.4f}")
    print(f"  Defect-rate winner:   p={int(best_defect['period'])}, "
          f"defect_rate={best_defect['defect_rate']:.4f}")
    if best_comb["period"] == best_defect["period"]:
        print("  WARNING: Combinatorial score selects same as defect rate — "
              "raw template bits may be too weak a penalty!")

    test_flattening_order_sensitivity()


if __name__ == "__main__":
    main()
