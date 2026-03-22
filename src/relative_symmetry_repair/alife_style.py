from __future__ import annotations

from matplotlib.colors import ListedColormap

BACKGROUND_COLOR = "#efe2d0"
PAPER_COLOR = "#ffffff"
TEXT_COLOR = "#3b3b3b"
ACCENT_COLOR = "#b00300"
ACCENT_SOFT_COLOR = "#fcdeb9"
SECONDARY_COLOR = "#5f5f5f"
BORDER_COLOR = "#dbdbdb"
GRID_COLOR = "#cfc3b3"
MUTED_COLOR = "#e2e2e2"
BLUSH_COLOR = "#f3d5d0"
LEGEND_EDGE_COLOR = "#444444"

ZERO_COLOR = ACCENT_SOFT_COLOR
ONE_COLOR = TEXT_COLOR
DEFECT_COLOR = ACCENT_COLOR

BINARY_CMAP = ListedColormap([ZERO_COLOR, ONE_COLOR])
DEFECT_CMAP = ListedColormap([ZERO_COLOR, DEFECT_COLOR])
ORBIT_COLORS = [ACCENT_SOFT_COLOR, BACKGROUND_COLOR, MUTED_COLOR, BLUSH_COLOR]


def apply_figure_theme(fig, *, facecolor: str = BACKGROUND_COLOR) -> None:
    fig.patch.set_facecolor(facecolor)


def apply_axis_theme(
    ax,
    *,
    facecolor: str = BACKGROUND_COLOR,
    tick_color: str = SECONDARY_COLOR,
    spine_color: str = GRID_COLOR,
    grid: bool = False,
) -> None:
    ax.set_facecolor(facecolor)
    ax.tick_params(colors=tick_color)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_color(spine_color)
    if grid:
        ax.grid(color=spine_color, alpha=0.8, linewidth=0.6)
