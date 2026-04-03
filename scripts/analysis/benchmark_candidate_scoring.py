#!/usr/bin/env python3
"""Benchmark the optimized candidate-scoring pipeline against the reference path."""

from __future__ import annotations

import argparse
import gc
import time
from dataclasses import dataclass
from statistics import median

import pandas as pd

from relative_symmetry_repair.ca2d import parse_rulestring, random_initial_grid, simulate_2d_general
from relative_symmetry_repair.eca import random_initial_state, simulate_eca
from relative_symmetry_repair.repair import (
    _scan_relative_periodicity_reference,
    scan_relative_periodicity,
)
from relative_symmetry_repair.repair_nd import (
    _scan_relative_periodicity_nd_reference,
    scan_relative_periodicity_nd,
)


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    name: str
    shape: tuple[int, ...]
    candidate_count: int
    backend: str
    reference_seconds: float
    optimized_seconds: float
    speedup: float
    packed_bits: bool = False
    gpu: bool = False


def _time_call(fn, *, repeat: int) -> tuple[float, tuple[pd.DataFrame, dict]]:
    timings: list[float] = []
    last_result = None
    for _ in range(int(repeat)):
        gc.collect()
        started = time.perf_counter()
        last_result = fn()
        timings.append(time.perf_counter() - started)
    assert last_result is not None
    return median(timings), last_result


def benchmark_1d(*, repeat: int) -> BenchmarkCase:
    initial = random_initial_state(width=192, density=0.5, seed=11)
    spacetime = simulate_eca(rule=110, initial=initial, steps=200)
    shifts = list(range(-6, 7))
    periods = list(range(1, 11))

    ref_time, (ref_frame, _) = _time_call(
        lambda: _scan_relative_periodicity_reference(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode="hybrid",
        ),
        repeat=repeat,
    )
    opt_time, (opt_frame, _) = _time_call(
        lambda: scan_relative_periodicity(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode="hybrid",
        ),
        repeat=repeat,
    )
    pd.testing.assert_frame_equal(ref_frame, opt_frame)

    return BenchmarkCase(
        name="eca110_scan",
        shape=tuple(int(dim) for dim in spacetime.shape),
        candidate_count=len(shifts) * len(periods),
        backend="cpu",
        reference_seconds=ref_time,
        optimized_seconds=opt_time,
        speedup=ref_time / opt_time,
    )


def benchmark_2d(*, repeat: int) -> BenchmarkCase:
    birth, survive = parse_rulestring("B35678/S5678")
    initial = random_initial_grid(width=48, height=48, density=0.5, seed=42)
    spacetime = simulate_2d_general(initial, steps=80, birth=birth, survive=survive)
    shift_values = list(range(-2, 3))
    periods = list(range(1, 7))

    ref_time, (ref_frame, _) = _time_call(
        lambda: _scan_relative_periodicity_nd_reference(
            spacetime,
            shift_ranges=[shift_values, shift_values],
            periods=periods,
            nml_mode="hybrid",
        ),
        repeat=repeat,
    )
    opt_time, (opt_frame, _) = _time_call(
        lambda: scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=[shift_values, shift_values],
            periods=periods,
            nml_mode="hybrid",
        ),
        repeat=repeat,
    )
    pd.testing.assert_frame_equal(ref_frame, opt_frame)

    return BenchmarkCase(
        name="diamoeba_like_2d_scan",
        shape=tuple(int(dim) for dim in spacetime.shape),
        candidate_count=len(shift_values) * len(shift_values) * len(periods),
        backend="cpu",
        reference_seconds=ref_time,
        optimized_seconds=opt_time,
        speedup=ref_time / opt_time,
    )


def print_case(result: BenchmarkCase) -> None:
    print(f"{result.name}:")
    print(f"  shape: {result.shape}")
    print(f"  candidates: {result.candidate_count}")
    print(f"  backend: {result.backend}")
    print(f"  reference: {result.reference_seconds:.4f} s")
    print(f"  optimized: {result.optimized_seconds:.4f} s")
    print(f"  speedup: {result.speedup:.2f}x")
    print(f"  packed_bits: {result.packed_bits}")
    print(f"  gpu: {result.gpu}")
    print("  memory_note: reuses orbit-id, background, and residual buffers across candidates;")
    print("               caches class sizes and NML complexity per period")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repeat",
        type=int,
        default=3,
        help="Number of timed repetitions per benchmark case (median reported).",
    )
    args = parser.parse_args()

    results = [
        benchmark_1d(repeat=args.repeat),
        benchmark_2d(repeat=args.repeat),
    ]
    for result in results:
        print_case(result)


if __name__ == "__main__":
    main()
