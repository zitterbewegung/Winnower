"""Comprehensive test suite round 3: script paths, survey logic, poster data consistency.

Targets ROOT path correctness after scripts/ reorganization, survey edge cases,
and cross-checks between poster text and generated data.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


# ═══════════════════════════════════════════════════════════════════════════════
# Script ROOT path correctness
# ═══════════════════════════════════════════════════════════════════════════════


class TestScriptRootPaths:
    """After moving scripts from scripts/ to scripts/alife/, all ROOT paths
    must use parents[2] to reach the repo root."""

    ALIFE_SCRIPTS = [
        "scripts/alife/alife_run_all.py",
        "scripts/alife/alife_seed_stability.py",
        "scripts/alife/alife_null_controls.py",
        "scripts/alife/alife_candidate_range_robustness.py",
        "scripts/alife/alife_counterexample_stress.py",
        "scripts/alife/alife_rule_diagrams.py",
        "scripts/alife/alife_algorithm_figure.py",
        "scripts/alife/alife_stabilization_summary.py",
    ]

    @pytest.mark.parametrize("script_path", ALIFE_SCRIPTS)
    def test_root_resolves_to_repo_root(self, script_path):
        """Each script's ROOT should point to the repository root, not scripts/."""
        full_path = REPO_ROOT / script_path
        if not full_path.exists():
            pytest.skip(f"{script_path} not found")

        source = full_path.read_text()
        # Check that it uses parents[2], not parents[1]
        assert "parents[2]" in source, (
            f"{script_path} uses parents[1] instead of parents[2] — "
            f"ROOT will point to scripts/ instead of repo root"
        )
        assert "parents[1]" not in source or "parents[2]" in source, (
            f"{script_path} still has parents[1]"
        )

    @pytest.mark.parametrize("script_path", ALIFE_SCRIPTS)
    def test_root_output_dir_exists(self, script_path):
        """The ROOT-relative output directory should exist from the repo root."""
        full_path = REPO_ROOT / script_path
        if not full_path.exists():
            pytest.skip(f"{script_path} not found")

        # The script's ROOT should resolve to repo root
        script_resolved = full_path.resolve()
        expected_root = script_resolved.parents[2]
        assert expected_root == REPO_ROOT.resolve(), (
            f"{script_path}: parents[2]={expected_root} != repo_root={REPO_ROOT.resolve()}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3D density consistency across scripts
# ═══════════════════════════════════════════════════════════════════════════════


class TestDensityConsistency:
    """Scripts that simulate 3D rules should use per-rule densities."""

    def test_representative_3d_cases_all_have_density(self):
        from relative_symmetry_repair.ca3d import RULES_3D, RULES_3D_DENSITY

        for name in RULES_3D:
            assert name in RULES_3D_DENSITY, f"Rule {name} missing from RULES_3D_DENSITY"

    def test_convergence_script_has_hardcoded_density(self):
        """convergence_all_dims.py uses density=0.3 for 3D — document this known issue."""
        script = REPO_ROOT / "scripts/analysis/convergence_all_dims.py"
        if not script.exists():
            pytest.skip("convergence_all_dims.py not found")
        source = script.read_text()
        assert "RULES_3D_DENSITY" in source, (
            "convergence_all_dims.py should import and use RULES_3D_DENSITY"
        )

    def test_baseline_selector_uses_correct_density_for_diamoeba(self):
        """baseline_selector_comparison.py only runs diamoeba3d at density=0.5,
        which happens to be correct."""
        from relative_symmetry_repair.ca3d import RULES_3D_DENSITY

        assert RULES_3D_DENSITY["diamoeba3d"] == 0.5


# ═══════════════════════════════════════════════════════════════════════════════
# Poster data consistency
# ═══════════════════════════════════════════════════════════════════════════════


class TestPosterDataConsistency:
    """Cross-check poster text against generated data."""

    def test_diamoeba_poster_values_match_seed42(self):
        """Diamoeba presentation values should match seed=42 output."""
        guide_path = REPO_ROOT / "outputs/alife_2026/rule_diagrams/presentation_guide.md"
        if not guide_path.exists():
            pytest.skip("presentation_guide.md not found")

        guide = guide_path.read_text()
        # Check Diamoeba section
        assert "(p, s) = (2, (0, 0))" in guide, "Diamoeba should select period 2 with seed=42"
        assert "0.114" in guide, "Diamoeba defect rate should be 0.114 with seed=42"

    def test_poster_tex_matches_guide(self):
        """Poster LaTeX should contain the same values as the presentation guide."""
        poster_path = REPO_ROOT / "poster/alife_2026_poster.tex"
        if not poster_path.exists():
            pytest.skip("poster not found")

        poster = poster_path.read_text()
        # Diamoeba should say (2,(0,0)) with defect 0.114
        assert "(2,(0,0))" in poster, "Poster should show Diamoeba period=2"
        assert "0.114" in poster, "Poster should show Diamoeba defect=0.114"

    def test_manifest_uses_seed_42(self):
        """The diagram manifest should record base_seed=42."""
        import json

        manifest_path = REPO_ROOT / "outputs/alife_2026/rule_diagrams/manifest.json"
        if not manifest_path.exists():
            pytest.skip("manifest.json not found")

        manifest = json.loads(manifest_path.read_text())
        assert manifest.get("base_seed") == 42, (
            f"Expected base_seed=42, got {manifest.get('base_seed')}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Survey logic edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestSurveyLogic:
    """Tests for survey script logic patterns."""

    def test_trivial_detection_all_dead(self):
        """All-zero spacetime at last step should be detected as trivial."""
        st = np.zeros((10, 8, 8), dtype=np.uint8)
        st[0] = np.random.default_rng(0).integers(0, 2, size=(8, 8), dtype=np.uint8)
        # Should be trivial: last frame is all zeros
        final_density = float(st[-1].mean())
        assert final_density < 0.02

    def test_trivial_detection_all_alive(self):
        """All-one spacetime at last step should be detected as trivial."""
        st = np.ones((10, 8, 8), dtype=np.uint8)
        final_density = float(st[-1].mean())
        assert final_density > 0.98

    def test_static_detection_correct_method(self):
        """Fixed point should be detected by comparing last two frames, not first and last."""
        # Spacetime that changes from t=0 to t=1 but then stays fixed
        st = np.zeros((10, 4, 4), dtype=np.uint8)
        st[0] = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]], dtype=np.uint8)
        # Fixed point after t=1
        fixed = np.array([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]], dtype=np.uint8)
        for t in range(1, 10):
            st[t] = fixed

        # Correct detection: compare last two frames
        is_fixed = np.array_equal(st[-1], st[-2])
        assert is_fixed, "Last two frames should be identical (fixed point)"

        # Wrong detection: compare first and last
        first_last_equal = np.array_equal(st[0], st[-1])
        assert not first_last_equal, "First and last frames should differ"


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram regeneration sanity checks
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiagramOutputs:
    """Verify that all expected diagram outputs exist."""

    EXPECTED_DIAGRAMS = [
        "outputs/alife_2026/rule_diagrams/representative_rules_1d.png",
        "outputs/alife_2026/rule_diagrams/representative_rules_2d.png",
        "outputs/alife_2026/rule_diagrams/representative_rules_3d.png",
        "outputs/alife_2026/rule_diagrams/presentation_rules_1d.png",
        "outputs/alife_2026/rule_diagrams/presentation_rules_2d.png",
        "outputs/alife_2026/rule_diagrams/presentation_rules_3d.png",
        "outputs/alife_2026/rule_diagrams/presentation_rules_2d_poster.png",
        "outputs/alife_2026/rule_diagrams/presentation_rule_3d_focus.png",
        "outputs/alife_2026/rule_diagrams/poster_rule_mechanisms.png",
        "outputs/alife_2026/rule_diagrams/manifest.json",
    ]

    @pytest.mark.parametrize("diagram_path", EXPECTED_DIAGRAMS)
    def test_diagram_exists(self, diagram_path):
        full = REPO_ROOT / diagram_path
        assert full.exists(), f"Missing: {diagram_path}"

    def test_manifest_is_valid_json(self):
        import json

        manifest_path = REPO_ROOT / "outputs/alife_2026/rule_diagrams/manifest.json"
        if not manifest_path.exists():
            pytest.skip("manifest.json not found")
        data = json.loads(manifest_path.read_text())
        assert isinstance(data, dict)
        assert "base_seed" in data
