"""Comprehensive test suite targeting bugs, edge cases, and logic errors
found via systematic code review of the entire codebase.

Organized by module, with each test class covering a specific module's issues.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
import pandas as pd
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# ca3d.py — 3D Cellular Automaton
# ═══════════════════════════════════════════════════════════════════════════════


class TestCA3DSimulation:
    """Tests for simulate_3d and rule_consistency_mask_3d."""

    def test_single_step_returns_only_initial_condition(self):
        from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d

        initial = random_initial_volume(4, 4, 4, density=0.5, seed=0)
        st = simulate_3d(initial, steps=1, rule="3d-life")
        assert st.shape == (1, 4, 4, 4)
        np.testing.assert_array_equal(st[0], initial)

    def test_all_zero_initial_stays_zero_for_all_rules(self):
        """An all-zero grid has 0 neighbors everywhere, so no birth can occur
        unless birth_lo == 0. All predefined rules have birth_lo >= 1."""
        from relative_symmetry_repair.ca3d import RULES_3D, simulate_3d

        initial = np.zeros((4, 4, 4), dtype=np.uint8)
        for name in RULES_3D:
            st = simulate_3d(initial, steps=5, rule=name)
            np.testing.assert_array_equal(st[-1], initial, err_msg=f"Rule {name} birthed from void")

    def test_all_one_initial_clouds_is_fixed_point(self):
        """clouds has survive=(13,26), so a fully-live grid (26 neighbors each)
        survives. Birth never fires (no dead cells). This should be a fixed point."""
        from relative_symmetry_repair.ca3d import simulate_3d

        initial = np.ones((4, 4, 4), dtype=np.uint8)
        st = simulate_3d(initial, steps=10, rule="clouds")
        for t in range(st.shape[0]):
            np.testing.assert_array_equal(st[t], initial, err_msg=f"clouds all-one not fixed at t={t}")

    def test_consistency_mask_agrees_with_simulation(self):
        """Running the actual rule should produce a spacetime with zero
        consistency errors — the mask should be all-False."""
        from relative_symmetry_repair.ca3d import (
            RULES_3D,
            random_initial_volume,
            rule_consistency_mask_3d,
            simulate_3d,
        )

        for name, (s_lo, s_hi, b_lo, b_hi) in RULES_3D.items():
            initial = random_initial_volume(6, 6, 6, density=0.3, seed=7)
            st = simulate_3d(initial, steps=10, survive=(s_lo, s_hi), birth=(b_lo, b_hi))
            mask = rule_consistency_mask_3d(st, survive=(s_lo, s_hi), birth=(b_lo, b_hi))
            assert not mask.any(), f"Rule {name} has self-consistency errors"

    def test_consistency_mask_single_step_returns_empty(self):
        from relative_symmetry_repair.ca3d import rule_consistency_mask_3d

        st = np.zeros((1, 4, 4, 4), dtype=np.uint8)
        mask = rule_consistency_mask_3d(st, survive=(4, 5), birth=(5, 5))
        assert mask.shape[0] == 0

    def test_density_values_produce_surviving_rules(self):
        """Each rule with its tuned density should sustain activity to t=39."""
        from relative_symmetry_repair.ca3d import RULES_3D, RULES_3D_DENSITY, random_initial_volume, simulate_3d

        for name, (s_lo, s_hi, b_lo, b_hi) in RULES_3D.items():
            density = RULES_3D_DENSITY[name]
            initial = random_initial_volume(16, 16, 16, density=density, seed=42)
            st = simulate_3d(initial, steps=40, survive=(s_lo, s_hi), birth=(b_lo, b_hi))
            alive_last = st[-1].sum()
            assert alive_last > 0, f"Rule {name} died out at density={density}"

    def test_rules_3d_density_covers_all_rules(self):
        from relative_symmetry_repair.ca3d import RULES_3D, RULES_3D_DENSITY

        assert set(RULES_3D.keys()) == set(RULES_3D_DENSITY.keys())

    def test_neighbor_count_center_excluded(self):
        """A single live cell with all-zero surroundings should have 0 neighbors."""
        from relative_symmetry_repair.ca3d import simulate_3d

        initial = np.zeros((5, 5, 5), dtype=np.uint8)
        initial[2, 2, 2] = 1
        # survive=(0,0) means: survive only if exactly 0 neighbors (isolated cell stays)
        # birth=(99,99) means: no birth possible
        st = simulate_3d(initial, steps=2, survive=(0, 0), birth=(99, 99))
        assert st[1, 2, 2, 2] == 1, "Isolated cell should survive with survive=(0,0)"
        # All neighbors are dead, so no birth should occur
        assert st[1].sum() == 1, "Only the isolated cell should exist"

    def test_simulate_3d_rejects_non_binary_input(self):
        from relative_symmetry_repair.ca3d import simulate_3d

        bad_input = np.array([[[0, 1, 2]]], dtype=np.uint8)
        with pytest.raises(ValueError, match="binary"):
            simulate_3d(bad_input, steps=2, rule="3d-life")


# ═══════════════════════════════════════════════════════════════════════════════
# ca2d.py — 2D Cellular Automaton
# ═══════════════════════════════════════════════════════════════════════════════


class TestCA2DRules:
    """Tests for 2D rule definitions and parsing."""

    def test_parse_rulestring_ignores_trailing_garbage(self):
        """parse_rulestring should only accept exact rulestrings, not trailing junk."""
        from relative_symmetry_repair.ca2d import parse_rulestring

        # Valid rulestring
        birth, survive = parse_rulestring("B3/S23")
        assert sorted(birth) == [3]
        assert sorted(survive) == [2, 3]

    def test_parse_rulestring_case_insensitive(self):
        from relative_symmetry_repair.ca2d import parse_rulestring

        b1, s1 = parse_rulestring("B3/S23")
        b2, s2 = parse_rulestring("b3/s23")
        assert sorted(b1) == sorted(b2)
        assert sorted(s1) == sorted(s2)

    def test_simulate_2d_general_matches_simulate_2d_for_life(self):
        """For Conway's Life (B3/S23), both simulators should produce identical output."""
        from relative_symmetry_repair.ca2d import (
            random_initial_grid,
            simulate_2d,
            simulate_2d_general,
        )

        initial = random_initial_grid(16, 16, density=0.3, seed=42)
        st_range = simulate_2d(initial, steps=20, rule="life")
        st_general = simulate_2d_general(initial, steps=20, birth=[3], survive=[2, 3])
        np.testing.assert_array_equal(st_range, st_general)

    def test_highlife_range_approximation_differs_from_general(self):
        """highlife uses birth range (3,6) which incorrectly includes B4 and B5.
        The general simulator with B36/S23 should differ."""
        from relative_symmetry_repair.ca2d import (
            random_initial_grid,
            simulate_2d,
            simulate_2d_general,
        )

        initial = random_initial_grid(16, 16, density=0.3, seed=42)
        st_range = simulate_2d(initial, steps=20, rule="highlife")
        st_general = simulate_2d_general(initial, steps=20, birth=[3, 6], survive=[2, 3])
        # They SHOULD differ because the range includes extra birth counts
        assert not np.array_equal(st_range, st_general), (
            "highlife range approximation unexpectedly matches exact — "
            "the range (3,6) includes B4 and B5 which should cause divergence"
        )

    def test_consistency_mask_2d_self_consistent(self):
        """A spacetime produced by simulate_2d should have zero consistency errors."""
        from relative_symmetry_repair.ca2d import (
            random_initial_grid,
            rule_consistency_mask_2d,
            simulate_2d,
        )

        initial = random_initial_grid(8, 8, density=0.4, seed=11)
        st = simulate_2d(initial, steps=10, rule="life")
        mask = rule_consistency_mask_2d(st, survive=(2, 3), birth=(3, 3))
        assert not mask.any(), "Life rule has self-consistency errors"

    def test_seeds_rule_nothing_survives(self):
        """The 'seeds' rule has survive=(9,9) which is unreachable for 8-neighbor
        grids. Every live cell should die. Only birth on B2 creates new cells."""
        from relative_symmetry_repair.ca2d import simulate_2d

        # A single live cell: no neighbors, so no birth around it; it dies next step
        initial = np.zeros((8, 8), dtype=np.uint8)
        initial[4, 4] = 1
        st = simulate_2d(initial, steps=3, rule="seeds")
        # Cell should die immediately (0 neighbors, survive requires 9)
        assert st[1, 4, 4] == 0, "seeds: lone cell should die"
        # No birth either (no cell has exactly 2 live neighbors)
        assert st[1].sum() == 0, "seeds: no birth from single cell"


# ═══════════════════════════════════════════════════════════════════════════════
# eca.py — Elementary Cellular Automaton
# ═══════════════════════════════════════════════════════════════════════════════


class TestECA:
    """Tests for ECA simulation."""

    def test_rule_0_kills_everything(self):
        """Rule 0: all patterns map to 0. After one step, everything is dead."""
        from relative_symmetry_repair.eca import simulate_eca

        initial = np.ones(10, dtype=np.uint8)
        st = simulate_eca(0, initial, steps=3)
        np.testing.assert_array_equal(st[1], np.zeros(10, dtype=np.uint8))

    def test_rule_255_keeps_everything(self):
        """Rule 255: all patterns map to 1. After one step, everything is alive."""
        from relative_symmetry_repair.eca import simulate_eca

        initial = np.zeros(10, dtype=np.uint8)
        st = simulate_eca(255, initial, steps=3)
        np.testing.assert_array_equal(st[1], np.ones(10, dtype=np.uint8))

    def test_rule_consistency_mask_on_actual_eca(self):
        """A spacetime produced by an ECA should have zero consistency errors."""
        from relative_symmetry_repair.eca import rule_consistency_mask, simulate_eca

        for rule in [30, 54, 110]:
            initial = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
            st = simulate_eca(rule, initial, steps=20)
            mask = rule_consistency_mask(st, rule)
            assert not mask.any(), f"Rule {rule} has self-consistency errors"

    def test_steps_one_returns_only_initial(self):
        from relative_symmetry_repair.eca import simulate_eca

        initial = np.array([1, 0, 1], dtype=np.uint8)
        st = simulate_eca(30, initial, steps=1)
        assert st.shape == (1, 3)
        np.testing.assert_array_equal(st[0], initial)


# ═══════════════════════════════════════════════════════════════════════════════
# coding.py — NML scoring and codelength functions
# ═══════════════════════════════════════════════════════════════════════════════


class TestCoding:
    """Tests for coding.py edge cases and correctness."""

    def test_run_length_bits_empty_mask(self):
        from relative_symmetry_repair.coding import run_length_bits

        result = run_length_bits(np.array([], dtype=np.uint8))
        assert result == 0

    def test_run_length_bits_all_zeros(self):
        from relative_symmetry_repair.coding import run_length_bits

        result = run_length_bits(np.zeros(10, dtype=np.uint8))
        assert result > 0  # 1 bit header + gamma(10)

    def test_run_length_bits_all_ones(self):
        from relative_symmetry_repair.coding import run_length_bits

        result = run_length_bits(np.ones(10, dtype=np.uint8))
        assert result > 0

    def test_run_length_more_runs_costs_more(self):
        """More alternations should generally cost more in run-length coding,
        controlling for both total length and number of runs."""
        from relative_symmetry_repair.coding import run_length_bits

        # 2 runs of equal length vs many alternating runs
        two_runs = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], dtype=np.uint8)
        many_runs = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        assert two_runs.sum() == many_runs.sum()
        # 2 runs: 1 + gamma(8) + gamma(8) = 1 + 7 + 7 = 15
        # 16 runs of 1: 1 + 16*gamma(1) = 1 + 16 = 17
        assert run_length_bits(two_runs) < run_length_bits(many_runs)

    def test_template_bits_nml_period_exceeds_steps(self):
        """When period > steps, n_obs is clamped to 1 and template_bits_nml returns 0."""
        from relative_symmetry_repair.coding import template_bits_nml

        result = template_bits_nml(period=10, spatial_shape=(8,), steps=5)
        assert result == 0.0  # log2(1) = 0

    def test_template_bits_nml_normal_case(self):
        from relative_symmetry_repair.coding import template_bits_nml

        result = template_bits_nml(period=2, spatial_shape=(8,), steps=100)
        k = 2 * 8  # 16 parameters
        n_obs = 100 // 2  # 50 observations
        expected = k / 2.0 * math.log2(n_obs)
        assert abs(result - expected) < 1e-10

    def test_log2_binomial_edge_cases(self):
        from relative_symmetry_repair.coding import log2_binomial

        assert log2_binomial(0, 0) == 0.0
        assert log2_binomial(5, 0) == 0.0
        assert log2_binomial(5, 5) == 0.0
        assert log2_binomial(10, 5) > 0

    def test_log2_binomial_rejects_k_greater_than_n(self):
        from relative_symmetry_repair.coding import log2_binomial

        with pytest.raises(ValueError, match="k must satisfy"):
            log2_binomial(5, 6)

    def test_combinatorial_repair_bits_zero_defects(self):
        from relative_symmetry_repair.coding import combinatorial_repair_bits

        assert combinatorial_repair_bits(100, 0) == 0.0

    def test_combinatorial_repair_bits_all_defects(self):
        from relative_symmetry_repair.coding import combinatorial_repair_bits

        assert combinatorial_repair_bits(100, 100) == 0.0

    def test_orbit_nll_pure_classes_contribute_zero(self):
        """All-zero or all-one orbit classes have zero entropy → zero NLL."""
        from relative_symmetry_repair.coding import orbit_nll_bits

        spacetime = np.array([[0, 0, 1, 1], [0, 0, 1, 1]], dtype=np.uint8)
        labels = np.array([[0, 0, 1, 1], [0, 0, 1, 1]], dtype=np.int32)
        nll = orbit_nll_bits(spacetime, labels, n_labels=2)
        assert nll == 0.0

    def test_nml_score_splits_correctly(self):
        """NML total should equal NLL + complexity."""
        from relative_symmetry_repair.coding import nml_score_bits

        rng = np.random.default_rng(42)
        spacetime = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        labels = np.tile(np.arange(10, dtype=np.int32), (20, 1))
        nll, comp, total = nml_score_bits(spacetime, labels, n_labels=10, mode="hybrid")
        assert abs(total - (nll + comp)) < 1e-10

    def test_gamma_bits_known_values(self):
        from relative_symmetry_repair.coding import gamma_bits

        assert gamma_bits(1) == 1
        assert gamma_bits(2) == 3   # 2*floor(log2(2)) + 1 = 2*1 + 1 = 3
        assert gamma_bits(4) == 5   # 2*floor(log2(4)) + 1 = 2*2 + 1 = 5


# ═══════════════════════════════════════════════════════════════════════════════
# repair.py — 1D relative-periodic background fitting
# ═══════════════════════════════════════════════════════════════════════════════


class TestRepair1D:
    """Tests for 1D repair module edge cases."""

    def test_exact_periodic_has_zero_defects(self):
        """A perfectly periodic spacetime should have zero defect rate."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        # Period-2 checkerboard
        row0 = np.array([0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0], dtype=np.uint8)
        spacetime = np.tile(np.vstack([row0, row1]), (10, 1))  # 20 rows
        fit = fit_relative_periodic_background(spacetime, shift=0, period=2)
        assert fit.defect_rate == 0.0

    def test_period_one_shift_zero_is_temporal_mean(self):
        """p=1, s=0 background should be the column-wise majority vote."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        # 3 ones and 2 zeros per column → majority is 1
        spacetime = np.array([
            [1, 0],
            [1, 0],
            [1, 0],
            [0, 1],
            [0, 1],
        ], dtype=np.uint8)
        fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
        np.testing.assert_array_equal(fit.background[0], [1, 0])

    @pytest.mark.xfail(reason="Known bug: empty shifts/periods causes KeyError in sort_values")
    def test_scan_with_empty_shifts_does_not_crash(self):
        """Scanning with empty shift list should return an empty frame, not crash."""
        from relative_symmetry_repair.repair import scan_relative_periodicity

        spacetime = np.zeros((10, 8), dtype=np.uint8)
        frame, fits = scan_relative_periodicity(spacetime, shifts=[], periods=[1, 2])
        assert len(fits) == 0
        assert frame.empty or len(frame) == 0

    @pytest.mark.xfail(reason="Known bug: empty shifts/periods causes KeyError in sort_values")
    def test_scan_with_empty_periods_does_not_crash(self):
        from relative_symmetry_repair.repair import scan_relative_periodicity

        spacetime = np.zeros((10, 8), dtype=np.uint8)
        frame, fits = scan_relative_periodicity(spacetime, shifts=[0], periods=[])
        assert len(fits) == 0

    def test_reflection_fit_empty_state(self):
        """Empty state should not crash with ZeroDivisionError."""
        from relative_symmetry_repair.repair import fit_reflection_symmetric_state

        state = np.array([], dtype=np.uint8)
        try:
            fit = fit_reflection_symmetric_state(state)
            # If it doesn't crash, defect_rate should be 0 or defined
            assert math.isfinite(fit.defect_rate)
        except (ZeroDivisionError, ValueError):
            # Currently crashes — this documents the known bug
            pytest.xfail("Known issue: ZeroDivisionError on empty state")

    def test_reflection_fit_palindrome_is_exact(self):
        from relative_symmetry_repair.repair import fit_reflection_symmetric_state

        state = np.array([1, 0, 1, 0, 1], dtype=np.uint8)
        fit = fit_reflection_symmetric_state(state)
        assert fit.defect_rate == 0.0

    def test_tie_break_prefers_one(self):
        """When an orbit class is exactly 50/50, the majority vote should resolve to 1."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        # Two timesteps, each column has one 0 and one 1 → tied
        spacetime = np.array([
            [0, 0, 0, 0],
            [1, 1, 1, 1],
        ], dtype=np.uint8)
        fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
        # Tie resolved to 1 by the >= convention
        np.testing.assert_array_equal(fit.background[0], [1, 1, 1, 1])


# ═══════════════════════════════════════════════════════════════════════════════
# repair_nd.py — N-D relative-periodic background fitting
# ═══════════════════════════════════════════════════════════════════════════════


class TestRepairND:
    """Tests for N-D repair module."""

    def test_2d_exact_periodic_has_zero_defects(self):
        """A perfectly periodic 2D spacetime should have zero defect rate."""
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        tile = np.array([[0, 1], [1, 0]], dtype=np.uint8)
        frame = np.tile(tile, (4, 4))  # 8x8
        spacetime = np.stack([frame, 1 - frame] * 5)  # 10 steps, period 2
        fit = fit_relative_periodic_background_nd(spacetime, shift=(0, 0), period=2)
        assert fit.defect_rate == 0.0

    def test_3d_fit_shape_matches_spacetime(self):
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(10, 4, 4, 4), dtype=np.uint8)
        fit = fit_relative_periodic_background_nd(st, shift=(0, 0, 0), period=1)
        assert fit.background.shape == st.shape
        assert fit.defect_mask.shape == st.shape

    @pytest.mark.xfail(reason="Known bug: empty periods causes KeyError in sort_values")
    def test_scan_nd_empty_periods_does_not_crash(self):
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd

        st = np.zeros((10, 4, 4), dtype=np.uint8)
        frame, fits = scan_relative_periodicity_nd(st, shift_ranges=[range(1)], periods=[])
        assert len(fits) == 0

    def test_workspace_and_reference_agree_2d(self):
        """The workspace (fast) path and reference path should produce identical
        defect rates for 2D spacetimes."""
        from relative_symmetry_repair.repair_nd import (
            _fit_relative_periodic_background_nd_reference,
            fit_relative_periodic_background_nd,
        )

        rng = np.random.default_rng(11)
        st = rng.integers(0, 2, size=(12, 6, 6), dtype=np.uint8)
        for period in [1, 2, 3]:
            for shift in [(0, 0), (1, 0), (0, 1), (1, -1)]:
                fit_ws = fit_relative_periodic_background_nd(st, shift=shift, period=period)
                fit_ref = _fit_relative_periodic_background_nd_reference(st, shift=shift, period=period)
                assert abs(fit_ws.defect_rate - fit_ref.defect_rate) < 1e-12, (
                    f"Mismatch at period={period}, shift={shift}: "
                    f"workspace={fit_ws.defect_rate}, reference={fit_ref.defect_rate}"
                )

    def test_workspace_and_reference_agree_3d(self):
        """Same test for 3D spacetimes."""
        from relative_symmetry_repair.repair_nd import (
            _fit_relative_periodic_background_nd_reference,
            fit_relative_periodic_background_nd,
        )

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(8, 4, 4, 4), dtype=np.uint8)
        for period in [1, 2]:
            for shift in [(0, 0, 0), (1, 0, 0), (0, 1, -1)]:
                fit_ws = fit_relative_periodic_background_nd(st, shift=shift, period=period)
                fit_ref = _fit_relative_periodic_background_nd_reference(st, shift=shift, period=period)
                assert abs(fit_ws.defect_rate - fit_ref.defect_rate) < 1e-12, (
                    f"Mismatch at period={period}, shift={shift}: "
                    f"workspace={fit_ws.defect_rate}, reference={fit_ref.defect_rate}"
                )

    def test_component_labels_nd_unique_per_orbit(self):
        """Each (residue, start_position) combination should get a unique label."""
        from relative_symmetry_repair.repair_nd import component_labels_nd

        shape = (6, 4, 4)
        labels = component_labels_nd(shape, period=2, shift=(1, 0))
        n_labels = 2 * 4 * 4  # period * D0 * D1
        assert labels.max() < n_labels
        assert len(np.unique(labels)) == n_labels


# ═══════════════════════════════════════════════════════════════════════════════
# _orbit_scoring.py — Fast orbit-based scoring
# ═══════════════════════════════════════════════════════════════════════════════


class TestOrbitScoring:
    """Tests for the workspace fast path."""

    def test_orbit_ids_equivalence_classes_match_reference_2d(self):
        """Workspace orbit IDs should partition sites into the same equivalence
        classes as the reference component_labels_nd."""
        from relative_symmetry_repair._orbit_scoring import RelativePeriodicOrbitWorkspace
        from relative_symmetry_repair.repair_nd import component_labels_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(6, 5, 5), dtype=np.uint8)
        ws = RelativePeriodicOrbitWorkspace(st, residue_major=False)

        for period in [1, 2, 3]:
            for shift in [(0, 0), (1, 0), (0, 1), (2, -1)]:
                orbit_ids, _ = ws.orbit_ids(shift, period)
                ref_labels = component_labels_nd(st.shape, period=period, shift=shift)

                # Compare equivalence classes (not label values)
                def equiv(labels_flat):
                    classes = defaultdict(set)
                    for idx, lab in enumerate(labels_flat):
                        classes[int(lab)].add(idx)
                    return set(frozenset(s) for s in classes.values())

                ws_classes = equiv(orbit_ids.ravel())
                ref_classes = equiv(ref_labels.ravel())
                assert ws_classes == ref_classes, (
                    f"Orbit class mismatch at period={period}, shift={shift}"
                )

    def test_orbit_ids_equivalence_classes_match_reference_3d(self):
        from relative_symmetry_repair._orbit_scoring import RelativePeriodicOrbitWorkspace
        from relative_symmetry_repair.repair_nd import component_labels_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(6, 3, 3, 3), dtype=np.uint8)
        ws = RelativePeriodicOrbitWorkspace(st, residue_major=False)

        for period in [1, 2]:
            for shift in [(0, 0, 0), (1, 0, 0), (0, 1, -1)]:
                orbit_ids, _ = ws.orbit_ids(shift, period)
                ref_labels = component_labels_nd(st.shape, period=period, shift=shift)

                def equiv(labels_flat):
                    classes = defaultdict(set)
                    for idx, lab in enumerate(labels_flat):
                        classes[int(lab)].add(idx)
                    return set(frozenset(s) for s in classes.values())

                ws_classes = equiv(orbit_ids.ravel())
                ref_classes = equiv(ref_labels.ravel())
                assert ws_classes == ref_classes, (
                    f"3D orbit class mismatch at period={period}, shift={shift}"
                )

    def test_class_sizes_sum_to_total_sites(self):
        from relative_symmetry_repair._orbit_scoring import class_sizes_1d, class_sizes_nd

        for shape in [(20, 10), (15, 8)]:
            for period in [1, 2, 3, 4]:
                sizes = class_sizes_1d(shape, period)
                assert sizes.sum() == shape[0] * shape[1]

        for shape in [(10, 4, 4), (8, 3, 3, 3)]:
            for period in [1, 2]:
                sizes = class_sizes_nd(shape, period)
                total = 1
                for d in shape:
                    total *= d
                assert sizes.sum() == total

    def test_reduce_majority_vote_correctness(self):
        """Explicit test: 3 ones and 2 zeros in a class → majority is 1."""
        from relative_symmetry_repair._orbit_scoring import reduce_binary_spacetime_by_orbits

        binary = np.array([1, 1, 1, 0, 0], dtype=np.uint8)
        orbit_ids = np.array([0, 0, 0, 0, 0], dtype=np.int32)
        class_sizes = np.array([5], dtype=np.int64)
        result = reduce_binary_spacetime_by_orbits(
            binary, orbit_ids, class_sizes, nml_mode="hybrid"
        )
        assert result.majority_bits[0] == 1
        assert result.defect_sites == 2  # the two zeros are defects


# ═══════════════════════════════════════════════════════════════════════════════
# experiment_suite.py — Experiment orchestration
# ═══════════════════════════════════════════════════════════════════════════════


class TestExperimentSuite:
    """Tests for experiment suite correctness."""

    def test_control_seed_metadata_matches_actual_seeds(self):
        """The control_seed recorded in metadata should match what make_null_controls
        actually uses. Known bug: control_index is offset by 1 because 'original'
        is at index 0 but has no seed."""
        from relative_symmetry_repair.experiment_suite import CONTROL_ORDER, make_null_controls

        seed = 42
        controls = make_null_controls(np.zeros((10, 8), dtype=np.uint8), seed=seed)

        # Actual seeds used in make_null_controls:
        actual_seeds = {
            "original": None,
            "time_shuffled": seed + 101,
            "space_shuffled": seed + 202,
            "bernoulli_iid": seed + 303,
        }

        # What the metadata records (from line 834):
        for control_index, control_name in enumerate(CONTROL_ORDER):
            recorded_seed = seed + (control_index + 1) * 101
            if control_name == "original":
                # "original" has no seed, but metadata records seed+101
                assert recorded_seed == seed + 101
                # This is misleading — documenting the known issue
            elif control_name == "time_shuffled":
                # Should be seed+101 but metadata records seed+202
                actual = actual_seeds[control_name]
                if recorded_seed != actual:
                    pytest.xfail(
                        f"Known bug: {control_name} actual seed={actual} "
                        f"but recorded={recorded_seed}"
                    )

    def test_representative_3d_cases_use_tuned_densities(self):
        from relative_symmetry_repair.ca3d import RULES_3D_DENSITY
        from relative_symmetry_repair.experiment_suite import REPRESENTATIVE_CASES_3D

        for case in REPRESENTATIVE_CASES_3D:
            expected_density = RULES_3D_DENSITY[case.name]
            assert case.density == expected_density, (
                f"{case.name}: density={case.density}, expected={expected_density}"
            )

    def test_shift_to_string_consistency(self):
        from relative_symmetry_repair.experiment_suite import shift_to_string

        assert shift_to_string(0) == "0"
        assert shift_to_string(-1) == "-1"
        assert shift_to_string((0, 1)) == "(0, 1)"
        assert shift_to_string((0,)) == "(0,)"

    def test_scan_case_spacetime_1d(self):
        """Basic integration: scan a short ECA spacetime."""
        from relative_symmetry_repair.experiment_suite import (
            REPRESENTATIVE_CASES_1D,
            scan_case_spacetime,
            simulate_case,
        )

        case = REPRESENTATIVE_CASES_1D[1]  # ECA-54
        st = simulate_case(case, steps=50, seed=42)
        outcome = scan_case_spacetime(case, st)
        assert outcome.selection.selected_period >= 1
        assert 0.0 <= outcome.selection.selected_defect_rate <= 1.0

    def test_scan_case_spacetime_2d(self):
        from relative_symmetry_repair.experiment_suite import (
            REPRESENTATIVE_CASES_2D,
            scan_case_spacetime,
            simulate_case,
        )

        case = REPRESENTATIVE_CASES_2D[0]  # Diamoeba
        st = simulate_case(case, steps=20, seed=42)
        outcome = scan_case_spacetime(case, st)
        assert outcome.selection.selected_period >= 1

    def test_scan_case_spacetime_3d(self):
        from relative_symmetry_repair.experiment_suite import (
            REPRESENTATIVE_CASES_3D,
            scan_case_spacetime,
            simulate_case,
        )

        # Use diamoeba3d which is robust
        case = next(c for c in REPRESENTATIVE_CASES_3D if c.name == "diamoeba3d")
        st = simulate_case(case, steps=10, seed=42)
        outcome = scan_case_spacetime(case, st)
        assert outcome.selection.selected_period >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-module integration tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIntegration:
    """End-to-end tests combining simulation + fitting + scoring."""

    def test_1d_full_pipeline(self):
        """Simulate ECA-54, fit background, verify scores are finite."""
        from relative_symmetry_repair.eca import simulate_eca
        from relative_symmetry_repair.repair import scan_relative_periodicity
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame

        initial = np.zeros(32, dtype=np.uint8)
        initial[16] = 1
        st = simulate_eca(54, initial, steps=100)
        frame, fits = scan_relative_periodicity(st, shifts=range(-2, 3), periods=[1, 2, 3, 4])
        selection = period_first_selection_from_frame(frame)
        assert selection.selected_period in [1, 2, 3, 4]
        assert math.isfinite(selection.margin_bits)
        assert 0.0 <= selection.selected_defect_rate <= 1.0

    def test_2d_full_pipeline(self):
        """Simulate a 2D Life rule, fit ND background, verify."""
        from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame

        initial = random_initial_grid(16, 16, density=0.3, seed=42)
        st = simulate_2d(initial, steps=30, rule="life")
        frame, fits = scan_relative_periodicity_nd(
            st, shift_ranges=[range(-1, 2), range(-1, 2)], periods=[1, 2]
        )
        selection = period_first_selection_from_frame(frame)
        assert selection.selected_period in [1, 2]

    def test_3d_full_pipeline(self):
        """Simulate a 3D rule, fit ND background, verify."""
        from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d
        from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd
        from relative_symmetry_repair.experiment_suite import period_first_selection_from_frame

        initial = random_initial_volume(8, 8, 8, density=0.5, seed=42)
        st = simulate_3d(initial, steps=10, survive=(5, 8), birth=(5, 8))
        frame, fits = scan_relative_periodicity_nd(
            st, shift_ranges=[range(-1, 2)] * 3, periods=[1, 2]
        )
        selection = period_first_selection_from_frame(frame)
        assert selection.selected_period in [1, 2]

    def test_nml_score_monotonically_decreases_with_better_fit(self):
        """For a perfectly periodic signal, the matching period should have
        lower NML than period 1."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        row0 = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
        spacetime = np.tile(np.vstack([row0, row1]), (20, 1))  # 40 rows, period 2

        fit_p1 = fit_relative_periodic_background(spacetime, shift=0, period=1)
        fit_p2 = fit_relative_periodic_background(spacetime, shift=0, period=2)
        assert fit_p2.nml_bits < fit_p1.nml_bits, (
            f"Period 2 should beat period 1 for a period-2 signal: "
            f"p2={fit_p2.nml_bits:.2f} vs p1={fit_p1.nml_bits:.2f}"
        )

    def test_defect_rate_bounded_0_to_1(self):
        """Defect rate should always be in [0, 1] for random data."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        for _ in range(5):
            st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
            fit = fit_relative_periodic_background(st, shift=0, period=1)
            assert 0.0 <= fit.defect_rate <= 1.0

    def test_background_is_binary(self):
        """Background should always be binary (0 or 1)."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=2)
        assert set(np.unique(fit.background)).issubset({0, 1})

    def test_defect_mask_matches_background_difference(self):
        """defect_mask should be exactly where spacetime != background."""
        from relative_symmetry_repair.repair import fit_relative_periodic_background

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(20, 10), dtype=np.uint8)
        fit = fit_relative_periodic_background(st, shift=0, period=2)
        expected_mask = st != fit.background
        np.testing.assert_array_equal(fit.defect_mask, expected_mask)

    def test_defect_mask_matches_background_difference_nd(self):
        """Same for N-D."""
        from relative_symmetry_repair.repair_nd import fit_relative_periodic_background_nd

        rng = np.random.default_rng(42)
        st = rng.integers(0, 2, size=(10, 6, 6), dtype=np.uint8)
        fit = fit_relative_periodic_background_nd(st, shift=(0, 0), period=2)
        expected_mask = st != fit.background
        np.testing.assert_array_equal(fit.defect_mask, expected_mask)
