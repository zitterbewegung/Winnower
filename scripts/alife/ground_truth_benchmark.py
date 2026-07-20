#!/usr/bin/env python3
"""Ground-truth recovery benchmark for the relative-periodic selector.

Constructs spacetimes that are exactly relative-periodic with a KNOWN
(period, shift) — a random base tile extended by the relative-periodicity
relation B[t+p, x+s mod W] = B[t, x] — optionally corrupted by i.i.d. bit
flips at rate eps, and measures how often the shipped selector (the same
default search grids and period-first Bernoulli-NML selection used in every
paper experiment) recovers the true period and shift.

This provides the accuracy-versus-known-ground-truth statistics requested in
review, complementing the null-control experiments (which establish behavior
on data with NO planted periodicity).

Outputs:
    outputs/alife_2026/ground_truth/ground_truth_runs.csv
    outputs/alife_2026/ground_truth/ground_truth_summary.csv
    outputs/alife_2026/ground_truth/manifest.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_core import (  # noqa: E402
    DEFAULT_SEARCH_1D,
    DEFAULT_SEARCH_2D,
    DEFAULT_SEARCH_3D,
    period_first_selection_from_frame,
    write_json_manifest,
    write_summary_csv,
)
from relative_symmetry_repair.repair import scan_relative_periodicity  # noqa: E402
from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd  # noqa: E402


def make_relative_periodic_spacetime(
    steps: int,
    spatial: tuple[int, ...],
    period: int,
    shift: tuple[int, ...],
    *,
    rng: np.random.Generator,
    flip_rate: float,
) -> np.ndarray:
    """Random base tile extended by B[t+p, x+s mod D] = B[t, x], then noise."""
    tile = (rng.random((period, *spatial)) < 0.5).astype(np.uint8)
    spacetime = np.empty((steps, *spatial), dtype=np.uint8)
    for t in range(steps):
        block, residue = divmod(t, period)
        frame = tile[residue]
        # after `block` applications of the defining relation, the frame is
        # rolled by block * shift along each spatial axis
        for axis, component in enumerate(shift):
            offset = (block * component) % spatial[axis]
            if offset:
                frame = np.roll(frame, offset, axis=axis)
        spacetime[t] = frame
    if flip_rate > 0.0:
        flips = rng.random(spacetime.shape) < flip_rate
        spacetime = np.where(flips, 1 - spacetime, spacetime).astype(np.uint8)
    return spacetime


def run_case(dimension: int, steps: int, spatial, period, shift, flip_rate, seed):
    rng = np.random.default_rng(seed)
    spacetime = make_relative_periodic_spacetime(
        steps, tuple(spatial), period, tuple(shift), rng=rng, flip_rate=flip_rate
    )
    started = time.time()
    if dimension == 1:
        frame, fits = scan_relative_periodicity(
            spacetime,
            shifts=DEFAULT_SEARCH_1D.shift_ranges[0],
            periods=DEFAULT_SEARCH_1D.periods,
            nml_mode="hybrid",
        )
        fits.clear()
        selection = period_first_selection_from_frame(frame)
        selected_shift = (int(selection.selected_shift),)
    else:
        search = DEFAULT_SEARCH_2D if dimension == 2 else DEFAULT_SEARCH_3D
        frame, fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=search.shift_ranges,
            periods=search.periods,
            nml_mode="hybrid",
        )
        fits.clear()
        selection = period_first_selection_from_frame(frame)
        selected_shift = tuple(int(v) for v in selection.selected_shift)
    runtime = time.time() - started

    true_shift = tuple(int(v) for v in shift)
    period_ok = int(selection.selected_period == period)
    shift_ok = int(selected_shift == true_shift)
    return {
        "dimension": dimension,
        "steps": steps,
        "spatial": "x".join(str(v) for v in spatial),
        "true_period": period,
        "true_shift": str(true_shift),
        "flip_rate": flip_rate,
        "seed": seed,
        "selected_period": selection.selected_period,
        "selected_shift": str(selected_shift),
        "period_correct": period_ok,
        "shift_correct": shift_ok,
        "both_correct": int(period_ok and shift_ok),
        "margin_bits": selection.margin_bits,
        "selected_defect_rate": selection.selected_defect_rate,
        "runtime_s": round(runtime, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--base-seed", type=int, default=11)
    parser.add_argument("--n-seeds", type=int, default=3)
    args = parser.parse_args()

    out_dir = args.output_root / "ground_truth"
    out_dir.mkdir(parents=True, exist_ok=True)

    flip_rates = [0.0, 0.02, 0.05, 0.10, 0.20]
    seeds = [args.base_seed + i for i in range(args.n_seeds)]
    rows = []

    # 1D: every scanned period, a spread of shifts, all noise levels.
    for period, shift, eps, seed in itertools.product(
        [1, 2, 3, 4, 5, 6, 7, 8], [-4, -1, 0, 2], flip_rates, seeds
    ):
        rows.append(run_case(1, 200, (192,), period, (shift,), eps, seed))

    # 2D: periods and shift vectors within the default +/-2 grid.
    for period, shift, eps, seed in itertools.product(
        [1, 2, 3, 4], [(0, 0), (1, 0), (2, -1)], [0.0, 0.05, 0.10], seeds
    ):
        rows.append(run_case(2, 60, (32, 32), period, shift, eps, seed))

    # 3D: small volumes, default +/-2 grid.
    for period, shift, eps, seed in itertools.product(
        [1, 2, 3], [(0, 0, 0), (1, -1, 0)], [0.0, 0.05, 0.10], seeds
    ):
        rows.append(run_case(3, 20, (12, 12, 12), period, shift, eps, seed))

    runs = pd.DataFrame.from_records(rows)
    runs.to_csv(out_dir / "ground_truth_runs.csv", index=False)

    summary = (
        runs.groupby(["dimension", "flip_rate"])
        .agg(
            runs=("both_correct", "size"),
            period_accuracy=("period_correct", "mean"),
            shift_accuracy=("shift_correct", "mean"),
            joint_accuracy=("both_correct", "mean"),
            mean_margin_bits=("margin_bits", "mean"),
            mean_runtime_s=("runtime_s", "mean"),
        )
        .reset_index()
    )
    write_summary_csv(summary, out_dir / "ground_truth_summary.csv")

    write_json_manifest(
        out_dir / "manifest.json",
        {
            "experiment": "ground_truth_benchmark",
            "base_seed": args.base_seed,
            "n_seeds": args.n_seeds,
            "flip_rates": flip_rates,
            "search": {
                "1d": DEFAULT_SEARCH_1D.to_manifest(),
                "2d": DEFAULT_SEARCH_2D.to_manifest(),
                "3d": DEFAULT_SEARCH_3D.to_manifest(),
            },
            "construction": "random base tile extended by B[t+p, x+s mod D] = B[t, x]; i.i.d. bit flips at flip_rate",
        },
    )

    print(summary.to_string(index=False))
    print(f"\n{len(runs)} runs -> {out_dir}")


if __name__ == "__main__":
    main()
