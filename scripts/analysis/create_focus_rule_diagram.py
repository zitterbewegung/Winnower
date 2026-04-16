#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.alife_style import ACCENT_COLOR, BACKGROUND_COLOR, TEXT_COLOR  # noqa: E402
from relative_symmetry_repair.experiment_suite import (  # noqa: E402
    PLOT_RC,
    REPRESENTATIVE_CASES_1D,
    REPRESENTATIVE_CASES_2D,
    REPRESENTATIVE_CASES_3D,
    ensure_output_dir,
    shift_to_string,
    simulate_case,
)
from relative_symmetry_repair.plotting import BINARY_CMAP, DEFECT_CMAP, DEFECT_COLOR, save_figure  # noqa: E402
from relative_symmetry_repair.repair import fit_relative_periodic_background  # noqa: E402
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd  # noqa: E402


SEED = 42
STABILIZATION_RESULTS = ROOT / "outputs" / "csv" / "stabilization_results.csv"


@dataclass(frozen=True)
class FocusRule:
    case_name: str
    display_name: str
    rule_label: str
    finding: str
    view_kind: str


@dataclass(frozen=True)
class SelectionRecord:
    horizon: int
    period: int
    shift: int | tuple[int, ...]
    margin_bits: float


@dataclass(frozen=True)
class RenderPayload:
    focus: FocusRule
    horizon: int
    period: int
    shift: int | tuple[int, ...]
    margin_bits: float
    defect_rate: float
    observed: np.ndarray
    background: np.ndarray
    defect: np.ndarray


FOCUS_RULES = (
    FocusRule(
        case_name="ECA-54",
        display_name="Rule 54",
        rule_label="1D Wolfram rule 54",
        finding="Finds a period-4 scaffold and leaves clean domain walls and particle world-tubes in the residual.",
        view_kind="spacetime",
    ),
    FocusRule(
        case_name="ECA-110",
        display_name="Rule 110",
        rule_label="1D Wolfram rule 110",
        finding="Finds a drifting period-4 scaffold with shift -2 at long horizon; the residual keeps coherent but more tangled lanes.",
        view_kind="spacetime",
    ),
    FocusRule(
        case_name="S24/B11",
        display_name="S24/B11",
        rule_label="2D Life-like S24/B11",
        finding="Finds a period-2 scaffold at long horizon; the leftover mask stays sparse and persistent instead of collapsing to noise.",
        view_kind="late_slice",
    ),
    FocusRule(
        case_name="diamoeba3d",
        display_name="3D Rule 5858",
        rule_label="3D totalistic S5-8/B5-8",
        finding="Finds a simple period-1 scaffold; the residual highlights broad volumetric interfaces and coherent masses.",
        view_kind="midplane",
    ),
)


def _load_selection_rows(path: Path) -> dict[str, SelectionRecord]:
    rows_by_rule: dict[str, list[dict[str, str]]] = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows_by_rule.setdefault(row["rule"], []).append(row)

    selections: dict[str, SelectionRecord] = {}
    for rule, rows in rows_by_rule.items():
        latest = max(rows, key=lambda row: int(row["T"]))
        shift_text = latest["selected_shift"].strip()
        shift: int | tuple[int, ...]
        if shift_text.startswith("("):
            parsed = ast.literal_eval(shift_text)
            shift = tuple(int(value) for value in parsed)
        else:
            shift = int(shift_text)
        selections[rule] = SelectionRecord(
            horizon=int(latest["T"]),
            period=int(latest["selected_period"]),
            shift=shift,
            margin_bits=float(latest["margin"]),
        )
    return selections


def _max_projection(volume: np.ndarray) -> np.ndarray:
    return np.asarray(volume).max(axis=0)


def _midplane(volume: np.ndarray) -> np.ndarray:
    volume = np.asarray(volume)
    return volume[volume.shape[0] // 2]


def _select_view(array: np.ndarray, *, view_kind: str) -> np.ndarray:
    if view_kind == "spacetime":
        return np.asarray(array)
    if view_kind == "late_slice":
        return np.asarray(array[-1])
    if view_kind == "midplane":
        return _midplane(np.asarray(array[-1]))
    if view_kind == "max_projection":
        return _max_projection(np.asarray(array[-1]))
    raise ValueError(f"Unsupported view kind: {view_kind}")


def _build_payloads() -> list[RenderPayload]:
    case_lookup = {
        case.name: case
        for case in (
            *REPRESENTATIVE_CASES_1D,
            *REPRESENTATIVE_CASES_2D,
            *REPRESENTATIVE_CASES_3D,
        )
    }
    selections = _load_selection_rows(STABILIZATION_RESULTS)
    payloads: list[RenderPayload] = []

    for focus in FOCUS_RULES:
        case = case_lookup[focus.case_name]
        selection = selections[focus.case_name]
        spacetime = simulate_case(case, steps=selection.horizon, seed=SEED)
        if case.dimension == 1:
            assert isinstance(selection.shift, int)
            fit = fit_relative_periodic_background(
                spacetime,
                shift=selection.shift,
                period=selection.period,
                rule=case.rule_number,
                nml_mode="hybrid",
            )
        else:
            assert isinstance(selection.shift, tuple)
            fit = fit_relative_periodic_background_nd(
                spacetime,
                shift=selection.shift,
                period=selection.period,
                nml_mode="hybrid",
            )
        payloads.append(
            RenderPayload(
                focus=focus,
                horizon=selection.horizon,
                period=selection.period,
                shift=selection.shift,
                margin_bits=selection.margin_bits,
                defect_rate=float(fit.defect_rate),
                observed=_select_view(spacetime, view_kind=focus.view_kind),
                background=_select_view(fit.background, view_kind=focus.view_kind),
                defect=_select_view(fit.defect_mask.astype(np.uint8), view_kind=focus.view_kind),
            )
        )
    return payloads


def _decorate_image_axis(ax: plt.Axes, image: np.ndarray, *, defect: bool, title: str) -> None:
    cmap = DEFECT_CMAP if defect else BINARY_CMAP
    ax.imshow(np.asarray(image), interpolation="nearest", aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_title(title, fontsize=10, color=TEXT_COLOR, pad=6)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(BACKGROUND_COLOR)


def _panel_note(payload: RenderPayload) -> str:
    lines = [
        f"{payload.focus.display_name}",
        f"{payload.focus.rule_label}",
        f"NML-selected scaffold: p={payload.period}, s={shift_to_string(payload.shift)}",
        f"margin={payload.margin_bits:.1f} bits, defect rate={payload.defect_rate:.3f}",
        fill(payload.focus.finding, width=64),
    ]
    return "\n".join(lines)


def render_focus_rule_diagram(output_path: Path) -> Path:
    payloads = _build_payloads()
    ensure_output_dir(output_path.parent)

    with plt.rc_context(
        {
            **PLOT_RC,
            "font.family": "DejaVu Sans",
            "axes.facecolor": BACKGROUND_COLOR,
            "figure.facecolor": BACKGROUND_COLOR,
            "savefig.facecolor": BACKGROUND_COLOR,
        }
    ):
        fig = plt.figure(figsize=(18, 13), constrained_layout=False)
        outer = fig.add_gridspec(3, 2, height_ratios=[0.38, 1.0, 1.0], hspace=0.18, wspace=0.12)

        header_ax = fig.add_subplot(outer[0, :])
        header_ax.axis("off")
        header_ax.text(
            0.0,
            0.92,
            "Relative Symmetry Repair: What The Four Focus Rules Reveal",
            fontsize=20,
            color=ACCENT_COLOR,
            fontweight="bold",
            ha="left",
            va="top",
        )
        header_ax.text(
            0.0,
            0.58,
            fill(
                "Across all four examples, the method finds a low-complexity scaffold plus a structured residual. "
                "Rule 54 leaves the cleanest 1D particles, Rule 110 keeps drifting coherent lanes, "
                "S24/B11 keeps sparse persistent 2D patches, and 3D rule 5858 keeps broad volumetric fronts.",
                width=118,
            ),
            fontsize=10.8,
            color=TEXT_COLOR,
            ha="left",
            va="top",
            linespacing=1.35,
        )
        header_ax.text(
            0.0,
            0.16,
            "Each panel shows the NML-selected observed state, fitted background, and residual defect mask. "
            f"Defects use {DEFECT_COLOR}; the 3D rule is shown with a midplane slice.",
            fontsize=9.6,
            color=TEXT_COLOR,
            ha="left",
            va="bottom",
        )

        for index, payload in enumerate(payloads):
            row = 1 + index // 2
            col = index % 2
            panel = outer[row, col].subgridspec(2, 3, height_ratios=[1.0, 0.38], hspace=0.12, wspace=0.06)
            titles = ("Observed", "Background", "Residual")
            images = (payload.observed, payload.background, payload.defect)
            for image_col, (title, image) in enumerate(zip(titles, images, strict=True)):
                ax = fig.add_subplot(panel[0, image_col])
                _decorate_image_axis(ax, image, defect=(image_col == 2), title=title)

            text_ax = fig.add_subplot(panel[1, :])
            text_ax.axis("off")
            text_ax.text(
                0.0,
                1.0,
                _panel_note(payload),
                ha="left",
                va="top",
                fontsize=10.4,
                color=TEXT_COLOR,
                linespacing=1.35,
            )

        fig.subplots_adjust(left=0.03, right=0.99, top=0.97, bottom=0.03)
        save_figure(fig, output_path, extra_formats=("svg",))
        plt.close(fig)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a focused relative-symmetry-repair summary diagram.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "figures" / "relative_symmetry_repair_focus_rules.png",
    )
    args = parser.parse_args()
    path = render_focus_rule_diagram(args.output)
    print(path.resolve())


if __name__ == "__main__":
    main()
