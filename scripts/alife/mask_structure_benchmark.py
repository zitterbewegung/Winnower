#!/usr/bin/env python3
"""Quantify residual-mask organization against density-matched shuffles.

The paper's structured-residual claim ("the residual mask is sparse but
visibly organized") needs a number. For each representative rule this
benchmark:

1. simulates the rule, runs the shipped selector, and refits the winning
   candidate to obtain the residual mask M;
2. compares M's run-length codelength and connected-component count against
   the same statistics for uniformly shuffled masks of identical density
   (20 shuffles) — an organized mask codes far below its shuffled baseline
   (rl_ratio << 1) and clumps into far fewer components (comp_ratio << 1);
3. repeats the whole procedure on time-shuffled and density-matched
   Bernoulli control spacetimes, extending the null-control coverage from
   the selection claim to the mask-structure claim: control masks should
   show no organization (ratios near 1).

Because the run-length statistic is raster-order dependent, the ratio is
also reported with the axis order reversed (rl_ratio_reversed); agreement
between the two orders indicates the conclusion does not hinge on raster
order.

Outputs:
    outputs/alife_2026/mask_structure/mask_structure_runs.csv
    outputs/alife_2026/mask_structure/mask_structure_summary.csv
    outputs/alife_2026/mask_structure/manifest.json
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.coding import run_length_bits  # noqa: E402
from relative_symmetry_repair.experiment_core import (  # noqa: E402
    REPRESENTATIVE_CASES_1D,
    REPRESENTATIVE_CASES_2D,
    REPRESENTATIVE_CASES_3D,
    bernoulli_iid_control,
    simulate_case,
    time_shuffled_control,
    scan_case_spacetime,
    write_json_manifest,
    write_summary_csv,
)

N_SHUFFLES = 20
HORIZONS = {1: 200, 2: 400, 3: 40}


def mask_stats(mask: np.ndarray) -> tuple[int, int]:
    """Run-length bits (native raster order) and connected-component count."""
    structure = np.ones((3,) * mask.ndim, dtype=np.uint8)
    _, n_components = ndimage.label(mask.astype(np.uint8), structure=structure)
    return run_length_bits(mask), int(n_components)


def shuffled_baseline(mask: np.ndarray, rng: np.random.Generator) -> tuple[float, float, float, float]:
    """Mean/std RL bits and mean component count over uniform permutations."""
    flat = np.ravel(mask).astype(np.uint8)
    rl_values, comp_values = [], []
    for _ in range(N_SHUFFLES):
        shuffled = rng.permutation(flat).reshape(mask.shape)
        rl, n_comp = mask_stats(shuffled)
        rl_values.append(rl)
        comp_values.append(n_comp)
    return (
        float(np.mean(rl_values)),
        float(np.std(rl_values)),
        float(np.mean(comp_values)),
        float(np.std(comp_values)),
    )


def analyze_variant(case, spacetime: np.ndarray, *, variant: str, seed: int) -> dict:
    started = time.time()
    outcome = scan_case_spacetime(case, spacetime)
    mask = outcome.best_fit.defect_mask.astype(bool)
    density = float(mask.mean())
    rl_bits, n_components = mask_stats(mask)
    rl_bits_reversed, _ = mask_stats(np.transpose(mask))

    rng = np.random.default_rng(seed * 100003 + case.dimension)
    rl_mean, rl_std, comp_mean, comp_std = shuffled_baseline(mask, rng)
    rl_mean_rev, _, _, _ = shuffled_baseline(np.transpose(mask), rng)

    def ratio(value, baseline):
        return float(value / baseline) if baseline > 0 else float("nan")

    return {
        "rule": case.name,
        "dimension": case.dimension,
        "variant": variant,
        "seed": seed,
        "horizon": spacetime.shape[0],
        "selected_period": outcome.selection.selected_period,
        "mask_density": density,
        "defect_sites": int(mask.sum()),
        "rl_bits": rl_bits,
        "rl_shuffled_mean": rl_mean,
        "rl_ratio": ratio(rl_bits, rl_mean),
        "rl_z": float((rl_bits - rl_mean) / rl_std) if rl_std > 0 else float("nan"),
        "rl_ratio_reversed": ratio(rl_bits_reversed, rl_mean_rev),
        "n_components": n_components,
        "comp_shuffled_mean": comp_mean,
        "comp_ratio": ratio(n_components, comp_mean),
        "runtime_s": round(time.time() - started, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--base-seed", type=int, default=11)
    parser.add_argument("--n-seeds", type=int, default=3)
    args = parser.parse_args()

    out_dir = args.output_root / "mask_structure"
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = (*REPRESENTATIVE_CASES_1D, *REPRESENTATIVE_CASES_2D, *REPRESENTATIVE_CASES_3D)
    rows = []
    for case in cases:
        horizon = HORIZONS[case.dimension]
        for seed in range(args.base_seed, args.base_seed + args.n_seeds):
            spacetime = simulate_case(case, steps=horizon, seed=seed)
            rows.append(analyze_variant(case, spacetime, variant="original", seed=seed))
            rows.append(analyze_variant(
                case, time_shuffled_control(spacetime, seed=seed), variant="time_shuffled", seed=seed))
            rows.append(analyze_variant(
                case, bernoulli_iid_control(spacetime, seed=seed), variant="bernoulli_iid", seed=seed))
            print(f"{case.name} seed {seed} done", flush=True)

    runs = pd.DataFrame.from_records(rows)
    runs.to_csv(out_dir / "mask_structure_runs.csv", index=False)

    summary = (
        runs.groupby(["rule", "dimension", "variant"])
        .agg(
            runs=("rl_ratio", "size"),
            mean_mask_density=("mask_density", "mean"),
            mean_rl_ratio=("rl_ratio", "mean"),
            mean_rl_ratio_reversed=("rl_ratio_reversed", "mean"),
            mean_comp_ratio=("comp_ratio", "mean"),
            mean_rl_z=("rl_z", "mean"),
        )
        .reset_index()
        .sort_values(["dimension", "rule", "variant"], kind="mergesort")
    )
    write_summary_csv(summary, out_dir / "mask_structure_summary.csv")

    write_json_manifest(
        out_dir / "manifest.json",
        {
            "experiment": "mask_structure_benchmark",
            "base_seed": args.base_seed,
            "n_seeds": args.n_seeds,
            "n_shuffles": N_SHUFFLES,
            "horizons": HORIZONS,
            "statistics": "run-length bits and 3^d-connectivity component count vs uniform permutation baseline",
        },
    )
    print(summary.to_string(index=False))
    print(f"\n{len(runs)} runs -> {out_dir}")


if __name__ == "__main__":
    main()
