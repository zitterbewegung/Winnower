#!/usr/bin/env python3
"""Generate one registered split of the synthetic-FSM residual/leverage study.

Writes deterministic row-level artifacts for a single split.  The holdout split
additionally requires the protocol freeze SHA, a clean worktree, and a
scientific-code tree that matches the freeze commit (unless an explicit
protocol revision is documented on the command line).

Example
-------
    PYTHONPATH=src python scripts/research/run_synthetic_fsm.py \\
        --split development --out-dir research/synthetic_fsm/results/raw
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from relative_symmetry_repair import synthetic_fsm as sf  # noqa: E402

SCIENTIFIC_CODE = (
    "src/relative_symmetry_repair/synthetic_fsm.py",
    "scripts/research/run_synthetic_fsm.py",
    "scripts/research/analyze_synthetic_fsm.py",
    "scripts/research/verify_synthetic_fsm_estimator.py",
    "research/synthetic_fsm/PROTOCOL.md",
)

ENTRY_SORT = ["split", "family", "seed", "state"]
SUMMARY_SORT = ["split", "family", "seed"]
MATCHED_SORT = ["split", "family", "seed", "analysis", "entry_state", "control_state"]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def worktree_is_dirty() -> bool:
    return bool(_git("status", "--porcelain"))


def code_hashes() -> dict[str, str]:
    out = {}
    for rel in SCIENTIFIC_CODE:
        p = REPO_ROOT / rel
        out[rel] = sf.sha256_path(p) if p.exists() else "MISSING"
    return out


def freeze_code_hashes(freeze_sha: str) -> dict[str, str]:
    out = {}
    for rel in SCIENTIFIC_CODE:
        try:
            blob = subprocess.run(
                ["git", "-C", str(REPO_ROOT), "show", f"{freeze_sha}:{rel}"],
                capture_output=True,
                check=True,
            ).stdout
            out[rel] = sf.sha256_bytes(blob)
        except subprocess.CalledProcessError:
            out[rel] = "MISSING"
    return out


def build_one(job: tuple[str, str, int, int]) -> tuple[dict, list[dict], list[dict]]:
    split, family, seed, revision = job
    inst = sf.generate_fsm(split, family, seed, protocol_revision=revision)
    fit = sf.fit_mdl(inst.table)
    entries = sf.entry_rows(inst, fit)
    summary = sf.summary_row(inst, fit, entries)
    matched = sf.matched_effect_rows(inst, fit, entries)
    return summary, entries, matched


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--split",
        required=True,
        choices=list(sf.SPLITS),
        help="registered split to generate",
    )
    ap.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="directory for the raw per-split artifacts",
    )
    ap.add_argument(
        "--protocol-revision",
        type=int,
        default=0,
        help="protocol revision; shifts every seed by 1_000_000 * revision",
    )
    ap.add_argument(
        "--freeze-sha",
        default=None,
        help="40-character protocol freeze commit SHA (required for --split holdout)",
    )
    ap.add_argument(
        "--revision-note",
        default=None,
        help="documented reason when the scientific code differs from the freeze commit",
    )
    ap.add_argument(
        "--continuation-blocks",
        type=int,
        default=0,
        help="number of pre-frozen 40-FSM continuation blocks to append per "
        "structured family (only under the registered informative-count rule)",
    )
    ap.add_argument(
        "--limit-per-family",
        type=int,
        default=0,
        help="TEST ONLY: truncate each family to the first N seeds",
    )
    ap.add_argument(
        "--allow-dirty",
        action="store_true",
        help="TEST ONLY: skip the clean-worktree and freeze-tree guards",
    )
    ap.add_argument("--jobs", type=int, default=1, help="worker processes")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    started = time.time()

    if args.split == "holdout" and not args.freeze_sha:
        print("ERROR: --freeze-sha is required for the holdout split", file=sys.stderr)
        return 2
    if args.freeze_sha and len(args.freeze_sha) != 40:
        print("ERROR: --freeze-sha must be the full 40-character SHA", file=sys.stderr)
        return 2

    if not args.allow_dirty:
        if worktree_is_dirty():
            print(
                "ERROR: worktree is dirty; commit or stash before running",
                file=sys.stderr,
            )
            return 3
        if args.freeze_sha:
            now, frozen = code_hashes(), freeze_code_hashes(args.freeze_sha)
            drift = sorted(k for k in now if now[k] != frozen[k])
            if drift and not (args.protocol_revision > 0 and args.revision_note):
                print(
                    "ERROR: scientific code differs from the freeze commit for "
                    f"{drift}; supply --protocol-revision > 0 and --revision-note",
                    file=sys.stderr,
                )
                return 4

    plan = sf.seed_plan(args.protocol_revision)
    jobs: list[tuple[str, str, int, int]] = []
    for family in sf.FAMILIES:
        seeds = list(plan[(args.split, family)])
        if args.limit_per_family:
            seeds = seeds[: args.limit_per_family]
        for seed in seeds:
            jobs.append((args.split, family, seed, args.protocol_revision))
    for block in range(args.continuation_blocks):
        for family in ("permutation", "contracting"):
            for seed in sf.continuation_seeds(family, block, args.protocol_revision):
                jobs.append((args.split, family, seed, args.protocol_revision))

    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(build_one, jobs, chunksize=8))
    else:
        results = [build_one(job) for job in jobs]

    summaries = [r[0] for r in results]
    entries = [row for r in results for row in r[1]]
    matched = [row for r in results for row in r[2]]

    freeze = args.freeze_sha or ""
    for coll in (summaries, entries, matched):
        for row in coll:
            row["freeze_sha"] = freeze
            row["protocol_revision"] = args.protocol_revision

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    sf.write_csv_gz(pd.DataFrame(summaries), out / f"summary_{args.split}.csv.gz", SUMMARY_SORT)
    sf.write_csv_gz(pd.DataFrame(entries), out / f"entries_{args.split}.csv.gz", ENTRY_SORT)
    sf.write_csv_gz(pd.DataFrame(matched), out / f"matched_{args.split}.csv.gz", MATCHED_SORT)

    n_informative = {
        fam: int(
            sum(
                1
                for s in summaries
                if s["family"] == fam and s["informative"] == 1
            )
        )
        for fam in ("permutation", "contracting")
    }
    meta = {
        "split": args.split,
        "protocol_revision": args.protocol_revision,
        "freeze_sha": freeze,
        "revision_note": args.revision_note or "",
        "bit_generator": sf.BIT_GENERATOR,
        "seeds": {
            fam: [j[2] for j in jobs if j[1] == fam] for fam in sf.FAMILIES
        },
        "n_fsms": len(summaries),
        "n_entries": len(entries),
        "n_matched_rows": len(matched),
        "n_informative": n_informative,
        "continuation_blocks": args.continuation_blocks,
        "limit_per_family": args.limit_per_family,
        "code_hashes": code_hashes(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "platform": platform.platform(),
        "command": "python " + " ".join(sys.argv),
    }
    sf.write_json(meta, out / f"run_meta_{args.split}.json")
    print(
        f"{args.split}: {len(summaries)} FSMs, informative={n_informative}, "
        f"{time.time() - started:.1f}s -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
