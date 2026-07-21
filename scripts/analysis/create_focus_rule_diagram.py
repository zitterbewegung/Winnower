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
from matplotlib.colors import ListedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_suite import (  # noqa: E402
    REPRESENTATIVE_CASES_1D,
    REPRESENTATIVE_CASES_2D,
    REPRESENTATIVE_CASES_3D,
    ensure_output_dir,
    shift_to_string,
    simulate_case,
)
from relative_symmetry_repair.repair import fit_relative_periodic_background  # noqa: E402
from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd  # noqa: E402


SEED = 42
STABILIZATION_RESULTS = ROOT / "outputs" / "csv" / "stabilization_results.csv"

TEXT_COLOR = "#222222"
STATE_ONE_COLOR = "#303030"
STATE_ZERO_COLOR = "#ffffff"
DEFECT_ONE_COLOR = "#c44e52"
STATE_CMAP = ListedColormap([STATE_ZERO_COLOR, STATE_ONE_COLOR])
DEFECT_CMAP = ListedColormap([STATE_ZERO_COLOR, DEFECT_ONE_COLOR])


@dataclass(frozen=True)
class FocusRule:
    case_name: str
    display_name: str
    rule_label: str
    summary: str
    view_kind: str
    display_rows: int | None = None
    display_time_mode: str | None = None


@dataclass(frozen=True)
class SelectionRecord:
    horizon: int
    period: int
    shift: int | tuple[int, ...]
    margin_bits: float


@dataclass(frozen=True)
class RenderPayload:
    focus: FocusRule
    selection_horizon: int
    period: int
    shift: int | tuple[int, ...]
    margin_bits: float
    defect_rate: float
    display_note: str
    observed: np.ndarray
    background: np.ndarray
    defect: np.ndarray


FOCUS_RULES = (
    FocusRule(
        case_name="ECA-54",
        display_name="Rule 54",
        rule_label="1D Wolfram rule 54",
        summary="Finds a period-4 domain template; the defect mask isolates clean domain walls and particle-like world-tubes.",
        view_kind="spacetime_tail",
        display_rows=240,
    ),
    FocusRule(
        case_name="ECA-110",
        display_name="Rule 110",
        rule_label="1D Wolfram rule 110",
        summary="Finds a drifting period-4 domain template with shift -2; the defect mask keeps coherent but more tangled lanes.",
        view_kind="spacetime_tail",
        display_rows=240,
    ),
    FocusRule(
        case_name="S24/B11",
        display_name="S24/B11",
        rule_label="2D Life-like S24/B11",
        summary="Finds a period-2 domain template and leaves a sparse persistent defect population instead of featureless noise.",
        view_kind="slice_2d",
        display_time_mode="late_representative",
    ),
    FocusRule(
        case_name="3d-life",
        display_name="3D Life",
        rule_label="3D Bays Life B5/S45",
        summary="At the stabilized horizon, NML selects only a trivial period-1 domain template here, so the defect mask is essentially the observed 3D mass.",
        view_kind="slice_3d",
        display_time_mode="stabilized_mid",
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


def _midplane(volume: np.ndarray) -> np.ndarray:
    volume = np.asarray(volume)
    return volume[volume.shape[0] // 2]


def _representative_late_time(defect_mask: np.ndarray) -> int:
    if defect_mask.ndim != 3:
        raise ValueError("expected a 2D spacetime defect mask")
    defect_counts = defect_mask.sum(axis=(1, 2))
    tail_start = max(defect_counts.size // 2, defect_counts.size - min(100, defect_counts.size))
    tail = defect_counts[tail_start:]
    target = float(tail.mean())
    offset = int(np.argmin(np.abs(tail - target)))
    return tail_start + offset


def _resolve_display_time(focus: FocusRule, defect_mask: np.ndarray, selection_horizon: int) -> int:
    if focus.display_time_mode == "late_representative":
        return _representative_late_time(defect_mask)
    if focus.display_time_mode == "stabilized_mid":
        return min(40, selection_horizon - 1)
    raise ValueError(f"Unsupported display time mode: {focus.display_time_mode}")


def _crop_spacetime_tail(spacetime: np.ndarray, rows: int) -> np.ndarray:
    rows = min(int(rows), spacetime.shape[0])
    return np.asarray(spacetime[-rows:])


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

        if focus.view_kind == "spacetime_tail":
            rows = focus.display_rows or selection.horizon
            observed = _crop_spacetime_tail(spacetime, rows)
            background = _crop_spacetime_tail(fit.background, rows)
            defect = _crop_spacetime_tail(fit.defect_mask.astype(np.uint8), rows)
            display_note = f"Display: last {rows} rows of the run."
        elif focus.view_kind == "slice_2d":
            time_index = _resolve_display_time(focus, fit.defect_mask, selection.horizon)
            observed = np.asarray(spacetime[time_index])
            background = np.asarray(fit.background[time_index])
            defect = np.asarray(fit.defect_mask[time_index]).astype(np.uint8)
            display_note = f"Display: late slice at t={time_index}."
        elif focus.view_kind == "slice_3d":
            time_index = _resolve_display_time(focus, fit.defect_mask, selection.horizon)
            observed = _midplane(spacetime[time_index])
            background = _midplane(fit.background[time_index])
            defect = _midplane(fit.defect_mask[time_index].astype(np.uint8))
            display_note = f"Display: z-midplane at t={time_index}."
        else:
            raise ValueError(f"Unsupported view kind: {focus.view_kind}")

        payloads.append(
            RenderPayload(
                focus=focus,
                selection_horizon=selection.horizon,
                period=selection.period,
                shift=selection.shift,
                margin_bits=selection.margin_bits,
                defect_rate=float(fit.defect_rate),
                display_note=display_note,
                observed=observed,
                background=background,
                defect=defect,
            )
        )
    return payloads


def _panel_text(payload: RenderPayload) -> str:
    lines = [
        payload.focus.display_name,
        payload.focus.rule_label,
        f"T={payload.selection_horizon} -> p={payload.period}, s={shift_to_string(payload.shift)}, defect={payload.defect_rate:.3f}.",
        payload.display_note.replace("Display: ", ""),
        fill(payload.focus.summary, width=33),
    ]
    return "\n".join(lines)


def _decorate_text_axis(ax: plt.Axes, payload: RenderPayload) -> None:
    ax.axis("off")
    ax.text(
        0.0,
        1.0,
        _panel_text(payload),
        ha="left",
        va="top",
        fontsize=7.9,
        color=TEXT_COLOR,
        linespacing=1.35,
        transform=ax.transAxes,
    )


def _decorate_image_axis(ax: plt.Axes, image: np.ndarray, *, defect: bool, title: str | None = None) -> None:
    cmap = DEFECT_CMAP if defect else STATE_CMAP
    ax.imshow(np.asarray(image), interpolation="nearest", aspect="auto", cmap=cmap, vmin=0, vmax=1)
    if title:
        ax.set_title(title, fontsize=9.2, color=TEXT_COLOR, pad=4)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(STATE_ZERO_COLOR)


def _save_figure(fig: plt.Figure, path: Path, *, formats: tuple[str, ...]) -> None:
    ensure_output_dir(path.parent)
    for fmt in formats:
        target = path.with_suffix(f".{fmt}")
        fig.savefig(target, dpi=300, bbox_inches="tight", facecolor="white")


def render_focus_rule_figure(*, preview_path: Path, paper_path: Path) -> tuple[Path, Path]:
    payloads = _build_payloads()

    with plt.rc_context(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "font.family": "DejaVu Sans",
            "font.size": 8.2,
            "axes.titlesize": 9.2,
        }
    ):
        fig = plt.figure(figsize=(8.0, 8.7), constrained_layout=False)
        grid = fig.add_gridspec(
            nrows=len(payloads),
            ncols=4,
            width_ratios=[1.70, 1.05, 1.05, 1.05],
            hspace=0.30,
            wspace=0.10,
        )

        column_titles = ("Observed", "Domain Template", "Defect Mask")
        for row, payload in enumerate(payloads):
            text_ax = fig.add_subplot(grid[row, 0])
            _decorate_text_axis(text_ax, payload)

            image_axes = (
                fig.add_subplot(grid[row, 1]),
                fig.add_subplot(grid[row, 2]),
                fig.add_subplot(grid[row, 3]),
            )
            images = (payload.observed, payload.background, payload.defect)
            for col, (ax, image) in enumerate(zip(image_axes, images, strict=True)):
                title = column_titles[col] if row == 0 else None
                _decorate_image_axis(ax, image, defect=(col == 2), title=title)

        fig.subplots_adjust(left=0.04, right=0.995, top=0.98, bottom=0.03)
        _save_figure(fig, preview_path, formats=("png", "pdf", "svg"))
        _save_figure(fig, paper_path, formats=("png", "pdf"))
        plt.close(fig)

    return preview_path.with_suffix(".png"), paper_path.with_suffix(".pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a manuscript-ready focus-rule figure.")
    parser.add_argument(
        "--preview-output",
        type=Path,
        default=ROOT / "outputs" / "figures" / "relative_symmetry_repair_focus_rules.png",
    )
    parser.add_argument(
        "--paper-output",
        type=Path,
        default=ROOT / "paper" / "figures" / "relative_symmetry_repair_focus_rules.png",
    )
    args = parser.parse_args()
    preview_path, paper_path = render_focus_rule_figure(
        preview_path=args.preview_output,
        paper_path=args.paper_output,
    )
    print(preview_path.resolve())
    print(paper_path.resolve())


if __name__ == "__main__":
    main()
