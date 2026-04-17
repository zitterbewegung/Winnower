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
    DEFECT_OFF_COLOR,
    DEFECT_ON_COLOR,
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


def _style_voxel_axes(ax, shape_xyz: tuple[int, int, int]) -> None:
    """Apply consistent theming to a 3D voxel axes."""
    sx, sy, sz = shape_xyz
    ax.set_xlim(0, sx)
    ax.set_ylim(0, sy)
    ax.set_zlim(0, sz)
    try:
        ax.set_box_aspect((sx, sy, sz))
    except Exception:
        pass
    ax.set_facecolor(BACKGROUND_COLOR)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.label.set_color(TEXT_COLOR)
        axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        axis._axinfo["grid"]["color"] = GRID_COLOR
        axis._axinfo["grid"]["linewidth"] = 0.4
    ax.tick_params(colors=SECONDARY_COLOR, pad=-2)
    ax.title.set_color(TEXT_COLOR)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=22, azim=-58)


def _to_voxel_filled(volume: np.ndarray) -> np.ndarray:
    """Convert a (Sz, Sy, Sx) binary volume into the (Sx, Sy, Sz) layout matplotlib voxels expects."""
    if volume.ndim != 3:
        raise ValueError(f"voxel volume must be 3D (Sz, Sy, Sx); got shape {volume.shape}")
    return np.ascontiguousarray(volume.astype(bool).transpose(2, 1, 0))


def plot_3d_volume_decomposition(
    fit: RelativePeriodicFitND,
    *,
    source: np.ndarray,
    time_index: int | None = None,
    title_prefix: str = "",
    elev: float = 22.0,
    azim: float = -58.0,
    background_alpha: float = 0.18,
):
    """Render a true 3D voxel decomposition (source / background / defects) at one time slice.

    The defect panel overlays the (semi-transparent) background volume so that
    defect voxels can be located against the inferred orbit structure.

    Parameters
    ----------
    fit : RelativePeriodicFitND from a 3D fit (spacetime shape (steps, Sz, Sy, Sx)).
    source : the original 4D spacetime that produced ``fit``.
    time_index : which time step to render; defaults to the middle of the run.
    title_prefix : prepended to each panel title (e.g. ``"3d-life "``).
    elev, azim : matplotlib 3D view angles applied to all three panels.
    background_alpha : opacity of the background voxels in the defect overlay.
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)

    if source.ndim != 4:
        raise ValueError(f"source must be 4D (steps, Sz, Sy, Sx); got shape {source.shape}")
    if fit.background.shape != source.shape:
        raise ValueError("fit.background shape must match source shape")
    if time_index is None:
        time_index = source.shape[0] // 2
    if not 0 <= time_index < source.shape[0]:
        raise IndexError(f"time_index {time_index} out of range for {source.shape[0]} steps")

    src_vol = source[time_index].astype(np.uint8)
    bg_vol = fit.background[time_index].astype(np.uint8)
    defect_vol = fit.defect_mask[time_index].astype(bool)

    sz, sy, sx = src_vol.shape
    src_filled = _to_voxel_filled(src_vol)
    bg_filled = _to_voxel_filled(bg_vol)
    defect_filled = _to_voxel_filled(defect_vol)

    fig = plt.figure(figsize=(13.5, 4.6))
    axes = [fig.add_subplot(1, 3, i + 1, projection="3d") for i in range(3)]

    edge = (0.20, 0.20, 0.20, 0.55)

    axes[0].voxels(
        src_filled,
        facecolors=ONE_COLOR,
        edgecolor=edge,
        linewidth=0.25,
        shade=True,
    )
    axes[0].set_title(f"{title_prefix}source  t={time_index}")

    axes[1].voxels(
        bg_filled,
        facecolors=ONE_COLOR,
        edgecolor=edge,
        linewidth=0.25,
        shade=True,
    )
    shift_str = ",".join(str(s) for s in fit.shift)
    axes[1].set_title(f"{title_prefix}background\ns=({shift_str}), p={fit.period}")

    # Three-category overlay: correctly-predicted background, "surprise ON", "surprise OFF"
    bg_only = bg_filled & ~defect_filled         # background=1, source=1 (correct)
    defect_on = defect_filled & ~bg_filled       # background=0, source=1 ("surprise ON")
    defect_off = defect_filled & bg_filled       # background=1, source=0 ("surprise OFF")

    bg_overlay_color = (0.30, 0.30, 0.30, background_alpha)
    if bg_only.any():
        axes[2].voxels(
            bg_only,
            facecolors=bg_overlay_color,
            edgecolor=(0.30, 0.30, 0.30, 0.10),
            linewidth=0.15,
            shade=False,
        )
    if defect_on.any():
        axes[2].voxels(
            defect_on,
            facecolors=DEFECT_ON_COLOR,
            edgecolor=(0.45, 0.05, 0.05, 0.80),
            linewidth=0.30,
            shade=True,
        )
    if defect_off.any():
        axes[2].voxels(
            defect_off,
            facecolors=DEFECT_OFF_COLOR,
            edgecolor=(0.10, 0.25, 0.45, 0.80),
            linewidth=0.30,
            shade=True,
        )
    axes[2].set_title(
        f"{title_prefix}defects (overlay)\n"
        f"rate={fit.defect_rate:.3f}  ({fit.defect_sites}/{fit.total_sites} cells)"
    )

    legend_handles = [
        Patch(facecolor=ONE_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="live cell"),
        Patch(facecolor=bg_overlay_color, edgecolor=LEGEND_EDGE_COLOR, label="background (correct)"),
        Patch(facecolor=DEFECT_ON_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="surprise ON (src=1, bg=0)"),
        Patch(facecolor=DEFECT_OFF_COLOR, edgecolor=LEGEND_EDGE_COLOR, label="surprise OFF (src=0, bg=1)"),
    ]
    axes[2].legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        frameon=False,
        fontsize=8,
        labelcolor=TEXT_COLOR,
    )

    for ax in axes:
        _style_voxel_axes(ax, (sx, sy, sz))
        ax.view_init(elev=elev, azim=azim)

    apply_figure_theme(fig)
    fig.tight_layout()
    return fig, axes


def plot_3d_volume_montage(
    fit: RelativePeriodicFitND,
    *,
    source: np.ndarray,
    time_indices: list[int] | None = None,
    n_panels: int = 4,
    title: str = "",
    elev: float = 22.0,
    azim: float = -58.0,
    background_alpha: float = 0.15,
    saturation_threshold: float = 0.30,
    cutaway_plane: str = "x",
):
    """Render a row of 3D defect-vs-background voxel panels across several time slices.

    Useful for showing how a 3D defect cloud evolves under a fixed (shift, period) fit.
    When a time slice's defect mask is denser than ``saturation_threshold`` of the
    volume, the panel is rendered as a cutaway (half of the cube hidden along
    ``cutaway_plane``) so that internal structure stays legible.
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    if source.ndim != 4:
        raise ValueError(f"source must be 4D (steps, Sz, Sy, Sx); got shape {source.shape}")
    if cutaway_plane not in ("x", "y", "z"):
        raise ValueError("cutaway_plane must be one of 'x', 'y', 'z'")

    steps = source.shape[0]
    if time_indices is None:
        n_panels = max(1, min(n_panels, steps))
        time_indices = list(np.linspace(0, steps - 1, n_panels, dtype=int))
    else:
        time_indices = [int(t) for t in time_indices]
        for t in time_indices:
            if not 0 <= t < steps:
                raise IndexError(f"time_index {t} out of range for {steps} steps")

    n = len(time_indices)
    sz, sy, sx = source.shape[1:]
    fig = plt.figure(figsize=(3.4 * n + 0.4, 4.0))
    axes = [fig.add_subplot(1, n, i + 1, projection="3d") for i in range(n)]

    bg_overlay_color = (0.30, 0.30, 0.30, background_alpha)
    for ax, t in zip(axes, time_indices):
        bg_filled = _to_voxel_filled(fit.background[t])
        defect_filled = _to_voxel_filled(fit.defect_mask[t])

        density = float(defect_filled.mean()) if defect_filled.size > 0 else 0.0
        title_suffix = ""
        if density > saturation_threshold:
            mask = np.ones_like(defect_filled, dtype=bool)
            if cutaway_plane == "x":
                mask[: sx // 2, :, :] = False
            elif cutaway_plane == "y":
                mask[:, : sy // 2, :] = False
            else:  # "z"
                mask[:, :, : sz // 2] = False
            bg_filled = bg_filled & mask
            defect_filled = defect_filled & mask
            title_suffix = f"  (cutaway, density={density:.2f})"

        bg_only = bg_filled & ~defect_filled
        defect_on = defect_filled & ~bg_filled
        defect_off = defect_filled & bg_filled

        if bg_only.any():
            ax.voxels(
                bg_only,
                facecolors=bg_overlay_color,
                edgecolor=(0.30, 0.30, 0.30, 0.08),
                linewidth=0.12,
                shade=False,
            )
        if defect_on.any():
            ax.voxels(
                defect_on,
                facecolors=DEFECT_ON_COLOR,
                edgecolor=(0.45, 0.05, 0.05, 0.80),
                linewidth=0.25,
                shade=True,
            )
        if defect_off.any():
            ax.voxels(
                defect_off,
                facecolors=DEFECT_OFF_COLOR,
                edgecolor=(0.10, 0.25, 0.45, 0.80),
                linewidth=0.25,
                shade=True,
            )
        ax.set_title(f"t={t}{title_suffix}", fontsize=10)
        _style_voxel_axes(ax, (sx, sy, sz))
        ax.view_init(elev=elev, azim=azim)

    if title:
        fig.suptitle(title, fontsize=11, color=TEXT_COLOR)
        rect = (0.0, 0.0, 1.0, 0.92)
    else:
        rect = (0.0, 0.0, 1.0, 1.0)
    apply_figure_theme(fig)
    fig.tight_layout(rect=rect)
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
