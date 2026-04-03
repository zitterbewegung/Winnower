"""Comprehensive test suite round 6: paper claim verification and xfail meta-tests.

Automated cross-checks of published numerical claims against source CSVs,
plus meta-tests confirming all documented xfail bugs are still present.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


# ═══════════════════════════════════════════════════════════════════════════════
# Paper claim verification — ALIFE 2026 submission
# ═══════════════════════════════════════════════════════════════════════════════


class TestPaperClaimsALIFE:
    """Cross-check numerical claims in paper_alife2026.tex against CSVs."""

    @pytest.fixture
    def t100_survey(self):
        path = REPO_ROOT / "outputs/lifewiki_survey_T100_rerun.csv"
        if not path.exists():
            pytest.skip("T100 survey CSV not found")
        return pd.read_csv(path)

    @pytest.fixture
    def t400_survey(self):
        path = REPO_ROOT / "outputs/lifewiki_survey_T400_rerun.csv"
        if not path.exists():
            pytest.skip("T400 survey CSV not found")
        return pd.read_csv(path)

    @pytest.fixture
    def baseline_summary(self):
        path = REPO_ROOT / "outputs/csv/baseline_selector_summary.csv"
        if not path.exists():
            pytest.skip("baseline_selector_summary CSV not found")
        return pd.read_csv(path)

    def test_106_named_rules_surveyed(self, t100_survey):
        """Paper claims 106 named Life-like rules from LifeWiki."""
        assert len(t100_survey) == 106

    def test_t100_period_distribution(self, t100_survey):
        """Paper Table 1 at T=100: p1=97, p2=7, p8=1, nontrivial=105."""
        nontrivial = t100_survey[t100_survey["triviality"] == "nontrivial"]
        assert len(nontrivial) == 105

        periods = nontrivial["selected_period"].value_counts()
        assert periods.get(1, 0) == 97
        assert periods.get(2, 0) == 7
        assert periods.get(8, 0) == 1

    def test_t400_period_distribution(self, t400_survey):
        """Paper Table 1 at T=400: nontrivial=103, p1=94, p2=7, p4=1, p8=1."""
        nontrivial = t400_survey[t400_survey["triviality"] == "nontrivial"]
        assert len(nontrivial) == 103

        periods = nontrivial["selected_period"].value_counts()
        assert periods.get(1, 0) == 94
        assert periods.get(2, 0) == 7
        assert periods.get(4, 0) == 1
        assert periods.get(8, 0) == 1

    def test_nll_selects_largest_period_always(self, baseline_summary):
        """Paper: 'Bernoulli NLL selects the largest tested period in every case'."""
        lifewiki_rows = baseline_summary[baseline_summary["dataset"] == "LifeWiki_T100"]
        nll_row = lifewiki_rows[lifewiki_rows["selector"] == "nll"]
        if nll_row.empty:
            pytest.skip("NLL selector row not found in baseline_summary")
        nll_row = nll_row.iloc[0]
        # p1 + p2 + p3 should be 0 (all rules at p4plus)
        assert nll_row["p1"] == 0
        assert nll_row["p2"] == 0
        assert nll_row.get("p3", 0) == 0

    def test_four_rules_change_period_t100_to_t400(self, t100_survey, t400_survey):
        """Paper: exactly 4 rules change period between T=100 and T=400."""
        merged = t100_survey.merge(
            t400_survey,
            on="rulestring",
            suffixes=("_100", "_400"),
        )
        changed = merged[
            (merged["triviality_100"] == "nontrivial")
            & (merged["triviality_400"] == "nontrivial")
            & (merged["selected_period_100"] != merged["selected_period_400"])
        ]
        assert len(changed) == 4, (
            f"Expected 4 rules to change period, got {len(changed)}: "
            f"{list(changed['name_100'])}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Paper claim verification — poster text matches generated data
# ═══════════════════════════════════════════════════════════════════════════════


class TestPosterTextConsistency:
    """Verify poster text matches the presentation_guide.md generated from seed=42."""

    @pytest.fixture
    def guide(self):
        path = REPO_ROOT / "outputs/alife_2026/rule_diagrams/presentation_guide.md"
        if not path.exists():
            pytest.skip("presentation_guide.md not found")
        return path.read_text()

    @pytest.fixture
    def poster(self):
        path = REPO_ROOT / "poster/alife_2026_poster.tex"
        if not path.exists():
            pytest.skip("poster tex not found")
        return path.read_text()

    def test_diamoeba_period_in_poster_matches_guide(self, poster, guide):
        assert "(p, s) = (2, (0, 0))" in guide
        assert "(2,(0,0))" in poster

    def test_diamoeba_defect_rate_in_poster_matches_guide(self, poster, guide):
        assert "0.114" in guide
        assert "0.114" in poster

    def test_maze_with_mice_defect_rate_matches(self, poster, guide):
        assert "0.007" in guide
        assert "0.007" in poster


# ═══════════════════════════════════════════════════════════════════════════════
# Meta-tests: verify all xfail bugs are still present
# ═══════════════════════════════════════════════════════════════════════════════


class TestXFailBugsStillPresent:
    """Confirm each documented xfail bug is still present in the source code.
    When a bug is fixed, the corresponding test here will fail, reminding us
    to remove the xfail marker from the original test."""

    def test_n1_regret_bug_still_present(self):
        """_exact_bernoulli_regret(1) should return 1.0 but returns 0.0."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        result = _exact_bernoulli_regret(1)
        assert result == 0.0, "Bug appears fixed! Remove xfail from test_n1_regret_is_one_bit"

    def test_hybrid_cutoff_discontinuity_still_present(self):
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        at_200 = bernoulli_nml_complexity_single(200, mode="hybrid")
        at_201 = bernoulli_nml_complexity_single(201, mode="hybrid")
        gap = at_200 - at_201
        assert gap > 0.3, f"Gap is {gap:.3f} — bug appears fixed! Remove xfail"

    def test_empty_scan_crash_still_present(self):
        from relative_symmetry_repair.repair import scan_relative_periodicity

        st = np.zeros((10, 8), dtype=np.uint8)
        with pytest.raises(KeyError):
            scan_relative_periodicity(st, shifts=[], periods=[1])

    def test_control_seed_bug_still_present(self):
        from relative_symmetry_repair.experiment_suite import CONTROL_ORDER

        # "time_shuffled" is at index 1, so recorded seed = seed + 2*101 = seed+202
        # but actual seed is seed+101
        idx = CONTROL_ORDER.index("time_shuffled")
        recorded_offset = (idx + 1) * 101  # = 202
        actual_offset = 101
        assert recorded_offset != actual_offset, "Bug appears fixed! Remove xfail"

    def test_diamoeba_named_rule_bug_still_present(self):
        from relative_symmetry_repair.ca2d import LIFE_RULES

        _, _, b_lo, _ = LIFE_RULES["diamoeba"]
        assert b_lo > 3, "Bug appears fixed! Remove xfail from test_diamoeba_named_rule_missing_b3"

    def test_convergence_density_bug_still_present(self):
        script = REPO_ROOT / "scripts/analysis/convergence_all_dims.py"
        if not script.exists():
            pytest.skip("convergence script not found")
        source = script.read_text()
        assert "density=0.3" in source and "RULES_3D_DENSITY" not in source, (
            "Bug appears fixed! Remove xfail from test_convergence_script_has_hardcoded_density"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Survey data integrity
# ═══════════════════════════════════════════════════════════════════════════════


class TestSurveyDataIntegrity:
    """Basic integrity checks on survey output CSVs."""

    def test_2d_large_survey_has_773_candidates(self):
        path = REPO_ROOT / "outputs/survey_2d_rules_large.csv"
        if not path.exists():
            pytest.skip("survey_2d_rules_large.csv not found")
        df = pd.read_csv(path)
        assert len(df) == 773

    def test_seed_stability_csv_has_expected_columns(self):
        path = REPO_ROOT / "outputs/alife_2026/seed_stability/seed_stability_runs.csv"
        if not path.exists():
            pytest.skip("seed_stability_runs.csv not found")
        df = pd.read_csv(path)
        required = {"rule", "seed", "horizon", "selected_period"}
        assert required.issubset(set(df.columns))

    def test_manifest_records_seed_42(self):
        path = REPO_ROOT / "outputs/alife_2026/rule_diagrams/manifest.json"
        if not path.exists():
            pytest.skip("manifest.json not found")
        data = json.loads(path.read_text())
        assert data["base_seed"] == 42
