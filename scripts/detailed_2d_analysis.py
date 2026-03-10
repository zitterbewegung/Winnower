"""Detailed analysis of top candidate rules from the survey."""
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
    plot_2d_decomposition,
    plot_2d_kymograph,
    plot_2d_slices,
    plot_spectrum_nd,
)
from relative_symmetry_repair.plotting import save_figure


CANDIDATES = [
    # (name, survive, birth, density, description)
    ("S14_B11", (1, 4), (1, 1), 0.5, "Best overall: 0.85% defect, period 2"),
    ("S25_B12", (2, 5), (1, 2), 0.5, "Second: 0.91% defect, period 4"),
    ("S66_B36", (6, 6), (3, 6), 0.5, "Third: 0.98% defect, period 2"),
    ("S36_B23", (3, 6), (2, 3), 0.5, "Like Life but wider survival"),
    ("S25_B33", (2, 5), (3, 3), 0.5, "Period 1, 1.4% defect"),
    ("S00_B11", (0, 0), (1, 1), 0.5, "Best nonzero shift: 18.7%, shift=(2,-2)"),
    ("S66_B22", (6, 6), (2, 2), 0.5, "Nonzero shift: 20.3%, shift=(2,-2)"),
]


def analyze_candidate(
    name: str,
    survive: tuple[int, int],
    birth: tuple[int, int],
    density: float,
    description: str,
    width: int = 96,
    height: int = 96,
    steps: int = 80,
    seed: int = 11,
    shift_radius: int = 4,
    max_period: int = 8,
):
    print(f"\n{'='*60}")
    print(f"Analyzing {name}: S{survive[0]}{survive[1]}/B{birth[0]}{birth[1]}")
    print(f"  {description}")
    print(f"  Grid: {width}x{height}, steps={steps}, density={density}")
    print(f"{'='*60}")

    out_dir = Path(f"outputs/survey_detailed/{name}")
    out_dir.mkdir(parents=True, exist_ok=True)

    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d(initial, steps=steps, rule="custom", survive=survive, birth=birth)

    end_density = float(spacetime[-10:].mean())
    print(f"  End density: {end_density:.4f}")

    def rule_error_fn(bg):
        return rule_consistency_rate_2d(bg, survive, birth)

    shift_range = range(-shift_radius, shift_radius + 1)
    print(f"  Scanning {(2*shift_radius+1)**2 * max_period} (shift, period) pairs...")
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    best = frame.sort_values(["defect_rate", "run_length_bits"]).iloc[0]
    best_shift = (int(best["shift_0"]), int(best["shift_1"]))
    best_period = int(best["period"])
    best_fit = fits[(best_shift, best_period)]

    print(f"  Best fit: shift={best_shift}, period={best_period}")
    print(f"  Defect rate: {best_fit.defect_rate:.5f}")
    print(f"  Defect sites: {best_fit.defect_sites} / {best_fit.total_sites}")
    print(f"  Run-length bits: {best_fit.run_length_bits}")
    print(f"  LZ4 bits: {best_fit.lz4_bits}")
    print(f"  Rule error: {best_fit.rule_error:.5f}")

    labels, n_components = extract_components_nd(best_fit.defect_mask, min_size=4)
    components = summarise_components_nd(labels)
    print(f"  Connected defect components (size >= 4): {n_components}")
    if len(components) > 0:
        print(f"  Largest component: {components.iloc[0]['size']} sites")

    # Save CSV
    frame.to_csv(out_dir / "spectrum.csv", index=False)
    components.to_csv(out_dir / "components.csv", index=False)

    # Time slices
    fig, _ = plot_2d_slices(spacetime, title=f"{name} time slices")
    save_figure(fig, out_dir / "slices.png")
    plt.close(fig)

    # Kymograph
    fig, _ = plot_2d_kymograph(spacetime, axis=1, title=f"{name} kymograph")
    save_figure(fig, out_dir / "kymograph.png")
    plt.close(fig)

    # Spectrum
    fig, _ = plot_spectrum_nd(frame, value="defect_rate", title=f"{name} defect-rate spectrum")
    save_figure(fig, out_dir / "defect_rate_spectrum.png")
    plt.close(fig)

    fig, _ = plot_spectrum_nd(frame, value="run_length_bits", title=f"{name} run-length spectrum")
    save_figure(fig, out_dir / "run_length_spectrum.png")
    plt.close(fig)

    # Decomposition at multiple time slices
    for t_frac in [0.25, 0.5, 0.75, 1.0]:
        t_idx = min(int(t_frac * steps) - 1, steps - 1)
        fig, _ = plot_2d_decomposition(best_fit, source=spacetime, time_index=t_idx,
                                        title_prefix=f"{name} ")
        save_figure(fig, out_dir / f"decomposition_t{t_idx}.png")
        plt.close(fig)

    # Defect mask time evolution: show defect mask at several times
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    from relative_symmetry_repair.plotting_nd import DEFECT_CMAP
    t_indices = np.linspace(0, steps - 1, 8, dtype=int)
    for ax, t in zip(axes.ravel(), t_indices):
        ax.imshow(best_fit.defect_mask[t].astype(np.uint8), interpolation="nearest",
                  cmap=DEFECT_CMAP, vmin=0, vmax=1)
        defects_at_t = best_fit.defect_mask[t].sum()
        ax.set_title(f"t={t} ({defects_at_t} defects)", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(f"{name} defect mask evolution", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(fig, out_dir / "defect_evolution.png")
    plt.close(fig)

    print(f"  Saved outputs to {out_dir}")
    return {
        "name": name,
        "survive": survive,
        "birth": birth,
        "end_density": end_density,
        "best_shift": best_shift,
        "best_period": best_period,
        "defect_rate": best_fit.defect_rate,
        "rule_error": best_fit.rule_error,
        "n_components": n_components,
        "run_length_bits": best_fit.run_length_bits,
        "lz4_bits": best_fit.lz4_bits,
    }


def main():
    results = []
    for name, survive, birth, density, desc in CANDIDATES:
        result = analyze_candidate(name, survive, birth, density, desc)
        results.append(result)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in sorted(results, key=lambda x: x["defect_rate"]):
        shift_str = f"({r['best_shift'][0]},{r['best_shift'][1]})"
        print(f"  {r['name']:12s}  shift={shift_str:8s}  p={r['best_period']}  "
              f"defect={r['defect_rate']:.5f}  rule_err={r['rule_error']:.5f}  "
              f"components={r['n_components']:3d}  end_dens={r['end_density']:.3f}")


if __name__ == "__main__":
    main()
