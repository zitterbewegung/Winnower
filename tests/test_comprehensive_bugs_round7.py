"""Comprehensive test suite round 7: post-fix regression tests and new edge cases.

Covers: NML formula consistency, empty-frame handling in selection,
division-by-zero guards, and end-to-end verification after all 12 bug fixes.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# NML formula consistency after correction
# ═══════════════════════════════════════════════════════════════════════════════


class TestNMLFormulaConsistency:
    """Verify the corrected NML formula is internally consistent."""

    def test_asymptotic_always_nonnegative(self):
        """The asymptotic formula 0.5*log2(n*pi/2) should be non-negative for all n >= 1."""
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        for n in range(0, 300):
            result = bernoulli_nml_complexity_single(n, mode="asymptotic")
            assert result >= 0.0, f"Negative complexity at n={n}: {result}"

    def test_hybrid_small_gap_at_cutoff(self):
        """The gap at the exact/asymptotic switchover should be small."""
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        at_200 = bernoulli_nml_complexity_single(200, mode="hybrid")
        at_201 = bernoulli_nml_complexity_single(201, mode="hybrid")
        gap = abs(at_200 - at_201)
        # With the corrected formula, the gap should be < 0.1 bits
        assert gap < 0.1, f"Gap at cutoff: {gap:.4f} bits"

    def test_all_modes_agree_at_n1(self):
        """All NML modes should return 1.0 for n=1."""
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        for mode in ["exact", "hybrid", "asymptotic"]:
            result = bernoulli_nml_complexity_single(1, mode=mode)
            assert result == 1.0, f"mode={mode}: got {result}, expected 1.0"

    def test_exact_and_hybrid_agree_below_cutoff(self):
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        for n in [1, 2, 5, 10, 50, 100, 200]:
            exact = bernoulli_nml_complexity_single(n, mode="exact")
            hybrid = bernoulli_nml_complexity_single(n, mode="hybrid")
            assert exact == hybrid, f"n={n}: exact={exact}, hybrid={hybrid}"

    def test_nml_decomposition_holds_for_corrected_formula(self):
        """NML = NLL + complexity must still hold after the formula correction."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        for mode in ["exact", "hybrid", "asymptotic"]:
            st = rng.integers(0, 2, size=(30, 12), dtype=np.uint8)
            fit = fit_relative_periodic_background(st, shift=0, period=2, nml_mode=mode)
            assert abs(fit.nml_bits - (fit.nll_bits + fit.nml_complexity)) < 1e-10, (
                f"mode={mode}: nml={fit.nml_bits} != nll+comp={fit.nll_bits + fit.nml_complexity}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Empty frame handling in selection module
# ═══════════════════════════════════════════════════════════════════════════════


class TestEmptyFrameHandling:
    """Verify that empty scan results propagate cleanly through the selection pipeline."""

    def test_group_by_period_returns_empty_on_empty_frame(self):
        """_group_by_period should return [] on an empty frame, not crash."""
        import pandas as pd

        from relative_symmetry_repair.selection import _group_by_period

        empty = pd.DataFrame()
        result = _group_by_period(empty, fits={}, nd=False)
        assert result == []

    def test_group_by_period_returns_empty_on_columnless_frame(self):
        import pandas as pd

        from relative_symmetry_repair.selection import _group_by_period

        # DataFrame with rows but no "period" column
        frame = pd.DataFrame({"x": [1, 2]})
        result = _group_by_period(frame, fits={}, nd=False)
        assert result == []

    def test_select_period_from_scan_raises_on_empty(self):
        """select_period_from_scan should raise ValueError with a clear message."""
        import pandas as pd

        from relative_symmetry_repair.selection import select_period_from_scan

        empty = pd.DataFrame()
        with pytest.raises(ValueError, match="[Nn]o candidate"):
            select_period_from_scan(empty, {})

    def test_scan_empty_shifts_returns_empty_frame(self):
        from relative_symmetry_repair.repair import scan_relative_periodicity

        st = np.zeros((10, 8), dtype=np.uint8)
        frame, fits = scan_relative_periodicity(st, shifts=[], periods=[1, 2])
        assert frame.empty
        assert len(fits) == 0

    def test_scan_nd_empty_periods_returns_empty_frame(self):
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd

        st = np.zeros((10, 4, 4), dtype=np.uint8)
        frame, fits = scan_relative_periodicity_nd(st, shift_ranges=[range(-1, 2)]*2, periods=[])
        assert frame.empty
        assert len(fits) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Division-by-zero guards in 1D repair
# ═══════════════════════════════════════════════════════════════════════════════


class TestDivisionByZeroGuards:
    """Verify defect_rate computation doesn't crash on edge cases."""

    def test_1d_fit_on_zero_width_spacetime(self):
        """A zero-width spacetime should not crash."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        st = np.zeros((10, 0), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=1)
        assert fit.defect_rate == 0.0
        assert fit.total_sites == 0

    def test_1d_fit_on_zero_steps_spacetime(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        st = np.zeros((0, 8), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=1)
        assert fit.defect_rate == 0.0
        assert fit.total_sites == 0


# ═══════════════════════════════════════════════════════════════════════════════
# End-to-end: period selection stability after NML correction
# ═══════════════════════════════════════════════════════════════════════════════


class TestPeriodSelectionStability:
    """Verify that the NML formula correction doesn't change period selections
    for the representative rules used in the paper."""

    def test_eca54_selects_period_2_or_4(self):
        from relative_symmetry_repair.eca import simulate_eca
        from relative_symmetry_repair.repair import scan_relative_periodicity
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame

        initial = np.zeros(64, dtype=np.uint8)
        initial[32] = 1
        st = simulate_eca(54, initial, steps=200)
        frame, fits = scan_relative_periodicity(st, shifts=range(-2, 3), periods=[1, 2, 3, 4])
        result = period_first_selection_from_frame(frame)
        assert result.selected_period in [2, 4], f"ECA-54 selected period {result.selected_period}"

    def test_eca110_selects_period_4_or_7(self):
        from relative_symmetry_repair.eca import simulate_eca
        from relative_symmetry_repair.repair import scan_relative_periodicity
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame

        initial = np.zeros(64, dtype=np.uint8)
        initial[32] = 1
        st = simulate_eca(110, initial, steps=200)
        frame, fits = scan_relative_periodicity(st, shifts=range(-2, 3), periods=[1, 2, 3, 4, 7])
        result = period_first_selection_from_frame(frame)
        assert result.selected_period in [4, 7], f"ECA-110 selected period {result.selected_period}"

    def test_checkerboard_still_selects_period_2(self):
        from relative_symmetry_repair.repair import scan_relative_periodicity
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame

        row0 = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
        st = np.tile(np.vstack([row0, row1]), (20, 1))
        frame, fits = scan_relative_periodicity(st, shifts=[0], periods=[1, 2, 4])
        result = period_first_selection_from_frame(frame)
        assert result.selected_period == 2


# ═══════════════════════════════════════════════════════════════════════════════
# Docstring consistency
# ═══════════════════════════════════════════════════════════════════════════════


class TestDocstringConsistency:
    """Verify docstrings match implementation."""

    def test_complexity_single_docstring_mentions_pi(self):
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        doc = bernoulli_nml_complexity_single.__doc__
        assert "π/2" in doc or "pi/2" in doc or "π" in doc, (
            "Docstring should mention the pi/2 constant in the asymptotic formula"
        )
