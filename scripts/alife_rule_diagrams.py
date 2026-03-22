#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.ca2d import parse_rulestring  # noqa: E402
from relative_symmetry_repair.experiment_suite import (  # noqa: E402
    PLOT_RC,
    ALifeCase,
    REPRESENTATIVE_CASES_1D,
    REPRESENTATIVE_CASES_2D,
    REPRESENTATIVE_CASES_3D,
    ensure_output_dir,
    scan_case_spacetime,
    shift_to_string,
    simulate_case,
    write_json_manifest,
)
from relative_symmetry_repair.alife_style import (  # noqa: E402
    ACCENT_COLOR,
    ACCENT_SOFT_COLOR,
    BACKGROUND_COLOR,
    GRID_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR as ALIFE_TEXT_COLOR,
)
from relative_symmetry_repair.plotting import (  # noqa: E402
    BINARY_CMAP,
    DEFECT_CMAP,
    DEFECT_COLOR,
    ONE_COLOR,
    ZERO_COLOR,
    save_figure,
)

DIAGRAM_HORIZONS = {
    1: 200,
    2: 400,
    3: 40,
}

PAPER_FIGURE_OVERVIEW_NAME = "alife_representative_rules.png"
PAPER_FIGURE_MECHANISMS_NAME = "alife_rule_mechanisms.png"
PAPER_FIGURE_SNIPPETS_NAME = "alife_figure_snippets.md"
PRESENTATION_GUIDE_NAME = "presentation_guide.md"

PAPER_OVERVIEW_CAPTION = (
    "Representative rules across 1D, 2D, and 3D. "
    "(A) Elementary cellular automata show the raw spacetime, the selected relative-periodic background, "
    "and the residual defect mask. "
    "(B) Representative 2D rules show early, middle, and late slices together with the selected background "
    "and the final residual mask. "
    "(C) Representative 3D rules show midplane slices through the observed spacetime, selected background, "
    "and residual mask. "
    "Across dimensions, the same selector extracts a global scaffold and isolates the structured residuals that remain."
)

PAPER_MECHANISMS_CAPTION = (
    "Local update mechanisms for the representative rule panel. "
    "(A) The studied 1D elementary rules are lookup tables on three-cell neighborhoods. "
    "(B) The studied 2D rules are totalistic Moore-neighborhood rules on eight neighbors, specified by birth and survival counts. "
    "(C) The studied 3D rules are totalistic 26-neighbor rules, again determined only by birth and survival counts. "
    "These mechanism diagrams clarify the local rule families whose global spatiotemporal organization is analyzed by the NML selector."
)

ALIFE_BG = BACKGROUND_COLOR
ALIFE_CARD = ACCENT_SOFT_COLOR
TITLE_COLOR = ACCENT_COLOR
BIRTH_COLOR = ACCENT_COLOR
SURVIVE_COLOR = SECONDARY_COLOR
CENTER_COLOR = ACCENT_SOFT_COLOR
TEXT_COLOR = ALIFE_TEXT_COLOR

RULE_NOTES = {
    "ECA-30": "Chaotic texture with little large-scale repetition; the selector still prefers a simple background.",
    "ECA-54": "Alternating domains and clearer phase locking make the periodic scaffold easier to see.",
    "ECA-110": "Drifting multi-phase lanes are visible; the best fit uses a nonzero shift to follow motion.",
    "Diamoeba": "Large breathing blobs dominate the frame and create a stronger long-horizon periodic signal.",
    "Maze with Mice": "Maze-like corridors remain coherent while local fluctuations ride on top of them.",
    "S24/B11": "Sparse patches form and dissolve, so the background captures only the broadest cadence.",
    "S11/B37": "Explosive local birth competes with fast die-out, producing noisy but still structured slices.",
    "S37/B11": "Persistent residual structure remains after fitting, making the defect mask especially informative.",
    "3d-life": "Dense midplane activity shows how a simple 3D rule can still look highly textured in projection.",
    "clouds": "High-count thresholds create bulky, cloud-like regions instead of thin fronts.",
    "crystal": "Low-count thresholds favor sparse growth and faceted, crystal-like fronts.",
    "diamoeba3d": "Large volumetric domains survive for long periods, so the midplane slices show broad coherent masses.",
}

PRESENTATION_FOCUS_RULES_1D = ("ECA-54", "ECA-110")
PRESENTATION_FOCUS_RULES_2D = ("Diamoeba", "Maze with Mice", "S37/B11")
PRESENTATION_FOCUS_RULES_3D = ("3d-life", "clouds", "diamoeba3d")
EXPORT_FORMATS: tuple[str, ...] = ()


@dataclass(slots=True)
class DiagramPayload:
    case: ALifeCase
    horizon: int
    seed: int
    spacetime: np.ndarray
    selected_period: int
    selected_shift: str
    winner_margin_bits: float
    defect_rate: float
    background: np.ndarray
    defect_mask: np.ndarray


def _rule_label(case: ALifeCase) -> str:
    if case.family == "eca":
        return f"Wolfram rule {case.rule_number}"
    if case.family == "life_rulestring":
        return str(case.rulestring)
    if case.family == "life_range":
        assert case.survive is not None and case.birth is not None
        s_lo, s_hi = case.survive
        b_lo, b_hi = case.birth
        s_text = f"S{s_lo}" if s_lo == s_hi else f"S{s_lo}-{s_hi}"
        b_text = f"B{b_lo}" if b_lo == b_hi else f"B{b_lo}-{b_hi}"
        return f"{s_text}/{b_text}"
    if case.family == "rule3d":
        assert case.survive is not None and case.birth is not None
        s_lo, s_hi = case.survive
        b_lo, b_hi = case.birth
        return f"3D S{s_lo}-{s_hi}/B{b_lo}-{b_hi}"
    raise ValueError(f"Unsupported family: {case.family}")


def _counts_for_case(case: ALifeCase) -> tuple[list[int], list[int], int]:
    if case.family == "life_rulestring":
        birth, survive = parse_rulestring(str(case.rulestring))
        return birth, survive, 8
    if case.family == "life_range":
        assert case.survive is not None and case.birth is not None
        birth = list(range(case.birth[0], case.birth[1] + 1))
        survive = list(range(case.survive[0], case.survive[1] + 1))
        return birth, survive, 8
    if case.family == "rule3d":
        assert case.survive is not None and case.birth is not None
        birth = list(range(case.birth[0], case.birth[1] + 1))
        survive = list(range(case.survive[0], case.survive[1] + 1))
        return birth, survive, 26
    raise ValueError(f"Unsupported count extraction for {case.family}")


def _note_for_case(case: ALifeCase) -> str:
    return RULE_NOTES.get(case.name, "Look for coherent domains, drift, and compact residuals.")


def _wrap_note(note: str, *, width: int = 30) -> str:
    return fill(note, width=width)


def _text_block(payload: DiagramPayload) -> str:
    note = _wrap_note(_note_for_case(payload.case), width=28)
    return "\n".join(
        [
            payload.case.name,
            _rule_label(payload.case),
            f"grid = {payload.case.size}",
            f"T = {payload.horizon}",
            f"best p = {payload.selected_period}",
            f"best s = {payload.selected_shift}",
            f"margin = {payload.winner_margin_bits:.1f} bits",
            f"defect = {payload.defect_rate:.3f}",
            "",
            "What to notice:",
            note,
        ]
    )


def _time_indices(steps: int) -> tuple[int, int, int]:
    if steps <= 1:
        return (0, 0, 0)
    return (0, steps // 2, steps - 1)


def _midplane(volume: np.ndarray) -> np.ndarray:
    z_index = volume.shape[0] // 2
    return volume[z_index]


def _max_projection(volume: np.ndarray) -> np.ndarray:
    return volume.max(axis=0)


def _focus_payloads(payloads: list[DiagramPayload], names: tuple[str, ...]) -> list[DiagramPayload]:
    lookup = {payload.case.name: payload for payload in payloads}
    return [lookup[name] for name in names if name in lookup]


def _activity_bbox(images: list[np.ndarray], *, padding: int = 2) -> tuple[int, int, int, int]:
    if not images:
        raise ValueError("images must not be empty")
    height, width = images[0].shape
    support = np.zeros((height, width), dtype=bool)
    for image in images:
        support |= np.asarray(image) != 0
    if not support.any():
        return (0, height, 0, width)
    ys, xs = np.where(support)
    y0 = max(0, int(ys.min()) - padding)
    y1 = min(height, int(ys.max()) + padding + 1)
    x0 = max(0, int(xs.min()) - padding)
    x1 = min(width, int(xs.max()) + padding + 1)
    return (y0, y1, x0, x1)


def _crop_image(image: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    y0, y1, x0, x1 = bbox
    return np.asarray(image)[y0:y1, x0:x1]


def _presentation_panel_meaning() -> str:
    return (
        "The observed panel shows the raw CA state. "
        "The background panel shows the selected relative-periodic scaffold. "
        "The defect panel shows the cells that the scaffold cannot explain."
    )


def _eca_rule_rows(rule: int) -> list[tuple[tuple[int, int, int], int]]:
    rows: list[tuple[tuple[int, int, int], int]] = []
    for pattern in range(7, -1, -1):
        bits = ((pattern >> 2) & 1, (pattern >> 1) & 1, pattern & 1)
        rows.append((bits, int((rule >> pattern) & 1)))
    return rows


def _build_payload(case: ALifeCase, *, seed: int) -> DiagramPayload:
    horizon = DIAGRAM_HORIZONS[case.dimension]
    spacetime = simulate_case(case, steps=horizon, seed=seed)
    outcome = scan_case_spacetime(case, spacetime, search=case.search, nml_mode="hybrid")
    return DiagramPayload(
        case=case,
        horizon=horizon,
        seed=seed,
        spacetime=spacetime,
        selected_period=outcome.selection.selected_period,
        selected_shift=shift_to_string(outcome.selection.selected_shift),
        winner_margin_bits=float(outcome.selection.margin_bits),
        defect_rate=float(outcome.selection.selected_defect_rate),
        background=np.asarray(outcome.best_fit.background),
        defect_mask=np.asarray(outcome.best_fit.defect_mask).astype(np.uint8),
    )


def _decorate_binary_axis(ax: plt.Axes, title: str | None = None) -> None:
    ax.set_facecolor(ALIFE_BG)
    if title:
        ax.set_title(title, fontsize=10, color=TEXT_COLOR)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _save_diagram(fig, path: Path) -> None:
    fig.patch.set_facecolor(ALIFE_BG)
    for ax in fig.axes:
        ax.set_facecolor(ALIFE_BG)
    save_figure(fig, path, extra_formats=EXPORT_FORMATS)


def _plot_1d_overview(payloads: list[DiagramPayload], path: Path) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(payloads),
            4,
            figsize=(15.0, 3.0 * len(payloads)),
            gridspec_kw={"width_ratios": [2.2, 2.5, 2.5, 2.5]},
        )
        if len(payloads) == 1:
            axes = np.asarray([axes])

        headers = ["Rule", "Observed spacetime", "Selected background", "Defect mask"]
        for col, header in enumerate(headers):
            if col == 0:
                axes[0, col].set_title(header, fontsize=11)
            else:
                axes[0, col].set_title(header, fontsize=11)

        for row, payload in enumerate(payloads):
            text_ax = axes[row, 0]
            text_ax.axis("off")
            text_ax.text(
                0.0,
                0.5,
                _text_block(payload),
                ha="left",
                va="center",
                fontsize=9.1,
                color=TEXT_COLOR,
                linespacing=1.35,
            )

            images = [
                payload.spacetime,
                payload.background,
                payload.defect_mask.astype(np.uint8),
            ]
            for col, image in enumerate(images, start=1):
                ax = axes[row, col]
                cmap = DEFECT_CMAP if col == 3 else BINARY_CMAP
                ax.imshow(image, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=1)
                _decorate_binary_axis(ax)

        fig.suptitle(
            "Representative 1D rules: raw evolution, selected background, and what the fit leaves behind",
            fontsize=13,
            y=0.995,
            color=TITLE_COLOR,
        )
        fig.text(
            0.5,
            0.012,
            "Use these as reading panels: first see the raw texture, then the fitted scaffold, then the residual structure in red.",
            ha="center",
            va="bottom",
            fontsize=9,
            color=TEXT_COLOR,
        )
        fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.97))
        _save_diagram(fig, path)
        plt.close(fig)


def _extract_slice(payload: DiagramPayload, time_index: int) -> np.ndarray:
    if payload.case.dimension == 3:
        return _midplane(payload.spacetime[time_index])
    return payload.spacetime[time_index]


def _extract_background_slice(payload: DiagramPayload, time_index: int) -> np.ndarray:
    if payload.case.dimension == 3:
        return _midplane(payload.background[time_index])
    return payload.background[time_index]


def _extract_defect_slice(payload: DiagramPayload, time_index: int) -> np.ndarray:
    if payload.case.dimension == 3:
        return _midplane(payload.defect_mask[time_index].astype(np.uint8))
    return payload.defect_mask[time_index].astype(np.uint8)


def _extract_projection(payload: DiagramPayload, time_index: int) -> np.ndarray:
    if payload.case.dimension != 3:
        raise ValueError("projection view is only defined for 3D payloads")
    return _max_projection(payload.spacetime[time_index])


def _extract_background_projection(payload: DiagramPayload, time_index: int) -> np.ndarray:
    if payload.case.dimension != 3:
        raise ValueError("projection view is only defined for 3D payloads")
    return _max_projection(payload.background[time_index])


def _extract_defect_projection(payload: DiagramPayload, time_index: int) -> np.ndarray:
    if payload.case.dimension != 3:
        raise ValueError("projection view is only defined for 3D payloads")
    return _max_projection(payload.defect_mask[time_index].astype(np.uint8))


def _plot_nd_overview(payloads: list[DiagramPayload], *, title: str, caption: str, path: Path) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(payloads),
            6,
            figsize=(18.0, 3.0 * len(payloads)),
            gridspec_kw={"width_ratios": [2.1, 2.0, 2.0, 2.0, 2.0, 2.0]},
        )
        if len(payloads) == 1:
            axes = np.asarray([axes])

        headers = ["Rule", "t = 0", "t = mid", "t = last", "Background at last", "Defect at last"]
        for col, header in enumerate(headers):
            axes[0, col].set_title(header, fontsize=11)

        for row, payload in enumerate(payloads):
            text_ax = axes[row, 0]
            text_ax.axis("off")
            text_ax.text(
                0.0,
                0.5,
                _text_block(payload),
                ha="left",
                va="center",
                fontsize=8.9,
                color=TEXT_COLOR,
                linespacing=1.34,
            )

            t0, t_mid, t_last = _time_indices(payload.spacetime.shape[0])
            images = [
                _extract_slice(payload, t0),
                _extract_slice(payload, t_mid),
                _extract_slice(payload, t_last),
                _extract_background_slice(payload, t_last),
                _extract_defect_slice(payload, t_last),
            ]

            for col, image in enumerate(images, start=1):
                ax = axes[row, col]
                cmap = DEFECT_CMAP if col == 5 else BINARY_CMAP
                ax.imshow(image, interpolation="nearest", cmap=cmap, vmin=0, vmax=1)
                _decorate_binary_axis(ax)

        fig.suptitle(title, fontsize=13, y=0.995, color=TITLE_COLOR)
        fig.text(0.5, 0.012, caption, ha="center", va="bottom", fontsize=9, color=TEXT_COLOR)
        fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.97))
        _save_diagram(fig, path)
        plt.close(fig)


def _presentation_text_block(payload: DiagramPayload) -> str:
    note = _wrap_note(_note_for_case(payload.case), width=34)
    return "\n".join(
        [
            payload.case.name,
            _rule_label(payload.case),
            f"The selected winner is ({payload.selected_period}, {payload.selected_shift}).",
            f"The margin is {payload.winner_margin_bits:.1f} bits, and the defect rate is {payload.defect_rate:.3f}.",
            "",
            "The observed panel shows the raw state.",
            "The background panel shows the fitted scaffold.",
            "The defect panel shows the residual cells.",
            "",
            "Why this rule matters:",
            note,
        ]
    )


def _plot_presentation_1d(payloads: list[DiagramPayload], path: Path) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(payloads),
            4,
            figsize=(16.5, 4.2 * len(payloads)),
            gridspec_kw={"width_ratios": [2.6, 3.2, 3.2, 3.2]},
        )
        if len(payloads) == 1:
            axes = np.asarray([axes])

        headers = ["Rule", "Observed\n(raw spacetime)", "Background\n(selected scaffold)", "Defect\n(what the fit misses)"]
        for col, header in enumerate(headers):
            axes[0, col].set_title(header, fontsize=12)

        for row, payload in enumerate(payloads):
            info_ax = axes[row, 0]
            info_ax.axis("off")
            info_ax.text(
                0.0,
                0.5,
                _presentation_text_block(payload),
                ha="left",
                va="center",
                fontsize=9.7,
                color=TEXT_COLOR,
                linespacing=1.35,
            )
            panels = [
                payload.spacetime,
                payload.background,
                payload.defect_mask.astype(np.uint8),
            ]
            for col, image in enumerate(panels, start=1):
                ax = axes[row, col]
                cmap = DEFECT_CMAP if col == 3 else BINARY_CMAP
                ax.imshow(image, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=1)
                _decorate_binary_axis(ax)

        fig.suptitle(
            "Presentation set: 1D rules with clear periodic structure or drift",
            fontsize=14,
            y=0.995,
            color=TITLE_COLOR,
        )
        fig.text(
            0.5,
            0.014,
            _presentation_panel_meaning() + " In 1D, diagonal lanes make the role of the shift parameter easiest to see.",
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=TEXT_COLOR,
        )
        fig.tight_layout(rect=(0.0, 0.045, 1.0, 0.975))
        _save_diagram(fig, path)
        plt.close(fig)


def _plot_presentation_2d(payloads: list[DiagramPayload], path: Path) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(payloads),
            6,
            figsize=(18.5, 4.0 * len(payloads)),
            gridspec_kw={"width_ratios": [2.5, 3.0, 3.0, 3.0, 3.0, 3.0]},
        )
        if len(payloads) == 1:
            axes = np.asarray([axes])

        headers = [
            "Rule",
            "Observed t = 0",
            "Observed t = mid",
            "Observed t = last",
            "Background at last",
            "Defect at last",
        ]
        for col, header in enumerate(headers):
            axes[0, col].set_title(header, fontsize=12)

        for row, payload in enumerate(payloads):
            info_ax = axes[row, 0]
            info_ax.axis("off")
            info_ax.text(
                0.0,
                0.5,
                _presentation_text_block(payload),
                ha="left",
                va="center",
                fontsize=9.4,
                color=TEXT_COLOR,
                linespacing=1.34,
            )

            t0, t_mid, t_last = _time_indices(payload.spacetime.shape[0])
            raw0 = payload.spacetime[t0]
            raw_mid = payload.spacetime[t_mid]
            raw_last = payload.spacetime[t_last]
            background_last = payload.background[t_last]
            defect_last = payload.defect_mask[t_last].astype(np.uint8)
            bbox = _activity_bbox([raw0, raw_mid, raw_last, background_last, defect_last], padding=4)
            images = [
                _crop_image(raw0, bbox),
                _crop_image(raw_mid, bbox),
                _crop_image(raw_last, bbox),
                _crop_image(background_last, bbox),
                _crop_image(defect_last, bbox),
            ]
            for col, image in enumerate(images, start=1):
                ax = axes[row, col]
                cmap = DEFECT_CMAP if col == 5 else BINARY_CMAP
                ax.imshow(image, interpolation="nearest", cmap=cmap, vmin=0, vmax=1)
                _decorate_binary_axis(ax)

        fig.suptitle(
            "Presentation set: 2D rules cropped around the active region",
            fontsize=14,
            y=0.995,
            color=TITLE_COLOR,
        )
        fig.text(
            0.5,
            0.014,
            _presentation_panel_meaning() + " These panels are cropped to the active region so that the domains and residual structures read more clearly.",
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=TEXT_COLOR,
        )
        fig.tight_layout(rect=(0.0, 0.045, 1.0, 0.975))
        _save_diagram(fig, path)
        plt.close(fig)


def _plot_presentation_3d(payloads: list[DiagramPayload], path: Path) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(payloads),
            6,
            figsize=(18.5, 4.0 * len(payloads)),
            gridspec_kw={"width_ratios": [2.5, 3.0, 3.0, 3.0, 3.0, 3.0]},
        )
        if len(payloads) == 1:
            axes = np.asarray([axes])

        headers = [
            "Rule",
            "Observed projection t = 0",
            "Observed projection t = mid",
            "Observed projection t = last",
            "Background projection at last",
            "Defect projection at last",
        ]
        for col, header in enumerate(headers):
            axes[0, col].set_title(header, fontsize=12)

        for row, payload in enumerate(payloads):
            info_ax = axes[row, 0]
            info_ax.axis("off")
            info_ax.text(
                0.0,
                0.5,
                _presentation_text_block(payload) + "\n\n3D view: max projection over z",
                ha="left",
                va="center",
                fontsize=9.3,
                color=TEXT_COLOR,
                linespacing=1.32,
            )

            t0, t_mid, t_last = _time_indices(payload.spacetime.shape[0])
            raw0 = _extract_projection(payload, t0)
            raw_mid = _extract_projection(payload, t_mid)
            raw_last = _extract_projection(payload, t_last)
            background_last = _extract_background_projection(payload, t_last)
            defect_last = _extract_defect_projection(payload, t_last)
            bbox = _activity_bbox([raw0, raw_mid, raw_last, background_last, defect_last], padding=3)
            images = [
                _crop_image(raw0, bbox),
                _crop_image(raw_mid, bbox),
                _crop_image(raw_last, bbox),
                _crop_image(background_last, bbox),
                _crop_image(defect_last, bbox),
            ]
            for col, image in enumerate(images, start=1):
                ax = axes[row, col]
                cmap = DEFECT_CMAP if col == 5 else BINARY_CMAP
                ax.imshow(image, interpolation="nearest", cmap=cmap, vmin=0, vmax=1)
                _decorate_binary_axis(ax)

        fig.suptitle(
            "Presentation set: 3D rules shown as max projections",
            fontsize=14,
            y=0.995,
            color=TITLE_COLOR,
        )
        fig.text(
            0.5,
            0.014,
            _presentation_panel_meaning() + " Max projections make volumetric structure less likely to disappear in a single flat midplane slice.",
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=TEXT_COLOR,
        )
        fig.tight_layout(rect=(0.0, 0.045, 1.0, 0.975))
        _save_diagram(fig, path)
        plt.close(fig)


def _draw_count_strip(
    ax: plt.Axes,
    *,
    counts: list[int],
    max_neighbors: int,
    y: float,
    color: str,
    label: str,
) -> None:
    for count in range(max_neighbors + 1):
        active = count in counts
        rect = Rectangle(
            (count - 0.45, y - 0.35),
            0.9,
            0.7,
            facecolor=color if active else ZERO_COLOR,
            edgecolor=GRID_COLOR,
            linewidth=0.8,
        )
        ax.add_patch(rect)
    ax.text(-1.2, y, label, ha="right", va="center", fontsize=9, color=TEXT_COLOR)


def _draw_count_rule(ax: plt.Axes, *, birth: list[int], survive: list[int], max_neighbors: int) -> None:
    ax.set_xlim(-1.8, max_neighbors + 0.8)
    ax.set_ylim(-0.8, 1.6)
    _draw_count_strip(ax, counts=birth, max_neighbors=max_neighbors, y=1.0, color=BIRTH_COLOR, label="birth")
    _draw_count_strip(ax, counts=survive, max_neighbors=max_neighbors, y=0.0, color=SURVIVE_COLOR, label="survive")

    ticks = list(range(max_neighbors + 1))
    ax.set_xticks(ticks)
    if max_neighbors <= 8:
        ax.set_xticklabels([str(value) for value in ticks], fontsize=8)
    else:
        labels = [str(value) if value % 2 == 0 or value == max_neighbors else "" for value in ticks]
        ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticks([])
    ax.set_xlabel("live-neighbor count", fontsize=9)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.set_title("Local threshold rule", fontsize=10, color=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="x", length=0, colors=TEXT_COLOR)


def _draw_2d_neighborhood(ax: plt.Axes) -> None:
    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(-0.6, 2.6)
    for y in range(3):
        for x in range(3):
            face = CENTER_COLOR if (x, y) == (1, 1) else ZERO_COLOR
            rect = Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, facecolor=face, edgecolor=GRID_COLOR, linewidth=0.9)
            ax.add_patch(rect)
    ax.text(1.0, 1.0, "cell", ha="center", va="center", fontsize=8, color=TEXT_COLOR)
    ax.text(1.0, -0.38, "count live neighbors in the 8 surrounding cells", ha="center", va="top", fontsize=8.5, color=TEXT_COLOR)
    ax.set_title("2D Moore neighborhood", fontsize=10, color=TEXT_COLOR)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_aspect("equal")


def _draw_3d_neighborhood(ax: plt.Axes) -> None:
    def draw_layer(x_offset: float, layer_label: str, center: bool) -> None:
        for y in range(3):
            for x in range(3):
                is_center = center and (x, y) == (1, 1)
                face = CENTER_COLOR if is_center else ZERO_COLOR
                rect = Rectangle(
                    (x_offset + x - 0.4, y - 0.4),
                    0.8,
                    0.8,
                    facecolor=face,
                    edgecolor=GRID_COLOR,
                    linewidth=0.8,
                )
                ax.add_patch(rect)
        ax.text(x_offset + 1.0, 2.95, layer_label, ha="center", va="bottom", fontsize=8.5, color=TEXT_COLOR)

    ax.set_xlim(-0.8, 9.0)
    ax.set_ylim(-0.6, 3.4)
    draw_layer(0.0, "z - 1", center=False)
    draw_layer(3.2, "z", center=True)
    draw_layer(6.4, "z + 1", center=False)
    ax.text(4.2, -0.28, "count all live voxels except the center cell = 26 neighbors", ha="center", va="top", fontsize=8.3, color=TEXT_COLOR)
    ax.set_title("3D Moore neighborhood", fontsize=10, color=TEXT_COLOR)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_aspect("equal")


def _draw_eca_table(ax: plt.Axes, rule: int) -> None:
    rows = _eca_rule_rows(rule)
    grid = np.array([[*bits, out] for bits, out in rows], dtype=np.uint8)
    ax.imshow(grid, cmap=BINARY_CMAP, vmin=0, vmax=1, aspect="equal", interpolation="nearest")
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["L", "C", "R", "next"], fontsize=8)
    ax.xaxis.tick_top()
    ax.set_yticks(range(8))
    ax.set_yticklabels([f"{bits[0]}{bits[1]}{bits[2]}" for bits, _ in rows], fontsize=8)
    ax.axvline(2.5, color=GRID_COLOR, linewidth=1.2)
    ax.set_title(f"Local update table for rule {rule}", fontsize=10, color=TEXT_COLOR)
    ax.set_xticks(np.arange(-0.5, 4.0, 1.0), minor=True)
    ax.set_yticks(np.arange(-0.5, 8.0, 1.0), minor=True)
    ax.grid(which="minor", color=GRID_COLOR, linewidth=0.8)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def _plot_1d_mechanisms(cases: tuple[ALifeCase, ...], path: Path) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(cases),
            2,
            figsize=(12.0, 2.8 * len(cases)),
            gridspec_kw={"width_ratios": [1.8, 3.0]},
        )
        if len(cases) == 1:
            axes = np.asarray([axes])

        axes[0, 0].set_title("Rule", fontsize=11)
        axes[0, 1].set_title("Mechanism", fontsize=11)

        for row, case in enumerate(cases):
            text_ax = axes[row, 0]
            text_ax.axis("off")
            text_ax.text(
                0.0,
                0.5,
                "\n".join(
                    [
                        case.name,
                        _rule_label(case),
                        "",
                        _wrap_note(_note_for_case(case), width=28),
                    ]
                ),
                ha="left",
                va="center",
                fontsize=9.4,
                color=TEXT_COLOR,
                linespacing=1.38,
            )
            _draw_eca_table(axes[row, 1], int(case.rule_number))

        fig.suptitle(
            "1D representative rules: each Wolfram rule is just an 8-row lookup table on three-cell neighborhoods",
            fontsize=13,
            y=0.995,
            color=TITLE_COLOR,
        )
        fig.text(
            0.5,
            0.012,
            "Read each row left to right: a three-cell neighborhood on the ring maps to the next-state value in the final column.",
            ha="center",
            va="bottom",
            fontsize=9,
            color=TEXT_COLOR,
        )
        fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.97))
        _save_diagram(fig, path)
        plt.close(fig)


def _plot_totalistic_mechanisms(
    cases: tuple[ALifeCase, ...],
    *,
    title: str,
    caption: str,
    path: Path,
    neighborhood_kind: str,
) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 8}):
        fig, axes = plt.subplots(
            len(cases),
            3,
            figsize=(14.5, 2.8 * len(cases)),
            gridspec_kw={"width_ratios": [1.9, 2.0, 3.2]},
        )
        if len(cases) == 1:
            axes = np.asarray([axes])

        headers = ["Rule", "Neighborhood geometry", "Birth and survival counts"]
        for col, header in enumerate(headers):
            axes[0, col].set_title(header, fontsize=11)

        for row, case in enumerate(cases):
            birth, survive, max_neighbors = _counts_for_case(case)

            text_ax = axes[row, 0]
            text_ax.axis("off")
            text_ax.text(
                0.0,
                0.5,
                "\n".join(
                    [
                        case.name,
                        _rule_label(case),
                        "",
                        _wrap_note(_note_for_case(case), width=28),
                    ]
                ),
                ha="left",
                va="center",
                fontsize=9.2,
                color=TEXT_COLOR,
                linespacing=1.36,
            )

            if neighborhood_kind == "2d":
                _draw_2d_neighborhood(axes[row, 1])
            else:
                _draw_3d_neighborhood(axes[row, 1])

            _draw_count_rule(axes[row, 2], birth=birth, survive=survive, max_neighbors=max_neighbors)

        fig.suptitle(title, fontsize=13, y=0.995, color=TITLE_COLOR)
        fig.text(0.5, 0.012, caption, ha="center", va="bottom", fontsize=9, color=TEXT_COLOR)
        fig.tight_layout(rect=(0.0, 0.04, 1.0, 0.97))
        _save_diagram(fig, path)
        plt.close(fig)


def _write_rule_diagram_guide(
    output_dir: Path,
    *,
    payloads_1d: list[DiagramPayload],
    payloads_2d: list[DiagramPayload],
    payloads_3d: list[DiagramPayload],
) -> Path:
    guide_path = output_dir / "guide.md"

    def bullet_lines(payloads: list[DiagramPayload]) -> list[str]:
        lines: list[str] = []
        for payload in payloads:
            lines.append(
                f"- `{payload.case.name}`: best `(p, s) = ({payload.selected_period}, {payload.selected_shift})`, "
                f"margin `{payload.winner_margin_bits:.1f}` bits, defect rate `{payload.defect_rate:.3f}`. "
                f"{_note_for_case(payload.case)}"
            )
        return lines

    lines = [
        "# Rule Diagram Guide",
        "",
        "These figures are discussion aids for the representative ALIFE rules. They are meant to be used alongside the theorem and method notes in `paper/paper_talking_points.md`.",
        "",
        "## Files",
        "",
        "- `representative_rules_1d.png`: observed 1D spacetimes, selected backgrounds, and residual masks.",
        "- `representative_rules_2d.png`: early, middle, late, selected-background, and residual slices for the 2D panel.",
        "- `representative_rules_3d.png`: midplane slices through the 3D panel with selected-background and residual views.",
        "- `rule_mechanisms_1d.png`: lookup-table view of the studied elementary rules.",
        "- `rule_mechanisms_2d.png`: Moore-neighborhood plus birth/survival count diagrams for the studied 2D rules.",
        "- `rule_mechanisms_3d.png`: 3D Moore-neighborhood plus birth/survival count diagrams for the studied 3D rules.",
        "- `presentation_rules_1d.png`: larger 1D presentation figure with fewer, more legible rules.",
        "- `presentation_rules_2d.png`: larger 2D presentation figure cropped around active regions.",
        "- `presentation_rules_3d.png`: larger 3D presentation figure using max projections instead of only a midplane.",
        "- `presentation_guide.md`: plain-language explanation of what each presentation diagram means.",
        "- `paper/figures/alife_representative_rules.png`: composite manuscript-ready version of the three overview panels.",
        "- `paper/figures/alife_rule_mechanisms.png`: composite manuscript-ready version of the three mechanism panels.",
        "- `paper/alife_figure_snippets.md`: ready-to-paste captions and labels.",
        "",
        "## Recommended explanation order",
        "",
        "1. Start with the mechanism figures. They explain what the local update rule is actually doing.",
        "2. Move to the representative evolution panels. They show what those local rules look like at the scale of an entire spacetime.",
        "3. Use the background and defect columns to explain the paper's decomposition idea: the selector finds a global scaffold, then studies what is left over.",
        "",
        "## How to read the colors",
        "",
        f"- Light cells use `{ZERO_COLOR}` and mean value `0`.",
        f"- Dark cells use `{ONE_COLOR}` and mean value `1`.",
        f"- Red cells use `{DEFECT_COLOR}` and mark disagreement with the selected relative-periodic background.",
        f"- In mechanism figures, `{BIRTH_COLOR}` marks birth counts and `{SURVIVE_COLOR}` marks survival counts.",
        "",
        "## Representative 1D rules",
        "",
        *bullet_lines(payloads_1d),
        "",
        "## Representative 2D rules",
        "",
        *bullet_lines(payloads_2d),
        "",
        "## Representative 3D rules",
        "",
        *bullet_lines(payloads_3d),
        "",
        "## Suggested talking points",
        "",
        "- The mechanism figures explain the rule itself. The overview figures explain the global behavior that the selector is trying to summarize.",
        "- In 1D, the shift parameter is easiest to explain because diagonal motion is visually obvious.",
        "- In 2D and 3D, the defect masks are often more informative than the raw slices because they separate the fitted scaffold from the persistent irregular structures.",
        "- Use high-margin cases to explain stabilization. Use noisy or low-structure cases to explain why period 1 often wins.",
        "",
    ]
    guide_path.write_text("\n".join(lines) + "\n")
    return guide_path


def _write_presentation_guide(
    output_dir: Path,
    *,
    payloads_1d: list[DiagramPayload],
    payloads_2d: list[DiagramPayload],
    payloads_3d: list[DiagramPayload],
) -> Path:
    guide_path = output_dir / PRESENTATION_GUIDE_NAME

    def block(title: str, payloads: list[DiagramPayload]) -> list[str]:
        lines = [f"## {title}", ""]
        for payload in payloads:
            lines.extend(
                [
                    f"### {payload.case.name}",
                    "",
                    f"- Selected winner: `(p, s) = ({payload.selected_period}, {payload.selected_shift})`",
                    f"- Winner margin: `{payload.winner_margin_bits:.1f}` bits",
                    f"- Defect rate: `{payload.defect_rate:.3f}`",
                    f"- What the observed panel means: the raw CA state before any decomposition.",
                    f"- What the background panel means: the periodic scaffold chosen by the selector.",
                    f"- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.",
                    f"- Why this rule is in the presentation set: {_note_for_case(payload.case)}",
                    "",
                ]
            )
        return lines

    lines = [
        "# Presentation Diagram Guide",
        "",
        "This note exists for the less-flat presentation figure set. Use it when you want to show only the most interpretable rules at larger scale.",
        "",
        "## Files",
        "",
        "- `presentation_rules_1d.png`: larger 1D presentation panel.",
        "- `presentation_rules_2d.png`: larger 2D presentation panel, cropped around the active region.",
        "- `presentation_rules_3d.png`: larger 3D presentation panel using max projections rather than a single midplane slice.",
        "",
        "## What the three panel types mean",
        "",
        "- `Observed`: the raw cellular automaton state.",
        "- `Background`: the selected relative-periodic scaffold found by the period-first Bernoulli-NML selector.",
        "- `Defect`: the mismatch between the raw state and that scaffold.",
        "",
        "## Why these should look less flat",
        "",
        "- The 2D presentation panels are cropped to the active region instead of showing the full torus.",
        "- The 3D presentation panels use max projections, so more volumetric structure survives the visualization.",
        "- The rule list is smaller and biased toward visually stronger cases.",
        "",
        *block("1D presentation rules", payloads_1d),
        *block("2D presentation rules", payloads_2d),
        *block("3D presentation rules", payloads_3d),
    ]
    guide_path.write_text("\n".join(lines) + "\n")
    return guide_path


def _compose_paper_figure(
    panel_paths: list[Path],
    *,
    panel_titles: list[str],
    panel_labels: list[str],
    path: Path,
) -> None:
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 6}):
        fig, axes = plt.subplots(len(panel_paths), 1, figsize=(9.0, 12.5))
        if len(panel_paths) == 1:
            axes = np.asarray([axes])

        for index, (ax, panel_path, panel_title, panel_label) in enumerate(zip(axes, panel_paths, panel_titles, panel_labels)):
            image = plt.imread(panel_path)
            ax.imshow(image)
            ax.axis("off")
            ax.text(
                0.01,
                0.98,
                panel_label,
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=13,
                fontweight="bold",
                color=TEXT_COLOR,
                bbox={
                    "facecolor": ALIFE_CARD,
                    "edgecolor": "none",
                    "boxstyle": "round,pad=0.25",
                    "alpha": 0.92,
                },
            )
            ax.text(
                0.11,
                0.98,
                panel_title,
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=10,
                color=TEXT_COLOR,
                bbox={
                    "facecolor": ALIFE_CARD,
                    "edgecolor": "none",
                    "boxstyle": "round,pad=0.25",
                    "alpha": 0.92,
                },
            )
            if index < len(panel_paths) - 1:
                ax.plot([0.0, 1.0], [0.0, 0.0], transform=ax.transAxes, color=GRID_COLOR, linewidth=1.0)

        fig.tight_layout(rect=(0.0, 0.0, 1.0, 1.0))
        _save_diagram(fig, path)
        plt.close(fig)


def _write_paper_figure_snippets(paper_dir: Path, *, figure_dir: Path) -> Path:
    snippets_path = paper_dir / PAPER_FIGURE_SNIPPETS_NAME
    overview_rel = f"figures/{PAPER_FIGURE_OVERVIEW_NAME}"
    mechanisms_rel = f"figures/{PAPER_FIGURE_MECHANISMS_NAME}"
    lines = [
        "# ALIFE figure snippets",
        "",
        "## Figure 1",
        "",
        f"File: `{overview_rel}`",
        "",
        "Label: `fig:alife-representative-rules`",
        "",
        "Caption:",
        "",
        PAPER_OVERVIEW_CAPTION,
        "",
        "LaTeX:",
        "",
        "```tex",
        "\\begin{figure}[t]",
        "  \\centering",
        f"  \\includegraphics[width=\\linewidth]{{{overview_rel}}}",
        f"  \\caption{{{PAPER_OVERVIEW_CAPTION}}}",
        "  \\label{fig:alife-representative-rules}",
        "\\end{figure}",
        "```",
        "",
        "Markdown:",
        "",
        f"![Representative rules across 1D, 2D, and 3D.]({overview_rel})",
        "",
        "*Figure label suggestion: `fig:alife-representative-rules`*",
        "",
        "## Figure 2",
        "",
        f"File: `{mechanisms_rel}`",
        "",
        "Label: `fig:alife-rule-mechanisms`",
        "",
        "Caption:",
        "",
        PAPER_MECHANISMS_CAPTION,
        "",
        "LaTeX:",
        "",
        "```tex",
        "\\begin{figure}[t]",
        "  \\centering",
        f"  \\includegraphics[width=\\linewidth]{{{mechanisms_rel}}}",
        f"  \\caption{{{PAPER_MECHANISMS_CAPTION}}}",
        "  \\label{fig:alife-rule-mechanisms}",
        "\\end{figure}",
        "```",
        "",
        "Markdown:",
        "",
        f"![Local update mechanisms for the representative rule panel.]({mechanisms_rel})",
        "",
        "*Figure label suggestion: `fig:alife-rule-mechanisms`*",
        "",
    ]
    snippets_path.write_text("\n".join(lines) + "\n")
    return snippets_path


def build_rule_diagrams(output_root: Path, *, base_seed: int, paper_dir: Path) -> dict[str, object]:
    output_dir = ensure_output_dir(output_root / "rule_diagrams")
    paper_dir = ensure_output_dir(paper_dir)
    paper_figure_dir = ensure_output_dir(paper_dir / "figures")

    payloads_1d = [_build_payload(case, seed=base_seed) for case in REPRESENTATIVE_CASES_1D]
    payloads_2d = [_build_payload(case, seed=base_seed) for case in REPRESENTATIVE_CASES_2D]
    payloads_3d = [_build_payload(case, seed=base_seed) for case in REPRESENTATIVE_CASES_3D]

    overview_1d_path = output_dir / "representative_rules_1d.png"
    overview_2d_path = output_dir / "representative_rules_2d.png"
    overview_3d_path = output_dir / "representative_rules_3d.png"
    mechanisms_1d_path = output_dir / "rule_mechanisms_1d.png"
    mechanisms_2d_path = output_dir / "rule_mechanisms_2d.png"
    mechanisms_3d_path = output_dir / "rule_mechanisms_3d.png"
    presentation_1d_path = output_dir / "presentation_rules_1d.png"
    presentation_2d_path = output_dir / "presentation_rules_2d.png"
    presentation_3d_path = output_dir / "presentation_rules_3d.png"

    _plot_1d_overview(payloads_1d, overview_1d_path)
    _plot_nd_overview(
        payloads_2d,
        title="Representative 2D rules: evolution, fitted scaffold, and residual structure",
        caption="Read left to right: how the pattern starts, how it develops, what the selected background keeps, and what it cannot explain.",
        path=overview_2d_path,
    )
    _plot_nd_overview(
        payloads_3d,
        title="Representative 3D rules: midplane slices through the studied rule panel",
        caption="The 3D panels show central slices only, so use them as structural summaries rather than full volumetric renderings.",
        path=overview_3d_path,
    )
    _plot_1d_mechanisms(REPRESENTATIVE_CASES_1D, mechanisms_1d_path)
    _plot_totalistic_mechanisms(
        REPRESENTATIVE_CASES_2D,
        title="Representative 2D rules: each rule depends only on the 8-neighbor live count",
        caption="Birth and survival rows show which neighbor counts keep a cell alive or create a new one.",
        path=mechanisms_2d_path,
        neighborhood_kind="2d",
    )
    _plot_totalistic_mechanisms(
        REPRESENTATIVE_CASES_3D,
        title="Representative 3D rules: 26-neighbor count rules on a 3-torus",
        caption="The 3D rules are still totalistic: only the live-neighbor count matters, not the detailed arrangement.",
        path=mechanisms_3d_path,
        neighborhood_kind="3d",
    )

    presentation_payloads_1d = _focus_payloads(payloads_1d, PRESENTATION_FOCUS_RULES_1D)
    presentation_payloads_2d = _focus_payloads(payloads_2d, PRESENTATION_FOCUS_RULES_2D)
    presentation_payloads_3d = _focus_payloads(payloads_3d, PRESENTATION_FOCUS_RULES_3D)

    _plot_presentation_1d(presentation_payloads_1d, presentation_1d_path)
    _plot_presentation_2d(presentation_payloads_2d, presentation_2d_path)
    _plot_presentation_3d(presentation_payloads_3d, presentation_3d_path)

    guide_path = _write_rule_diagram_guide(
        output_dir,
        payloads_1d=payloads_1d,
        payloads_2d=payloads_2d,
        payloads_3d=payloads_3d,
    )
    presentation_guide_path = _write_presentation_guide(
        output_dir,
        payloads_1d=presentation_payloads_1d,
        payloads_2d=presentation_payloads_2d,
        payloads_3d=presentation_payloads_3d,
    )
    paper_overview_path = paper_figure_dir / PAPER_FIGURE_OVERVIEW_NAME
    paper_mechanisms_path = paper_figure_dir / PAPER_FIGURE_MECHANISMS_NAME
    _compose_paper_figure(
        [overview_1d_path, overview_2d_path, overview_3d_path],
        panel_titles=["1D representative rules", "2D representative rules", "3D representative rules"],
        panel_labels=["A", "B", "C"],
        path=paper_overview_path,
    )
    _compose_paper_figure(
        [mechanisms_1d_path, mechanisms_2d_path, mechanisms_3d_path],
        panel_titles=["1D local rule tables", "2D birth/survival rules", "3D birth/survival rules"],
        panel_labels=["A", "B", "C"],
        path=paper_mechanisms_path,
    )
    snippets_path = _write_paper_figure_snippets(paper_dir, figure_dir=paper_figure_dir)

    manifest = {
        "output_dir": str(output_dir.resolve()),
        "paper_dir": str(paper_dir.resolve()),
        "base_seed": int(base_seed),
        "export_formats": ["png", *EXPORT_FORMATS],
        "horizons": {str(key): int(value) for key, value in DIAGRAM_HORIZONS.items()},
        "files": {
            "overview_1d": str(overview_1d_path.resolve()),
            "overview_2d": str(overview_2d_path.resolve()),
            "overview_3d": str(overview_3d_path.resolve()),
            "mechanisms_1d": str(mechanisms_1d_path.resolve()),
            "mechanisms_2d": str(mechanisms_2d_path.resolve()),
            "mechanisms_3d": str(mechanisms_3d_path.resolve()),
            "presentation_1d": str(presentation_1d_path.resolve()),
            "presentation_2d": str(presentation_2d_path.resolve()),
            "presentation_3d": str(presentation_3d_path.resolve()),
            "guide": str(guide_path.resolve()),
            "presentation_guide": str(presentation_guide_path.resolve()),
            "paper_overview": str(paper_overview_path.resolve()),
            "paper_mechanisms": str(paper_mechanisms_path.resolve()),
            "paper_snippets": str(snippets_path.resolve()),
        },
        "legend": {
            "zero": ZERO_COLOR,
            "one": ONE_COLOR,
            "defect": DEFECT_COLOR,
            "birth": BIRTH_COLOR,
            "survive": SURVIVE_COLOR,
        },
    }
    write_json_manifest(output_dir / "manifest.json", manifest)
    return manifest


def main() -> None:
    global EXPORT_FORMATS
    parser = argparse.ArgumentParser(description="Render manuscript-friendly overview and mechanism diagrams for the representative ALIFE rules.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--base-seed", type=int, default=11)
    parser.add_argument("--paper-dir", type=Path, default=ROOT / "paper")
    parser.add_argument(
        "--export-formats",
        type=str,
        default="png",
        help="Comma-separated formats to write for generated figures, e.g. png,pdf,svg",
    )
    args = parser.parse_args()

    requested_formats = tuple(
        fmt.strip().lower().lstrip(".")
        for fmt in args.export_formats.split(",")
        if fmt.strip()
    )
    EXPORT_FORMATS = tuple(fmt for fmt in requested_formats if fmt != "png")

    manifest = build_rule_diagrams(args.output_root, base_seed=args.base_seed, paper_dir=args.paper_dir)
    print(f"Wrote rule diagrams to {manifest['output_dir']}")


if __name__ == "__main__":
    main()
