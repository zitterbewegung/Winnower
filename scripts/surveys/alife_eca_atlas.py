#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_suite import run_eca_atlas_suite


def _parse_horizons(value: str) -> list[int]:
    return [int(piece.strip()) for piece in value.split(",") if piece.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the full ALIFE ECA atlas.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--base-seed", type=int, default=11)
    parser.add_argument("--n-seeds", type=int, default=5)
    parser.add_argument("--horizons", type=str, default="50,100,200,400,800")
    parser.add_argument("--limit-rules", type=int, default=None)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.set_defaults(resume=True)
    args = parser.parse_args()

    manifest = run_eca_atlas_suite(
        output_root=args.output_root,
        base_seed=args.base_seed,
        n_seeds=args.n_seeds,
        horizons=_parse_horizons(args.horizons),
        limit_rules=args.limit_rules,
        resume=args.resume,
    )
    print(f"Wrote ECA atlas outputs to {Path(manifest['output_dir']).resolve()}")


if __name__ == "__main__":
    main()
