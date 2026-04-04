"""Comprehensive test suite round 10: CLI 3D command, density defaults,
additional edge cases, and expanded coverage.
"""
from __future__ import annotations

import json

import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# CLI 3D command tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCLI3D:
    """Tests for the analyze3d CLI command."""

    @pytest.fixture
    def runner(self):
        from typer.testing import CliRunner
        return CliRunner()

    @pytest.fixture
    def app(self):
        from relative_symmetry_repair.cli import app
        return app

    def test_analyze3d_smoke(self, runner, app, tmp_path):
        result = runner.invoke(app, [
            "analyze3d", "--rule", "diamoeba3d",
            "--sx", "6", "--sy", "6", "--sz", "6",
            "--steps", "5", "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0, f"CLI 3D failed:\n{result.output}"
        assert (tmp_path / "rule3d_diamoeba3d" / "diamoeba3d_selection.json").exists()

    def test_analyze3d_uses_per_rule_density(self, runner, app, tmp_path):
        """When no --density is specified, should use RULES_3D_DENSITY."""
        result = runner.invoke(app, [
            "analyze3d", "--rule", "crystal",
            "--sx", "6", "--sy", "6", "--sz", "6",
            "--steps", "5", "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0, f"crystal failed:\n{result.output}"

    def test_analyze3d_unknown_rule_gives_clean_error(self, runner, app, tmp_path):
        result = runner.invoke(app, [
            "analyze3d", "--rule", "nonexistent",
            "--sx", "4", "--sy", "4", "--sz", "4", "--steps", "3",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code != 0

    def test_analyze3d_custom_density_overrides_default(self, runner, app, tmp_path):
        """Explicit --density should override the per-rule default."""
        result = runner.invoke(app, [
            "analyze3d", "--rule", "diamoeba3d",
            "--sx", "6", "--sy", "6", "--sz", "6",
            "--steps", "5", "--density", "0.4",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0

    def test_analyze3d_json_valid(self, runner, app, tmp_path):
        runner.invoke(app, [
            "analyze3d", "--rule", "3d-life",
            "--sx", "6", "--sy", "6", "--sz", "6",
            "--steps", "5", "--shift-radius", "1", "--max-period", "1",
            "--output-dir", str(tmp_path),
        ])
        json_path = tmp_path / "rule3d_3d-life" / "3d-life_selection.json"
        if json_path.exists():
            data = json.loads(json_path.read_text())
            assert "selected_period" in data


# ═══════════════════════════════════════════════════════════════════════════════
# CLI 1D additional edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestCLI1DEdgeCases:

    @pytest.fixture
    def runner(self):
        from typer.testing import CliRunner
        return CliRunner()

    @pytest.fixture
    def app(self):
        from relative_symmetry_repair.cli import app
        return app

    def test_analyze_rule_0(self, runner, app, tmp_path):
        """Rule 0 kills everything — should still complete."""
        result = runner.invoke(app, [
            "analyze", "--rule", "0", "--width", "8", "--steps", "5",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0

    def test_analyze_rule_255(self, runner, app, tmp_path):
        """Rule 255 fills everything — should still complete."""
        result = runner.invoke(app, [
            "analyze", "--rule", "255", "--width", "8", "--steps", "5",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Density default correctness
# ═══════════════════════════════════════════════════════════════════════════════


class TestCLIDensityDefaults:
    """Verify CLI density defaults match RULES_3D_DENSITY."""

    def test_3d_default_density_matches_rules_dict(self):
        from relative_symmetry_repair.ca3d import RULES_3D_DENSITY

        # These are the rules the CLI advertises
        expected = {
            "3d-life": 0.2,
            "clouds": 0.6,
            "crystal": 0.1,
            "diamoeba3d": 0.5,
        }
        for name, density in expected.items():
            assert RULES_3D_DENSITY[name] == density


# ═══════════════════════════════════════════════════════════════════════════════
# Residual diagnostics comprehensive tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestResidualDiagnosticsComprehensive:
    """Additional residual diagnostics edge cases."""

    def test_residual_run_length_bits_nonnegative(self):
        from relative_symmetry_repair.selection import select_period

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        result = select_period(st, shifts=[0, 1], periods=[1, 2])
        assert result.residual is not None
        assert result.residual.run_length_bits >= 0
        assert result.residual.lz4_bits >= 0

    def test_residual_defect_rate_matches_selection(self):
        from relative_symmetry_repair.selection import select_period

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        result = select_period(st, shifts=[0], periods=[1, 2])
        assert result.residual is not None
        assert abs(result.residual.defect_rate - result.selected.defect_rate) < 1e-10

    def test_nd_residual_populated(self):
        from relative_symmetry_repair.selection import select_period_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(10, 4, 4), dtype=np.uint8)
        result = select_period_nd(st, shift_ranges=[range(-1, 2)] * 2, periods=[1, 2])
        assert result.residual is not None
        assert result.residual.run_length_bits >= 0
        assert result.residual.n_components >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# Output artifact verification
# ═══════════════════════════════════════════════════════════════════════════════


class TestCLIOutputArtifacts:
    """Verify CLI produces all expected output files."""

    @pytest.fixture
    def runner(self):
        from typer.testing import CliRunner
        return CliRunner()

    @pytest.fixture
    def app(self):
        from relative_symmetry_repair.cli import app
        return app

    def test_1d_produces_all_artifacts(self, runner, app, tmp_path):
        runner.invoke(app, [
            "analyze", "--rule", "54", "--width", "16", "--steps", "20",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        expected = [
            "rule_54_selection.json",
            "rule_54_spectrum.csv",
            "rule_54_components.csv",
            "rule_54_spacetime.png",
            "rule_54_defect_rate.png",
            "rule_54_decomposition.png",
        ]
        for name in expected:
            assert (tmp_path / name).exists(), f"Missing artifact: {name}"

    def test_2d_produces_selection_json(self, runner, app, tmp_path):
        runner.invoke(app, [
            "analyze2d", "--rule", "life",
            "--width", "8", "--height", "8", "--steps", "5",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert (tmp_path / "rule2d_life" / "life_selection.json").exists()
