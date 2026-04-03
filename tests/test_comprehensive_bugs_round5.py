"""Comprehensive test suite round 5: mathematical invariants, LIFE_RULES
correctness, and property-based checks.

Targets untested invariants found by systematic gap analysis:
- NML decomposition for ND path
- Background idempotence for 3D
- Shift commutativity
- Period-1 shift-0 temporal majority for ND
- LIFE_RULES dictionary correctness
"""
from __future__ import annotations

import numpy as np
import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# LIFE_RULES correctness
# ═══════════════════════════════════════════════════════════════════════════════


class TestLifeRulesCorrectness:
    """Verify named rules in LIFE_RULES match their canonical definitions."""

    def test_life_rule_is_b3_s23(self):
        from relative_symmetry_repair.ca2d import LIFE_RULES

        s_lo, s_hi, b_lo, b_hi = LIFE_RULES["life"]
        assert (s_lo, s_hi) == (2, 3), f"Life survive should be (2,3), got ({s_lo},{s_hi})"
        assert (b_lo, b_hi) == (3, 3), f"Life birth should be (3,3), got ({b_lo},{b_hi})"

    def test_diamoeba_named_rule_missing_b3(self):
        """LIFE_RULES['diamoeba'] is (5,8,5,8) = B5678/S5678, but canonical
        Diamoeba is B35678/S5678. The range (5,8) misses B3.
        The poster pipeline uses simulate_2d_general with the rulestring,
        so it's unaffected, but simulate_2d(rule='diamoeba') is wrong."""
        from relative_symmetry_repair.ca2d import LIFE_RULES

        s_lo, s_hi, b_lo, b_hi = LIFE_RULES["diamoeba"]
        # The range birth=(5,8) covers B5,B6,B7,B8 but NOT B3
        # Canonical Diamoeba has B3 in its birth set
        if b_lo > 3:
            pytest.xfail(
                f"Known bug: LIFE_RULES['diamoeba'] birth=({b_lo},{b_hi}) "
                f"misses B3 — should be B35678/S5678, not B5678/S5678"
            )

    def test_diamoeba_rulestring_vs_named_rule_differ(self):
        """The rulestring and named-rule paths should produce different results
        since they encode different rules."""
        from relative_symmetry_repair.ca2d import (
            random_initial_grid,
            simulate_2d,
            simulate_2d_general,
        )

        initial = random_initial_grid(16, 16, density=0.3, seed=42)
        st_named = simulate_2d(initial, steps=20, rule="diamoeba")
        st_general = simulate_2d_general(initial, steps=20, birth=[3, 5, 6, 7, 8], survive=[5, 6, 7, 8])
        # They should differ because the named rule omits B3
        assert not np.array_equal(st_named, st_general), (
            "Named 'diamoeba' rule matches rulestring B35678/S5678 — "
            "this means the bug was fixed"
        )

    def test_seeds_rule_correctly_kills_all(self):
        """Seeds (B2/S) should kill every live cell — survive range is unreachable."""
        from relative_symmetry_repair.ca2d import LIFE_RULES

        s_lo, s_hi, b_lo, b_hi = LIFE_RULES["seeds"]
        # survive=(9,9) is unreachable for 8-neighbor grid
        assert s_lo > 8, "Seeds survive_lo should be >8 to ensure nothing survives"


# ═══════════════════════════════════════════════════════════════════════════════
# Mathematical Invariant: NML decomposition for ND path
# ═══════════════════════════════════════════════════════════════════════════════


class TestNMLDecompositionND:
    """NML = NLL + complexity must hold for ND fits."""

    def test_nml_decomposition_2d(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(7)
        st = rng.integers(0, 2, size=(20, 6, 6), dtype=np.uint8)
        for shift, period in [((0, 0), 1), ((1, 2), 2), ((0, 0), 3)]:
            fit = fit_relative_periodic_background_nd(st, shift=shift, period=period)
            assert abs(fit.nml_bits - (fit.nll_bits + fit.nml_complexity)) < 1e-10, (
                f"NML decomposition failed for shift={shift}, period={period}: "
                f"nml={fit.nml_bits}, nll={fit.nll_bits}, comp={fit.nml_complexity}"
            )

    def test_nml_decomposition_3d(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(8, 4, 4, 4), dtype=np.uint8)
        for shift, period in [((0, 0, 0), 1), ((1, 0, -1), 2)]:
            fit = fit_relative_periodic_background_nd(st, shift=shift, period=period)
            assert abs(fit.nml_bits - (fit.nll_bits + fit.nml_complexity)) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# Mathematical Invariant: Background idempotence for 3D
# ═══════════════════════════════════════════════════════════════════════════════


class TestBackgroundIdempotence3D:
    """Fitting a perfectly periodic 3D spacetime should give defect_rate=0."""

    def test_3d_exact_periodic_has_zero_defects(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        # Period-2 alternating volumes
        vol0 = np.zeros((4, 4, 4), dtype=np.uint8)
        vol0[::2, ::2, ::2] = 1
        vol1 = 1 - vol0
        spacetime = np.stack([vol0, vol1] * 5)  # 10 steps, period 2
        fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0, 0), period=2)
        assert fit.defect_rate == 0.0
        assert fit.defect_sites == 0

    def test_3d_shifted_periodic_has_zero_defects(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        # Period-1 with shift (1,0,0): each frame is the previous rolled by 1 on z-axis
        frame = np.zeros((6, 6, 6), dtype=np.uint8)
        frame[0:3, 0:3, 0:3] = 1
        frames = [np.roll(frame, t, axis=0) for t in range(10)]
        spacetime = np.stack(frames)
        fit = fit_relative_periodic_background_nd(spacetime, shift=(1, 0, 0), period=1)
        assert fit.defect_rate == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Mathematical Invariant: Shift commutativity on symmetric spacetimes
# ═══════════════════════════════════════════════════════════════════════════════


class TestShiftCommutativity:
    """For a spacetime that is symmetric under axis permutation, permuting
    shift components should give the same defect rate."""

    def test_transpose_symmetry_2d(self):
        """Transposing spatial axes and swapping shift components should
        give the same defect rate."""
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(13)
        st = rng.integers(0, 2, size=(12, 6, 6), dtype=np.uint8)

        fit_12 = fit_relative_periodic_background_nd(st, shift=(1, 2), period=2)
        st_T = st.transpose(0, 2, 1).copy()
        fit_21 = fit_relative_periodic_background_nd(st_T, shift=(2, 1), period=2)

        assert abs(fit_12.defect_rate - fit_21.defect_rate) < 1e-12, (
            f"Shift commutativity failed: (1,2)={fit_12.defect_rate}, (2,1)={fit_21.defect_rate}"
        )

    def test_isotropic_spacetime_shift_permutation(self):
        """On a spacetime where H==W, shift (a,b) on original should give
        same defect_rate as shift (b,a) on transposed."""
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(99)
        st = rng.integers(0, 2, size=(15, 8, 8), dtype=np.uint8)

        for s1, s2 in [(0, 1), (1, -1), (2, 0)]:
            fit_orig = fit_relative_periodic_background_nd(st, shift=(s1, s2), period=2)
            st_T = st.transpose(0, 2, 1).copy()
            fit_swap = fit_relative_periodic_background_nd(st_T, shift=(s2, s1), period=2)
            assert abs(fit_orig.defect_rate - fit_swap.defect_rate) < 1e-12, (
                f"Commutativity failed for shift ({s1},{s2}): "
                f"orig={fit_orig.defect_rate}, swap={fit_swap.defect_rate}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Mathematical Invariant: Period-1 shift-0 is temporal majority for ND
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemporalMajorityND:
    """p=1, s=(0,...) background should be the temporal majority at each voxel."""

    def test_period_one_shift_zero_2d(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(5)
        st = rng.integers(0, 2, size=(9, 4, 4), dtype=np.uint8)  # odd T avoids ties
        fit = fit_relative_periodic_background_nd(st, shift=(0, 0), period=1)
        expected = (st.sum(axis=0) * 2 >= 9).astype(np.uint8)
        for t in range(9):
            np.testing.assert_array_equal(fit.background[t], expected)

    def test_period_one_shift_zero_3d(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(5)
        st = rng.integers(0, 2, size=(7, 3, 3, 3), dtype=np.uint8)
        fit = fit_relative_periodic_background_nd(st, shift=(0, 0, 0), period=1)
        expected = (st.sum(axis=0) * 2 >= 7).astype(np.uint8)
        for t in range(7):
            np.testing.assert_array_equal(fit.background[t], expected)


# ═══════════════════════════════════════════════════════════════════════════════
# Property-based: random spacetime invariants
# ═══════════════════════════════════════════════════════════════════════════════


class TestRandomSpacetimeProperties:
    """Properties that should hold for any random binary spacetime."""

    def test_defect_rate_in_0_1(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        for _ in range(10):
            st_1d = rng.integers(0, 2, size=(20, 8), dtype=np.uint8)
            fit = fit_relative_periodic_background(st_1d, shift=0, period=1)
            assert 0.0 <= fit.defect_rate <= 1.0

            st_2d = rng.integers(0, 2, size=(10, 4, 4), dtype=np.uint8)
            fit = fit_relative_periodic_background_nd(st_2d, shift=(0, 0), period=1)
            assert 0.0 <= fit.defect_rate <= 1.0

    def test_background_is_always_binary(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        for _ in range(5):
            st = rng.integers(0, 2, size=(20, 8), dtype=np.uint8)
            fit = fit_relative_periodic_background(st, shift=1, period=2)
            assert set(np.unique(fit.background)).issubset({0, 1})

            st_nd = rng.integers(0, 2, size=(10, 4, 4), dtype=np.uint8)
            fit = fit_relative_periodic_background_nd(st_nd, shift=(1, 0), period=2)
            assert set(np.unique(fit.background)).issubset({0, 1})

    def test_defect_mask_xor_property(self):
        """defect_mask should be exactly spacetime XOR background."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=2)
        expected = (st != fit.background)
        np.testing.assert_array_equal(fit.defect_mask, expected)

    def test_defect_sites_equals_mask_sum(self):
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=1)
        assert fit.defect_sites == int(fit.defect_mask.sum())

    def test_nml_nonnegative(self):
        """NML score should always be non-negative."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        for _ in range(10):
            st = rng.integers(0, 2, size=(20, 8), dtype=np.uint8)
            fit = fit_relative_periodic_background(st, shift=0, period=1)
            assert fit.nml_bits >= 0
            assert fit.nll_bits >= 0
            assert fit.nml_complexity >= 0

    def test_better_period_has_lower_or_equal_nll(self):
        """For velocity-matched shifts, refining the period should not
        increase NLL (finer partition can only decrease the MLE cost)."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(40, 12), dtype=np.uint8)
        fit_p1 = fit_relative_periodic_background(st, shift=0, period=1)
        fit_p2 = fit_relative_periodic_background(st, shift=0, period=2)
        # Period 2 refines period 1 (velocity-matched with s=0)
        assert fit_p2.nll_bits <= fit_p1.nll_bits + 1e-10, (
            f"NLL increased under refinement: p1={fit_p1.nll_bits}, p2={fit_p2.nll_bits}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Compression ordering
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressionOrdering:
    """Structured masks should compress better than random ones (for large enough N)."""

    def test_lz4_structured_cheaper_than_random_large(self):
        from relative_symmetry_repair.coding import lz4_mask_bits

        structured = np.zeros(1000, dtype=np.uint8)
        random_mask = np.random.default_rng(42).integers(0, 2, size=1000, dtype=np.uint8)
        assert lz4_mask_bits(structured) < lz4_mask_bits(random_mask)

    def test_run_length_structured_cheaper_than_random_large(self):
        from relative_symmetry_repair.coding import run_length_bits

        structured = np.zeros(100, dtype=np.uint8)
        random_mask = np.random.default_rng(42).integers(0, 2, size=100, dtype=np.uint8)
        assert run_length_bits(structured) < run_length_bits(random_mask)
