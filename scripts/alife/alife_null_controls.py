#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_suite import run_null_controls_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ALIFE null-controls panel.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--base-seed", type=int, default=11)
    parser.add_argument("--n-seeds", type=int, default=1)
    parser.add_argument("--save-decompositions", action="store_true")
    parser.add_argument("--max-decompositions", type=int, default=6)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.set_defaults(resume=True)
    args = parser.parse_args()

    manifest = run_null_controls_suite(
        output_root=args.output_root,
        base_seed=args.base_seed,
        n_seeds=args.n_seeds,
        resume=args.resume,
        save_decompositions=args.save_decompositions,
        max_decompositions=args.max_decompositions,
    )
    print(f"Wrote null-controls outputs to {Path(manifest['output_dir']).resolve()}")


if __name__ == "__main__":
    main()
