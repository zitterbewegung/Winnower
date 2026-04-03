#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_suite import run_all_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full ALIFE experiment suite.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--paper-dir", type=Path, default=ROOT / "paper")
    parser.add_argument("--base-seed", type=int, default=11)
    parser.add_argument("--lifewiki-limit", type=int, default=None)
    parser.add_argument("--eca-limit", type=int, default=None)
    parser.add_argument("--skip-null-controls", action="store_true")
    parser.add_argument("--skip-seed-stability", action="store_true")
    parser.add_argument("--skip-candidate-range-robustness", action="store_true")
    parser.add_argument("--skip-lifewiki-horizon-sweep", action="store_true")
    parser.add_argument("--skip-eca-atlas", action="store_true")
    parser.add_argument("--skip-3d-survey", action="store_true")
    parser.add_argument("--skip-counterexample-stress", action="store_true")
    parser.add_argument("--skip-paper-reports", action="store_true")
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.set_defaults(resume=True)
    args = parser.parse_args()

    manifest = run_all_suite(
        output_root=args.output_root,
        paper_dir=args.paper_dir,
        base_seed=args.base_seed,
        resume=args.resume,
        run_null_controls=not args.skip_null_controls,
        run_seed_stability=not args.skip_seed_stability,
        run_candidate_range_robustness=not args.skip_candidate_range_robustness,
        run_lifewiki_horizon_sweep=not args.skip_lifewiki_horizon_sweep,
        run_eca_atlas=not args.skip_eca_atlas,
        run_3d_survey=not args.skip_3d_survey,
        run_counterexample_stress=not args.skip_counterexample_stress,
        generate_paper_markdown=not args.skip_paper_reports,
        lifewiki_limit=args.lifewiki_limit,
        eca_limit=args.eca_limit,
    )
    print(f"Wrote ALIFE suite outputs to {Path(manifest['output_root']).resolve()}")


if __name__ == "__main__":
    main()
