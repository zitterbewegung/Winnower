from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_eca_stabilization_sequences_match_checked_results():
    df = pd.read_csv(ROOT / "results" / "stabilization_results.csv")
    expected = {
        "ECA-30": [2, 1, 1, 1, 1, 1],
        "ECA-54": [4, 4, 4, 4, 4, 4],
        "ECA-110": [1, 7, 4, 4, 4, 4],
    }
    for rule, periods in expected.items():
        actual = (
            df[df["rule"] == rule]
            .sort_values("T")["selected_period"]
            .astype(int)
            .tolist()
        )
        assert actual == periods


def test_lifewiki_named_rule_regressions_match_checked_outputs():
    t100 = pd.read_csv(ROOT / "outputs" / "lifewiki_survey.csv")
    t400 = pd.read_csv(ROOT / "outputs" / "lifewiki_survey_T400.csv")

    diamoeba_100 = t100[t100["name"] == "Diamoeba"].iloc[0]
    diamoeba_400 = t400[t400["name"] == "Diamoeba"].iloc[0]
    fredkin_100 = t100[t100["name"] == "Fredkin"].iloc[0]
    fredkin_400 = t400[t400["name"] == "Fredkin"].iloc[0]
    serviettes_100 = t100[t100["name"] == "Serviettes[5]"].iloc[0]
    serviettes_400 = t400[t400["name"] == "Serviettes[5]"].iloc[0]
    replicator_100 = t100[t100["name"] == "Replicator"].iloc[0]

    assert int(diamoeba_100["selected_period"]) == 1
    assert int(diamoeba_400["selected_period"]) == 2
    assert int(fredkin_100["selected_period"]) == 8
    assert int(fredkin_400["selected_period"]) == 8
    assert int(serviettes_100["selected_period"]) == 2
    assert int(serviettes_400["selected_period"]) == 1
    assert replicator_100["triviality"] == "dead"
    assert replicator_100["status"] == "trivial"


def test_range_threshold_survey_has_metadata_sidecar():
    assert (ROOT / "outputs" / "survey_2d_rules_large.csv.metadata.json").exists()
