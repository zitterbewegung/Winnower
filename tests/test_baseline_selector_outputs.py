from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCORE_COLUMNS = {
    "resid": "defect_rate",
    "nll": "nll_bits",
    "nml": "nml_bits",
}


def _candidate_shift_string(row: pd.Series) -> str:
    if "shift" in row and pd.notna(row["shift"]):
        return str(int(row["shift"]))
    shift_cols = sorted(col for col in row.index if col.startswith("shift_") and pd.notna(row[col]))
    return str(tuple(int(row[col]) for col in shift_cols))


def test_baseline_selector_summary_totals_match_rule_level_counts():
    summary = pd.read_csv(ROOT / "results" / "baseline_selector_summary.csv")
    for row in summary.itertuples(index=False):
        assert int(row.p1 + row.p2 + row.p3 + row.p4plus) == int(row.n_rules)


def test_baseline_rule_level_rows_match_candidate_winners():
    rule_level = pd.read_csv(ROOT / "results" / "baseline_selector_rule_level.csv")
    candidates = pd.read_csv(ROOT / "results" / "baseline_selector_candidates.csv")

    for row in rule_level.itertuples(index=False):
        if getattr(row, "trivial", False) is True:
            continue
        subset = candidates[
            (candidates["dataset"] == row.dataset) & (candidates["rule"] == row.rule)
        ]
        assert len(subset) >= 1
        for prefix in ["resid", "nll", "nml"]:
            selected = subset[subset[f"{prefix}_selected"] == True]
            assert len(selected) == 1
            candidate = selected.iloc[0]
            assert int(candidate["period"]) == int(getattr(row, f"{prefix}_period"))
            assert float(candidate[SCORE_COLUMNS[prefix]]) == float(getattr(row, f"{prefix}_score"))
            assert _candidate_shift_string(candidate) == str(getattr(row, f"{prefix}_shift"))


def test_baseline_nontrivial_rows_have_nonnull_scores():
    rule_level = pd.read_csv(ROOT / "results" / "baseline_selector_rule_level.csv")
    nontrivial = rule_level[rule_level.get("trivial", False) != True]
    for prefix in ["resid", "nll", "nml"]:
        assert nontrivial[f"{prefix}_score"].notna().all()
        assert nontrivial[f"{prefix}_shift"].notna().all()


def test_baseline_metadata_sidecars_exist():
    for name in [
        "baseline_selector_rule_level.csv.metadata.json",
        "baseline_selector_summary.csv.metadata.json",
        "baseline_selector_candidates.csv.metadata.json",
    ]:
        assert (ROOT / "results" / name).exists()
