#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.plotting import save_figure  # noqa: E402

FOCUS_RULES = ("ECA-54", "ECA-110", "S24/B11", "diamoeba3d")


def build_summary_figure(results_csv: Path, output_path: Path, *, extra_formats: tuple[str, ...]) -> None:
    df = pd.read_csv(results_csv)
    df = df[df["rule"].isin(FOCUS_RULES)].copy()
    order = {name: idx for idx, name in enumerate(FOCUS_RULES)}
    df["rule_order"] = df["rule"].map(order)
    df = df.sort_values(["rule_order", "T"])

    fig, axes = plt.subplots(2, len(FOCUS_RULES), figsize=(15.8, 7.0), sharex="col")
    colors = {
        "period": "#b00300",
        "margin": "#5f5f5f",
    }
    face = "#efe2d0"
    grid = "#cfc3b3"

    for col, rule in enumerate(FOCUS_RULES):
        group = df[df["rule"] == rule].sort_values("T")
        if group.empty:
            continue

        ax_period = axes[0, col]
        ax_margin = axes[1, col]

        ax_period.plot(group["T"], group["selected_period"], "o-", linewidth=2.2, markersize=5, color=colors["period"])
        ax_period.set_title(rule, fontsize=11, color="#3b3b3b")
        ax_period.set_ylabel("Selected period" if col == 0 else "", fontsize=10, color="#3b3b3b")
        ax_period.set_facecolor(face)
        ax_period.grid(color=grid, alpha=0.8, linewidth=0.6)
        ax_period.tick_params(colors="#5f5f5f", labelsize=9)
        for spine in ax_period.spines.values():
            spine.set_color("#cfc3b3")
        ax_period.set_ylim(0, max(1, int(group["selected_period"].max())) + 1)

        margins = group["margin"].replace([np.inf], np.nan)
        ax_margin.plot(group["T"], margins, "s-", linewidth=2.2, markersize=5, color=colors["margin"])
        ax_margin.set_xlabel("Horizon T", fontsize=10, color="#3b3b3b")
        ax_margin.set_ylabel("Margin (bits)" if col == 0 else "", fontsize=10, color="#3b3b3b")
        ax_margin.set_facecolor(face)
        ax_margin.grid(color=grid, alpha=0.8, linewidth=0.6)
        ax_margin.tick_params(colors="#5f5f5f", labelsize=9)
        for spine in ax_margin.spines.values():
            spine.set_color("#cfc3b3")

    fig.patch.set_facecolor("#efe2d0")
    fig.suptitle("How the selected period stabilizes in representative 1D, 2D, and 3D rules", fontsize=14, y=0.98, color="#b00300")
    fig.text(
        0.5,
        0.02,
        "The top row shows the selected period as a function of the horizon T. "
        "The bottom row shows the winning margin in bits. In these representative rules, "
        "the selected period either stabilizes immediately or changes only a few times before it locks.",
        ha="center",
        va="bottom",
        fontsize=10,
        color="#3b3b3b",
    )
    fig.tight_layout(rect=(0.02, 0.05, 0.98, 0.95))
    save_figure(fig, output_path, extra_formats=extra_formats)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the ALIFE stabilization summary figure in raster and vector formats.")
    parser.add_argument("--results-csv", type=Path, default=ROOT / "results" / "stabilization_results.csv")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "alife_2026" / "editable_figures" / "stabilization_summary.png",
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
    build_summary_figure(args.results_csv, args.output, extra_formats=extra_formats)
    print(f"Wrote stabilization summary to {args.output}")


if __name__ == "__main__":
    main()
