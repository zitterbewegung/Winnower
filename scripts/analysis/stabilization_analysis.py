#!/usr/bin/env python3
"""Experiment 2: finite-horizon stabilization analysis.

For representative rules, run the period-first Bernoulli-NML selector at
increasing horizons and record:
  - selected period
  - runner-up period
  - margin
  - period-level grouped scores
  - raw candidate tables for validation
  - metadata sidecars describing the selector definition
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from relative_symmetry_repair.ca2d import (
    parse_rulestring,
    random_initial_grid,
    simulate_2d,
    simulate_2d_general,
)
from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d
from relative_symmetry_repair.eca import simulate_eca
from relative_symmetry_repair.repair import scan_relative_periodicity
from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd
from relative_symmetry_repair.selection import (
    select_period_from_scan,
    select_period_nd_from_scan,
    selection_summary,
)
from relative_symmetry_repair.selector_tools import (
    SelectorVariant,
    shift_columns,
    shift_handling_from_1d,
    shift_handling_from_nd,
    write_metadata_sidecar,
)

HORIZONS = [50, 100, 200, 400, 600, 800]
# 3D horizons: 3d-life (Bays B5/S45) soup decays toward the quiescent domain and
# is essentially dead past T~50, so the 3D sweep stops there.
HORIZONS_3D = [10, 20, 30, 40, 50]
NML_MODE = "hybrid"
PERIOD_FIRST_SELECTOR = SelectorVariant(
    name="period_first_nml_joint_hybrid",
    selector_type="period_first",
    score_type="bernoulli_nml",
    score_column="nml_bits",
    shift_handling="joint_shift_optimization",
    nml_mode=NML_MODE,
)
SHIFT_ZERO_SELECTOR = SelectorVariant(
    name="period_first_nml_shift_zero_hybrid",
    selector_type="period_first",
    score_type="bernoulli_nml",
    score_column="nml_bits",
    shift_handling="shift_zero_only",
    nml_mode=NML_MODE,
)


def _shift_value(row: pd.Series):
    if "shift" in row:
        return int(row["shift"])
    return tuple(int(row[col]) for col in shift_columns(pd.DataFrame([row])))


def _shift_string(value) -> str:
    if isinstance(value, tuple):
        return str(tuple(int(v) for v in value))
    return str(int(value))


def _row_has_zero_shift(row: pd.Series) -> bool:
    if "shift" in row and pd.notna(row["shift"]):
        return int(row["shift"]) == 0
    cols = [col for col in row.index if col.startswith("shift_") and pd.notna(row[col])]
    return bool(cols) and all(int(row[col]) == 0 for col in cols)


def _period_scores_table(result, *, rule: str, horizon: int) -> pd.DataFrame:
    rows = []
    for rank, score in enumerate(result.all_periods, start=1):
        rows.append(
            {
                "rule": rule,
                "T": horizon,
                "period": score.period,
                "best_shift": _shift_string(score.best_shift),
                "nml_bits": score.nml_bits,
                "nll_bits": score.nll_bits,
                "nml_complexity": score.nml_complexity,
                "defect_rate": score.defect_rate,
                "n_shifts_scanned": score.n_shifts_scanned,
                "period_rank": rank,
                "is_selected_period": rank == 1,
            }
        )
    return pd.DataFrame.from_records(rows)


def _annotate_candidate_frame(
    frame: pd.DataFrame,
    result,
    *,
    rule: str,
    horizon: int,
) -> pd.DataFrame:
    annotated = frame.copy()
    best_shift_by_period = {
        period_score.period: period_score.best_shift for period_score in result.all_periods
    }
    annotated["rule"] = rule
    annotated["T"] = horizon
    annotated["candidate_shift"] = annotated.apply(_shift_value, axis=1)
    annotated["candidate_shift_str"] = annotated["candidate_shift"].map(_shift_string)
    annotated["is_period_best"] = annotated.apply(
        lambda row: row["candidate_shift"] == best_shift_by_period[int(row["period"])],
        axis=1,
    )
    annotated["is_selected_period"] = annotated["period"] == result.selected.period
    annotated["is_selected_candidate"] = annotated["is_period_best"] & annotated["is_selected_period"]
    return annotated.drop(columns=["candidate_shift"])


def run_1d_stabilization(
    rule_num,
    *,
    width: int = 192,
    shift_radius: int = 6,
    max_period: int = 10,
    density: float = 0.5,
    seed: int = 11,
) -> tuple[list[dict[str, object]], list[pd.DataFrame], list[pd.DataFrame]]:
    """Run stabilization sweep for a 1D ECA rule."""
    rng = np.random.default_rng(seed)
    initial = (rng.random(width) < density).astype(np.uint8)
    max_t = max(HORIZONS)
    full_spacetime = simulate_eca(rule_num, initial, max_t)

    shifts = list(range(-shift_radius, shift_radius + 1))
    periods = list(range(1, max_period + 1))
    records = []
    period_scores = []
    candidate_frames = []

    for horizon in HORIZONS:
        spacetime = full_spacetime[:horizon]
        frame, fits = scan_relative_periodicity(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode=NML_MODE,
        )
        result = select_period_from_scan(
            frame,
            fits,
            nml_mode=NML_MODE,
            shift_handling=shift_handling_from_1d(shifts),
        )
        summary = selection_summary(result)
        records.append(
            {
                "rule": f"ECA-{rule_num}",
                "T": horizon,
                "selected_period": summary["selected_period"],
                "selected_shift": _shift_string(summary["selected_shift"]),
                "nml_bits": summary["selected_nml_bits"],
                "runner_up_period": summary.get("runner_up_period"),
                "margin": summary["margin_bits"],
                "status": summary["status"],
                "selector_variant": PERIOD_FIRST_SELECTOR.name,
                "score_type": PERIOD_FIRST_SELECTOR.score_type,
                "nml_mode": NML_MODE,
            }
        )
        period_scores.append(_period_scores_table(result, rule=f"ECA-{rule_num}", horizon=horizon))
        candidate_frames.append(_annotate_candidate_frame(frame, result, rule=f"ECA-{rule_num}", horizon=horizon))
        print(
            f"  ECA-{rule_num} T={horizon:4d}: p={summary['selected_period']} "
            f"margin={summary['margin_bits']:.0f}"
        )

    return records, period_scores, candidate_frames


def run_2d_stabilization(
    rule_name,
    birth,
    survive,
    *,
    width: int = 64,
    height: int = 64,
    shift_radius: int = 2,
    max_period: int = 8,
    density: float = 0.5,
    seed: int = 11,
    rulestring=None,
) -> tuple[list[dict[str, object]], list[pd.DataFrame], list[pd.DataFrame]]:
    """Run stabilization sweep for a 2D rule."""
    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    max_t = max(HORIZONS)

    if rulestring is not None:
        birth_counts, survive_counts = parse_rulestring(rulestring)
        full_spacetime = simulate_2d_general(
            initial,
            steps=max_t,
            birth=birth_counts,
            survive=survive_counts,
        )
    else:
        full_spacetime = simulate_2d(initial, steps=max_t, survive=survive, birth=birth)

    shift_values = list(range(-shift_radius, shift_radius + 1))
    periods = list(range(1, max_period + 1))
    records = []
    period_scores = []
    candidate_frames = []

    for horizon in HORIZONS:
        spacetime = full_spacetime[:horizon]
        frame, fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=[shift_values, shift_values],
            periods=periods,
            nml_mode=NML_MODE,
        )
        result = select_period_nd_from_scan(
            frame,
            fits,
            nml_mode=NML_MODE,
            shift_handling=shift_handling_from_nd([shift_values, shift_values]),
        )
        summary = selection_summary(result)
        records.append(
            {
                "rule": rule_name,
                "T": horizon,
                "selected_period": summary["selected_period"],
                "selected_shift": _shift_string(summary["selected_shift"]),
                "nml_bits": summary["selected_nml_bits"],
                "runner_up_period": summary.get("runner_up_period"),
                "margin": summary["margin_bits"],
                "status": summary["status"],
                "selector_variant": PERIOD_FIRST_SELECTOR.name,
                "score_type": PERIOD_FIRST_SELECTOR.score_type,
                "nml_mode": NML_MODE,
            }
        )
        period_scores.append(_period_scores_table(result, rule=rule_name, horizon=horizon))
        candidate_frames.append(_annotate_candidate_frame(frame, result, rule=rule_name, horizon=horizon))
        print(
            f"  {rule_name:20s} T={horizon:4d}: p={summary['selected_period']} "
            f"margin={summary['margin_bits']:.0f}"
        )

    return records, period_scores, candidate_frames


def run_3d_stabilization(
    survive,
    birth,
    *,
    size: int = 16,
    density: float = 0.5,
    seed: int = 11,
    max_period: int = 6,
) -> tuple[list[dict[str, object]], list[pd.DataFrame], list[pd.DataFrame]]:
    """Run stabilization sweep for a 3D rule."""
    initial = random_initial_volume(size, size, size, density=density, seed=seed)
    max_t = max(HORIZONS_3D)
    full_spacetime = simulate_3d(initial, steps=max_t, survive=survive, birth=birth)

    shift_values = list(range(-1, 2))
    periods = list(range(1, max_period + 1))
    records = []
    period_scores = []
    candidate_frames = []

    for horizon in HORIZONS_3D:
        spacetime = full_spacetime[:horizon]
        frame, fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=[shift_values, shift_values, shift_values],
            periods=periods,
            nml_mode=NML_MODE,
        )
        result = select_period_nd_from_scan(
            frame,
            fits,
            nml_mode=NML_MODE,
            shift_handling=shift_handling_from_nd([shift_values, shift_values, shift_values]),
        )
        summary = selection_summary(result)
        records.append(
            {
                "rule": "3d-life",
                "T": horizon,
                "selected_period": summary["selected_period"],
                "selected_shift": _shift_string(summary["selected_shift"]),
                "nml_bits": summary["selected_nml_bits"],
                "runner_up_period": summary.get("runner_up_period"),
                "margin": summary["margin_bits"],
                "status": summary["status"],
                "selector_variant": PERIOD_FIRST_SELECTOR.name,
                "score_type": PERIOD_FIRST_SELECTOR.score_type,
                "nml_mode": NML_MODE,
            }
        )
        period_scores.append(_period_scores_table(result, rule="3d-life", horizon=horizon))
        candidate_frames.append(_annotate_candidate_frame(frame, result, rule="3d-life", horizon=horizon))
        print(
            f"  3d-life T={horizon:4d}: p={summary['selected_period']} "
            f"margin={summary['margin_bits']:.0f}"
        )

    return records, period_scores, candidate_frames


def compute_stabilization_stats(df_rule: pd.DataFrame) -> tuple[int, int | None]:
    """Compute stabilization point and number of transitions for one rule."""
    periods = df_rule.sort_values("T")["selected_period"].tolist()
    transitions = sum(1 for i in range(1, len(periods)) if periods[i] != periods[i - 1])
    stab_t = None
    for i in range(len(periods)):
        if all(period == periods[i] for period in periods[i:]):
            stab_t = int(df_rule.sort_values("T")["T"].iloc[i])
            break
    return transitions, stab_t


def try_plot(df: pd.DataFrame, figures_dir: Path) -> None:
    """Try to generate stabilization plots. Silently skip if matplotlib unavailable."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plots")
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    for rule_name, group in df.groupby("rule"):
        group = group.sort_values("T")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        ax1.plot(group["T"], group["selected_period"], "o-", linewidth=2)
        ax1.set_xlabel("Horizon T")
        ax1.set_ylabel("Selected Period")
        ax1.set_title(f"{rule_name}: Period vs Horizon")
        ax1.set_ylim(0, group["selected_period"].max() + 1)

        margins = group["margin"].replace([np.inf], np.nan)
        ax2.plot(group["T"], margins, "s-", linewidth=2, color="orange")
        ax2.set_xlabel("Horizon T")
        ax2.set_ylabel("Margin (bits)")
        ax2.set_title(f"{rule_name}: Margin vs Horizon")

        fig.tight_layout()
        safe_name = rule_name.replace("/", "_").replace(" ", "_")
        fig.savefig(figures_dir / f"period_stabilization_{safe_name}.png", dpi=150)
        plt.close(fig)
        print(f"  Saved figure for {rule_name}")


def derive_shift_zero_outputs(
    candidate_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Derive fixed-shift-zero period tables from the raw stabilization scan."""
    shift_zero_candidates = candidate_df[candidate_df.apply(_row_has_zero_shift, axis=1)].copy()
    results_rows: list[dict[str, object]] = []
    period_rows: list[dict[str, object]] = []

    for (rule, horizon), group in shift_zero_candidates.groupby(["rule", "T"]):
        ordered = group.sort_values(["nml_bits", "period"], kind="mergesort").reset_index(drop=True)
        ordered["period_rank"] = np.arange(1, len(ordered) + 1, dtype=np.int64)
        ordered["is_selected_period"] = ordered["period_rank"] == 1

        for candidate in ordered.itertuples(index=False):
            period_rows.append(
                {
                    "rule": rule,
                    "T": int(horizon),
                    "period": int(candidate.period),
                    "best_shift": str(candidate.candidate_shift_str),
                    "nml_bits": float(candidate.nml_bits),
                    "nll_bits": float(candidate.nll_bits),
                    "nml_complexity": float(candidate.nml_complexity),
                    "defect_rate": float(candidate.defect_rate),
                    "n_shifts_scanned": 1,
                    "period_rank": int(candidate.period_rank),
                    "is_selected_period": bool(candidate.is_selected_period),
                }
            )

        best = ordered.iloc[0]
        runner_up = ordered.iloc[1] if len(ordered) > 1 else None
        margin = (
            float(runner_up["nml_bits"] - best["nml_bits"])
            if runner_up is not None
            else float("inf")
        )
        results_rows.append(
            {
                "rule": rule,
                "T": int(horizon),
                "selected_period": int(best["period"]),
                "selected_shift": str(best["candidate_shift_str"]),
                "nml_bits": float(best["nml_bits"]),
                "runner_up_period": int(runner_up["period"]) if runner_up is not None else None,
                "margin": margin,
                "status": "stable_winner" if margin >= 2.0 else ("near_tie" if margin > 0 else "unresolved"),
                "selector_variant": SHIFT_ZERO_SELECTOR.name,
                "score_type": SHIFT_ZERO_SELECTOR.score_type,
                "nml_mode": NML_MODE,
            }
        )

    return (
        pd.DataFrame.from_records(results_rows).sort_values(["rule", "T"]).reset_index(drop=True),
        pd.DataFrame.from_records(period_rows).sort_values(
            ["rule", "T", "period_rank", "period"]
        ).reset_index(drop=True),
    )


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    results_dir = root / "results"
    figures_dir = root / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict[str, object]] = []
    period_score_tables: list[pd.DataFrame] = []
    candidate_tables: list[pd.DataFrame] = []

    print("\n### 1D Stabilization ###")
    for rule_num in [30, 54, 110]:
        records, period_scores, candidates = run_1d_stabilization(rule_num)
        all_records.extend(records)
        period_score_tables.extend(period_scores)
        candidate_tables.extend(candidates)

    print("\n### 2D Stabilization (contiguous-range) ###")
    rules_2d_contiguous = [
        ("S24/B11", (1, 1), (2, 4)),
        ("S11/B37", (3, 7), (1, 1)),
        ("S37/B11", (1, 1), (3, 7)),
    ]
    for name, birth, survive in rules_2d_contiguous:
        records, period_scores, candidates = run_2d_stabilization(
            name,
            birth=birth,
            survive=survive,
        )
        all_records.extend(records)
        period_score_tables.extend(period_scores)
        candidate_tables.extend(candidates)

    print("\n### 2D Stabilization (LifeWiki) ###")
    rules_2d_lifewiki = [
        ("Diamoeba", "B35678/S5678"),
        ("Maze_w_Mice", "B37/S12345"),
    ]
    for name, rulestring in rules_2d_lifewiki:
        records, period_scores, candidates = run_2d_stabilization(
            name,
            birth=None,
            survive=None,
            rulestring=rulestring,
        )
        all_records.extend(records)
        period_score_tables.extend(period_scores)
        candidate_tables.extend(candidates)

    print("\n### 3D Stabilization ###")
    # B5/S45 needs a sparse start (RULES_3D_DENSITY['3d-life']=0.2); at density 0.5
    # every cell has far more than 5 live neighbours and the soup dies in one step.
    # Seed 42 keeps the soup nontrivial across all HORIZONS_3D (seed 11 dies by T=60).
    records, period_scores, candidates = run_3d_stabilization(
        survive=(4, 5), birth=(5, 5), density=0.2, seed=42
    )
    all_records.extend(records)
    period_score_tables.extend(period_scores)
    candidate_tables.extend(candidates)

    results_df = pd.DataFrame.from_records(all_records).sort_values(["rule", "T"]).reset_index(drop=True)
    period_scores_df = pd.concat(period_score_tables, ignore_index=True).sort_values(
        ["rule", "T", "period_rank", "period"]
    ).reset_index(drop=True)
    candidate_df = pd.concat(candidate_tables, ignore_index=True).sort_values(
        ["rule", "T", "period", *shift_columns(pd.concat(candidate_tables, ignore_index=True))]
    ).reset_index(drop=True)

    results_path = results_dir / "stabilization_results.csv"
    period_scores_path = results_dir / "stabilization_period_scores.csv"
    candidates_path = results_dir / "stabilization_candidates.csv"
    shift_zero_results_path = results_dir / "stabilization_shift_zero_results.csv"
    shift_zero_period_scores_path = results_dir / "stabilization_shift_zero_period_scores.csv"

    results_df.to_csv(results_path, index=False)
    period_scores_df.to_csv(period_scores_path, index=False)
    candidate_df.to_csv(candidates_path, index=False)
    shift_zero_results_df, shift_zero_period_scores_df = derive_shift_zero_outputs(candidate_df)
    shift_zero_results_df.to_csv(shift_zero_results_path, index=False)
    shift_zero_period_scores_df.to_csv(shift_zero_period_scores_path, index=False)

    print("\n### Stabilization Statistics ###")
    print(f"{'Rule':<20} {'Transitions':>12} {'Stab. T':>8} {'Final p':>8}")
    for rule_name, group in results_df.groupby("rule"):
        transitions, stab_t = compute_stabilization_stats(group)
        final_p = int(group.sort_values("T")["selected_period"].iloc[-1])
        print(f"{rule_name:<20} {transitions:>12} {str(stab_t):>8} {final_p:>8}")

    try_plot(results_df, figures_dir)

    metadata = {
        "experiment": "stabilization_analysis",
        "boundary_condition": "periodic",
        "selector_variant": PERIOD_FIRST_SELECTOR.to_metadata(),
        "shift_zero_selector_variant": SHIFT_ZERO_SELECTOR.to_metadata(),
        "datasets": {
            "1D": {
                "rules": ["ECA-30", "ECA-54", "ECA-110"],
                "width": 192,
                "density": 0.5,
                "seed": 11,
                "period_range": list(range(1, 11)),
                "shift_range": list(range(-6, 7)),
                "shift_handling": shift_handling_from_1d(range(-6, 7)),
                "horizons": HORIZONS,
            },
            "2D_contiguous": {
                "rules": ["S24/B11", "S11/B37", "S37/B11"],
                "grid_size": [64, 64],
                "density": 0.5,
                "seed": 11,
                "period_range": list(range(1, 9)),
                "shift_range": list(range(-2, 3)),
                "shift_handling": shift_handling_from_nd([range(-2, 3), range(-2, 3)]),
                "horizons": HORIZONS,
            },
            "2D_lifewiki": {
                "rules": ["Diamoeba", "Maze_w_Mice"],
                "grid_size": [64, 64],
                "density": 0.5,
                "seed": 11,
                "period_range": list(range(1, 9)),
                "shift_range": list(range(-2, 3)),
                "shift_handling": shift_handling_from_nd([range(-2, 3), range(-2, 3)]),
                "horizons": HORIZONS,
            },
            "3D": {
                "rules": ["3d-life"],
                "grid_size": [16, 16, 16],
                "density": 0.5,
                "seed": 11,
                "period_range": list(range(1, 7)),
                "shift_range": list(range(-1, 2)),
                "shift_handling": shift_handling_from_nd([range(-1, 2)] * 3),
                "horizons": HORIZONS_3D,
            },
        },
        "outputs": {
            "results": str(results_path.relative_to(root)),
            "period_scores": str(period_scores_path.relative_to(root)),
            "candidates": str(candidates_path.relative_to(root)),
            "shift_zero_results": str(shift_zero_results_path.relative_to(root)),
            "shift_zero_period_scores": str(shift_zero_period_scores_path.relative_to(root)),
        },
    }
    write_metadata_sidecar(results_path, metadata)
    write_metadata_sidecar(period_scores_path, metadata)
    write_metadata_sidecar(candidates_path, metadata)
    write_metadata_sidecar(shift_zero_results_path, metadata)
    write_metadata_sidecar(shift_zero_period_scores_path, metadata)

    print(f"\nSaved results to {results_path}")


if __name__ == "__main__":
    main()
