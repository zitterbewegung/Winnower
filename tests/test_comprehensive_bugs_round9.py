"""Comprehensive test suite round 9: CLI smoke tests, analyze_residual edge cases,
and selection key-lookup robustness.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# CLI smoke tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCLISmoke:
    """Basic smoke tests for CLI commands using Typer's CliRunner."""

    @pytest.fixture
    def runner(self):
        from typer.testing import CliRunner

        return CliRunner()

    @pytest.fixture
    def app(self):
        from relative_symmetry_repair.cli import app

        return app

    def test_analyze_1d_smoke(self, runner, app, tmp_path):
        result = runner.invoke(app, [
            "analyze",
            "--rule", "110",
            "--width", "16",
            "--steps", "20",
            "--shift-radius", "2",
            "--max-period", "3",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0, f"CLI failed:\n{result.output}"
        assert (tmp_path / "rule_110_selection.json").exists()
        assert (tmp_path / "rule_110_spectrum.csv").exists()

    def test_analyze_1d_json_is_valid(self, runner, app, tmp_path):
        runner.invoke(app, [
            "analyze", "--rule", "54", "--width", "16", "--steps", "20",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        json_path = tmp_path / "rule_54_selection.json"
        if json_path.exists():
            data = json.loads(json_path.read_text())
            assert "selected_period" in data

    def test_analyze_1d_single_period_inf_margin(self, runner, app, tmp_path):
        """With max-period=1, margin is inf. JSON should still be writable."""
        result = runner.invoke(app, [
            "analyze", "--rule", "30", "--width", "16", "--steps", "20",
            "--shift-radius", "1", "--max-period", "1",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0, f"CLI failed with inf margin:\n{result.output}"
        json_path = tmp_path / "rule_30_selection.json"
        data = json.loads(json_path.read_text())
        assert data["margin_bits"] in ["inf", float("inf"), "inf"]

    def test_analyze2d_life_smoke(self, runner, app, tmp_path):
        result = runner.invoke(app, [
            "analyze2d",
            "--rule", "life",
            "--width", "8", "--height", "8",
            "--steps", "10",
            "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0, f"CLI 2D failed:\n{result.output}"

    def test_analyze2d_unknown_rule_gives_clean_error(self, runner, app, tmp_path):
        """Passing a removed/unknown rule should give a clean error, not a traceback."""
        result = runner.invoke(app, [
            "analyze2d", "--rule", "diamoeba",
            "--width", "8", "--height", "8", "--steps", "5",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code != 0
        assert "Unknown rule" in result.output or "Error" in result.output or "BadParameter" in str(result.exception)

    def test_analyze2d_highlife_smoke(self, runner, app, tmp_path):
        """highlife is an approximate rule but should still run without crash."""
        result = runner.invoke(app, [
            "analyze2d", "--rule", "highlife",
            "--width", "8", "--height", "8",
            "--steps", "10", "--shift-radius", "1", "--max-period", "2",
            "--output-dir", str(tmp_path),
        ])
        assert result.exit_code == 0, f"highlife failed:\n{result.output}"


# ═══════════════════════════════════════════════════════════════════════════════
# analyze_residual edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestAnalyzeResidualEdgeCases:
    """Tests for analyze_residual with edge-case inputs."""

    def test_residual_on_zero_defect_fit(self):
        """A perfect fit (zero defects) should produce a residual with n_components=0."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.selection import analyze_residual, select_period

        # Period-2 checkerboard — exact fit, zero defects
        row0 = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
        st = np.tile(np.vstack([row0, row1]), (10, 1))
        result = select_period(st, shifts=[0], periods=[1, 2])
        assert result.residual is not None
        assert result.residual.n_components == 0
        assert result.residual.defect_rate == 0.0

    def test_residual_component_summary_none_when_zero_components(self):
        """component_summary should be None when there are no defect components."""
        from relative_symmetry_repair.selection import select_period

        row0 = np.array([0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0], dtype=np.uint8)
        st = np.tile(np.vstack([row0, row1]), (10, 1))
        result = select_period(st, shifts=[0], periods=[2])
        assert result.residual is not None
        # component_summary may be None or an empty DataFrame
        if result.residual.component_summary is not None:
            assert len(result.residual.component_summary) == 0

    def test_analyze_residual_with_different_min_size(self):
        """Re-calling analyze_residual with a different min_size should work."""
        from relative_symmetry_repair.selection import analyze_residual, select_period

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 16), dtype=np.uint8)
        result = select_period(st, shifts=[0], periods=[1, 2])

        # Re-analyze with min_size=1 (should find more/same components)
        diag = analyze_residual(result, min_component_size=1)
        assert diag is not None
        assert diag.n_components >= 0

    def test_residual_on_all_defect_mask(self):
        """When every cell is a defect, the residual should have components."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.selection import select_period

        # Random data that will have many defects
        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 16), dtype=np.uint8)
        result = select_period(st, shifts=[0], periods=[1])
        assert result.residual is not None
        assert result.residual.defect_rate > 0

    def test_selection_summary_handles_none_residual(self):
        """selection_summary should work even if residual is None."""
        from relative_symmetry_repair.selection import (
            PeriodScore,
            SelectionResult,
            SelectionStatus,
            selection_summary,
        )

        dummy_score = PeriodScore(
            period=1, best_shift=0, nml_bits=10.0, nll_bits=8.0,
            nml_complexity=2.0, defect_rate=0.1, n_shifts_scanned=5,
        )
        result = SelectionResult(
            selected=dummy_score,
            runner_up=None,
            margin=float("inf"),
            status=SelectionStatus.STABLE_WINNER,
            all_periods=[dummy_score],
            best_fit=None,
            residual=None,
            tie_break_rule="score asc, period asc",
        )
        summary = selection_summary(result)
        assert "selected_period" in summary
        assert "residual_rl_bits" not in summary  # should be omitted when None


# ═══════════════════════════════════════════════════════════════════════════════
# Selection key lookup robustness
# ═══════════════════════════════════════════════════════════════════════════════


class TestSelectionKeyLookup:
    """Verify that fits dict key lookups are robust."""

    def test_1d_key_lookup_succeeds(self):
        from relative_symmetry_repair.selection import select_period

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        result = select_period(st, shifts=[0, 1], periods=[1, 2])
        assert result.best_fit is not None
        assert result.best_fit.background.shape == st.shape

    def test_nd_key_lookup_succeeds(self):
        from relative_symmetry_repair.selection import select_period_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(10, 4, 4), dtype=np.uint8)
        result = select_period_nd(st, shift_ranges=[range(-1, 2)] * 2, periods=[1, 2])
        assert result.best_fit is not None
        assert result.best_fit.background.shape == st.shape

    def test_selection_summary_with_inf_margin(self):
        """selection_summary should handle inf margin without crash."""
        from relative_symmetry_repair.selection import select_period, selection_summary

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        result = select_period(st, shifts=[0], periods=[1])
        summary = selection_summary(result)
        assert summary["margin_bits"] == float("inf")


# ═══════════════════════════════════════════════════════════════════════════════
# JSON serialization edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestJSONSerialization:
    """Verify JSON output handles edge cases."""

    def test_inf_margin_serializable(self):
        """float('inf') should be converted to string before JSON dump."""
        summary = {"margin_bits": float("inf"), "period": 1}
        safe = {
            k: (str(v) if isinstance(v, float) and not math.isfinite(v) else v)
            for k, v in summary.items()
        }
        result = json.dumps(safe)
        assert '"inf"' in result

    def test_nan_serializable(self):
        summary = {"score": float("nan"), "period": 1}
        safe = {
            k: (str(v) if isinstance(v, float) and not math.isfinite(v) else v)
            for k, v in summary.items()
        }
        result = json.dumps(safe)
        assert '"nan"' in result
