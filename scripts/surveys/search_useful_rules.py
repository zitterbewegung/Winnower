#!/usr/bin/env python3
"""Sweep a rule family for rules worth reporting, and rank them.

A rule is only informative if something is still happening at the horizon it
is observed over: a lattice that has died out or frozen is exactly
relative-periodic under ``p=1, s=0`` at zero defect rate, so it fits perfectly
without exhibiting anything.

This script makes the check mechanical: it screens a whole rule family for
sustained activity (each rule at its own best initial density), runs the
shipped selector on the survivors, and ranks them by defect rate --- the
paper's own target signature, a domain template covering most of the run with
a sparse set of localized departures.

Usage:
    # the family RULES_3D is drawn from (142,884 rules; ~11 min/core to screen)
    PYTHONPATH=src python scripts/surveys/search_useful_rules.py --space rule3d

    # a quick representative sample
    PYTHONPATH=src python scripts/surveys/search_useful_rules.py \\
        --space rule3d --limit 2000 --shuffle-seed 7

Outputs (under --output-root, default outputs/rule_search/<space>/):
    rule_search_results.csv    one row per rule that passed screening, ranked
    rule_search_screen.csv     verdict for every rule screened
    manifest.json              settings, counts, runtime
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd  # noqa: E402

from relative_symmetry_repair.experiment_core import (  # noqa: E402
    ensure_output_dir,
    write_json_manifest,
    write_summary_csv,
)
from relative_symmetry_repair.rule_search import (  # noqa: E402
    DEFAULT_SCREEN,
    RULE_SPACES,
    ScreenSettings,
    count_rule_space,
    evaluate_rule,
    rule_space,
    screen_rule,
    usefulness_key,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--space", choices=sorted(RULE_SPACES), default="rule3d")
    parser.add_argument("--limit", type=int, default=None, help="Screen at most this many rules.")
    parser.add_argument("--shuffle-seed", type=int, default=None,
                        help="Sample the space at random instead of taking the first --limit in order.")
    parser.add_argument("--screen-size", type=int, default=None)
    parser.add_argument("--screen-horizon", type=int, default=None)
    parser.add_argument("--eval-size", type=int, default=None)
    parser.add_argument("--eval-horizon", type=int, default=None)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--no-evaluate", dest="evaluate", action="store_false",
                        help="Screen only; skip the (much slower) selector stage.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "rule_search")
    parser.set_defaults(evaluate=True)
    args = parser.parse_args()

    specs = list(rule_space(args.space))
    total = len(specs)
    if args.shuffle_seed is not None:
        import numpy as np

        np.random.default_rng(args.shuffle_seed).shuffle(specs)
    if args.limit is not None:
        specs = specs[: args.limit]

    base = DEFAULT_SCREEN[specs[0].dimension]
    settings = ScreenSettings(
        size=args.screen_size or base.size,
        horizon=args.screen_horizon or base.horizon,
        densities=base.densities,
        seed=args.seed,
    )
    eval_size = args.eval_size or settings.size
    eval_horizon = args.eval_horizon or settings.horizon

    print(f"space {args.space!r}: {count_rule_space(args.space):,} rules total; screening {len(specs):,}")
    print(f"screen: {settings.size}^{specs[0].dimension} T={settings.horizon} "
          f"densities={list(settings.densities)}")
    if args.evaluate:
        print(f"evaluate survivors: {eval_size}^{specs[0].dimension} T={eval_horizon} (per-rule density)")

    started = time.time()
    screen_rows, results = [], []
    counts = {"extinct": 0, "saturated": 0, "frozen": 0, "active": 0}

    for index, spec in enumerate(specs):
        screen = screen_rule(spec, settings)
        counts[screen.verdict] += 1
        screen_rows.append({
            "label": spec.label, "family": spec.family, "dimension": spec.dimension,
            "verdict": screen.verdict, "density": screen.density,
            "extinct_at": screen.extinct_at, "frames": screen.frames,
            "final_density": screen.final_density, "activity": screen.activity,
        })
        if screen.passed and args.evaluate:
            evaluation = evaluate_rule(
                spec, screen, size=eval_size, horizon=eval_horizon,
                density=screen.density, seed=args.seed,
            )
            results.append(evaluation)
        if (index + 1) % 250 == 0 or index + 1 == len(specs):
            elapsed = time.time() - started
            rate = (index + 1) / elapsed
            print(f"  {index+1:>7,}/{len(specs):,}  {counts['active']:>6,} active  "
                  f"{rate:6.1f} rules/s  eta {(len(specs)-index-1)/rate/60:5.1f} min",
                  flush=True)

    results.sort(key=usefulness_key)
    output_dir = ensure_output_dir(Path(args.output_root) / args.space)

    screen_frame = pd.DataFrame.from_records(screen_rows)
    screen_path = write_summary_csv(screen_frame, output_dir / "rule_search_screen.csv")

    results_path = None
    if results:
        results_frame = pd.DataFrame.from_records([
            {
                "rank": rank,
                "label": e.spec.label,
                "family": e.spec.family,
                "dimension": e.spec.dimension,
                "survive_lo": e.spec.survive[0] if e.spec.survive else None,
                "survive_hi": e.spec.survive[1] if e.spec.survive else None,
                "birth_lo": e.spec.birth[0] if e.spec.birth else None,
                "birth_hi": e.spec.birth[1] if e.spec.birth else None,
                "rulestring": e.spec.rulestring,
                "rule_number": e.spec.rule_number,
                "density": e.density,
                "size": e.size,
                "horizon": e.horizon,
                "selected_period": e.selected_period,
                "selected_shift": str(e.selected_shift),
                "defect_rate": e.defect_rate,
                "bits_per_site": e.bits_per_site,
                "margin_bits": e.margin_bits,
                "status": e.status,
                "screen_activity": e.screen.activity,
                "screen_final_density": e.screen.final_density,
            }
            for rank, e in enumerate(results, start=1)
        ])
        results_path = write_summary_csv(results_frame, output_dir / "rule_search_results.csv")

    runtime = time.time() - started
    write_json_manifest(output_dir / "manifest.json", {
        "experiment": "rule_search",
        "space": args.space,
        "space_size": total,
        "screened": len(specs),
        "shuffle_seed": args.shuffle_seed,
        "counts": counts,
        "screen_settings": {
            "size": settings.size, "horizon": settings.horizon,
            "densities": list(settings.densities), "seed": settings.seed,
        },
        "evaluation_settings": {"size": eval_size, "horizon": eval_horizon, "seed": args.seed}
        if args.evaluate else None,
        "runtime_seconds": runtime,
    })

    print(f"\nscreened {len(specs):,} rules in {runtime/60:.1f} min: {counts}")
    print(f"  screen table : {screen_path}")
    if results_path:
        print(f"  ranked table : {results_path}  ({len(results):,} rules)")
        print("\ntop 10 by defect rate (sparsest mask = clearest domain + localized defects):")
        print(f"  {'rule':22s} {'dens':>5s} {'p':>3s} {'defect':>9s} {'bits/site':>10s}")
        for e in results[:10]:
            print(f"  {e.spec.label:22s} {e.density:5.2f} {e.selected_period:>3d} "
                  f"{e.defect_rate:9.5f} {e.bits_per_site:10.4f}")


if __name__ == "__main__":
    main()
