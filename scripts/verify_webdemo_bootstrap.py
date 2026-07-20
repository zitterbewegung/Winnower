#!/usr/bin/env python3
"""Verify that the web-demo bootstrap reproduces the committed result CSVs.

Runs ``webdemo/bootstrap.py``'s ``run_repro`` (the exact code path the
in-browser reproduction demo executes, including the vectorized simulator
kernels that replace the numba ones) for a sample of (rule, seed, horizon)
configurations, and compares every column of the produced record against the
committed row in ``outputs/alife_2026``.

Usage:
    python scripts/verify_webdemo_bootstrap.py               # numba installed
    python scripts/verify_webdemo_bootstrap.py --block-numba # emulate Pyodide

Exit code 0 iff every sampled configuration matches (ints/strings exactly,
floats to 1e-9 relative tolerance).
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REL_TOL = 1e-9
ABS_TOL = 1e-9

VERIFY_CONFIGS = [
    ("eca", 110, 11, 200),
    ("eca", 30, 13, 100),
    ("eca", 54, 20, 400),   # seed-stability-only row (seed > 15)
    ("eca", 200, 15, 50),   # atlas-only rule
    ("named", "Diamoeba", 12, 100),
]

SMOKE_CONFIGS = [
    ("named", "S37/B11", 11, 50),
    ("named", "crystal", 11, 10),
    ("life2d", "B36/S23", 11, 50),                                      # arbitrary rulestring (HighLife)
    ("rule3d", '{"survive": [4, 5], "birth": [5, 5], "density": 0.5}', 11, 10),  # custom 3D ranges
    ("rule3d", '{"rulestring": "B5,7,9/S4,6", "density": 0.4}', 11, 10),         # non-contiguous 3D sets
]


def load_committed_rows() -> dict[tuple[str, int, int], dict[str, str]]:
    rows: dict[tuple[str, int, int], dict[str, str]] = {}
    for rel in (
        "outputs/alife_2026/eca_atlas/eca_atlas_runs.csv",
        "outputs/alife_2026/seed_stability/seed_stability_runs.csv",
    ):
        with (ROOT / rel).open(newline="") as fh:
            for row in csv.DictReader(fh):
                rows[(row["rule"], int(row["seed"]), int(row["horizon"]))] = row
    return rows


def compare_value(expected: str, actual) -> tuple[bool, float]:
    """Return (matches, relative_difference)."""
    if expected in ("", "nan"):
        return actual in (None, "", "nan") or (isinstance(actual, float) and math.isnan(actual)), 0.0
    try:
        exp_num = float(expected)
    except ValueError:
        return str(actual) == expected, 0.0
    act_num = float(actual)
    if exp_num == act_num:
        return True, 0.0
    denom = max(abs(exp_num), abs(act_num))
    rel = abs(exp_num - act_num) / denom if denom else 0.0
    return math.isclose(exp_num, act_num, rel_tol=REL_TOL, abs_tol=ABS_TOL), rel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--block-numba", action="store_true",
        help="Make numba unimportable before loading the bootstrap, emulating Pyodide.",
    )
    args = parser.parse_args()

    if args.block_numba:
        sys.modules["numba"] = None  # forces ImportError -> bootstrap installs its stub

    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "webdemo"))
    import bootstrap

    committed = load_committed_rows()
    failures = 0
    max_rel_seen = 0.0

    for family, rule, seed, horizon in VERIFY_CONFIGS:
        result = bootstrap.run_repro(family, rule, seed, horizon)
        record = result["record"]
        key = (record["rule"], seed, horizon)
        expected = committed.get(key)
        if expected is None:
            print(f"FAIL {key}: no committed row found")
            failures += 1
            continue
        mismatches = []
        for column, exp in expected.items():
            ok, rel = compare_value(exp, record.get(column))
            max_rel_seen = max(max_rel_seen, rel)
            if not ok:
                mismatches.append(f"{column}: committed={exp!r} demo={record.get(column)!r}")
        if mismatches:
            failures += 1
            print(f"FAIL {key}:")
            for m in mismatches:
                print(f"    {m}")
        else:
            print(
                f"OK   {key}: period={record['selected_period']} "
                f"shift={record['selected_shift_str']} "
                f"nml={record['selected_nml_bits']:.6f} ({result['runtime_s']}s)"
            )

    for family, rule, seed, horizon in SMOKE_CONFIGS:
        result = bootstrap.run_repro(family, rule, seed, horizon)
        record = result["record"]
        print(
            f"SMOKE {record['rule']} seed={seed} T={horizon}: "
            f"period={record['selected_period']} shift={record['selected_shift_str']} "
            f"({result['runtime_s']}s, {result['n_candidates']} candidates)"
        )

    mode = "numba blocked (Pyodide emulation)" if args.block_numba else "numba available"
    print(f"\nMode: {mode}; max float rel-diff observed: {max_rel_seen:.3e}")
    if failures:
        print(f"{failures} configuration(s) FAILED")
        return 1
    print("All verified configurations reproduce the committed rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
