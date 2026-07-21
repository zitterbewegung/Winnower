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

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.alife_style import (  # noqa: E402
    ACCENT_COLOR,
    ACCENT_SOFT_COLOR,
    BACKGROUND_COLOR,
    BLUSH_COLOR,
    GRID_COLOR,
    MUTED_COLOR,
    ONE_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    ZERO_COLOR,
    apply_figure_theme,
)
from relative_symmetry_repair.plotting import save_figure  # noqa: E402

TEXT = TEXT_COLOR
ACCENT = ACCENT_COLOR
ARROW = SECONDARY_COLOR
BORDER = GRID_COLOR
PANEL_BG = BACKGROUND_COLOR
CARD_BG = ACCENT_SOFT_COLOR
MUTED = MUTED_COLOR
ZERO = ZERO_COLOR
ONE = ONE_COLOR


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
                    edgecolor=BORDER,
                    linewidth=0.7,
                )
            )
    ax.add_patch(Rectangle((left, bottom), width, height, fill=False, edgecolor=ARROW, linewidth=1.0))


def _square_frame(ax: plt.Axes, *, left: float, bottom: float, size: float) -> None:
    ax.add_patch(Rectangle((left, bottom), size, size, fill=False, edgecolor=BORDER, linewidth=1.0))


def _fit_rect_in_square(*, rows: int, cols: int, left: float, bottom: float, size: float, pad: float = 0.08) -> tuple[float, float, float, float]:
    usable = size * (1.0 - 2.0 * pad)
    cell = min(usable / cols, usable / rows)
    width = cols * cell
    height = rows * cell
    inner_left = left + (size - width) / 2.0
    inner_bottom = bottom + (size - height) / 2.0
    return inner_left, inner_bottom, width, height


def _panel_subtitle(ax: plt.Axes, line1: str, line2: str) -> None:
    ax.text(0.50, 0.79, line1, ha="center", va="center", fontsize=11.5, color=TEXT)
    ax.text(0.50, 0.73, line2, ha="center", va="center", fontsize=11.5, color=TEXT)


def _info_card(
    ax: plt.Axes,
    *,
    left: float,
    bottom: float,
    width: float,
    height: float,
    title: str,
    body: str,
    body_fontsize: float,
) -> None:
    ax.add_patch(Rectangle((left, bottom), width, height, facecolor=CARD_BG, edgecolor=BORDER, linewidth=1.0))
    ax.text(left + 0.03, bottom + height - 0.03, title, ha="left", va="top", fontsize=10.5, fontweight="bold", color=ACCENT)
    ax.text(left + width / 2, bottom + height * 0.44, body, ha="center", va="center", fontsize=body_fontsize, color=TEXT, linespacing=1.0)


def _observed_panel(ax: plt.Axes) -> None:
    _panel(ax, 1, "Observed space-time diagram")
    _panel_subtitle(ax, "Choose candidate $(p,s)$.", "Example: $p=2$, $s=1$.")

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
    frame_left, frame_bottom, frame_size = 0.26, 0.21, 0.48
    _square_frame(ax, left=frame_left, bottom=frame_bottom, size=frame_size)
    left, bottom, width, height = _fit_rect_in_square(
        rows=data.shape[0],
        cols=data.shape[1],
        left=frame_left,
        bottom=frame_bottom,
        size=frame_size,
        pad=0.10,
    )
    _draw_binary_grid(ax, data, left=left, bottom=bottom, width=width, height=height)
    ax.text(frame_left + frame_size / 2, frame_bottom + frame_size - 0.035, "$x$", ha="center", va="bottom", fontsize=13, color=TEXT)
    ax.text(frame_left - 0.055, frame_bottom + frame_size / 2, "$t$", ha="center", va="center", rotation=90, fontsize=13, color=TEXT)

    ax.text(
        0.50,
        0.12,
        "Raw CA space-time diagram to explain.",
        ha="center",
        va="center",
        fontsize=12,
        color=TEXT,
    )


def _orbit_panel(ax: plt.Axes) -> None:
    _panel(ax, 2, "Translation orbits")
    _panel_subtitle(ax, "Apply $(t,x)\\mapsto(t+p,x+s)$.", "Same color = same orbit.")

    colors = [CARD_BG, PANEL_BG, MUTED, BLUSH_COLOR]
    labels = np.array(
        [
            [1, 2, 3, 4, 1, 2],
            [4, 1, 2, 3, 4, 1],
            [3, 4, 1, 2, 3, 4],
            [2, 3, 4, 1, 2, 3],
            [1, 2, 3, 4, 1, 2],
        ]
    )
    frame_left, frame_bottom, frame_size = 0.24, 0.20, 0.50
    _square_frame(ax, left=frame_left, bottom=frame_bottom, size=frame_size)
    x0, y0, grid_w, grid_h = _fit_rect_in_square(
        rows=labels.shape[0],
        cols=labels.shape[1],
        left=frame_left,
        bottom=frame_bottom,
        size=frame_size,
        pad=0.10,
    )
    w = grid_w / labels.shape[1]
    h = grid_h / labels.shape[0]
    for r in range(labels.shape[0]):
        for c in range(labels.shape[1]):
            lab = int(labels[r, c])
            ax.add_patch(
                Rectangle(
                    (x0 + c * w, y0 + (labels.shape[0] - 1 - r) * h),
                    w,
                    h,
                    facecolor=colors[(lab - 1) % len(colors)],
                    edgecolor=BORDER,
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
                color=TEXT,
            )

    ax.text(
        0.50,
        0.12,
        "Each orbit contributes one domain-template bit.",
        ha="center",
        va="center",
        fontsize=12,
        color=TEXT,
    )


def _majority_panel(ax: plt.Axes) -> None:
    _panel(ax, 3, "Majority-vote fit")
    _panel_subtitle(ax, "Count ones and zeros in each orbit.", "Choose the majority bit.")

    frame_left, frame_bottom, frame_size = 0.20, 0.20, 0.50
    _square_frame(ax, left=frame_left, bottom=frame_bottom, size=frame_size)
    table_x, table_y, table_w, table_h = frame_left + 0.05, frame_bottom + 0.09, 0.25, 0.40
    ax.add_patch(Rectangle((table_x, table_y), table_w, table_h, facecolor=CARD_BG, edgecolor=ARROW, linewidth=1.0))
    row_h = table_h / 4
    col_split = table_x + 0.40 * table_w
    for i in range(1, 4):
        ax.plot([table_x, table_x + table_w], [table_y + i * row_h, table_y + i * row_h], color=BORDER, linewidth=0.8)
    ax.plot([col_split, col_split], [table_y, table_y + table_h], color=BORDER, linewidth=0.8)
    ax.text(table_x + 0.20 * table_w, table_y + table_h - row_h / 2, "orbit", ha="center", va="center", fontsize=11.5, fontweight="bold")
    ax.text(col_split + 0.30 * table_w, table_y + table_h - row_h / 2, "ones /\nzeros", ha="center", va="center", fontsize=11.0, fontweight="bold", linespacing=0.95)
    rows = [("1", "5 / 1"), ("2", "1 / 5"), ("3", "4 / 2")]
    for idx, (orbit, counts) in enumerate(rows, start=1):
        yc = table_y + table_h - (idx + 0.5) * row_h
        ax.text(table_x + 0.20 * table_w, yc, orbit, ha="center", va="center", fontsize=12.5)
        ax.text(col_split + 0.30 * table_w, yc, counts, ha="center", va="center", fontsize=12.5)

    card_left, card_bottom, card_w, card_h = frame_left + 0.34, frame_bottom + 0.16, 0.12, 0.18
    _info_card(
        ax,
        left=card_left,
        bottom=card_bottom,
        width=card_w,
        height=card_h,
        title="Output",
        body="one bit\nper orbit",
        body_fontsize=12.2,
    )
    ax.add_patch(FancyArrowPatch((table_x + table_w + 0.015, frame_bottom + 0.25), (card_left - 0.01, frame_bottom + 0.25), arrowstyle="->", mutation_scale=14, linewidth=1.8, color=ARROW))
    ax.text(0.50, 0.13, "Defect mask: $M = U \\oplus B^*$.", ha="center", va="center", fontsize=14, color=TEXT)


def _score_panel(ax: plt.Axes) -> None:
    _panel(ax, 4, "Score and select")
    _panel_subtitle(ax, "NML = fit + penalty.", "Keep the best period.")

    frame_left, frame_bottom, frame_size = 0.14, 0.18, 0.54
    _square_frame(ax, left=frame_left, bottom=frame_bottom, size=frame_size)
    grid_left, grid_bottom, grid_size = frame_left + 0.04, frame_bottom + 0.16, 0.22
    data = np.array(
        [
            [0, 1, 1, 0],
            [1, 0, 1, 1],
            [0, 1, 0, 1],
            [1, 0, 1, 0],
        ],
        dtype=np.uint8,
    )
    _square_frame(ax, left=grid_left, bottom=grid_bottom, size=grid_size)
    left, bottom, width, height = _fit_rect_in_square(
        rows=data.shape[0],
        cols=data.shape[1],
        left=grid_left,
        bottom=grid_bottom,
        size=grid_size,
        pad=0.08,
    )
    _draw_binary_grid(ax, data, left=left, bottom=bottom, width=width, height=height)
    ax.text(grid_left + grid_size / 2, grid_bottom + grid_size + 0.035, "$B^*(p,s)$", ha="center", va="bottom", fontsize=14.5)

    _info_card(
        ax,
        left=0.44,
        bottom=0.56,
        width=0.43,
        height=0.14,
        title="Fit",
        body=r"$\sum_j n_j H_b(\hat{\theta}_j)$",
        body_fontsize=15.0,
    )
    _info_card(
        ax,
        left=0.44,
        bottom=0.39,
        width=0.43,
        height=0.14,
        title="Penalty",
        body=r"$\frac{1}{2}\sum_j \log_2 n_j$",
        body_fontsize=15.0,
    )
    _info_card(
        ax,
        left=0.44,
        bottom=0.20,
        width=0.43,
        height=0.15,
        title="Select",
        body="Lowest NML wins.",
        body_fontsize=13.4,
    )

    ax.add_patch(FancyArrowPatch((0.655, 0.37), (0.655, 0.30), arrowstyle="->", mutation_scale=14, linewidth=1.6, color=ACCENT))
    ax.text(
        0.50,
        0.10,
        "Output: periodic domain template + defect mask.",
        ha="center",
        va="center",
        fontsize=12,
        color=TEXT,
    )


def build_figure(output_path: Path, *, extra_formats: tuple[str, ...], bundle_png: Path | None) -> None:
    fig, axes = plt.subplots(
        1,
        4,
        figsize=(18.0, 5.5),
        gridspec_kw={"width_ratios": [1.00, 1.00, 0.98, 1.10]},
    )
    fig.subplots_adjust(left=0.018, right=0.982, top=0.89, bottom=0.075, wspace=0.072)
    apply_figure_theme(fig)
    fig.suptitle("Relative-periodic domain selection by Bernoulli NML", fontsize=22, fontweight="bold", y=0.968, color=ACCENT)

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
                color=ARROW,
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
