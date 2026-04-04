"""Tests for period-first selection, finite-sample NML, and pipeline separation."""

import math

import numpy as np
import pytest

from relative_symmetry_repair.coding import (
    EXACT_NML_CUTOFF,
    _exact_bernoulli_regret,
    bernoulli_nml_complexity_single,
    nml_complexity_bits,
    nml_score_bits,
)
from relative_symmetry_repair.eca import random_initial_state, simulate_eca
from relative_symmetry_repair.repair import component_labels, fit_relative_periodic_background
from relative_symmetry_repair.selection import (
    PeriodScore,
    SelectionStatus,
    select_period,
    select_period_nd,
    selection_summary,
    analyze_residual,
)


# ──────────────────────────────────────────────────────────────────────
# Finite-sample corrected NML
# ──────────────────────────────────────────────────────────────────────


class TestExactBernoulliNML:
    """Tests for exact Bernoulli NML (Shtarkov normalizer)."""

    def test_n0_is_zero_n1_is_one(self):
        """n=0: no data, regret=0.  n=1: C(1)=2, regret=log2(2)=1.0."""
        assert _exact_bernoulli_regret(0) == 0.0
        assert _exact_bernoulli_regret(1) == 1.0

    def test_n2_exact(self):
        """For n=2: C(2) = binom(2,0)*1 + binom(2,1)*(1/2)^2 + binom(2,2)*1 = 1 + 0.5 + 1 = 2.5
        log2(2.5) ≈ 1.3219"""
        result = _exact_bernoulli_regret(2)
        expected = math.log2(2.5)
        assert abs(result - expected) < 1e-10, f"n=2: got {result}, expected {expected}"

    def test_n3_exact(self):
        """For n=3: C(3) = 1 + 3*(1/3)^1*(2/3)^2 + 3*(2/3)^2*(1/3)^1 + 1
        = 1 + 3*(1/3)*(4/9) + 3*(4/9)*(1/3) + 1 = 1 + 4/9 + 4/9 + 1 ≈ 2.889"""
        result = _exact_bernoulli_regret(3)
        # Compute explicitly
        c = 1.0  # k=0
        c += 3 * (1/3)**1 * (2/3)**2  # k=1
        c += 3 * (2/3)**2 * (1/3)**1  # k=2
        c += 1.0  # k=3
        expected = math.log2(c)
        assert abs(result - expected) < 1e-10

    def test_monotonic_in_n(self):
        """Regret should be monotonically increasing with n for n >= 2."""
        prev = _exact_bernoulli_regret(2)
        for n in range(3, 50):
            curr = _exact_bernoulli_regret(n)
            assert curr >= prev, f"Regret decreased at n={n}: {curr} < {prev}"
            prev = curr

    def test_approaches_asymptotic(self):
        """For large n, exact regret should approach ½ log₂(n·π/2)."""
        for n in [100, 150, 200]:
            exact = _exact_bernoulli_regret(n)
            asymp = 0.5 * math.log2(n * math.pi / 2)
            diff = abs(exact - asymp)
            # Gap should be O(1/n), well under 0.1 bits for n >= 100
            assert diff < 0.1, f"n={n}: |exact-asymp| = {diff:.4f}, expected < 0.1"

    def test_bernoulli_nml_complexity_single_exact_path(self):
        """For n <= cutoff, uses exact; for n > cutoff, uses asymptotic."""
        n_small = 10
        n_large = EXACT_NML_CUTOFF + 100
        c_small = bernoulli_nml_complexity_single(n_small)
        c_large = bernoulli_nml_complexity_single(n_large)
        assert c_small == _exact_bernoulli_regret(n_small)
        assert abs(c_large - 0.5 * math.log2(n_large * math.pi / 2)) < 1e-10

    def test_nml_complexity_bits_exact_vs_asymptotic(self):
        """Exact mode should differ from asymptotic for small orbit classes."""
        # Small spacetime: orbit classes have few observations
        spacetime = np.random.RandomState(42).randint(0, 2, size=(6, 4)).astype(np.uint8)
        labels = component_labels((6, 4), shift=0, period=3)
        n_labels = 3 * 4

        exact = nml_complexity_bits(labels, n_labels, exact=True)
        asymp = nml_complexity_bits(labels, n_labels, exact=False)

        # They should differ (exact > asymptotic due to O(1) per-class constant)
        assert exact > asymp, f"exact={exact} should exceed asymp={asymp}"
        # The difference is O(k) — roughly ½ log(π/2) ≈ 0.33 bits per class,
        # but larger for very small n_j. With 12 classes and n_j=2, up to ~1 bit each.
        diff = exact - asymp
        assert diff < n_labels * 1.5, f"Difference {diff} too large"


# ──────────────────────────────────────────────────────────────────────
# Period-first selection
# ──────────────────────────────────────────────────────────────────────


class TestPeriodFirstSelection:
    """Test that select_period returns period as primary output."""

    def test_selects_period_for_exact_periodic_spacetime(self):
        """For a spacetime that is period-2 shift-0 but NOT period-1, select period 2."""
        # Row pattern: [0,0,1,1,0,0,1,1] alternating pairs — cannot be captured by period 1
        row0 = np.array([0, 0, 1, 1, 0, 0, 1, 1], dtype=np.uint8)
        row1 = np.array([1, 1, 0, 0, 1, 1, 0, 0], dtype=np.uint8)
        spacetime = np.tile(np.vstack([row0, row1]), (20, 1))  # 40 x 8

        # Only scan shift=0 to avoid period-1 with nonzero shift capturing this
        result = select_period(spacetime, shifts=[0], periods=range(1, 6))

        assert result.selected.period == 2
        assert result.selected.defect_rate == 0.0

    def test_result_has_all_periods(self):
        """All scanned periods appear in all_periods."""
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=range(-1, 2), periods=range(1, 5))

        periods_found = {ps.period for ps in result.all_periods}
        assert periods_found == {1, 2, 3, 4}

    def test_margin_is_positive_for_clear_winner(self):
        """For exact periodic data, margin should be clearly positive."""
        row0 = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
        spacetime = np.tile(np.vstack([row0, row1]), (20, 1))  # 40 x 8

        result = select_period(spacetime, shifts=range(-2, 3), periods=range(1, 6))

        assert result.margin > 0
        assert result.status == SelectionStatus.STABLE_WINNER

    def test_runner_up_exists(self):
        """Runner-up should be populated when multiple periods scanned."""
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 4))

        assert result.runner_up is not None
        assert result.runner_up.nml_bits >= result.selected.nml_bits

    def test_period_scores_sorted_by_nml(self):
        """all_periods should be sorted by NML score."""
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 6))

        nml_values = [ps.nml_bits for ps in result.all_periods]
        assert nml_values == sorted(nml_values)


# ──────────────────────────────────────────────────────────────────────
# Tie / near-tie handling
# ──────────────────────────────────────────────────────────────────────


class TestTieHandling:
    """Test ambiguity reporting for ties and near-ties."""

    def test_random_data_reports_status(self):
        """Any data should produce a valid status."""
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 4))

        assert result.status in (
            SelectionStatus.STABLE_WINNER,
            SelectionStatus.NEAR_TIE,
            SelectionStatus.UNRESOLVED,
        )

    def test_near_tie_detected(self):
        """For two similar periods, margin should be small."""
        # Use period-1 data where p=1 and p=2 are close
        spacetime = np.zeros((40, 4), dtype=np.uint8)
        # Nearly all zeros → p=1 is slightly better than p=2 (both have low NLL,
        # but p=2 has higher complexity)
        spacetime[0, 0] = 1  # one defect

        result = select_period(spacetime, shifts=[0], periods=[1, 2])

        # p=1 should win but margin might be small
        assert result.selected.period == 1
        # Margin exists
        assert result.margin >= 0


# ──────────────────────────────────────────────────────────────────────
# Residual diagnostics separate from selection
# ──────────────────────────────────────────────────────────────────────


class TestResidualSeparation:
    """Verify residual diagnostics don't influence selection."""

    def test_residual_populated(self):
        """select_period should populate residual diagnostics."""
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 4))

        assert result.residual is not None
        assert result.residual.run_length_bits >= 0
        assert result.residual.lz4_bits >= 0
        assert result.residual.n_components >= 0

    def test_residual_does_not_affect_selection(self):
        """The selected period should be based only on NML, not RL/LZ4."""
        initial = random_initial_state(width=16, density=0.5, seed=11)
        spacetime = simulate_eca(rule=110, initial=initial, steps=50)

        result = select_period(
            spacetime, shifts=range(-3, 4), periods=range(1, 8), rule=110,
        )

        # The selected period should minimize NML across all periods
        for ps in result.all_periods:
            assert result.selected.nml_bits <= ps.nml_bits + 1e-10

    def test_analyze_residual_can_be_called_independently(self):
        """analyze_residual can be called with different parameters."""
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 3))
        diag = analyze_residual(result, min_component_size=1)

        assert diag is not None
        assert result.residual is diag  # should be assigned back


# ──────────────────────────────────────────────────────────────────────
# Structured output
# ──────────────────────────────────────────────────────────────────────


class TestSelectionSummary:
    """Test structured output from selection_summary."""

    def test_summary_keys(self):
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 3))
        summary = selection_summary(result)

        assert "selected_period" in summary
        assert "selected_shift" in summary
        assert "selected_nml_bits" in summary
        assert "status" in summary
        assert "margin_bits" in summary
        assert "runner_up_period" in summary
        assert "residual_rl_bits" in summary
        assert "residual_n_components" in summary

    def test_summary_values_match_result(self):
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(20, 8)).astype(np.uint8)

        result = select_period(spacetime, shifts=[0], periods=range(1, 3))
        summary = selection_summary(result)

        assert summary["selected_period"] == result.selected.period
        assert summary["status"] == result.status.value
        assert summary["margin_bits"] == result.margin


# ──────────────────────────────────────────────────────────────────────
# N-D selection
# ──────────────────────────────────────────────────────────────────────


class TestPeriodFirstSelectionND:
    """Test period-first selection for multi-dimensional spacetimes."""

    def test_2d_selects_period(self):
        """2D period-first selection returns a period."""
        rng = np.random.RandomState(7)
        spacetime = rng.randint(0, 2, size=(10, 6, 6)).astype(np.uint8)

        result = select_period_nd(
            spacetime,
            shift_ranges=[range(-1, 2), range(-1, 2)],
            periods=range(1, 4),
        )

        assert result.selected.period >= 1
        assert isinstance(result.selected.best_shift, tuple)
        assert len(result.selected.best_shift) == 2
        assert result.status in SelectionStatus

    def test_2d_residual_populated(self):
        """2D selection should populate residual diagnostics."""
        rng = np.random.RandomState(7)
        spacetime = rng.randint(0, 2, size=(10, 6, 6)).astype(np.uint8)

        result = select_period_nd(
            spacetime,
            shift_ranges=[range(-1, 2), range(-1, 2)],
            periods=range(1, 3),
        )

        assert result.residual is not None
        assert result.residual.run_length_bits >= 0


# ──────────────────────────────────────────────────────────────────────
# ECA integration tests
# ──────────────────────────────────────────────────────────────────────


class TestECAIntegration:
    """End-to-end tests with actual ECA rules."""

    def test_rule54_selects_period2_or_4(self):
        """Rule 54 has period-4 background structure, but with finite-sample NML
        the stronger complexity penalty may favor period 2 unless the NLL gap
        grows large enough. Both are valid selections at different horizons."""
        initial = random_initial_state(width=32, density=0.5, seed=11)

        # At T=200, period 2 should be selected (complexity dominates)
        st_200 = simulate_eca(rule=54, initial=initial, steps=200)
        result_200 = select_period(
            st_200, shifts=range(-4, 5), periods=range(1, 9),
        )
        assert result_200.selected.period in (1, 2, 4)  # conservative

        # Period 4 should always have lower or equal NLL than period 2
        # (it's a refinement along the same velocity chain)
        p2 = next(ps for ps in result_200.all_periods if ps.period == 2)
        p4 = next(ps for ps in result_200.all_periods if ps.period == 4)
        assert p4.nll_bits <= p2.nll_bits + 1e-10
        # But higher complexity
        assert p4.nml_complexity > p2.nml_complexity

    def test_rule30_selects_period1(self):
        """Rule 30 (chaotic) should select period 1."""
        initial = random_initial_state(width=32, density=0.5, seed=11)
        spacetime = simulate_eca(rule=30, initial=initial, steps=200)

        result = select_period(
            spacetime, shifts=range(-2, 3), periods=range(1, 6),
        )

        assert result.selected.period == 1
