"""Detailed analysis of top candidates with persistent structured defects."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d, rule_consistency_rate_2d
from relative_symmetry_repair.repair_nd import (
    extract_components_nd,
    fit_relative_periodic_background_nd,
    scan_relative_periodicity_nd,
    summarise_components_nd,
)
from relative_symmetry_repair.plotting_nd import (
    DEFECT_CMAP, BINARY_CMAP,
    plot_2d_decomposition,
    plot_2d_slices,
    plot_spectrum_nd,
)
from relative_symmetry_repair.plotting import save_figure


CANDIDATES = [
    ("S24_B11", (2, 4), (1, 1)),
    ("S11_B37", (1, 1), (3, 7)),
    ("S37_B11", (3, 7), (1, 1)),
    ("S36_B11", (3, 6), (1, 1)),
    ("S01_B37", (0, 1), (3, 7)),
    ("S36_B25", (3, 6), (2, 5)),
]


def analyze(name, survive, birth):
    print(f"\n{'='*60}")
    print(f"  {name}: S{survive}/B{birth}")
    print(f"{'='*60}")

    out_dir = Path(f"outputs/top_candidates/{name}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Larger grid, more steps for better statistics
    width, height, steps = 128, 128, 120
    initial = random_initial_grid(width=width, height=height, density=0.5, seed=11)
    spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

    end_density = float(spacetime[-20:].mean())
    print(f"  End density: {end_density:.4f}")

    def rule_error_fn(bg):
        return rule_consistency_rate_2d(bg, survive, birth)

    shift_range = range(-4, 5)
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, 9),
        rule_error_fn=rule_error_fn,
    )

    best = frame.sort_values(["defect_rate", "run_length_bits"]).iloc[0]
    best_shift = (int(best["shift_0"]), int(best["shift_1"]))
    best_period = int(best["period"])
    best_fit = fits[(best_shift, best_period)]

    print(f"  Best fit: shift={best_shift}, period={best_period}")
    print(f"  Defect rate: {best_fit.defect_rate:.5f} ({best_fit.defect_sites}/{best_fit.total_sites})")
    print(f"  Rule error: {best_fit.rule_error:.5f}")

    # Defect time series
    defects_per_t = best_fit.defect_mask.sum(axis=(1, 2))
    print(f"  Defects per frame: early={defects_per_t[:20].mean():.1f}, "
          f"late={defects_per_t[-40:].mean():.1f} ± {defects_per_t[-40:].std():.1f}")

    # Components
    labels, n_comp = extract_components_nd(best_fit.defect_mask, min_size=3)
    components = summarise_components_nd(labels)
    print(f"  Components (size>=3): {n_comp}")
    if len(components) > 0 and 't_span' in components.columns:
        long_lived = components[components['t_span'] > steps // 3]
        print(f"  Long-lived components (span > {steps//3} steps): {len(long_lived)}")
        if len(long_lived) > 0:
            print(f"    Sizes: {list(long_lived['size'].values[:10])}")

    # Save CSVs
    frame.to_csv(out_dir / "spectrum.csv", index=False)
    components.to_csv(out_dir / "components.csv", index=False)

    # --- Plots ---
    # 1. Time slices
    fig, _ = plot_2d_slices(spacetime, title=f"{name} time slices", max_slices=8)
    save_figure(fig, out_dir / "slices.png")
    plt.close(fig)

    # 2. Spectrum
    fig, _ = plot_spectrum_nd(frame, value="defect_rate", title=f"{name} defect-rate spectrum")
    save_figure(fig, out_dir / "defect_rate.png")
    plt.close(fig)

    # 3. Decomposition at several times
    for t_idx in [10, steps//4, steps//2, 3*steps//4, steps-1]:
        fig, _ = plot_2d_decomposition(best_fit, source=spacetime, time_index=t_idx,
                                        title_prefix=f"{name} ")
        save_figure(fig, out_dir / f"decomposition_t{t_idx}.png")
        plt.close(fig)

    # 4. Defect mask evolution (key plot)
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    t_indices = np.linspace(0, steps - 1, 10, dtype=int)
    for ax, t in zip(axes.ravel(), t_indices):
        ax.imshow(best_fit.defect_mask[t].astype(np.uint8), interpolation="nearest",
                  cmap=DEFECT_CMAP, vmin=0, vmax=1)
        n_def = best_fit.defect_mask[t].sum()
        ax.set_title(f"t={t} ({n_def})", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle(f"{name} defect mask evolution — s={best_shift}, p={best_period}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(fig, out_dir / "defect_evolution.png")
    plt.close(fig)

    # 5. Defect count time series
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(defects_per_t, color='#c83f49', linewidth=1.2)
    ax.set_xlabel("time step")
    ax.set_ylabel("defect count per frame")
    ax.set_title(f"{name} — defect count over time (shift={best_shift}, period={best_period})")
    ax.axhline(defects_per_t[-40:].mean(), color='gray', linestyle='--', alpha=0.7,
               label=f"late mean={defects_per_t[-40:].mean():.1f}")
    ax.legend()
    fig.tight_layout()
    save_figure(fig, out_dir / "defect_timeseries.png")
    plt.close(fig)

    print(f"  Saved to {out_dir}")


def main():
    for name, survive, birth in CANDIDATES:
        analyze(name, survive, birth)


if __name__ == "__main__":
    main()
