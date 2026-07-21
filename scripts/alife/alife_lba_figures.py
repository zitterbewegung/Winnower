#!/usr/bin/env python3
"""Generate the ALIFE 2026 late-breaking-abstract figures from real tool runs.

Follows the LBA paper "Winnower: Detecting Periodic Domains in Cellular
Automata": white canvas, domain-template / defect-mask terminology, and the
representative panel

  - 1D: ECA-54            (seed 11, 192 cells, T=144)
  - 2D: S24/B11           (seed 11, 64x64,    T=600)
  - 3D: 3d-life (B5/S45)  (seed 42, 16^3,     T=24; Bays' 3D Life)

Outputs
  outputs/alife_2026/lba_figures/lba_row_{1d,2d,3d}.png   per-dimension rows
  paper/figures/lba_decompositions.png                    stitched composite
  paper/figures/stabilization_real.png                    horizon-sweep panel
    (reads outputs/convergence/convergence_all_dims.csv; run
     scripts/analysis/convergence_all_dims.py first)
"""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair import alife_style as style  # noqa: E402
from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d  # noqa: E402
from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d  # noqa: E402
from relative_symmetry_repair.eca import random_initial_state, simulate_eca  # noqa: E402
from relative_symmetry_repair.plotting import plot_decomposition, save_figure  # noqa: E402
from relative_symmetry_repair.plotting_nd import (  # noqa: E402
    plot_2d_decomposition,
    plot_3d_volume_decomposition,
)
from relative_symmetry_repair.selection import select_period, select_period_nd  # noqa: E402

OUT_DIR = ROOT / "outputs" / "alife_2026" / "lba_figures"
PAPER_FIG_DIR = ROOT / "paper" / "figures"
DPI = 200


def row_1d() -> tuple[Path, dict]:
    initial = random_initial_state(width=192, density=0.5, seed=11)
    spacetime = simulate_eca(rule=54, initial=initial, steps=144)
    result = select_period(spacetime, shifts=range(-6, 7), periods=range(1, 11))
    fit = result.best_fit
    fig, _ = plot_decomposition(fit, source=spacetime, title_prefix="1D ECA-54 ")
    path = OUT_DIR / "lba_row_1d.png"
    save_figure(fig, path)
    plt.close(fig)
    return path, {
        "rule": "ECA-54",
        "period": fit.period,
        "shift": fit.shift,
        "defect_rate": round(float(fit.defect_rate), 4),
    }


def row_2d() -> tuple[Path, dict]:
    initial = random_initial_grid(width=64, height=64, density=0.5, seed=11)
    spacetime = simulate_2d(
        initial, steps=600, rule="custom", survive=(2, 4), birth=(1, 1)
    )
    result = select_period_nd(
        spacetime, shift_ranges=[range(-3, 4), range(-3, 4)], periods=range(1, 9)
    )
    fit = result.best_fit
    fig, _ = plot_2d_decomposition(fit, source=spacetime, title_prefix="2D S24/B11 ")
    path = OUT_DIR / "lba_row_2d.png"
    save_figure(fig, path)
    plt.close(fig)
    return path, {
        "rule": "S24/B11",
        "period": fit.period,
        "shift": tuple(fit.shift),
        "defect_rate": round(float(fit.defect_rate), 4),
    }


def row_3d() -> tuple[Path, dict]:
    initial = random_initial_volume(sx=16, sy=16, sz=16, density=0.2, seed=42)
    spacetime = simulate_3d(initial, steps=24, rule="3d-life")
    result = select_period_nd(
        spacetime,
        shift_ranges=[range(-2, 3), range(-2, 3), range(-2, 3)],
        periods=range(1, 5),
    )
    fit = result.best_fit
    fig, _ = plot_3d_volume_decomposition(
        fit, source=spacetime, title_prefix="3D Life (B5/S45) "
    )
    path = OUT_DIR / "lba_row_3d.png"
    save_figure(fig, path)
    plt.close(fig)
    return path, {
        "rule": "3d-life",
        "period": fit.period,
        "shift": tuple(fit.shift),
        "defect_rate": round(float(fit.defect_rate), 4),
    }


def stitch_rows(paths: list[Path], out_path: Path, gap: int = 24) -> None:
    """Stack row images vertically on a white canvas at a common width."""
    images = [(plt.imread(str(p)) * 255).astype(np.uint8) for p in paths]
    images = [img[:, :, :3] if img.shape[2] == 4 else img for img in images]
    width = max(img.shape[1] for img in images)
    rows: list[np.ndarray] = []
    for img in images:
        pad = width - img.shape[1]
        left, right = pad // 2, pad - pad // 2
        rows.append(
            np.pad(
                img,
                ((0, 0), (left, right), (0, 0)),
                mode="constant",
                constant_values=255,
            )
        )
    spacer = np.full((gap, width, 3), 255, dtype=np.uint8)
    composite = rows[0]
    for row in rows[1:]:
        composite = np.vstack([composite, spacer, row])
    plt.imsave(str(out_path), composite)


def stabilization_figure(out_path: Path) -> None:
    csv_path = ROOT / "outputs" / "convergence" / "convergence_all_dims.csv"
    df = pd.read_csv(csv_path)
    rules = [
        ("ECA-54", "1D ECA-54"),
        ("ECA-110", "1D ECA-110"),
        ("S24_B11", "2D S24/B11"),
        ("3d-life", "3D Life (B5/S45)"),
    ]
    colors = [style.ACCENT_COLOR, style.TEXT_COLOR, style.SECONDARY_COLOR, "#8a6d3b"]
    # Shared log y-limits so margins are visually comparable across panels
    # (observed range across all four rules is ~84-17,900 bits).
    margin_ylim = (60, 30000)
    fig, ax = plt.subplots(2, 4, figsize=(11, 4.2))
    style.apply_figure_theme(fig, facecolor="white")
    for j, (key, title) in enumerate(rules):
        d = df[df.rule == key].sort_values("T")
        horizons = d["T"].values
        margins = d["margin"].values
        for r in (0, 1):
            style.apply_axis_theme(ax[r, j], facecolor="white")
        ax[0, j].plot(horizons, d["best_period"].values, marker="o", color=colors[j], lw=2, ms=5)
        ax[0, j].set_title(title, fontsize=11, fontweight="bold")
        ax[0, j].set_ylim(0, 8.6)
        ax[0, j].set_yticks([1, 2, 4, 7, 8])
        ax[1, j].plot(horizons, margins, marker="s", color=colors[j], lw=2, ms=4)
        ax[1, j].set_yscale("log")
        ax[1, j].set_ylim(*margin_ylim)
        ax[1, j].set_xlabel("horizon T", fontsize=10)
        # Mark the horizon where the selected period changes: the margin dips
        # toward zero right at a transition (near-tied candidates), then
        # climbs again once the new winner pulls ahead.
        periods = d["best_period"].values
        for k in range(1, len(periods)):
            if periods[k] != periods[k - 1]:
                ax[1, j].annotate(
                    "period changes",
                    xy=(horizons[k], margins[k]),
                    xytext=(8, 22),
                    textcoords="offset points",
                    ha="left",
                    fontsize=7.5,
                    color=style.SECONDARY_COLOR,
                    arrowprops=dict(arrowstyle="-", color=style.SECONDARY_COLOR, lw=0.8),
                )
        if j == 0:
            ax[0, j].set_ylabel("selected period", fontsize=10)
            ax[1, j].set_ylabel("margin (bits)", fontsize=10)
    fig.suptitle(
        "Selected period stabilizes as the horizon grows (exact Bernoulli NML)",
        fontsize=12,
        fontweight="bold",
        color=style.TEXT_COLOR,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path, dpi=DPI, facecolor="white")
    plt.close(fig)



def results_3d_figure(out_path: Path) -> None:
    """3D-only results figure: voxel decomposition row above the 3D horizon sweep."""
    import numpy as np
    from PIL import Image

    # --- sweep row: 3d-life only (selected period | margin) ---
    csv_path = ROOT / "outputs" / "convergence" / "convergence_all_dims.csv"
    df = pd.read_csv(csv_path)
    d = df[df.rule == "3d-life"].sort_values("T")
    horizons, periods, margins = d["T"].values, d["best_period"].values, d["margin"].values
    fig, ax = plt.subplots(1, 2, figsize=(8.6, 2.5))
    style.apply_figure_theme(fig, facecolor="white")
    for a in ax:
        style.apply_axis_theme(a, facecolor="white")
    ax[0].plot(horizons, periods, marker="o", color=style.ACCENT_COLOR, lw=2, ms=5)
    ax[0].set_ylim(0, 4.4)
    ax[0].set_yticks([1, 2, 3, 4])
    ax[0].set_title("selected period", fontsize=11)
    ax[1].plot(horizons, margins, marker="s", color=style.TEXT_COLOR, lw=2, ms=4)
    ax[1].set_yscale("log")
    ax[1].set_ylim(1000, 30000)
    ax[1].set_title("margin over runner-up (bits)", fontsize=11)
    for a in ax:
        a.set_xlabel("horizon T", fontsize=10)
    fig.tight_layout()
    sweep_path = OUT_DIR / "lba_sweep_3d.png"
    fig.savefig(sweep_path, dpi=DPI, facecolor="white")
    plt.close(fig)

    # --- stitch: voxel decomposition row above the sweep row ---
    def load_trim(path, pad=8):
        a = np.array(Image.open(path).convert("RGB"))
        keep_r = np.where(~np.all(a > 250, axis=2).all(axis=1))[0]
        keep_c = np.where(~np.all(a > 250, axis=2).all(axis=0))[0]
        return a[max(0, keep_r.min() - pad):keep_r.max() + pad,
                 max(0, keep_c.min() - pad):keep_c.max() + pad]

    top = load_trim(OUT_DIR / "lba_row_3d.png")
    bot = load_trim(sweep_path)
    W = 2600

    def to_w(a, W):
        im = Image.fromarray(a)
        h = round(im.height * W / im.width)
        return np.array(im.resize((W, h), Image.LANCZOS))

    top, bot = to_w(top, W), to_w(bot, W)
    gap = np.full((30, W, 3), 255, np.uint8)
    combined = np.vstack([top, gap, bot])
    Image.fromarray(combined).save(out_path)
    print(f"3D results figure -> {out_path} "
          f"({combined.shape[1]}x{combined.shape[0]}, w/h={combined.shape[1]/combined.shape[0]:.2f})")


def combined_eca_figure(out_path: Path) -> None:
    """One figure: ECA-54 and ECA-110, each row = decomposition + line graphs.

    Columns: observed / domain template / defect mask / selected period(T) /
    margin(T).  Decompositions are fresh runs (seed 11); the line graphs read
    the horizon sweep from convergence_all_dims.csv.
    """
    from matplotlib.gridspec import GridSpec
    from relative_symmetry_repair.alife_style import BINARY_CMAP, DEFECT_CMAP

    df = pd.read_csv(ROOT / "outputs" / "convergence" / "convergence_all_dims.csv")
    cases = [
        ("ECA-54", 54, 144, style.ACCENT_COLOR),
        ("ECA-110", 110, 200, style.TEXT_COLOR),
    ]

    fig = plt.figure(figsize=(11, 5.0))
    style.apply_figure_theme(fig, facecolor="white")
    gs = GridSpec(2, 5, figure=fig, width_ratios=[1, 1, 1, 1.25, 1.25],
                  wspace=0.42, hspace=0.30)
    col_titles = ["observed", "domain template", "defect mask",
                  "selected period", "margin (bits)"]

    for i, (name, rule, steps, color) in enumerate(cases):
        initial = random_initial_state(width=192, density=0.5, seed=11)
        spacetime = simulate_eca(rule=rule, initial=initial, steps=steps)
        # Fit at shift 0 to match the horizon sweep (which scans shift 0),
        # so the decomposition period agrees with the line graph.
        result = select_period(spacetime, shifts=[0], periods=range(1, 11))
        fit = result.best_fit

        # --- decomposition images ---
        panels = [
            (spacetime, BINARY_CMAP, f"$p{{=}}{fit.period}$, $s{{=}}{fit.shift}$"),
            (fit.background, BINARY_CMAP, ""),
            (fit.defect_mask.astype(int), DEFECT_CMAP,
             f"rate {fit.defect_rate:.3f}"),
        ]
        for c, (img, cmap, sub) in enumerate(panels):
            ax = fig.add_subplot(gs[i, c])
            style.apply_axis_theme(ax, facecolor="white")
            ax.imshow(img, aspect="auto", interpolation="nearest",
                      cmap=cmap, vmin=0, vmax=1)
            ax.set_xticks([]); ax.set_yticks([])
            if i == 0:
                ax.set_title(col_titles[c], fontsize=10)
            if sub:
                ax.set_xlabel(sub, fontsize=8)
            if c == 0:
                ax.set_ylabel(f"{name}\n(time down)", fontsize=10, fontweight="bold")

        # --- line graphs from the sweep ---
        key = name  # convergence CSV uses ECA-54 / ECA-110 verbatim
        d = df[df.rule == key].sort_values("T")
        T, P, M = d["T"].values, d["best_period"].values, d["margin"].values

        axp = fig.add_subplot(gs[i, 3])
        style.apply_axis_theme(axp, facecolor="white")
        axp.plot(T, P, marker="o", color=color, lw=2, ms=4)
        axp.set_ylim(0, 8.6); axp.set_yticks([1, 2, 4, 7])
        if i == 0:
            axp.set_title(col_titles[3], fontsize=10)
        axp.set_xlabel("horizon T", fontsize=8)

        axm = fig.add_subplot(gs[i, 4])
        style.apply_axis_theme(axm, facecolor="white")
        axm.plot(T, M, marker="s", color=color, lw=2, ms=3.5)
        axm.set_yscale("log"); axm.set_ylim(150, 30000)
        if i == 0:
            axm.set_title(col_titles[4], fontsize=10)
        axm.set_xlabel("horizon T", fontsize=8)
        for k in range(1, len(P)):
            if P[k] != P[k - 1]:
                axm.annotate("period\nchanges", xy=(T[k], M[k]), xytext=(6, 16),
                             textcoords="offset points", fontsize=7,
                             color=style.SECONDARY_COLOR,
                             arrowprops=dict(arrowstyle="-",
                                             color=style.SECONDARY_COLOR, lw=0.7))

    fig.savefig(out_path, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"combined ECA figure -> {out_path}")

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for builder in (row_1d, row_2d, row_3d):
        path, info = builder()
        print(f"{info['rule']}: period={info['period']} shift={info['shift']} "
              f"defect_rate={info['defect_rate']} -> {path}")
        paths.append(path)
    composite = PAPER_FIG_DIR / "lba_decompositions.png"
    stitch_rows(paths, composite)
    print(f"composite -> {composite}")
    stabilization_figure(PAPER_FIG_DIR / "stabilization_real.png")
    combined_eca_figure(PAPER_FIG_DIR / "lba_results.png")
    results_3d_figure(PAPER_FIG_DIR / "lba_results_3d.png")
    print(f"stabilization -> {PAPER_FIG_DIR / 'stabilization_real.png'}")


if __name__ == "__main__":
    main()
