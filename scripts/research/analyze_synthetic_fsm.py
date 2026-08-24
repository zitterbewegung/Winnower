#!/usr/bin/env python3
"""Analyse the synthetic-FSM residual/leverage study and emit final artifacts.

Reads the deterministic per-split raw artifacts produced by
``run_synthetic_fsm.py`` and writes the committed result set: combined
row-level CSVs, ``summary.json``, ``manifest.json``, one plot and a hash record.

Example
-------
    PYTHONPATH=src python scripts/research/analyze_synthetic_fsm.py \\
        --raw-dir research/synthetic_fsm/results/raw \\
        --out-dir research/synthetic_fsm/results \\
        --freeze-sha <40-char-sha>
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "winnower-synthetic-fsm"
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["path.simplify"] = False
import matplotlib.pyplot as plt  # noqa: E402

from relative_symmetry_repair import synthetic_fsm as sf  # noqa: E402

ENTRY_SORT = ["split", "family", "seed", "state"]
SUMMARY_SORT = ["split", "family", "seed"]
MATCHED_SORT = ["split", "family", "seed", "analysis", "entry_state", "control_state"]

RECOVERY_GATE = 0.99
SPECIFICITY_GATE = 0.95
INFORMATIVE_GATE = 100

SCIENTIFIC_ARTIFACTS = (
    "fsm_summary.csv.gz",
    "entry_metrics.csv.gz",
    "matched_effects.csv.gz",
    "summary.json",
    "effect_by_split_family.svg",
)


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def _porcelain_lines() -> list[str]:
    """Raw ``git status --porcelain`` lines, with their two-column status
    prefix preserved exactly (no whitespace stripping)."""
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    return [line for line in proc.stdout.split("\n") if line]


def dirty_paths(ignore_dir: Path | None = None) -> list[str]:
    """Porcelain status entries, excluding the analysis output directory."""
    ignore_rel = None
    if ignore_dir is not None:
        try:
            ignore_rel = ignore_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            ignore_rel = None
    entries = []
    for line in _porcelain_lines():
        rel = line[3:].strip().strip('"')
        if ignore_rel and (rel == ignore_rel or rel.startswith(ignore_rel.rstrip("/") + "/")):
            continue
        entries.append(line)
    return entries


def _pkg_versions() -> dict[str, str]:
    import scipy

    return {
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
    }


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------


def recovery_gate(summary: pd.DataFrame) -> dict:
    """Positive control on holdout structured FSMs."""
    s = summary[
        (summary["split"] == "holdout")
        & summary["family"].isin(["permutation", "contracting"])
    ]
    out: dict = {}
    tp = fp = fn = 0
    per_fsm_prec: list[float] = []
    per_fsm_rec: list[float] = []
    for _, row in s.iterrows():
        residuals = set(json.loads(row["fitted_residual_states_json"]))
        planted = int(row["planted_source"])
        hit = planted in residuals
        tp += int(hit)
        fp += len(residuals - {planted})
        fn += int(not hit)
        per_fsm_prec.append(
            (1.0 if hit else 0.0) / len(residuals) if residuals else 0.0
        )
        per_fsm_rec.append(1.0 if hit else 0.0)
    out["n_structured"] = int(len(s))
    out["skeleton_recovery_rate"] = float(s["skeleton_recovered"].mean())
    out["pooled_TP"] = int(tp)
    out["pooled_FP"] = int(fp)
    out["pooled_FN"] = int(fn)
    out["pooled_precision"] = float(tp / (tp + fp)) if (tp + fp) else 0.0
    out["pooled_recall"] = float(tp / (tp + fn)) if (tp + fn) else 0.0
    out["macro_precision"] = float(np.mean(per_fsm_prec)) if per_fsm_prec else 0.0
    out["macro_recall"] = float(np.mean(per_fsm_rec)) if per_fsm_rec else 0.0
    out["residual_count_distribution"] = {
        str(int(k)): int(v)
        for k, v in sorted(s["fitted_residual_count"].value_counts().items())
    }
    for fam in ("permutation", "contracting"):
        f = s[s["family"] == fam]
        f_tp = int(f["planted_source_recovered"].sum())
        f_fp = int(
            sum(
                len(set(json.loads(r["fitted_residual_states_json"])) - {int(r["planted_source"])})
                for _, r in f.iterrows()
            )
        )
        f_fn = int(len(f) - f_tp)
        out[fam] = {
            "n": int(len(f)),
            "skeleton_recovery_rate": float(f["skeleton_recovered"].mean())
            if len(f)
            else float("nan"),
            "pooled_precision": float(f_tp / (f_tp + f_fp)) if (f_tp + f_fp) else 0.0,
            "pooled_recall": float(f_tp / (f_tp + f_fn)) if (f_tp + f_fn) else 0.0,
        }
    out["threshold"] = RECOVERY_GATE
    out["pass"] = bool(
        out["skeleton_recovery_rate"] >= RECOVERY_GATE
        and out["pooled_precision"] >= RECOVERY_GATE
        and out["pooled_recall"] >= RECOVERY_GATE
    )
    return out


def specificity_gate(summary: pd.DataFrame) -> dict:
    r = summary[(summary["split"] == "holdout") & (summary["family"] == "random")]
    n = int(len(r))
    full = int((r["selected_model"] == "full_table").sum())
    rate = float(full / n) if n else 0.0
    return {
        "n_random": n,
        "n_full_table": full,
        "specificity": rate,
        "threshold": SPECIFICITY_GATE,
        "pass": bool(rate >= SPECIFICITY_GATE),
    }


# --------------------------------------------------------------------------
# Estimators
# --------------------------------------------------------------------------


def per_fsm_primary(summary: pd.DataFrame, split: str, outcome: str) -> dict[str, list[float]]:
    s = summary[
        (summary["split"] == split)
        & (summary["informative"] == 1)
        & summary["family"].isin(["permutation", "contracting"])
    ].sort_values(SUMMARY_SORT, kind="mergesort")
    return {
        fam: [float(v) for v in s[s["family"] == fam][outcome].to_numpy()]
        for fam in ("permutation", "contracting")
    }


def per_fsm_secondary(matched: pd.DataFrame, split: str, analysis: str) -> dict[str, list[float]]:
    m = matched[(matched["split"] == split) & (matched["analysis"] == analysis)]
    if m.empty:
        return {"permutation": [], "contracting": []}
    m = m.assign(term=m["diff_theta"] * m["entry_weight"] * m["control_weight"])
    grouped = (
        m.groupby(["family", "fsm_id"], sort=True)["term"].sum().reset_index()
    )
    return {
        fam: [float(v) for v in grouped[grouped["family"] == fam]["term"].to_numpy()]
        for fam in ("permutation", "contracting")
    }


def estimate_block(
    effects: dict[str, list[float]],
    rng: np.random.Generator,
    n_bootstrap: int,
    n_sign_flip: int,
    bootstrap_seed: int,
) -> dict:
    perm, contract = effects["permutation"], effects["contracting"]
    if not perm or not contract:
        return {
            "n_permutation": len(perm),
            "n_contracting": len(contract),
            "combined": float("nan"),
            "available": False,
        }
    combined = sf.equal_family_mean(perm, contract)
    boot = sf.cluster_bootstrap(
        perm, contract, n_resamples=n_bootstrap, seed=bootstrap_seed
    )
    flip = sf.sign_flip_test(perm, contract, combined, rng, n_sign_flip)
    fam_flips = {}
    for fam, vals in (("permutation", perm), ("contracting", contract)):
        obs = float(np.mean(vals))
        fam_flips[fam] = sf.sign_flip_test(vals, None, obs, rng, n_sign_flip)
        fam_flips[fam]["mean"] = obs
        fam_flips[fam]["n"] = len(vals)
        fam_flips[fam]["ci_lo"] = boot[f"{fam}_lo"]
        fam_flips[fam]["ci_hi"] = boot[f"{fam}_hi"]
    raw_left = [fam_flips["permutation"]["p_left"], fam_flips["contracting"]["p_left"]]
    raw_two = [
        fam_flips["permutation"]["p_two_sided"],
        fam_flips["contracting"]["p_two_sided"],
    ]
    holm_left = sf.holm_adjust(raw_left)
    holm_two = sf.holm_adjust(raw_two)
    for i, fam in enumerate(("permutation", "contracting")):
        fam_flips[fam]["p_left_holm"] = holm_left[i]
        fam_flips[fam]["p_two_sided_holm"] = holm_two[i]
    return {
        "available": True,
        "n_permutation": len(perm),
        "n_contracting": len(contract),
        "permutation_mean": float(np.mean(perm)),
        "contracting_mean": float(np.mean(contract)),
        "combined": combined,
        "bootstrap": boot,
        "sign_flip": flip,
        "families": fam_flips,
        "per_fsm_permutation": perm,
        "per_fsm_contracting": contract,
    }


def diagnostics(summary: pd.DataFrame, entries: pd.DataFrame, split: str) -> dict:
    s = summary[
        (summary["split"] == split)
        & (summary["informative"] == 1)
        & summary["family"].isin(["permutation", "contracting"])
    ]
    ent = entries[entries["split"] == split]
    planted = ent[ent["is_planted_source"] == 1][
        ["fsm_id", "pre_on_cycle", "pre_visit_count", "post_cycle_length"]
    ]
    merged = s.merge(planted, on="fsm_id", how="left")

    def by(col):
        g = merged.groupby(col, sort=True)["delta_theta"]
        return {
            str(k): {"n": int(v), "mean": float(m)}
            for (k, m), v in zip(g.mean().items(), g.count().to_numpy())
        }

    return {
        "by_pre_on_cycle": by("pre_on_cycle"),
        "by_pre_visit_count": by("pre_visit_count"),
        "by_planted_cycle_length": by("post_cycle_length"),
        "by_planted_destination_type": by("planted_destination_type"),
        "by_family": by("family"),
    }


# --------------------------------------------------------------------------
# Plot
# --------------------------------------------------------------------------


def make_plot(results: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.2), sharey=True)
    families = ("permutation", "contracting")
    colors = {"permutation": "#1f4e79", "contracting": "#a03030"}
    for ax, split in zip(axes, ("development", "holdout")):
        block = results[split]["primary_theta"]
        ax.axhline(0.0, color="black", linewidth=0.8, zorder=1)
        for xi, fam in enumerate(families):
            vals = block.get(f"per_fsm_{fam}", []) if block.get("available") else []
            n = len(vals)
            if n:
                offs = np.array(
                    [(i / max(n - 1, 1) - 0.5) * 0.55 for i in range(n)]
                )
                ax.scatter(
                    xi + offs,
                    vals,
                    s=6,
                    alpha=0.45,
                    color=colors[fam],
                    linewidths=0,
                    zorder=2,
                )
                mean = block["families"][fam]["mean"]
                lo = block["families"][fam]["ci_lo"]
                hi = block["families"][fam]["ci_hi"]
                ax.errorbar(
                    [xi],
                    [mean],
                    yerr=[[mean - lo], [hi - mean]],
                    fmt="o",
                    color="black",
                    markersize=5,
                    capsize=4,
                    linewidth=1.4,
                    zorder=3,
                )
        if block.get("available"):
            ax.set_title(
                f"{split}\nDelta = {block['combined']:.4f} "
                f"[{block['bootstrap']['combined_lo']:.4f}, "
                f"{block['bootstrap']['combined_hi']:.4f}]",
                fontsize=9,
            )
        else:
            ax.set_title(f"{split}\n(unavailable)", fontsize=9)
        ax.set_xticks(range(len(families)))
        ax.set_xticklabels(families, fontsize=9)
        ax.set_xlim(-0.6, len(families) - 0.4)
    axes[0].set_ylabel(r"per-FSM $\delta_\theta$ (planted - matched controls)", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, format="svg", metadata={"Date": None})
    plt.close(fig)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--freeze-sha", default=None)
    ap.add_argument("--base-sha", default="598a774abaef70236f62a5df8f312632e6cb7caa")
    ap.add_argument("--protocol-revision", type=int, default=0)
    ap.add_argument("--bootstrap-resamples", type=int, default=sf.N_BOOTSTRAP)
    ap.add_argument("--sign-flip-draws", type=int, default=sf.N_SIGN_FLIP)
    ap.add_argument("--allow-dirty", action="store_true")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    started = time.time()
    raw, out = args.raw_dir, args.out_dir
    if not args.allow_dirty:
        dirty = dirty_paths(out)
        if dirty:
            print(
                "ERROR: worktree is dirty outside the output directory:\n  "
                + "\n  ".join(dirty),
                file=sys.stderr,
            )
            return 3
    out.mkdir(parents=True, exist_ok=True)

    frames = {}
    for kind, sort in (
        ("summary", SUMMARY_SORT),
        ("entries", ENTRY_SORT),
        ("matched", MATCHED_SORT),
    ):
        parts = []
        for split in sf.SPLITS:
            p = raw / f"{kind}_{split}.csv.gz"
            if not p.exists():
                print(f"ERROR: missing raw artifact {p}", file=sys.stderr)
                return 2
            parts.append(pd.read_csv(p, compression="gzip"))
        frames[kind] = pd.concat(parts, ignore_index=True)

    summary, entries, matched = frames["summary"], frames["entries"], frames["matched"]

    sf.write_csv_gz(summary, out / "fsm_summary.csv.gz", SUMMARY_SORT)
    sf.write_csv_gz(entries, out / "entry_metrics.csv.gz", ENTRY_SORT)
    sf.write_csv_gz(matched, out / "matched_effects.csv.gz", MATCHED_SORT)

    flip_rng = np.random.Generator(np.random.PCG64(sf.ANALYSIS_SEED_SIGN_FLIP))
    results: dict = {}
    for split in sf.SPLITS:
        block = {}
        block["primary_theta"] = estimate_block(
            per_fsm_primary(summary, split, "delta_theta"),
            flip_rng,
            args.bootstrap_resamples,
            args.sign_flip_draws,
            sf.ANALYSIS_SEED_BOOTSTRAP,
        )
        for outcome in ("delta_C", "delta_w"):
            block[f"secondary_{outcome}"] = estimate_block(
                per_fsm_primary(summary, split, outcome),
                flip_rng,
                args.bootstrap_resamples,
                args.sign_flip_draws,
                sf.ANALYSIS_SEED_BOOTSTRAP,
            )
        for analysis in ("secondary_fitted_pre", "secondary_fitted_post"):
            block[analysis] = estimate_block(
                per_fsm_secondary(matched, split, analysis),
                flip_rng,
                args.bootstrap_resamples,
                args.sign_flip_draws,
                sf.ANALYSIS_SEED_BOOTSTRAP,
            )
        block["diagnostics"] = diagnostics(summary, entries, split)
        results[split] = block

    rec = recovery_gate(summary)
    spec = specificity_gate(summary)
    hold = results["holdout"]["primary_theta"]
    info_counts = {
        "permutation": hold["n_permutation"],
        "contracting": hold["n_contracting"],
    }
    info_gate = {
        "counts": info_counts,
        "threshold": INFORMATIVE_GATE,
        "pass": bool(
            info_counts["permutation"] >= INFORMATIVE_GATE
            and info_counts["contracting"] >= INFORMATIVE_GATE
        ),
    }

    h1_ci = hold["available"] and hold["bootstrap"]["combined_hi"] < 0.0
    h1_p = hold["available"] and hold["sign_flip"]["p_left"] < 0.05
    h1_confirmed = bool(h1_ci and h1_p)
    signs_differ = bool(
        hold["available"]
        and np.sign(hold["permutation_mean"]) != np.sign(hold["contracting_mean"])
    )
    gates_pass = rec["pass"] and spec["pass"]
    if not gates_pass:
        interpretation = (
            "directional effect observed, but not diagnostic of the registered "
            "compression-residual interpretation"
            if h1_confirmed
            else "not diagnostic of the registered compression-residual interpretation"
        )
    elif h1_confirmed:
        interpretation = (
            "FSM-H1 confirmed: sparse compression deviations have lower conditional "
            "attractor-switch leverage than pre-exposure-matched regular transitions"
        )
    else:
        interpretation = (
            "FSM-H1 not confirmed: no registered evidence for lower conditional "
            "attractor-switch leverage at compression residuals"
        )

    summary_json = {
        "protocol_revision": args.protocol_revision,
        "freeze_sha": args.freeze_sha or "",
        "gates": {
            "recovery": rec,
            "specificity": spec,
            "informative_clusters": info_gate,
        },
        "primary": {
            "estimand": "equal-family-weighted mean of per-FSM delta_theta "
            "(planted source minus mean of exact pre-treatment stratum controls)",
            "split": "holdout",
            "n_permutation": hold["n_permutation"],
            "n_contracting": hold["n_contracting"],
            "permutation_mean": hold.get("permutation_mean"),
            "contracting_mean": hold.get("contracting_mean"),
            "Delta": hold.get("combined"),
            "bootstrap_ci_lo": hold["bootstrap"]["combined_lo"] if hold["available"] else None,
            "bootstrap_ci_hi": hold["bootstrap"]["combined_hi"] if hold["available"] else None,
            "p_one_sided_left": hold["sign_flip"]["p_left"] if hold["available"] else None,
            "p_right": hold["sign_flip"]["p_right"] if hold["available"] else None,
            "p_two_sided": hold["sign_flip"]["p_two_sided"] if hold["available"] else None,
            "families": {
                fam: {
                    k: v
                    for k, v in hold["families"][fam].items()
                    if k != "n_draws"
                }
                for fam in ("permutation", "contracting")
            }
            if hold["available"]
            else {},
        },
        "verdicts": {
            "FSM_H1_bootstrap_interval_below_zero": bool(h1_ci),
            "FSM_H1_one_sided_p_below_0.05": bool(h1_p),
            "FSM_H1_confirmed": h1_confirmed,
            "recovery_gate_pass": bool(rec["pass"]),
            "specificity_gate_pass": bool(spec["pass"]),
            "informative_cluster_gate_pass": bool(info_gate["pass"]),
            "family_signs_differ": signs_differ,
            "interpretation_gate": interpretation,
        },
        "development": _strip(results["development"]),
        "holdout": _strip(results["holdout"]),
        "counts": {
            "n_fsms": int(len(summary)),
            "n_entry_rows": int(len(entries)),
            "n_matched_rows": int(len(matched)),
            "by_split_family": {
                f"{s}|{f}": int(
                    ((summary["split"] == s) & (summary["family"] == f)).sum()
                )
                for s in sf.SPLITS
                for f in sf.FAMILIES
            },
        },
        "analysis_config": {
            "bootstrap_resamples": args.bootstrap_resamples,
            "sign_flip_draws": args.sign_flip_draws,
            "bootstrap_seed": sf.ANALYSIS_SEED_BOOTSTRAP,
            "sign_flip_seed": sf.ANALYSIS_SEED_SIGN_FLIP,
            "bit_generator": sf.BIT_GENERATOR,
        },
    }
    sf.write_json(summary_json, out / "summary.json")
    make_plot(results, out / "effect_by_split_family.svg")

    meta = {}
    for split in sf.SPLITS:
        p = raw / f"run_meta_{split}.json"
        if p.exists():
            meta[split] = json.loads(p.read_text())

    artifact_hashes = {}
    for name in SCIENTIFIC_ARTIFACTS:
        p = out / name
        artifact_hashes[name] = {"sha256": sf.sha256_path(p)}
        if name.endswith(".csv.gz"):
            artifact_hashes[name]["content_sha256"] = sf.sha256_csv_gz_content(p)

    manifest = {
        "repository": "zitterbewegung/Winnower",
        "base_sha": args.base_sha,
        "freeze_sha": args.freeze_sha or "",
        "protocol_revision": args.protocol_revision,
        "protocol_sha256": sf.sha256_path(REPO_ROOT / "research/synthetic_fsm/PROTOCOL.md")
        if (REPO_ROOT / "research/synthetic_fsm/PROTOCOL.md").exists()
        else "MISSING",
        "code_hashes": (
            meta.get("holdout", {}).get("code_hashes")
            or meta.get("development", {}).get("code_hashes")
            or {}
        ),
        "result_parent_sha": _git("rev-parse", "HEAD"),
        "result_commit_sha": "recorded externally: the result commit cannot hash itself",
        "python": sys.version.split()[0],
        "packages": _pkg_versions(),
        "platform": platform.platform(),
        "bit_generator": sf.BIT_GENERATOR,
        "commands": {
            split: meta.get(split, {}).get("command", "") for split in sf.SPLITS
        },
        "generator_seeds": {
            split: meta.get(split, {}).get("seeds", {}) for split in sf.SPLITS
        },
        "continuation_blocks": {
            split: meta.get(split, {}).get("continuation_blocks", 0)
            for split in sf.SPLITS
        },
        "resampling_seeds": {
            "cluster_bootstrap": sf.ANALYSIS_SEED_BOOTSTRAP,
            "cluster_sign_flip": sf.ANALYSIS_SEED_SIGN_FLIP,
        },
        "row_counts": summary_json["counts"],
        "informative_clusters": info_counts,
        "runtimes_seconds": {
            "analysis": round(time.time() - started, 3),
        },
        "artifact_hashes": artifact_hashes,
    }
    sf.write_json(manifest, out / "manifest.json")

    lines = []
    for name in SCIENTIFIC_ARTIFACTS:
        lines.append(f"{artifact_hashes[name]['sha256']}  {name}")
        if "content_sha256" in artifact_hashes[name]:
            lines.append(
                f"{artifact_hashes[name]['content_sha256']}  {name} (decompressed content)"
            )
    (out / "hashes.sha256").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    print(json.dumps(summary_json["primary"], indent=2, sort_keys=True))
    print(json.dumps(summary_json["verdicts"], indent=2, sort_keys=True))
    return 0


def _strip(block: dict) -> dict:
    """Drop the bulky per-FSM vectors from the JSON-serialised block."""
    out = {}
    for key, val in block.items():
        if isinstance(val, dict):
            out[key] = {
                k: v
                for k, v in val.items()
                if k not in ("per_fsm_permutation", "per_fsm_contracting")
            }
        else:
            out[key] = val
    return out


if __name__ == "__main__":
    raise SystemExit(main())
