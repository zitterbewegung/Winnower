from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from .alife_style import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BINARY_CMAP,
    DEFECT_CMAP,
    DEFECT_COLOR,
    GRID_COLOR,
    LEGEND_EDGE_COLOR,
    ONE_COLOR,
    PAPER_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    ZERO_COLOR,
    apply_axis_theme,
    apply_figure_theme,
)
from .repair import RelativePeriodicFit


def _binary_legend_handles() -> list[Patch]:
    return [
        Patch(facecolor=ZERO_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="0 = light"),
        Patch(facecolor=ONE_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="1 = dark"),
    ]


def _decorate_figure(fig, *, caption: str, legend_handles: list | None = None, legend_ncol: int | None = None) -> None:
    apply_figure_theme(fig)
    fig.tight_layout(rect=(0.0, 0.07, 1.0, 0.88))
    if legend_handles:
        legend = fig.legend(
            handles=legend_handles,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.985),
            ncol=legend_ncol or len(legend_handles),
            frameon=False,
            handlelength=1.6,
            columnspacing=1.3,
        )
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)
    fig.text(0.5, 0.02, caption, ha="center", va="bottom", fontsize=9, color=TEXT_COLOR)


def _style_binary_axis(ax, title: str | None = None) -> None:
    ax.set_xlabel("cell index")
    ax.set_ylabel("time (top to bottom)")
    if title:
        ax.set_title(title)
    apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)


def plot_spacetime(spacetime: np.ndarray, *, title: str | None = None):
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.imshow(spacetime, aspect="auto", interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    _style_binary_axis(ax, title=title)
    _decorate_figure(
        fig,
        caption="Look for repeated diagonals, stable domains, and long-lived lanes that persist across many rows.",
        legend_handles=_binary_legend_handles(),
    )
    return fig, ax


def plot_spectrum(frame: pd.DataFrame, *, value: str = "defect_rate", title: str | None = None):
    pivot = frame.pivot(index="period", columns="shift", values=value).sort_index().sort_index(axis=1)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    image = ax.imshow(pivot.values, aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(list(pivot.columns))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(list(pivot.index))
    ax.set_xlabel("shift")
    ax.set_ylabel("period")
    ax.set_title(title or value.replace("_", " ").title())
    apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)

    best_row, best_col = np.unravel_index(np.nanargmin(pivot.values), pivot.shape)
    best_shift = int(pivot.columns[best_col])
    best_period = int(pivot.index[best_row])
    ax.scatter(best_col, best_row, s=240, marker="s", facecolors="none", edgecolors=TEXT_COLOR, linewidths=2.6)
    ax.scatter(best_col, best_row, s=200, marker="s", facecolors="none", edgecolors=PAPER_COLOR, linewidths=1.5)

    display_value = value.replace("_", " ")
    colorbar = fig.colorbar(image, ax=ax, label=f"{display_value} (lower is better)")
    colorbar.ax.yaxis.label.set_color(TEXT_COLOR)
    colorbar.ax.tick_params(colors=SECONDARY_COLOR)
    colorbar.outline.set_edgecolor(GRID_COLOR)

    if value == "defect_rate":
        caption = (
            f"Darker cells mean fewer mismatches to the fitted background. "
            f"Minimum scanned value at shift={best_shift}, period={best_period}."
        )
    elif value == "run_length_bits":
        caption = (
            f"Darker cells mean a more compressible defect mask. "
            f"Minimum scanned value at shift={best_shift}, period={best_period}."
        )
    else:
        caption = f"Darker cells indicate smaller {display_value} values. Minimum scanned value at shift={best_shift}, period={best_period}."

    _decorate_figure(
        fig,
        caption=caption,
        legend_handles=[
            Line2D(
                [0],
                [0],
                marker="s",
                markersize=8,
                markerfacecolor="none",
                markeredgecolor=TEXT_COLOR,
                markeredgewidth=1.8,
                linestyle="None",
                label="minimum scanned value",
            )
        ],
        legend_ncol=1,
    )
    return fig, ax


def plot_decomposition(fit: RelativePeriodicFit, *, source: np.ndarray, title_prefix: str = ""):
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    axes[0].imshow(source, aspect="auto", interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    axes[0].set_title(f"{title_prefix}source")
    axes[1].imshow(fit.background, aspect="auto", interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    axes[1].set_title(f"{title_prefix}background\nbest fit: s={fit.shift}, p={fit.period}")
    axes[2].imshow(fit.defect_mask.astype(np.uint8), aspect="auto", interpolation="nearest", cmap=DEFECT_CMAP, vmin=0, vmax=1)
    axes[2].set_title(f"{title_prefix}defect mask\ndefect rate={fit.defect_rate:.3f}")
    for ax in axes:
        ax.set_xlabel("cell index")
        ax.set_ylabel("time (top to bottom)")

    _decorate_figure(
        fig,
        caption="Red cells disagree with the fitted background. Look for compact world-tubes and clean boundaries instead of diffuse pepper noise.",
        legend_handles=[
            *_binary_legend_handles(),
            Patch(facecolor=DEFECT_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="defect = red"),
        ],
    )
    return fig, axes


def save_figure(
    fig,
    path: str | Path,
    *,
    extra_formats: tuple[str, ...] = (),
    close: bool = False,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raster_formats = {"png", "jpg", "jpeg", "tif", "tiff", "webp"}
    raster_dpi = 360
    vector_image_dpi = 320

    def _save(target: Path) -> None:
        fmt = target.suffix.lower().lstrip(".")
        kwargs = {
            "bbox_inches": "tight",
            "pad_inches": 0,
            "facecolor": fig.get_facecolor(),
            "edgecolor": fig.get_edgecolor(),
        }
        if fmt in raster_formats:
            kwargs["dpi"] = raster_dpi
        else:
            # Vector backends still rasterize image artists like imshow panels.
            kwargs["dpi"] = vector_image_dpi
        fig.savefig(target, **kwargs)

    _save(path)

    seen_formats = {path.suffix.lower().lstrip(".")}
    for fmt in extra_formats:
        normalized = fmt.lower().lstrip(".")
        if not normalized or normalized in seen_formats:
            continue
        seen_formats.add(normalized)
        _save(path.with_suffix(f".{normalized}"))

    if close:
        plt.close(fig)
