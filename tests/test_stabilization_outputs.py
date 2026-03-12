from pathlib import Path
import sys

import pandas as pd
from pandas.testing import assert_frame_equal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.stabilization_analysis import run_1d_stabilization


def test_stabilization_outputs_are_internally_consistent():
    results = pd.read_csv(ROOT / "results" / "stabilization_results.csv")
    period_scores = pd.read_csv(ROOT / "results" / "stabilization_period_scores.csv")
    candidates = pd.read_csv(ROOT / "results" / "stabilization_candidates.csv")

    for row in results.itertuples(index=False):
        period_subset = period_scores[
            (period_scores["rule"] == row.rule) & (period_scores["T"] == row.T)
        ].sort_values(["period_rank", "period"])
        assert len(period_subset) >= 1
        best = period_subset.iloc[0]
        assert int(best["period"]) == int(row.selected_period)
        assert str(best["best_shift"]) == str(row.selected_shift)
        if len(period_subset) == 1:
            assert row.margin == float("inf")
        else:
            runner_up = period_subset.iloc[1]
            expected_margin = float(runner_up["nml_bits"] - best["nml_bits"])
            assert abs(expected_margin - float(row.margin)) < 1e-9

        candidate_subset = candidates[
            (candidates["rule"] == row.rule) & (candidates["T"] == row.T)
        ]
        selected_candidates = candidate_subset[candidate_subset["is_selected_candidate"] == True]
        assert len(selected_candidates) == 1
        selected_candidate = selected_candidates.iloc[0]
        assert int(selected_candidate["period"]) == int(row.selected_period)
        assert str(selected_candidate["candidate_shift_str"]) == str(row.selected_shift)


def test_stabilization_metadata_sidecars_exist():
    for name in [
        "stabilization_results.csv.metadata.json",
        "stabilization_period_scores.csv.metadata.json",
        "stabilization_candidates.csv.metadata.json",
        "stabilization_shift_zero_results.csv.metadata.json",
        "stabilization_shift_zero_period_scores.csv.metadata.json",
    ]:
        assert (ROOT / "results" / name).exists()


def test_shift_zero_stabilization_outputs_are_self_consistent():
    results = pd.read_csv(ROOT / "results" / "stabilization_shift_zero_results.csv")
    period_scores = pd.read_csv(ROOT / "results" / "stabilization_shift_zero_period_scores.csv")

    for row in results.itertuples(index=False):
        subset = period_scores[
            (period_scores["rule"] == row.rule) & (period_scores["T"] == row.T)
        ].sort_values(["period_rank", "period"])
        assert len(subset) >= 1
        best = subset.iloc[0]
        assert int(best["period"]) == int(row.selected_period)
        assert str(best["best_shift"]) == str(row.selected_shift)
        assert str(row.selected_shift) in {"0", "(0, 0)", "(0, 0, 0)"}


def test_small_1d_stabilization_run_is_reproducible():
    first_records, first_periods, first_candidates = run_1d_stabilization(
        30,
        width=48,
        shift_radius=3,
        max_period=5,
        seed=11,
    )
    second_records, second_periods, second_candidates = run_1d_stabilization(
        30,
        width=48,
        shift_radius=3,
        max_period=5,
        seed=11,
    )
    assert first_records == second_records
    for left, right in zip(first_periods, second_periods, strict=True):
        assert_frame_equal(left, right)
    for left, right in zip(first_candidates, second_candidates, strict=True):
        assert_frame_equal(left, right)
