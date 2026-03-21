#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.plotting import save_figure  # noqa: E402

TEXT = "#1b1f23"
ACCENT = "#2b6cb0"
ARROW = "#4f9d69"
BORDER = "#c7c7c7"
PANEL_BG = "#f7f7f7"
ZERO = "#f4f3ee"
ONE = "#222222"


def _panel(ax: plt.Axes, number: int, title: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0.02, 0.04), 0.96, 0.90, facecolor=PANEL_BG, edgecolor=BORDER, linewidth=1.2))
    ax.add_patch(Circle((0.09, 0.905), 0.04, facecolor=ACCENT, edgecolor="none"))
    ax.text(0.09, 0.905, str(number), ha="center", va="center", fontsize=13, fontweight="bold", color="white")
    ax.text(0.20, 0.905, title, ha="left", va="center", fontsize=15, fontweight="bold", color=TEXT)


def _draw_binary_grid(ax: plt.Axes, data: np.ndarray, *, left: float, bottom: float, width: float, height: float) -> None:
    rows, cols = data.shape
    cell_w = width / cols
    cell_h = height / rows
    for r in range(rows):
        for c in range(cols):
            value = int(data[r, c])
            x = left + c * cell_w
            y = bottom + (rows - 1 - r) * cell_h
            ax.add_patch(
                Rectangle(
                    (x, y),
                    cell_w,
                    cell_h,
                    facecolor=ONE if value else ZERO,
                    edgecolor="#8a8a8a",
                    linewidth=0.7,
                )
            )
    ax.add_patch(Rectangle((left, bottom), width, height, fill=False, edgecolor="#777777", linewidth=1.0))


def _observed_panel(ax: plt.Axes) -> None:
    _panel(ax, 1, "Observed spacetime")
    ax.text(
        0.50,
        0.78,
        "Choose candidate $(p,s)$.",
        ha="center",
        va="bottom",
        fontsize=12,
        color=TEXT,
    )
    ax.text(0.50, 0.72, "Example below: $p=2$, $s=1$.", ha="center", va="bottom", fontsize=12, color=TEXT)

    data = np.array(
        [
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
        ],
        dtype=np.uint8,
    )
    left, right, bottom, top = 0.25, 0.84, 0.19, 0.63
    _draw_binary_grid(ax, data, left=left, bottom=bottom, width=right - left, height=top - bottom)
    ax.text((left + right) / 2, top + 0.03, "space $x$", ha="center", va="bottom", fontsize=12, color=TEXT)
    ax.text(left - 0.06, (bottom + top) / 2, "time $t$", ha="center", va="center", rotation=90, fontsize=12, color=TEXT)

    ax.text(
        0.50,
        0.12,
        "Raw CA spacetime to explain.",
        ha="center",
        va="center",
        fontsize=12,
        color=TEXT,
    )


def _orbit_panel(ax: plt.Axes) -> None:
    _panel(ax, 2, "Orbit classes")
    ax.text(
        0.50,
        0.78,
        "Apply $(t,x)\\mapsto(t+p,x+s)$.",
        ha="center",
        va="bottom",
        fontsize=12,
        color=TEXT,
    )
    ax.text(0.50, 0.72, "Same color = same orbit.", ha="center", va="bottom", fontsize=12, color=TEXT)

    colors = ["#d7e8fb", "#f8d1d1", "#d4f0e0", "#ffe88b", "#d9c8f0", "#f7d6b8"]
    x0, y0, w, h = 0.25, 0.18, 0.11, 0.11
    labels = np.array(
        [
            [1, 2, 3, 4, 1, 2],
            [4, 1, 2, 3, 4, 1],
            [3, 4, 1, 2, 3, 4],
            [2, 3, 4, 1, 2, 3],
            [1, 2, 3, 4, 1, 2],
        ]
    )
    for r in range(labels.shape[0]):
        for c in range(labels.shape[1]):
            lab = int(labels[r, c])
            ax.add_patch(
                Rectangle(
                    (x0 + c * w, y0 + (labels.shape[0] - 1 - r) * h),
                    w,
                    h,
                    facecolor=colors[(lab - 1) % len(colors)],
                    edgecolor="#8c8c8c",
                    linewidth=0.8,
                )
            )
            ax.text(
                x0 + c * w + w / 2,
                y0 + (labels.shape[0] - 1 - r) * h + h / 2,
                str(lab),
                ha="center",
                va="center",
                fontsize=12,
                color="#444444",
            )

    ax.add_patch(
        FancyArrowPatch(
            (0.50, 0.57),
            (0.41, 0.49),
            arrowstyle="->",
            mutation_scale=14,
            linewidth=1.6,
            color=ACCENT,
        )
    )
    ax.text(0.54, 0.53, "$(p,s)$", ha="left", va="center", fontsize=14, color=ACCENT)
    ax.text(
        0.50,
        0.12,
        "Each orbit contributes one background bit.",
        ha="center",
        va="center",
        fontsize=12,
        color=TEXT,
    )


def _majority_panel(ax: plt.Axes) -> None:
    _panel(ax, 3, "Majority-vote fit")
    ax.text(
        0.50,
        0.78,
        "Count ones and zeros in each orbit.",
        ha="center",
        va="bottom",
        fontsize=12,
        color=TEXT,
    )
    ax.text(0.50, 0.72, "Choose the majority bit.", ha="center", va="bottom", fontsize=12, color=TEXT)

    table_x, table_y, table_w, table_h = 0.23, 0.22, 0.38, 0.46
    ax.add_patch(Rectangle((table_x, table_y), table_w, table_h, facecolor="white", edgecolor="#9a9a9a", linewidth=1.0))
    row_h = table_h / 4
    col_split = table_x + 0.45 * table_w
    for i in range(1, 4):
        ax.plot([table_x, table_x + table_w], [table_y + i * row_h, table_y + i * row_h], color="#c0c0c0", linewidth=0.8)
    ax.plot([col_split, col_split], [table_y, table_y + table_h], color="#c0c0c0", linewidth=0.8)
    ax.text(table_x + 0.225 * table_w, table_y + table_h - row_h / 2, "orbit", ha="center", va="center", fontsize=13, fontweight="bold")
    ax.text(col_split + 0.275 * table_w, table_y + table_h - row_h / 2, "ones / zeros", ha="center", va="center", fontsize=13, fontweight="bold")
    rows = [("1", "5 / 1"), ("2", "1 / 5"), ("3", "4 / 2")]
    for idx, (orbit, counts) in enumerate(rows, start=1):
        yc = table_y + table_h - (idx + 0.5) * row_h
        ax.text(table_x + 0.225 * table_w, yc, orbit, ha="center", va="center", fontsize=13)
        ax.text(col_split + 0.275 * table_w, yc, counts, ha="center", va="center", fontsize=13)

    ax.text(0.72, 0.54, "$B^*(p,s)$", ha="center", va="center", fontsize=16, color=TEXT)
    ax.add_patch(FancyArrowPatch((0.68, 0.48), (0.84, 0.48), arrowstyle="->", mutation_scale=14, linewidth=1.8, color=ARROW))
    ax.text(0.50, 0.13, "Residual mask: $M = U \\oplus B^*$.", ha="center", va="center", fontsize=14, color=TEXT)


def _score_panel(ax: plt.Axes) -> None:
    _panel(ax, 4, "Score and select")
    ax.text(
        0.50,
        0.78,
        "NML = fit + complexity.",
        ha="center",
        va="bottom",
        fontsize=12,
        color=TEXT,
    )
    ax.text(0.50, 0.72, "Keep the best period.", ha="center", va="bottom", fontsize=12, color=TEXT)

    left, right, bottom, top = 0.07, 0.32, 0.23, 0.62
    data = np.array(
        [
            [0, 1, 1, 0],
            [1, 0, 1, 1],
            [0, 1, 0, 1],
            [1, 0, 1, 0],
        ],
        dtype=np.uint8,
    )
    _draw_binary_grid(ax, data, left=left, bottom=bottom, width=right - left, height=top - bottom)
    ax.text((left + right) / 2, top + 0.03, "$B^*(p,s)$", ha="center", va="bottom", fontsize=15)

    box_specs = [
        (0.42, 0.56, 0.47, 0.13, r"$\mathrm{NLL}(p,s)=\sum_j n_j H_b(\hat{\theta}_j)$"),
        (0.42, 0.39, 0.50, 0.13, r"$\mathrm{NML}=\mathrm{NLL}+\frac{1}{2}\sum_j \log_2 n_j$"),
        (0.42, 0.12, 0.50, 0.15, r"$p^*=\arg\min_p\ \min_s\,\mathrm{NML}(p,s)$"),
    ]
    for x, y, w, h, text in box_specs:
        ax.add_patch(Rectangle((x, y), w, h, facecolor="white", edgecolor="#c8c8c8", linewidth=1.0))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=14, color=TEXT)

    ax.add_patch(FancyArrowPatch((0.67, 0.37), (0.67, 0.28), arrowstyle="->", mutation_scale=14, linewidth=1.6, color=ACCENT))
    ax.text(
        0.50,
        0.10,
        "Output: periodic background + residual.",
        ha="center",
        va="center",
        fontsize=12,
        color=TEXT,
    )


def build_figure(output_path: Path, *, extra_formats: tuple[str, ...], bundle_png: Path | None) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(16.2, 4.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.08, wspace=0.10)
    fig.suptitle("Relative-periodic domain selection by Bernoulli NML", fontsize=22, fontweight="bold", y=0.965)

    _observed_panel(axes[0])
    _orbit_panel(axes[1])
    _majority_panel(axes[2])
    _score_panel(axes[3])

    for i in range(3):
        start = axes[i].get_position()
        end = axes[i + 1].get_position()
        fig.add_artist(
            FancyArrowPatch(
                (start.x1 + 0.005, 0.50),
                (end.x0 - 0.005, 0.50),
                transform=fig.transFigure,
                arrowstyle="simple",
                mutation_scale=28,
                color="#b0b9c6",
                alpha=0.85,
            )
        )

    save_figure(fig, output_path, extra_formats=extra_formats)
    if bundle_png is not None:
        save_figure(fig, bundle_png)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the ALIFE algorithm figure with cleaner bounds and vector outputs.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "alife_2026" / "editable_figures" / "algorithm_detailed.png",
    )
    parser.add_argument(
        "--bundle-png",
        type=Path,
        default=ROOT / "alife_lba_bundle" / "figures" / "algorithm_detailed.png",
    )
    parser.add_argument(
        "--export-formats",
        type=str,
        default="png,pdf,svg",
        help="Comma-separated formats to write, e.g. png,pdf,svg",
    )
    args = parser.parse_args()

    requested_formats = tuple(
        fmt.strip().lower().lstrip(".")
        for fmt in args.export_formats.split(",")
        if fmt.strip()
    )
    extra_formats = tuple(fmt for fmt in requested_formats if fmt != args.output.suffix.lower().lstrip("."))
    build_figure(args.output, extra_formats=extra_formats, bundle_png=args.bundle_png)
    print(f"Wrote algorithm figure to {args.output}")


if __name__ == "__main__":
    main()
