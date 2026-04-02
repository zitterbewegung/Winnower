#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_suite import run_counterexample_stress_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan generated ALIFE outputs for stress cases.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--very-small-margin-bits", type=float, default=0.5)
    parser.add_argument("--repeated-tie-threshold", type=int, default=3)
    args = parser.parse_args()

    manifest = run_counterexample_stress_suite(
        output_root=args.output_root,
        very_small_margin_bits=args.very_small_margin_bits,
        repeated_tie_threshold=args.repeated_tie_threshold,
    )
    print(f"Wrote counterexample stress outputs to {Path(manifest['output_dir']).resolve()}")


if __name__ == "__main__":
    main()
