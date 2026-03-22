"""Plotting utilities for 2D and 3D cellular automata spacetimes."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from .alife_style import (
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
from .repair_nd import RelativePeriodicFitND


def _binary_legend_handles() -> list[Patch]:
    return [
        Patch(facecolor=ZERO_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="0 = light"),
        Patch(facecolor=ONE_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="1 = dark"),
    ]


def plot_2d_slices(spacetime: np.ndarray, *, title: str = "", max_slices: int = 8):
    """Plot time slices of a 2D CA spacetime (steps, H, W)."""
    steps = spacetime.shape[0]
    indices = np.linspace(0, steps - 1, min(max_slices, steps), dtype=int)
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(2.5 * n, 2.8))
    if n == 1:
        axes = [axes]
    for ax, t in zip(axes, indices):
        ax.imshow(spacetime[t], interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
        ax.set_title(f"t={t}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)
    fig.suptitle(title or "2D CA time slices", fontsize=11)
    apply_figure_theme(fig)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.92))
    return fig, axes


def plot_2d_decomposition(
    fit: RelativePeriodicFitND,
    *,
    source: np.ndarray,
    time_index: int | None = None,
    title_prefix: str = "",
):
    """Plot a single time-slice decomposition for a 2D CA."""
    if time_index is None:
        time_index = source.shape[0] // 2
    t = time_index

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(source[t], interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    axes[0].set_title(f"{title_prefix}source t={t}")
    axes[1].imshow(fit.background[t], interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    shift_str = ",".join(str(s) for s in fit.shift)
    axes[1].set_title(f"{title_prefix}background\ns=({shift_str}), p={fit.period}")
    axes[2].imshow(fit.defect_mask[t].astype(np.uint8), interpolation="nearest", cmap=DEFECT_CMAP, vmin=0, vmax=1)
    axes[2].set_title(f"{title_prefix}defects\nrate={fit.defect_rate:.3f}")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)
    apply_figure_theme(fig)
    fig.tight_layout()
    return fig, axes


def plot_2d_kymograph(spacetime: np.ndarray, *, axis: int = 1, title: str = ""):
    """Plot a kymograph (space-time slice) from a 2D CA by averaging along one spatial axis.

    axis=1 averages over y (shows x vs t), axis=2 averages over x (shows y vs t).
    """
    avg = spacetime.mean(axis=axis)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(avg, aspect="auto", interpolation="nearest", cmap="gray_r", vmin=0, vmax=1)
    dim_label = "x" if axis == 1 else "y"
    ax.set_xlabel(f"{dim_label} index")
    ax.set_ylabel("time (top to bottom)")
    ax.set_title(title or f"Kymograph (averaged over {'y' if axis == 1 else 'x'})")
    apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)
    apply_figure_theme(fig)
    fig.tight_layout()
    return fig, ax


def plot_3d_slices(spacetime: np.ndarray, *, z_index: int | None = None, title: str = "", max_slices: int = 6):
    """Plot time slices of a 3D CA spacetime (steps, Sz, Sy, Sx) at a fixed z-index."""
    steps = spacetime.shape[0]
    if z_index is None:
        z_index = spacetime.shape[1] // 2
    indices = np.linspace(0, steps - 1, min(max_slices, steps), dtype=int)
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(2.5 * n, 2.8))
    if n == 1:
        axes = [axes]
    for ax, t in zip(axes, indices):
        ax.imshow(spacetime[t, z_index], interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
        ax.set_title(f"t={t}, z={z_index}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)
    fig.suptitle(title or "3D CA time slices (z-slice)", fontsize=11)
    apply_figure_theme(fig)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.92))
    return fig, axes


def plot_3d_decomposition(
    fit: RelativePeriodicFitND,
    *,
    source: np.ndarray,
    time_index: int | None = None,
    z_index: int | None = None,
    title_prefix: str = "",
):
    """Plot a single (t, z) slice decomposition for a 3D CA."""
    if time_index is None:
        time_index = source.shape[0] // 2
    if z_index is None:
        z_index = source.shape[1] // 2
    t, z = time_index, z_index

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(source[t, z], interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    axes[0].set_title(f"{title_prefix}source t={t},z={z}")
    axes[1].imshow(fit.background[t, z], interpolation="nearest", cmap=BINARY_CMAP, vmin=0, vmax=1)
    shift_str = ",".join(str(s) for s in fit.shift)
    axes[1].set_title(f"{title_prefix}background\ns=({shift_str}), p={fit.period}")
    axes[2].imshow(fit.defect_mask[t, z].astype(np.uint8), interpolation="nearest", cmap=DEFECT_CMAP, vmin=0, vmax=1)
    axes[2].set_title(f"{title_prefix}defects\nrate={fit.defect_rate:.3f}")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)
    apply_figure_theme(fig)
    fig.tight_layout()
    return fig, axes


def plot_spectrum_nd(frame: pd.DataFrame, *, value: str = "defect_rate", title: str | None = None):
    """Plot defect spectrum for 2D CA (shift_0 vs period heatmap, minimized over shift_1 etc.)."""
    shift_cols = sorted(c for c in frame.columns if c.startswith("shift_"))

    if len(shift_cols) <= 1:
        # Simple case: one spatial shift dimension
        s_col = shift_cols[0] if shift_cols else "shift_0"
        pivot = frame.pivot(index="period", columns=s_col, values=value).sort_index().sort_index(axis=1)
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        image = ax.imshow(pivot.values, aspect="auto", interpolation="nearest")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(list(pivot.columns))
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(list(pivot.index))
        ax.set_xlabel(s_col.replace("_", " "))
        ax.set_ylabel("period")
    else:
        # Multi-shift: take min over shift_1+ for each (shift_0, period)
        group_cols = ["period", shift_cols[0]]
        grouped = frame.groupby(group_cols)[value].min().reset_index()
        pivot = grouped.pivot(index="period", columns=shift_cols[0], values=value).sort_index().sort_index(axis=1)
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        image = ax.imshow(pivot.values, aspect="auto", interpolation="nearest")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(list(pivot.columns))
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(list(pivot.index))
        ax.set_xlabel(f"{shift_cols[0].replace('_', ' ')} (min over other shifts)")
        ax.set_ylabel("period")

    ax.set_title(title or value.replace("_", " ").title())
    apply_axis_theme(ax, facecolor=BACKGROUND_COLOR)
    best_row, best_col = np.unravel_index(np.nanargmin(pivot.values), pivot.shape)
    ax.scatter(best_col, best_row, s=240, marker="s", facecolors="none", edgecolors=TEXT_COLOR, linewidths=2.6)
    ax.scatter(best_col, best_row, s=200, marker="s", facecolors="none", edgecolors=PAPER_COLOR, linewidths=1.5)
    display_value = value.replace("_", " ")
    colorbar = fig.colorbar(image, ax=ax, label=f"{display_value} (lower is better)")
    colorbar.ax.yaxis.label.set_color(TEXT_COLOR)
    colorbar.ax.tick_params(colors=SECONDARY_COLOR)
    colorbar.outline.set_edgecolor(GRID_COLOR)
    apply_figure_theme(fig)
    fig.tight_layout()
    return fig, ax
