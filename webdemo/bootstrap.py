"""Bootstrap for the in-browser (Pyodide) interactive reproduction demo.

Loads the real ``relative_symmetry_repair`` package inside WebAssembly Python
and exposes ``run_repro``, which regenerates a single run-level row of the
paper's result CSVs (``eca_atlas_runs.csv`` / ``seed_stability_runs.csv``)
using the same code path as the experiment suite:

    simulate_case -> scan (per candidate) -> period_first_selection_from_frame

Two environment adaptations are made, neither of which changes results:

- ``numba`` does not exist under WebAssembly, so a stub is installed and the
  three ``@njit`` simulator kernels are replaced with exactly-equivalent
  vectorized NumPy implementations (verified bit-identical against the
  committed CSVs by ``scripts/verify_webdemo_bootstrap.py``).
- ``lz4`` is loaded if the runtime provides it; otherwise a zlib-based shim is
  installed. The lz4 column is cosmetic (it never enters NML selection or the
  compared columns) and is flagged as approximate when the shim is active.

This module must be imported *before* any ``relative_symmetry_repair`` module.
"""

from __future__ import annotations

import sys
import time
import types
from itertools import product


def _install_numba_stub() -> None:
    try:
        import numba  # noqa: F401  (native environments that have it keep it)
        return
    except ImportError:
        sys.modules.pop("numba", None)
    numba = types.ModuleType("numba")

    def njit(*args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]

        def deco(fn):
            return fn

        return deco

    numba.njit = njit
    numba.jit = njit
    numba.vectorize = njit
    numba.prange = range
    sys.modules["numba"] = numba


def _install_lz4_shim() -> bool:
    try:
        import lz4.frame  # noqa: F401
        return False
    except ImportError:
        pass
    import zlib

    lz4_mod = types.ModuleType("lz4")
    frame_mod = types.ModuleType("lz4.frame")

    def compress(data, *args, **kwargs):
        return zlib.compress(bytes(data), 6)

    frame_mod.compress = compress
    lz4_mod.frame = frame_mod
    sys.modules["lz4"] = lz4_mod
    sys.modules["lz4.frame"] = frame_mod
    return True


_install_numba_stub()
LZ4_SHIMMED = _install_lz4_shim()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from relative_symmetry_repair import ca2d as _ca2d_mod  # noqa: E402
from relative_symmetry_repair import ca3d as _ca3d_mod  # noqa: E402
from relative_symmetry_repair import eca as _eca_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Vectorized replacements for the @njit simulator kernels. Each mirrors the
# loop semantics of its counterpart exactly (torus wrap, LSB-first rule
# lookup, uint8 spacetime with row 0 = initial condition).
# ---------------------------------------------------------------------------


def _simulate_eca_vec(rule: int, initial: np.ndarray, steps: int) -> np.ndarray:
    rule = int(rule)
    spacetime = np.empty((steps, initial.size), dtype=np.uint8)
    spacetime[0] = initial
    for t in range(1, steps):
        prev = spacetime[t - 1].astype(np.int64)
        patterns = (np.roll(prev, 1) << 2) | (prev << 1) | np.roll(prev, -1)
        spacetime[t] = (rule >> patterns) & 1
    return spacetime


def _neighbor_totals(prev: np.ndarray) -> np.ndarray:
    p = prev.astype(np.int64)
    total = np.zeros_like(p)
    for offsets in product((-1, 0, 1), repeat=p.ndim):
        if not any(offsets):
            continue
        rolled = p
        for axis, off in enumerate(offsets):
            if off:
                rolled = np.roll(rolled, off, axis=axis)
        total += rolled
    return total


def _simulate_range_vec(
    initial: np.ndarray,
    steps: int,
    survive_lo: int,
    survive_hi: int,
    birth_lo: int,
    birth_hi: int,
) -> np.ndarray:
    spacetime = np.empty((steps,) + initial.shape, dtype=np.uint8)
    spacetime[0] = initial
    for t in range(1, steps):
        prev = spacetime[t - 1]
        total = _neighbor_totals(prev)
        spacetime[t] = np.where(
            prev == 1,
            (total >= survive_lo) & (total <= survive_hi),
            (total >= birth_lo) & (total <= birth_hi),
        ).astype(np.uint8)
    return spacetime


def _simulate_life_general_vec(
    initial: np.ndarray,
    steps: int,
    birth_lut: np.ndarray,
    survive_lut: np.ndarray,
) -> np.ndarray:
    spacetime = np.empty((steps,) + initial.shape, dtype=np.uint8)
    spacetime[0] = initial
    for t in range(1, steps):
        prev = spacetime[t - 1]
        total = _neighbor_totals(prev)
        spacetime[t] = np.where(prev == 1, survive_lut[total], birth_lut[total]).astype(np.uint8)
    return spacetime


_eca_mod._simulate_eca_numba = _simulate_eca_vec
_ca2d_mod._simulate_life_numba = _simulate_range_vec
_ca2d_mod._simulate_life_general_numba = _simulate_life_general_vec
_ca3d_mod._simulate_3d_numba = _simulate_range_vec


from relative_symmetry_repair.experiment_core import (  # noqa: E402
    REPRESENTATIVE_CASES_2D,
    REPRESENTATIVE_CASES_3D,
    _add_selection_metrics,
    _record_base,
    eca_case,
    period_first_selection_from_frame,
    simulate_case,
)
from relative_symmetry_repair.repair import scan_relative_periodicity  # noqa: E402
from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd  # noqa: E402

NAMED_CASES = {case.name: case for case in (*REPRESENTATIVE_CASES_2D, *REPRESENTATIVE_CASES_3D)}


def _py(value):
    """Convert numpy scalars/containers to plain Python for JS bridging."""
    if isinstance(value, dict):
        return {str(k): _py(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_py(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and value != value:  # NaN
        return None
    return value


def _image(array: np.ndarray) -> dict:
    arr = np.ascontiguousarray(array.astype(np.uint8))
    return {"shape": list(arr.shape), "data": arr.tobytes()}


def build_case(family: str, rule):
    if family == "eca":
        return eca_case(int(rule))
    return NAMED_CASES[str(rule)]


def run_repro(family: str, rule, seed: int, horizon: int, progress=None) -> dict:
    """Regenerate one run-level result row, exactly as the experiment suite does."""
    started = time.time()
    case = build_case(family, rule)
    seed = int(seed)
    horizon = int(horizon)

    if progress is not None:
        progress(0.0, f"simulating {case.name} (seed {seed}, T={horizon})")
    spacetime = simulate_case(case, steps=horizon, seed=seed)

    periods = list(case.search.periods)
    frames = []
    for index, period in enumerate(periods):
        if case.dimension == 1:
            frame, fits = scan_relative_periodicity(
                spacetime,
                shifts=case.search.shift_ranges[0],
                periods=[period],
                rule=case.rule_number,
                nml_mode="hybrid",
            )
        else:
            frame, fits = scan_relative_periodicity_nd(
                spacetime,
                shift_ranges=case.search.shift_ranges,
                periods=[period],
                nml_mode="hybrid",
            )
        fits.clear()
        frames.append(frame)
        if progress is not None:
            progress((index + 1) / len(periods), f"scanned period {period}/{periods[-1]}")

    full_frame = pd.concat(frames, ignore_index=True)
    selection = period_first_selection_from_frame(full_frame)

    # Refit only the winning candidate to recover its background/defect arrays.
    if case.dimension == 1:
        selected_shift = int(selection.selected_shift)
        _, fits = scan_relative_periodicity(
            spacetime,
            shifts=[selected_shift],
            periods=[selection.selected_period],
            rule=case.rule_number,
            nml_mode="hybrid",
        )
        fit = fits[(selected_shift, selection.selected_period)]
    else:
        selected_shift = tuple(int(v) for v in selection.selected_shift)
        _, fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=[[component] for component in selected_shift],
            periods=[selection.selected_period],
            nml_mode="hybrid",
        )
        fit = fits[(selected_shift, selection.selected_period)]

    record = _record_base(case, seed=seed, horizon=horizon)
    _add_selection_metrics(record, selection)

    defect = fit.defect_mask.astype(np.uint8)
    if case.dimension == 1:
        images = {
            "spacetime": _image(spacetime),
            "background": _image(fit.background),
            "defect": _image(defect),
        }
    elif case.dimension == 2:
        images = {
            "spacetime": _image(spacetime[-1]),
            "background": _image(fit.background[-1]),
            "defect": _image(defect[-1]),
        }
    else:
        mid = spacetime.shape[1] // 2
        images = {
            "spacetime": _image(spacetime[-1][mid]),
            "background": _image(fit.background[-1][mid]),
            "defect": _image(defect[-1][mid]),
        }

    period_summary = selection.period_summary[
        ["period_rank", "period", "best_shift_str", "nml_bits", "nll_bits", "nml_complexity", "defect_rate"]
    ].to_dict("records")

    return {
        "record": _py(record),
        "period_summary": _py(period_summary),
        "defects_per_frame": [int(v) for v in defect.reshape(defect.shape[0], -1).sum(axis=1)],
        "images": images,
        "dimension": case.dimension,
        "case_name": case.name,
        "search_label": case.search.label,
        "n_candidates": int(len(full_frame)),
        "lz4_shimmed": bool(LZ4_SHIMMED),
        "runtime_s": round(time.time() - started, 2),
    }
