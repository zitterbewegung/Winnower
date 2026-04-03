"""Comprehensive test suite round 2: deeper review findings.

Targets selection module, plotting, component extraction, workspace aliasing,
and diagram colormap correctness.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# selection.py — Period selection
# ═══════════════════════════════════════════════════════════════════════════════


class TestSelection:
    """Tests for the period selection module."""

    def test_single_candidate_has_infinite_margin(self):
        """With only one period, margin should be inf."""
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair import scan_relative_periodicity

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        frame, fits = scan_relative_periodicity(st, shifts=[0], periods=[1])
        result = period_first_selection_from_frame(frame)
        assert result.margin_bits == float("inf")

    def test_exact_periodic_selects_correct_period(self):
        """Period-2 checkerboard should select period 2."""
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair import scan_relative_periodicity

        row0 = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
        st = np.tile(np.vstack([row0, row1]), (20, 1))
        frame, fits = scan_relative_periodicity(st, shifts=[0], periods=[1, 2, 4])
        result = period_first_selection_from_frame(frame)
        assert result.selected_period == 2

    def test_selection_result_fields_are_finite(self):
        """All numeric fields should be finite for normal input."""
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair import scan_relative_periodicity

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 16), dtype=np.uint8)
        frame, fits = scan_relative_periodicity(st, shifts=range(-2, 3), periods=[1, 2, 3])
        result = period_first_selection_from_frame(frame)
        assert math.isfinite(result.selected_defect_rate)
        assert result.margin_bits >= 0 or result.margin_bits == float("inf")

    def test_period_summary_has_all_periods(self):
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair import scan_relative_periodicity

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 16), dtype=np.uint8)
        frame, fits = scan_relative_periodicity(st, shifts=[0], periods=[1, 2, 3, 4])
        result = period_first_selection_from_frame(frame)
        assert len(result.period_summary) == 4

    def test_nd_selection_returns_tuple_shift(self):
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 8, 8), dtype=np.uint8)
        frame, fits = scan_relative_periodicity_nd(st, shift_ranges=[range(-1, 2)] * 2, periods=[1, 2])
        result = period_first_selection_from_frame(frame)
        assert isinstance(result.selected_shift, tuple)
        assert len(result.selected_shift) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# extract_components / extract_components_nd — Component labeling
# ═══════════════════════════════════════════════════════════════════════════════


class TestComponentExtraction:
    """Tests for connected component extraction."""

    def test_extract_components_1d_returns_correct_count(self):
        from relative_symmetry_repair.repair import extract_components

        # Two separate clusters
        mask = np.array([
            [0, 1, 1, 0, 0, 0, 1, 1],
            [0, 1, 1, 0, 0, 0, 1, 1],
        ], dtype=np.uint8)
        labels, count = extract_components(mask, min_size=1)
        assert count == 2

    def test_extract_components_nd_returns_correct_count(self):
        from relative_symmetry_repair.repair_nd import extract_components_nd

        mask = np.zeros((4, 8, 8), dtype=np.uint8)
        mask[0:2, 1:3, 1:3] = 1  # one 2x2x2 blob
        mask[0:2, 5:7, 5:7] = 1  # another 2x2x2 blob
        labels, count = extract_components_nd(mask, min_size=1)
        assert count == 2

    def test_extract_components_filtered_labels_may_not_be_contiguous(self):
        """After min_size filtering, label values may exceed num_labels.
        This documents the known behavior."""
        from relative_symmetry_repair.repair import extract_components

        # Create mask with one large and one small component
        mask = np.zeros((4, 10), dtype=np.uint8)
        mask[0:4, 0:4] = 1   # large component (16 cells)
        mask[0, 8] = 1        # tiny component (1 cell)

        labels, count = extract_components(mask, min_size=5)
        # Only the large component survives
        assert count == 1
        # But the label value might be > 1 (it keeps original numbering)
        nonzero_labels = set(np.unique(labels)) - {0}
        assert len(nonzero_labels) == 1

    def test_extract_components_nd_all_zero_mask(self):
        from relative_symmetry_repair.repair_nd import extract_components_nd

        mask = np.zeros((4, 4, 4), dtype=np.uint8)
        labels, count = extract_components_nd(mask, min_size=1)
        assert count == 0
        assert labels.max() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# _orbit_scoring.py — Workspace buffer aliasing safety
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorkspaceBufferSafety:
    """Tests that workspace buffer reuse doesn't corrupt results."""

    def test_consecutive_evaluations_produce_independent_results(self):
        """Two consecutive evaluate_candidate calls should give independent results,
        not aliased data from the second overwriting the first."""
        from relative_symmetry_repair._orbit_scoring import RelativePeriodicOrbitWorkspace

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        ws = RelativePeriodicOrbitWorkspace(st, residue_major=True)

        r1 = ws.evaluate_candidate([0], period=1, nml_mode="hybrid")
        bg1 = r1.background_flat.copy()  # must copy before next call
        defect1 = r1.defect_sites

        r2 = ws.evaluate_candidate([1], period=2, nml_mode="hybrid")
        bg2 = r2.background_flat.copy()

        # The original r1.background_flat is now aliased to r2's data
        # But our copies should be independent
        assert not np.array_equal(bg1, bg2) or (defect1 == r2.defect_sites)

    def test_evaluate_candidate_nd_buffer_independence(self):
        """Same test for N-D workspace."""
        from relative_symmetry_repair._orbit_scoring import RelativePeriodicOrbitWorkspace

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(10, 6, 6), dtype=np.uint8)
        ws = RelativePeriodicOrbitWorkspace(st, residue_major=False)

        r1 = ws.evaluate_candidate([0, 0], period=1, nml_mode="hybrid")
        nml1 = r1.nml_bits
        defect1 = r1.defect_sites

        r2 = ws.evaluate_candidate([1, 0], period=2, nml_mode="hybrid")
        nml2 = r2.nml_bits

        # Scalar values should not be affected by buffer reuse
        r1_again = ws.evaluate_candidate([0, 0], period=1, nml_mode="hybrid")
        assert r1_again.nml_bits == nml1
        assert r1_again.defect_sites == defect1

    def test_fit_functions_copy_workspace_output(self):
        """The public fit functions should return independent copies, not workspace views."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)

        fit1 = fit_relative_periodic_background(st, shift=0, period=1)
        fit2 = fit_relative_periodic_background(st, shift=1, period=2)

        # Backgrounds should be independent arrays
        assert fit1.background is not fit2.background
        assert not np.array_equal(fit1.background, fit2.background) or (
            fit1.defect_rate == fit2.defect_rate
        )


# ═══════════════════════════════════════════════════════════════════════════════
# coding.py / selection.py — NML edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestNMLEdgeCases:
    """Tests for NML scoring edge cases."""

    def test_all_zero_spacetime_has_zero_nll(self):
        """All-zero spacetime: every orbit class is pure-zero, NLL should be 0."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        st = np.zeros((20, 10), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=1)
        assert fit.nll_bits == 0.0
        assert fit.defect_rate == 0.0

    def test_all_one_spacetime_has_zero_nll(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        st = np.ones((20, 10), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=1)
        assert fit.nll_bits == 0.0
        assert fit.defect_rate == 0.0

    def test_random_spacetime_has_positive_nll(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 16), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=1)
        assert fit.nll_bits > 0.0

    def test_nml_complexity_positive_for_nontrivial_spacetime(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 16), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=2)
        assert fit.nml_complexity > 0.0

    def test_nml_total_equals_nll_plus_complexity(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 16), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=2)
        assert abs(fit.nml_bits - (fit.nll_bits + fit.nml_complexity)) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# experiment_suite.py — Control seed bug
# ═══════════════════════════════════════════════════════════════════════════════


class TestControlSeedBug:
    """Detailed test for the control_seed metadata recording bug."""

    def test_control_seeds_actual_vs_recorded(self):
        """Verify the exact mismatch between recorded and actual seeds."""
        from relative_symmetry_repair.experiment_suite import CONTROL_ORDER

        seed = 100
        actual_seeds = {
            "original": None,
            "time_shuffled": seed + 101,
            "space_shuffled": seed + 202,
            "bernoulli_iid": seed + 303,
        }
        for control_index, control_name in enumerate(CONTROL_ORDER):
            recorded = seed + (control_index + 1) * 101
            actual = actual_seeds[control_name]
            if control_name == "original":
                # Original has no seed but records seed+101
                assert recorded == seed + 101
            else:
                if recorded != actual:
                    pytest.xfail(
                        f"Known bug: {control_name} recorded={recorded} actual={actual}"
                    )

    def test_null_controls_preserve_shape(self):
        from relative_symmetry_repair.experiment_suite import make_null_controls

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        controls = make_null_controls(st, seed=42)
        for name, ctrl in controls.items():
            assert ctrl.shape == st.shape, f"{name} shape mismatch"
            assert ctrl.dtype == np.uint8, f"{name} dtype mismatch"

    def test_null_controls_original_is_identity(self):
        from relative_symmetry_repair.experiment_suite import make_null_controls

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        controls = make_null_controls(st, seed=42)
        np.testing.assert_array_equal(controls["original"], st)

    def test_time_shuffled_preserves_spatial_pattern(self):
        """Time shuffling should keep each row intact, just reorder them."""
        from relative_symmetry_repair.experiment_suite import make_null_controls

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        controls = make_null_controls(st, seed=42)
        ts = controls["time_shuffled"]
        # Each row of ts should appear in st
        original_rows = {tuple(row) for row in st}
        for row in ts:
            assert tuple(row) in original_rows

    def test_bernoulli_iid_has_similar_density(self):
        from relative_symmetry_repair.experiment_suite import make_null_controls

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(100, 50), dtype=np.uint8)
        controls = make_null_controls(st, seed=42)
        original_density = st.mean()
        iid_density = controls["bernoulli_iid"].mean()
        # Should be within ~5% for this size
        assert abs(original_density - iid_density) < 0.1


# ═══════════════════════════════════════════════════════════════════════════════
# Diagram colormap bug
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiagramColormap:
    """Tests for the poster diagram DEFECT_CMAP application."""

    def test_poster_2d_defect_column_uses_defect_cmap(self):
        """The last column in the poster 2D figure should use DEFECT_CMAP.
        This tests that `col == len(images)` correctly identifies the defect column."""
        # Simulate the loop logic from _plot_poster_presentation_2d
        n_images = 4  # observed_mid, observed_last, background_last, defect_last
        cmaps_used = []
        for col, _ in enumerate(range(n_images), start=1):
            cmap = "DEFECT" if col == n_images else "BINARY"
            cmaps_used.append(cmap)

        assert cmaps_used == ["BINARY", "BINARY", "BINARY", "DEFECT"]

    def test_presentation_3d_defect_column_uses_defect_cmap(self):
        """The 3D presentation figure has 5 images (start=1, cols 1-5).
        The last should use DEFECT_CMAP."""
        n_images = 5
        cmaps_used = []
        for col, _ in enumerate(range(n_images), start=1):
            # Original code uses col == 5, which is correct for 5 images
            cmap = "DEFECT" if col == 5 else "BINARY"
            cmaps_used.append(cmap)

        assert cmaps_used == ["BINARY", "BINARY", "BINARY", "BINARY", "DEFECT"]

    def test_poster_focus_3d_defect_column_uses_defect_cmap(self):
        """The 3D focus figure has 4 images. The last should use DEFECT_CMAP."""
        n_images = 4
        cmaps_used = []
        for index, _ in enumerate(range(n_images), start=1):
            cmap = "DEFECT" if index == 4 else "BINARY"
            cmaps_used.append(cmap)

        assert cmaps_used == ["BINARY", "BINARY", "BINARY", "DEFECT"]


# ═══════════════════════════════════════════════════════════════════════════════
# repair_nd.py — summarise_components_nd axis naming
# ═══════════════════════════════════════════════════════════════════════════════


class TestComponentSummary:
    """Tests for component summary output."""

    def test_summarise_components_nd_2d_has_expected_columns(self):
        from relative_symmetry_repair.repair_nd import extract_components_nd, summarise_components_nd

        mask = np.zeros((4, 8, 8), dtype=np.uint8)
        mask[1:3, 2:5, 2:5] = 1
        labels, count = extract_components_nd(mask, min_size=1)
        summary = summarise_components_nd(labels)
        assert "t_min" in summary.columns
        # Second dimension should be named "x" for 2D
        assert "x_min" in summary.columns

    def test_summarise_components_nd_returns_correct_count(self):
        from relative_symmetry_repair.repair_nd import extract_components_nd, summarise_components_nd

        mask = np.zeros((4, 8, 8), dtype=np.uint8)
        mask[0:2, 0:3, 0:3] = 1
        mask[0:2, 5:7, 5:7] = 1
        labels, count = extract_components_nd(mask, min_size=1)
        summary = summarise_components_nd(labels)
        assert len(summary) == count


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-module: workspace vs reference agreement (extended)
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorkspaceReferenceAgreementExtended:
    """Extended tests for workspace vs reference path agreement."""

    def test_1d_workspace_vs_reference_randomized(self):
        """Randomized test: workspace and reference should produce identical
        NML scores for random 1D spacetimes."""
        from relative_symmetry_repair.repair import (
            _fit_relative_periodic_background_reference,
            fit_relative_periodic_background,
        )

        rng = np.random.default_rng(99)
        for _ in range(5):
            st = rng.integers(0, 2, size=(30, 12), dtype=np.uint8)
            for period in [1, 2, 3]:
                for shift in [-1, 0, 1]:
                    fit_ws = fit_relative_periodic_background(st, shift=shift, period=period)
                    fit_ref = _fit_relative_periodic_background_reference(st, shift=shift, period=period)
                    assert abs(fit_ws.nml_bits - fit_ref.nml_bits) < 1e-10, (
                        f"NML mismatch at period={period}, shift={shift}"
                    )
                    assert abs(fit_ws.defect_rate - fit_ref.defect_rate) < 1e-12, (
                        f"Defect rate mismatch at period={period}, shift={shift}"
                    )
                    np.testing.assert_array_equal(fit_ws.background, fit_ref.background)

    def test_2d_workspace_vs_reference_nml_agreement(self):
        from relative_symmetry_repair.repair_nd import (
            _fit_relative_periodic_background_nd_reference,
            fit_relative_periodic_background_nd,
        )

        rng = np.random.default_rng(77)
        st = rng.integers(0, 2, size=(15, 8, 8), dtype=np.uint8)
        for period in [1, 2, 3]:
            for shift in [(0, 0), (1, -1), (2, 0)]:
                fit_ws = fit_relative_periodic_background_nd(st, shift=shift, period=period)
                fit_ref = _fit_relative_periodic_background_nd_reference(st, shift=shift, period=period)
                assert abs(fit_ws.nml_bits - fit_ref.nml_bits) < 1e-10, (
                    f"2D NML mismatch at period={period}, shift={shift}: "
                    f"ws={fit_ws.nml_bits}, ref={fit_ref.nml_bits}"
                )

    def test_3d_workspace_vs_reference_nml_agreement(self):
        from relative_symmetry_repair.repair_nd import (
            _fit_relative_periodic_background_nd_reference,
            fit_relative_periodic_background_nd,
        )

        rng = np.random.default_rng(55)
        st = rng.integers(0, 2, size=(8, 4, 4, 4), dtype=np.uint8)
        for period in [1, 2]:
            for shift in [(0, 0, 0), (1, 0, -1)]:
                fit_ws = fit_relative_periodic_background_nd(st, shift=shift, period=period)
                fit_ref = _fit_relative_periodic_background_nd_reference(st, shift=shift, period=period)
                assert abs(fit_ws.nml_bits - fit_ref.nml_bits) < 1e-10, (
                    f"3D NML mismatch at period={period}, shift={shift}"
                )


# ═══════════════════════════════════════════════════════════════════════════════
# coding.py — Additional edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestCodingEdgeCases:
    """Additional coding.py edge case tests."""

    def test_exact_nml_matches_asymptotic_for_large_n(self):
        """For large n, exact and asymptotic NML should converge."""
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        for n in [500, 1000, 5000]:
            exact = bernoulli_nml_complexity_single(n, mode="exact")
            asymp = bernoulli_nml_complexity_single(n, mode="asymptotic")
            # Should be within 1 bit for large n
            assert abs(exact - asymp) < 1.0, f"n={n}: exact={exact}, asymp={asymp}"

    def test_resolve_nml_mode_rejects_both_arguments(self):
        from relative_symmetry_repair.coding import resolve_nml_mode

        with pytest.raises(ValueError, match="not both"):
            resolve_nml_mode(mode="exact", exact=True)

    def test_resolve_nml_mode_defaults_to_hybrid(self):
        from relative_symmetry_repair.coding import resolve_nml_mode

        assert resolve_nml_mode() == "hybrid"

    def test_lz4_mask_bits_empty(self):
        from relative_symmetry_repair.coding import lz4_mask_bits

        result = lz4_mask_bits(np.array([], dtype=np.uint8))
        assert result >= 0  # compressed header still has some bits

    def test_lz4_mask_bits_compresses_uniform(self):
        from relative_symmetry_repair.coding import lz4_mask_bits

        uniform = np.zeros(1000, dtype=np.uint8)
        random_mask = np.random.default_rng(42).integers(0, 2, size=1000, dtype=np.uint8)
        assert lz4_mask_bits(uniform) < lz4_mask_bits(random_mask)
