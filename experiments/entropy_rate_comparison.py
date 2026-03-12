"""Entropy-rate comparison: raw spacetime vs projection residual for ECA Rule 54.

Computes sliding-window conditional entropy H(X_t | X_{t-1}, ..., X_{t-L})
for three signals:
  1. Raw spacetime (local 3-cell neighborhoods over time)
  2. NML-selected periodic background
  3. Projection residual (defect mask)

If our periodic decomposition captures the same regular structure that
epsilon-machines identify as the "Ether" domain, the background should have
near-zero entropy rate while the residual concentrates the unpredictability.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.relative_symmetry_repair.eca import simulate_eca, random_initial_state
from src.relative_symmetry_repair.repair import (
    fit_relative_periodic_background,
    component_labels,
)


def sliding_window_entropy(
    spacetime: np.ndarray,
    neighborhood: int = 3,
    history: int = 4,
) -> float:
    """Estimate per-site conditional entropy rate via empirical block counting.

    For each site (t, x), form a context from a spatial neighborhood of width
    `neighborhood` over `history` past time steps, and predict the current
    center cell. Returns H(center | context) in bits.

    This is a plug-in estimator — biased upward for small data but consistent.
    """
    steps, width = spacetime.shape
    half_n = neighborhood // 2

    # Build (context, outcome) pairs
    context_list = []
    outcome_list = []

    for t in range(history, steps):
        for x in range(width):
            # Context: neighborhood x history block from past
            ctx = []
            for dt in range(1, history + 1):
                for dx in range(-half_n, half_n + 1):
                    ctx.append(spacetime[t - dt, (x + dx) % width])
            context_list.append(tuple(ctx))
            outcome_list.append(int(spacetime[t, x]))

    # Count joint and marginal frequencies
    from collections import Counter

    joint_counts: Counter[tuple] = Counter()
    context_counts: Counter[tuple] = Counter()

    for ctx, out in zip(context_list, outcome_list):
        joint_counts[(ctx, out)] += 1
        context_counts[ctx] += 1

    # H(outcome | context) = -Σ p(ctx, out) log2 p(out | ctx)
    n_total = len(context_list)
    entropy = 0.0
    for (ctx, out), count in joint_counts.items():
        p_joint = count / n_total
        p_cond = count / context_counts[ctx]
        entropy -= p_joint * np.log2(p_cond)

    return entropy


def per_site_entropy(spacetime: np.ndarray) -> float:
    """Unconditional per-site entropy (marginal)."""
    p1 = spacetime.mean()
    if p1 == 0 or p1 == 1:
        return 0.0
    return float(-p1 * np.log2(p1) - (1 - p1) * np.log2(1 - p1))


def domain_vs_residual_entropy(
    spacetime: np.ndarray,
    background: np.ndarray,
    defect_mask: np.ndarray,
    neighborhood: int = 3,
    history: int = 4,
) -> dict:
    """Compare entropy rates across raw, background, and residual."""
    results = {}

    # Marginal entropies
    results["raw_marginal_H"] = per_site_entropy(spacetime)
    results["background_marginal_H"] = per_site_entropy(background)
    results["residual_marginal_H"] = per_site_entropy(defect_mask.astype(np.uint8))
    results["defect_rate"] = float(defect_mask.mean())

    # Conditional entropy rates
    results["raw_cond_H"] = sliding_window_entropy(spacetime, neighborhood, history)
    results["background_cond_H"] = sliding_window_entropy(background, neighborhood, history)
    results["residual_cond_H"] = sliding_window_entropy(
        defect_mask.astype(np.uint8), neighborhood, history
    )

    return results


def main():
    # Parameters
    rules = [54, 110, 30]
    width = 192
    T = 800
    seed = 11
    history = 4
    neighborhood = 3

    # Known NML-selected periods (from stabilization analysis, shift=0)
    known_periods = {54: 4, 110: 7, 30: 1}
    known_shifts = {54: 0, 110: 0, 30: 0}

    all_results = []

    for rule in rules:
        print(f"\n{'='*60}")
        print(f"ECA Rule {rule} (width={width}, T={T}, seed={seed})")
        print(f"{'='*60}")

        initial = random_initial_state(width, seed=seed)
        spacetime = simulate_eca(rule, initial, T)

        period = known_periods[rule]
        shift = known_shifts[rule]

        fit = fit_relative_periodic_background(spacetime, shift=shift, period=period)

        print(f"Selected period: {period}, shift: {shift}")
        print(f"Defect rate: {fit.defect_rate:.4f}")
        print(f"NML bits: {fit.nml_bits:.1f}")

        results = domain_vs_residual_entropy(
            spacetime, fit.background, fit.defect_mask,
            neighborhood=neighborhood, history=history,
        )

        results["rule"] = rule
        results["period"] = period
        results["shift"] = shift
        results["T"] = T

        print(f"\nMarginal entropy (bits/site):")
        print(f"  Raw spacetime:  {results['raw_marginal_H']:.4f}")
        print(f"  Background:     {results['background_marginal_H']:.4f}")
        print(f"  Residual mask:  {results['residual_marginal_H']:.4f}")
        print(f"\nConditional entropy rate H(X_t | context), neighborhood={neighborhood}, history={history}:")
        print(f"  Raw spacetime:  {results['raw_cond_H']:.4f}")
        print(f"  Background:     {results['background_cond_H']:.4f}")
        print(f"  Residual mask:  {results['residual_cond_H']:.4f}")

        # Fraction of entropy in residual vs raw
        if results["raw_cond_H"] > 0:
            ratio = results["residual_cond_H"] / results["raw_cond_H"]
            print(f"\n  Residual/Raw entropy ratio: {ratio:.4f}")
            results["entropy_ratio"] = ratio

        all_results.append(results)

    # Save results
    df = pd.DataFrame(all_results)
    out_path = Path(__file__).resolve().parent.parent / "results" / "entropy_rate_comparison.csv"
    df.to_csv(out_path, index=False)
    print(f"\nResults saved to {out_path}")

    # Generate figure
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    for i, rule in enumerate(rules):
        r = all_results[i]
        ax = axes[i]

        labels = ["Raw\nspacetime", "Background\n(periodic)", "Residual\n(defects)"]
        marginals = [r["raw_marginal_H"], r["background_marginal_H"], r["residual_marginal_H"]]
        conditionals = [r["raw_cond_H"], r["background_cond_H"], r["residual_cond_H"]]

        x = np.arange(3)
        w = 0.35
        ax.bar(x - w / 2, marginals, w, label="Marginal H", color="#4878CF")
        ax.bar(x + w / 2, conditionals, w, label="Conditional H", color="#D65F5F")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("Entropy (bits/site)")
        ax.set_title(f"Rule {rule} (p={r['period']}, defect={r['defect_rate']:.1%})")
        ax.legend(fontsize=8)
        ax.set_ylim(0, 1.05)

    fig.suptitle(
        "Entropy rate decomposition: periodic background captures predictable structure",
        fontsize=12,
    )
    plt.tight_layout()

    fig_path = Path(__file__).resolve().parent.parent / "figures" / "entropy_rate_comparison.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to {fig_path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
