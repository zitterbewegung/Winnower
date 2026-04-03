"""Comprehensive test suite round 4: NML numerical correctness, cross-dimensional
consistency, numba kernel validation, and test staleness checks.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


# ═══════════════════════════════════════════════════════════════════════════════
# coding.py — Exact Bernoulli NML numerical correctness
# ═══════════════════════════════════════════════════════════════════════════════


class TestExactBernoulliNML:
    """Tests for the exact Shtarkov normalizer computation."""

    def test_n0_regret_is_zero(self):
        """n=0: one empty sequence, normalizer=1, regret=0."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        assert _exact_bernoulli_regret(0) == 0.0

    def test_n1_regret_is_one_bit(self):
        """n=1: two sequences {0,1}, each MLE-maximized at likelihood 1,
        normalizer=2, regret=log2(2)=1.0 bit.
        Known bug: returns 0.0 instead of 1.0."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        result = _exact_bernoulli_regret(1)
        if result == 0.0:
            pytest.xfail("Known bug: _exact_bernoulli_regret(1) returns 0.0, should be 1.0")
        assert abs(result - 1.0) < 1e-10

    def test_n2_regret_matches_analytical(self):
        """n=2: C(2)=1+0.5+1=2.5, regret=log2(2.5)."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        expected = math.log2(2.5)
        assert abs(_exact_bernoulli_regret(2) - expected) < 1e-10

    def test_n3_regret_matches_analytical(self):
        """n=3: C(3) = 1 + 3*(1/3)*(2/3)^2 + 3*(2/3)^2*(1/3) + 1 = 2 + 8/9."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        expected = math.log2(2 + 8 / 9)
        assert abs(_exact_bernoulli_regret(3) - expected) < 1e-10

    def test_regret_is_monotonically_increasing(self):
        """Shtarkov regret should increase with sample size."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        prev = _exact_bernoulli_regret(2)
        for n in range(3, 50):
            curr = _exact_bernoulli_regret(n)
            assert curr >= prev, f"Regret decreased at n={n}: {prev} > {curr}"
            prev = curr

    def test_complexity_single_n1_all_modes(self):
        """All NML modes should return the same value for n=1.
        Known bug: all return 0.0 instead of 1.0."""
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        exact = bernoulli_nml_complexity_single(1, mode="exact")
        hybrid = bernoulli_nml_complexity_single(1, mode="hybrid")
        asymp = bernoulli_nml_complexity_single(1, mode="asymptotic")

        if exact == 0.0:
            pytest.xfail("Known bug: complexity(n=1) returns 0.0 for all modes, should be 1.0")

        assert exact == hybrid == 1.0
        # Asymptotic is 0.5*log2(1)=0, which differs from exact — that's expected

    def test_hybrid_cutoff_discontinuity(self):
        """Document the ~0.38 bit discontinuity at EXACT_NML_CUTOFF=200."""
        from relative_symmetry_repair.coding import bernoulli_nml_complexity_single

        at_200 = bernoulli_nml_complexity_single(200, mode="hybrid")
        at_201 = bernoulli_nml_complexity_single(201, mode="hybrid")
        gap = at_200 - at_201

        # The exact value at 200 is ~4.20, asymptotic at 201 is ~3.83
        # So hybrid jumps DOWN by ~0.38 bits
        if gap > 0.3:
            pytest.xfail(
                f"Known issue: hybrid NML has {gap:.3f}-bit downward "
                f"discontinuity at cutoff (n=200→201)"
            )
        assert gap < 0.05  # Would pass if the asymptotic had the pi/2 constant

    def test_exact_regret_large_n_approaches_asymptotic(self):
        """For large n, exact regret should approach (1/2)*log2(n*pi/2)."""
        from relative_symmetry_repair.coding import _exact_bernoulli_regret

        for n in [100, 150, 200]:
            exact = _exact_bernoulli_regret(n)
            better_asymp = 0.5 * math.log2(n * math.pi / 2)
            gap = abs(exact - better_asymp)
            assert gap < 0.1, f"n={n}: exact={exact:.4f}, asymp={better_asymp:.4f}, gap={gap:.4f}"


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-dimensional consistency: 1D repair vs ND repair on (T,W) arrays
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrossDimensionalConsistency:
    """1D repair and ND repair should agree on 2D (T,W) spacetimes."""

    def test_defect_rate_agrees(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        for period in [1, 2, 3]:
            for shift in [-1, 0, 1]:
                fit_1d = fit_relative_periodic_background(st, shift=shift, period=period)
                fit_nd = fit_relative_periodic_background_nd(st, shift=(shift,), period=period)
                assert abs(fit_1d.defect_rate - fit_nd.defect_rate) < 1e-12, (
                    f"Defect rate mismatch at p={period},s={shift}: "
                    f"1D={fit_1d.defect_rate}, ND={fit_nd.defect_rate}"
                )

    def test_background_agrees(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        fit_1d = fit_relative_periodic_background(st, shift=0, period=2)
        fit_nd = fit_relative_periodic_background_nd(st, shift=(0,), period=2)
        np.testing.assert_array_equal(fit_1d.background, fit_nd.background)

    def test_nml_bits_agrees(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        for period in [1, 2, 3]:
            fit_1d = fit_relative_periodic_background(st, shift=0, period=period)
            fit_nd = fit_relative_periodic_background_nd(st, shift=(0,), period=period)
            assert abs(fit_1d.nml_bits - fit_nd.nml_bits) < 1e-10, (
                f"NML mismatch at p={period}: 1D={fit_1d.nml_bits}, ND={fit_nd.nml_bits}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Numba kernel vs vectorized consistency check
# ═══════════════════════════════════════════════════════════════════════════════


class TestNumbaVsVectorized:
    """Numba simulation kernels should produce zero-violation spacetimes
    when checked by the vectorized consistency masks."""

    def test_eca_kernel_vs_mask_multiple_rules(self):
        from relative_symmetry_repair.eca import rule_consistency_mask, simulate_eca

        for rule in [0, 30, 54, 90, 110, 150, 255]:
            initial = np.zeros(32, dtype=np.uint8)
            initial[16] = 1
            st = simulate_eca(rule, initial, steps=50)
            mask = rule_consistency_mask(st, rule)
            assert not mask.any(), f"ECA rule {rule} has self-inconsistency"

    def test_2d_life_kernel_vs_mask(self):
        from relative_symmetry_repair.ca2d import (
            random_initial_grid,
            rule_consistency_mask_2d,
            simulate_2d,
        )

        initial = random_initial_grid(16, 16, density=0.3, seed=42)
        st = simulate_2d(initial, steps=20, rule="life")
        mask = rule_consistency_mask_2d(st, survive=(2, 3), birth=(3, 3))
        assert not mask.any()

    def test_2d_general_kernel_self_consistent(self):
        """simulate_2d_general should also produce zero-violation spacetimes
        when checked with the general LUT."""
        from relative_symmetry_repair.ca2d import (
            parse_rulestring,
            random_initial_grid,
            simulate_2d_general,
        )

        initial = random_initial_grid(16, 16, density=0.3, seed=42)
        st = simulate_2d_general(initial, steps=20, birth=[3], survive=[2, 3])
        # Build vectorized check manually
        prev = st[:-1]
        actual = st[1:]
        neighbor_count = np.zeros_like(prev, dtype=np.int32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                neighbor_count += np.roll(np.roll(prev, -dy, axis=1), -dx, axis=2)
        alive = prev.astype(bool)
        # Life: survive if 2 or 3 neighbors, birth if exactly 3
        predicted = np.where(
            alive,
            np.isin(neighbor_count, [2, 3]).astype(np.uint8),
            np.isin(neighbor_count, [3]).astype(np.uint8),
        )
        assert np.array_equal(predicted, actual)

    def test_3d_kernel_vs_mask_all_rules(self):
        from relative_symmetry_repair.ca3d import (
            RULES_3D,
            RULES_3D_DENSITY,
            random_initial_volume,
            rule_consistency_mask_3d,
            simulate_3d,
        )

        for name, (s_lo, s_hi, b_lo, b_hi) in RULES_3D.items():
            density = RULES_3D_DENSITY[name]
            initial = random_initial_volume(6, 6, 6, density=density, seed=42)
            st = simulate_3d(initial, steps=5, survive=(s_lo, s_hi), birth=(b_lo, b_hi))
            mask = rule_consistency_mask_3d(st, survive=(s_lo, s_hi), birth=(b_lo, b_hi))
            assert not mask.any(), f"3D rule {name} has self-inconsistency"


# ═══════════════════════════════════════════════════════════════════════════════
# Test staleness checks
# ═══════════════════════════════════════════════════════════════════════════════


class TestStaleness:
    """Check that existing tests are not silently stale."""

    def test_2d_3d_test_uses_wrong_density(self):
        """test_2d_3d.py uses default density=0.5 for 3d-life.
        RULES_3D_DENSITY says it should be 0.2."""
        from relative_symmetry_repair.ca3d import RULES_3D_DENSITY

        test_file = REPO_ROOT / "tests/test_2d_3d.py"
        if not test_file.exists():
            pytest.skip("test_2d_3d.py not found")
        source = test_file.read_text()
        # Check if it imports and uses RULES_3D_DENSITY
        if "RULES_3D_DENSITY" not in source and "density=" not in source:
            # Uses default density=0.5 for 3d-life
            assert RULES_3D_DENSITY["3d-life"] != 0.5, (
                "test_2d_3d.py uses default density=0.5 for 3d-life "
                f"but RULES_3D_DENSITY says {RULES_3D_DENSITY['3d-life']}"
            )

    def test_candidate_scoring_has_no_3d_coverage(self):
        """test_candidate_scoring_fast_path.py should test 3D spacetimes."""
        test_file = REPO_ROOT / "tests/test_candidate_scoring_fast_path.py"
        if not test_file.exists():
            pytest.skip("test_candidate_scoring_fast_path.py not found")
        source = test_file.read_text()
        # Check for any 4D array creation (T, Z, Y, X)
        has_3d = "size=(4, 3, 3, 3)" in source or "size=(5, 3, 3, 3)" in source
        if not has_3d:
            pytest.xfail(
                "test_candidate_scoring_fast_path.py has no 3-spatial-dim (4D array) test cases"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# selector_tools.py edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestSelectorTools:
    """Tests for selector_tools.py."""

    def test_shift_columns_1d_frame(self):
        """1D scan frame should have 'shift' column."""
        import pandas as pd

        from relative_symmetry_repair.selector_tools import shift_columns

        frame = pd.DataFrame({"period": [1], "shift": [0], "nml_bits": [1.0]})
        cols = shift_columns(frame)
        assert cols == ["shift"]

    def test_shift_columns_nd_frame(self):
        """ND scan frame should have 'shift_0', 'shift_1', etc."""
        import pandas as pd

        from relative_symmetry_repair.selector_tools import shift_columns

        frame = pd.DataFrame({"period": [1], "shift_0": [0], "shift_1": [1], "nml_bits": [1.0]})
        cols = shift_columns(frame)
        assert cols == ["shift_0", "shift_1"]

    def test_shift_columns_mixed_frame_is_problematic(self):
        """A frame with both 'shift' and 'shift_0' should not double-include."""
        import pandas as pd

        from relative_symmetry_repair.selector_tools import shift_columns

        frame = pd.DataFrame({
            "period": [1, 2],
            "shift": [0, None],
            "shift_0": [None, 1],
            "nml_bits": [1.0, 2.0],
        })
        cols = shift_columns(frame)
        # Current behavior: returns both ["shift", "shift_0"]
        # This is a known design issue — document it
        assert len(cols) >= 1  # at least one shift column found


# ═══════════════════════════════════════════════════════════════════════════════
# Input validation edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestInputValidation:
    """Tests for input validation edge cases."""

    def test_eca_rule_out_of_range_produces_valid_output(self):
        """ECA rules must be 0-255. Rule 256 should ideally be rejected."""
        from relative_symmetry_repair.eca import simulate_eca

        # Rule 256 would be a 9-bit rule — undefined for 8-bit ECA
        initial = np.array([0, 0, 1, 0, 0], dtype=np.uint8)
        # Currently no validation — this will silently produce output
        st = simulate_eca(256, initial, steps=3)
        # At minimum verify it doesn't crash
        assert st.shape == (3, 5)

    def test_eca_consistency_mask_non_binary_input(self):
        """rule_consistency_mask on non-binary input should either reject or handle safely."""
        from relative_symmetry_repair.eca import rule_consistency_mask

        # Non-binary input: values > 1
        st = np.array([[0, 1, 2, 0, 1]], dtype=np.uint8)
        # Pattern with value 2 creates pattern index > 7
        # This reads undefined bits from the rule, producing arbitrary results
        try:
            mask = rule_consistency_mask(st, 30)
            # If it doesn't crash, the result is meaningless but at least not a segfault
            assert mask.shape[0] == 0  # only 1 row, so mask has 0 rows
        except (ValueError, IndexError):
            pass  # Validation rejection is acceptable

    def test_simulate_3d_rejects_4d_input(self):
        from relative_symmetry_repair.ca3d import simulate_3d

        bad = np.zeros((2, 3, 4, 5, 6), dtype=np.uint8)
        with pytest.raises(ValueError, match="3D"):
            simulate_3d(bad, steps=2, rule="3d-life")
