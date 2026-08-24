#!/usr/bin/env python3
"""Independent re-implementation of the registered primary estimator.

This script is a clean-room check.  It deliberately imports nothing from the
production experiment code: only the standard library and pandas.  It reads the
committed ``matched_effects.csv.gz`` bytes, recomputes the confirmatory
estimate from first principles, and compares against ``summary.json``.

Estimator, restated from the protocol without reference to the production code:

* keep the holdout rows whose ``analysis`` is ``primary_planted_pre``;
* for each FSM, average ``diff_theta`` over that FSM's control rows;
* average those per-FSM values within each structured family;
* combine the two family means with equal weight.

Example
-------
    python scripts/research/verify_synthetic_fsm_estimator.py \\
        --results-dir research/synthetic_fsm/results
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

TOLERANCE = 1e-12


def sha256_file(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def independent_primary_estimate(matched_path: str, split: str) -> dict:
    """Recompute the equal-family-weighted primary estimate from raw rows."""
    frame = pd.read_csv(matched_path, compression="gzip")
    rows = frame[
        (frame["split"] == split) & (frame["analysis"] == "primary_planted_pre")
    ]
    per_fsm: dict[str, list] = {}
    for record in rows.to_dict("records"):
        key = (str(record["family"]), str(record["fsm_id"]))
        per_fsm.setdefault(key, []).append(float(record["diff_theta"]))
    family_values: dict[str, list] = {"permutation": [], "contracting": []}
    for (family, _fsm_id), diffs in sorted(per_fsm.items()):
        if family not in family_values:
            continue
        family_values[family].append(sum(diffs) / len(diffs))
    means = {}
    for family, values in family_values.items():
        means[family] = sum(values) / len(values) if values else float("nan")
    combined = 0.5 * means["permutation"] + 0.5 * means["contracting"]
    return {
        "split": split,
        "permutation_mean": means["permutation"],
        "contracting_mean": means["contracting"],
        "combined": combined,
        "n_permutation": len(family_values["permutation"]),
        "n_contracting": len(family_values["contracting"]),
    }


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--results-dir",
        required=True,
        type=Path,
        help="directory containing matched_effects.csv.gz and summary.json",
    )
    parser.add_argument(
        "--split", default="holdout", help="split to verify (default: holdout)"
    )
    parser.add_argument(
        "--out", type=Path, default=None, help="path for independent_check.json"
    )
    parser.add_argument("--tolerance", type=float, default=TOLERANCE)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    matched = args.results_dir / "matched_effects.csv.gz"
    summary_path = args.results_dir / "summary.json"
    for path in (matched, summary_path):
        if not path.exists():
            print(f"ERROR: missing {path}", file=sys.stderr)
            return 2

    independent = independent_primary_estimate(str(matched), args.split)
    summary = json.loads(summary_path.read_text())
    production = {
        "combined": summary["primary"]["Delta"],
        "permutation_mean": summary["primary"]["permutation_mean"],
        "contracting_mean": summary["primary"]["contracting_mean"],
    }
    differences = {
        key: abs(float(production[key]) - float(independent[key]))
        for key in production
    }
    passed = all(value <= args.tolerance for value in differences.values())
    report = {
        "command": "python " + " ".join(sys.argv),
        "split": args.split,
        "tolerance": args.tolerance,
        "production": production,
        "independent": {
            key: independent[key]
            for key in ("combined", "permutation_mean", "contracting_mean")
        },
        "independent_counts": {
            "n_permutation": independent["n_permutation"],
            "n_contracting": independent["n_contracting"],
        },
        "absolute_differences": differences,
        "input_hashes": {
            "matched_effects.csv.gz": sha256_file(str(matched)),
            "summary.json": sha256_file(str(summary_path)),
        },
        "pass": bool(passed),
    }
    destination = args.out or (args.results_dir / "independent_check.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(
        (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
