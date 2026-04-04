"""Comprehensive test suite round 8: untested code paths, regenerated output
verification, and post-NML-correction stability checks.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# Untested code paths: simulate_2d custom path
# ═══════════════════════════════════════════════════════════════════════════════


class TestSimulate2DCustomPath:
    """Test the custom survive/birth parameter path in simulate_2d."""

    def test_custom_life_matches_named(self):
        from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d

        grid = random_initial_grid(8, 8, seed=0)
        st_named = simulate_2d(grid, steps=10, rule="life")
        st_custom = simulate_2d(grid, steps=10, rule="custom", survive=(2, 3), birth=(3, 3))
        np.testing.assert_array_equal(st_named, st_custom)

    def test_unknown_rule_raises(self):
        from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d

        grid = random_initial_grid(8, 8, seed=0)
        with pytest.raises(ValueError, match="Unknown rule"):
            simulate_2d(grid, steps=5, rule="not_a_rule")

    def test_custom_without_params_raises(self):
        from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d

        grid = random_initial_grid(8, 8, seed=0)
        with pytest.raises(ValueError):
            simulate_2d(grid, steps=5, rule="custom")


# ═══════════════════════════════════════════════════════════════════════════════
# Untested code paths: mdl_total_bits
# ═══════════════════════════════════════════════════════════════════════════════


class TestMDLTotalBits:
    """Test the legacy two-part MDL score function."""

    def test_run_length_encoding(self):
        from relative_symmetry_repair.coding import mdl_total_bits

        mask = np.zeros((10, 8), dtype=bool)
        template, defect, total = mdl_total_bits(2, (8,), 10, mask, defect_encoding="run_length")
        assert total == template + defect
        assert template >= 0
        assert defect >= 0

    def test_lz4_encoding(self):
        from relative_symmetry_repair.coding import mdl_total_bits

        mask = np.zeros((10, 8), dtype=bool)
        template, defect, total = mdl_total_bits(2, (8,), 10, mask, defect_encoding="lz4")
        assert total == template + defect

    def test_unknown_encoding_raises(self):
        from relative_symmetry_repair.coding import mdl_total_bits

        mask = np.zeros((10, 8), dtype=bool)
        with pytest.raises(ValueError, match="[Uu]nknown"):
            mdl_total_bits(2, (8,), 10, mask, defect_encoding="bogus")

    def test_structured_mask_cheaper_than_random(self):
        from relative_symmetry_repair.coding import mdl_total_bits

        structured = np.zeros((20, 16), dtype=bool)
        rng = np.random.default_rng(42)
        random_mask = rng.integers(0, 2, size=(20, 16)).astype(bool)
        _, d_struct, _ = mdl_total_bits(1, (16,), 20, structured, defect_encoding="run_length")
        _, d_random, _ = mdl_total_bits(1, (16,), 20, random_mask, defect_encoding="run_length")
        assert d_struct < d_random


# ═══════════════════════════════════════════════════════════════════════════════
# Untested code paths: template_bits_raw
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemplateBitsRaw:
    def test_1d(self):
        from relative_symmetry_repair.coding import template_bits_raw

        assert template_bits_raw(2, (8,)) == 16

    def test_2d(self):
        from relative_symmetry_repair.coding import template_bits_raw

        assert template_bits_raw(3, (4, 4)) == 48

    def test_3d(self):
        from relative_symmetry_repair.coding import template_bits_raw

        assert template_bits_raw(2, (4, 4, 4)) == 128


# ═══════════════════════════════════════════════════════════════════════════════
# Regenerated output verification
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegeneratedOutputs:
    """Verify that diagram outputs regenerated with the corrected NML formula
    are consistent with the poster text."""

    def test_diamoeba_still_period_2(self):
        """Diamoeba should still select period 2 after NML correction."""
        from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d_general
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd

        initial = random_initial_grid(64, 64, density=0.5, seed=42)
        st = simulate_2d_general(initial, steps=400, birth=[3, 5, 6, 7, 8], survive=[5, 6, 7, 8])
        frame, fits = scan_relative_periodicity_nd(
            st, shift_ranges=[range(-2, 3)] * 2, periods=[1, 2, 3, 4]
        )
        result = period_first_selection_from_frame(frame)
        assert result.selected_period == 2
        assert abs(result.selected_defect_rate - 0.114) < 0.01

    def test_maze_with_mice_still_period_2(self):
        from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d_general
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd

        initial = random_initial_grid(64, 64, density=0.5, seed=42)
        st = simulate_2d_general(initial, steps=400, birth=[3, 7], survive=[1, 2, 3, 4, 5])
        frame, fits = scan_relative_periodicity_nd(
            st, shift_ranges=[range(-2, 3)] * 2, periods=[1, 2, 3, 4]
        )
        result = period_first_selection_from_frame(frame)
        assert result.selected_period == 2


# ═══════════════════════════════════════════════════════════════════════════════
# NML correction stability: margin signs
# ═══════════════════════════════════════════════════════════════════════════════


class TestNMLCorrectionStability:
    """Verify NML correction doesn't flip any period selection."""

    def test_1d_eca54_margin_positive(self):
        from relative_symmetry_repair.eca import simulate_eca
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair import scan_relative_periodicity

        initial = np.zeros(64, dtype=np.uint8)
        initial[32] = 1
        st = simulate_eca(54, initial, steps=200)
        frame, _ = scan_relative_periodicity(st, shifts=range(-2, 3), periods=[1, 2, 3, 4])
        result = period_first_selection_from_frame(frame)
        assert result.margin_bits > 100, f"ECA-54 margin too small: {result.margin_bits}"

    def test_nml_scores_all_positive(self):
        """All NML scores should be positive after the formula correction."""
        from relative_symmetry_repair.repair import scan_relative_periodicity

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 16), dtype=np.uint8)
        frame, _ = scan_relative_periodicity(st, shifts=range(-2, 3), periods=[1, 2, 3, 4])
        assert (frame["nml_bits"] > 0).all(), "Some NML scores are non-positive"
        assert (frame["nml_complexity"] >= 0).all(), "Some complexities are negative"
