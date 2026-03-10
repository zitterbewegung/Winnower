"""Executable tests for the corrected theorem suite.

Tests cover:
- Partition projection theorem (Theorem A)
- Partition-refinement monotonicity (Theorem B)
- Counterexample to false monotonicity (paper's Theorem 2)
- Counterexample to false period-convergence claim (Theorem D)
- Correct velocity-matched refinement (Theorem C.2)
- RL codelength separation (Proposition 1)
- NML vs MDL score comparison basics
"""

import math

import numpy as np
import pytest

from relative_symmetry_repair.coding import (
    gamma_bits,
    log2_binomial,
    run_length_bits,
    template_bits_nml,
)
from relative_symmetry_repair.repair import (
    component_labels,
    fit_relative_periodic_background,
)
from relative_symmetry_repair.repair_nd import (
    component_labels_nd,
    fit_relative_periodic_background_nd,
)


# ──────────────────────────────────────────────────────────────────────
# A. Partition Projection Theorem
# ──────────────────────────────────────────────────────────────────────


class TestPartitionProjection:
    """Theorem A: majority vote minimizes Hamming distance to F_Pi."""

    def test_exact_periodic_spacetime_has_zero_defects(self):
        """If spacetime is exactly (p,s)-periodic, defect count = 0."""
        # Period-2, shift-0 checkerboard on a ring of width 6
        row0 = np.array([0, 1, 0, 1, 0, 1], dtype=np.uint8)
        row1 = np.array([1, 0, 1, 0, 1, 0], dtype=np.uint8)
        spacetime = np.tile(np.vstack([row0, row1]), (4, 1))  # 8 x 6
        fit = fit_relative_periodic_background(spacetime, shift=0, period=2)
        assert fit.defect_sites == 0

    def test_single_defect_counted_correctly(self):
        """Flip one site in an exact background; defect count = 1."""
        row0 = np.array([0, 0, 0, 0], dtype=np.uint8)
        spacetime = np.tile(row0, (8, 1))  # all zeros, period 1
        spacetime[3, 2] = 1  # one defect
        fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
        # Orbit class for position 2 has 8 members: 7 zeros, 1 one.
        # Majority = 0, so 1 defect.
        assert fit.defect_sites == 1

    def test_tied_orbit_class(self):
        """When an orbit class is exactly tied, defect count = half the class."""
        # 4 time steps, width 2, period 1, shift 0
        # Orbit class 0: positions (t, 0) for t=0..3
        # Orbit class 1: positions (t, 1) for t=0..3
        spacetime = np.array([
            [0, 1],
            [0, 1],
            [1, 0],
            [1, 0],
        ], dtype=np.uint8)
        fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
        # Each orbit class has 2 zeros and 2 ones (tied).
        # Code breaks toward 1 (2*ones >= totals when 2*2 >= 4).
        # So background = all 1s, defect_sites = 4 (the zeros).
        # OR background determined by tie-breaking, defect_sites = 4.
        assert fit.defect_sites == 4  # 2 defects per class * 2 classes

    def test_minimum_equals_sum_of_minorities(self):
        """The defect count equals sum of min(n_j^0, n_j^1)."""
        # 6 time steps, width 3, period 2, shift 0
        # 6 orbit classes, each with 3 members
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(6, 3)).astype(np.uint8)
        fit = fit_relative_periodic_background(spacetime, shift=0, period=2)

        labels = component_labels((6, 3), shift=0, period=2)
        n_labels = 2 * 3
        flat_labels = labels.ravel()
        flat_vals = spacetime.ravel()
        expected_defects = 0
        for j in range(n_labels):
            mask = flat_labels == j
            vals = flat_vals[mask]
            ones = vals.sum()
            zeros = mask.sum() - ones
            expected_defects += min(int(ones), int(zeros))
        assert fit.defect_sites == expected_defects

    def test_2d_projection_theorem(self):
        """Theorem A holds for 2D spacetimes too."""
        rng = np.random.RandomState(7)
        spacetime = rng.randint(0, 2, size=(6, 4, 4)).astype(np.uint8)
        fit = fit_relative_periodic_background_nd(
            spacetime, shift=(0, 0), period=2
        )

        labels = component_labels_nd((6, 4, 4), shift=(0, 0), period=2)
        n_labels = 2 * 4 * 4
        flat_labels = labels.ravel()
        flat_vals = spacetime.ravel()
        expected_defects = 0
        for j in range(n_labels):
            mask = flat_labels == j
            vals = flat_vals[mask]
            ones = vals.sum()
            zeros = mask.sum() - ones
            expected_defects += min(int(ones), int(zeros))
        assert fit.defect_sites == expected_defects


# ──────────────────────────────────────────────────────────────────────
# B. Partition-Refinement Monotonicity
# ──────────────────────────────────────────────────────────────────────


class TestPartitionRefinement:
    """Theorem B: refinement implies monotone decrease in defect count."""

    def test_refinement_monotonicity_shift_zero(self):
        """With shift 0, period 2p refines period p. d*(2p) <= d*(p)."""
        rng = np.random.RandomState(99)
        spacetime = rng.randint(0, 2, size=(12, 8)).astype(np.uint8)

        fit_p1 = fit_relative_periodic_background(spacetime, shift=0, period=2)
        fit_p2 = fit_relative_periodic_background(spacetime, shift=0, period=4)
        fit_p3 = fit_relative_periodic_background(spacetime, shift=0, period=8)

        assert fit_p2.defect_sites <= fit_p1.defect_sites
        assert fit_p3.defect_sites <= fit_p2.defect_sites

    def test_refinement_monotonicity_velocity_matched(self):
        """With velocity-matched shifts, refinement holds."""
        # p1=1, s1=1 on D=6. p2=2, s2=2*1=2 mod 6. p3=3, s3=3.
        rng = np.random.RandomState(42)
        spacetime = rng.randint(0, 2, size=(12, 6)).astype(np.uint8)

        fit1 = fit_relative_periodic_background(spacetime, shift=1, period=1)
        fit2 = fit_relative_periodic_background(spacetime, shift=2, period=2)
        fit3 = fit_relative_periodic_background(spacetime, shift=3, period=3)

        assert fit2.defect_sites <= fit1.defect_sites
        assert fit3.defect_sites <= fit1.defect_sites

    def test_refinement_chain_2d(self):
        """Velocity-matched refinement in 2D."""
        rng = np.random.RandomState(7)
        spacetime = rng.randint(0, 2, size=(12, 6, 6)).astype(np.uint8)

        fit1 = fit_relative_periodic_background_nd(
            spacetime, shift=(1, 2), period=1
        )
        # p=2, s should be (2, 4) for velocity match
        fit2 = fit_relative_periodic_background_nd(
            spacetime, shift=(2, 4), period=2
        )
        assert fit2.defect_sites <= fit1.defect_sites


# ──────────────────────────────────────────────────────────────────────
# C. Counterexample to FALSE Monotonicity (Paper's Theorem 2)
# ──────────────────────────────────────────────────────────────────────


class TestMonotonicityCounterexample:
    """Paper's Theorem 2 claims: same shift, p2 = m*p1 => d*(p2) <= d*(p1).
    This is FALSE. We exhibit a concrete counterexample."""

    def test_monotonicity_counterexample(self):
        """D=4, p1=1, s=1, p2=2, s=1: d*(2,1) > d*(1,1) on checkerboard."""
        # Checkerboard: U[t,x] = (t+x) mod 2
        spacetime = np.zeros((4, 4), dtype=np.uint8)
        for t in range(4):
            for x in range(4):
                spacetime[t, x] = (t + x) % 2

        fit1 = fit_relative_periodic_background(spacetime, shift=1, period=1)
        fit2 = fit_relative_periodic_background(spacetime, shift=1, period=2)

        # The spacetime IS exactly (1,1)-periodic (diagonal stripes)
        assert fit1.defect_sites == 0, f"Expected 0 defects for (p=1,s=1), got {fit1.defect_sites}"

        # But (p=2, s=1) partition is transverse to the diagonal structure
        assert fit2.defect_sites > 0, f"Expected >0 defects for (p=2,s=1), got {fit2.defect_sites}"

        # Monotonicity VIOLATED: higher period is worse
        assert fit2.defect_sites > fit1.defect_sites, (
            f"Counterexample failed: d*(2,1)={fit2.defect_sites} should be > d*(1,1)={fit1.defect_sites}"
        )

    def test_monotonicity_counterexample_larger(self):
        """Same counterexample on a larger grid to rule out edge effects."""
        D = 16
        T = 32
        spacetime = np.zeros((T, D), dtype=np.uint8)
        for t in range(T):
            for x in range(D):
                spacetime[t, x] = (t + x) % 2

        fit1 = fit_relative_periodic_background(spacetime, shift=1, period=1)
        fit2 = fit_relative_periodic_background(spacetime, shift=1, period=2)

        assert fit1.defect_sites == 0
        assert fit2.defect_sites > 0
        # On the larger grid, exactly half the sites should be defects
        # because every p2-orbit class mixes equal numbers of 0s and 1s
        assert fit2.defect_sites == T * D // 2  # maximal damage

    def test_monotonicity_counterexample_2d(self):
        """Counterexample extends to 2D.
        U[t,y,x] = (y - t) mod 2 is exactly (1,(1,1))-periodic:
          U[t+1,(y+1)%D,(x+1)%D] = ((y+1)-(t+1)) mod 2 = (y-t) mod 2 = U[t,y,x].
        But NOT (2,(1,1))-periodic: each p=2 orbit class mixes opposite parities.
        """
        D = 4
        T = 4
        spacetime = np.zeros((T, D, D), dtype=np.uint8)
        for t in range(T):
            for y in range(D):
                for x in range(D):
                    spacetime[t, y, x] = (y - t) % 2

        fit1 = fit_relative_periodic_background_nd(
            spacetime, shift=(1, 1), period=1
        )
        fit2 = fit_relative_periodic_background_nd(
            spacetime, shift=(1, 1), period=2
        )

        assert fit1.defect_sites == 0, f"Expected 0 defects for (p=1,s=(1,1)), got {fit1.defect_sites}"
        assert fit2.defect_sites > 0, f"Expected >0 defects for (p=2,s=(1,1)), got {fit2.defect_sites}"

    def test_partition_not_refinement(self):
        """Directly verify that p2-orbits span multiple p1-orbits."""
        D = 4
        T = 4
        labels_p1 = component_labels((T, D), shift=1, period=1)
        labels_p2 = component_labels((T, D), shift=1, period=2)

        # Check that some p2-orbit class contains sites from different p1-classes
        n_p2_classes = 2 * D
        found_violation = False
        for j in range(n_p2_classes):
            p2_mask = labels_p2 == j
            p1_labels_in_class = set(labels_p1[p2_mask].ravel())
            if len(p1_labels_in_class) > 1:
                found_violation = True
                break

        assert found_violation, "Expected p2-orbits to span multiple p1-orbits"


# ──────────────────────────────────────────────────────────────────────
# D. Nonidentifiability / Period Absorption
# ──────────────────────────────────────────────────────────────────────


class TestNonidentifiability:
    """Theorem D: periodic defects can be absorbed by higher periods."""

    def test_periodic_defects_absorbed(self):
        """Period-1 background with defects every 3rd step.
        Period 3 absorbs the defect pattern."""
        D = 8
        T = 30  # divisible by 3
        # Background: all zeros (period 1)
        spacetime = np.zeros((T, D), dtype=np.uint8)
        # Add defects at every 3rd time step
        for t in range(0, T, 3):
            spacetime[t, 0] = 1  # defect at position 0

        fit_p1 = fit_relative_periodic_background(spacetime, shift=0, period=1)
        fit_p3 = fit_relative_periodic_background(spacetime, shift=0, period=3)

        # p=1 sees defects (the ones at every 3rd step, pos 0)
        assert fit_p1.defect_sites > 0

        # p=3 absorbs the pattern: template row 0 has a 1 at position 0
        assert fit_p3.defect_sites == 0, (
            f"Expected 0 defects for p=3 (should absorb periodic defects), got {fit_p3.defect_sites}"
        )

    def test_absorbed_period_wins_mdl(self):
        """The absorbing period wins on MDL score for large T."""
        D = 8
        for T in [30, 60, 120, 300]:
            spacetime = np.zeros((T, D), dtype=np.uint8)
            for t in range(0, T, 3):
                spacetime[t, 0] = 1

            fit_p1 = fit_relative_periodic_background(spacetime, shift=0, period=1)
            fit_p3 = fit_relative_periodic_background(spacetime, shift=0, period=3)

            # For large T, p=3 should have lower NML score
            if T >= 60:
                assert fit_p3.nml_bits < fit_p1.nml_bits, (
                    f"T={T}: p=3 should beat p=1 on NML. "
                    f"p1={fit_p1.nml_bits:.1f}, p3={fit_p3.nml_bits:.1f}"
                )


# ──────────────────────────────────────────────────────────────────────
# E. Run-Length Separation (Proposition 1)
# ──────────────────────────────────────────────────────────────────────


class TestRunLengthSeparation:
    """Proposition 1: RL codelength separates clustered from scattered masks."""

    def test_clustered_vs_scattered(self):
        """Same Hamming weight, vastly different RL codelengths."""
        n = 512
        w = 64

        # Clustered: single block of 1s
        clustered = np.zeros(n, dtype=np.uint8)
        clustered[100:100 + w] = 1

        # Scattered: evenly spaced isolated 1s
        scattered = np.zeros(n, dtype=np.uint8)
        gap = n // w
        for i in range(w):
            scattered[i * gap] = 1

        rl_clustered = run_length_bits(clustered)
        rl_scattered = run_length_bits(scattered)

        # Clustered should be much cheaper
        assert rl_clustered < rl_scattered
        # The ratio should be significant
        ratio = rl_scattered / rl_clustered
        assert ratio > 3, f"Expected ratio > 3, got {ratio:.1f}"

    def test_same_hamming_weight(self):
        """Verify both masks have identical Hamming weight."""
        n = 512
        w = 64

        clustered = np.zeros(n, dtype=np.uint8)
        clustered[100:100 + w] = 1

        scattered = np.zeros(n, dtype=np.uint8)
        gap = n // w
        for i in range(w):
            scattered[i * gap] = 1

        assert clustered.sum() == scattered.sum() == w

    def test_rl_grows_with_fragmentation(self):
        """RL codelength increases monotonically with number of fragments."""
        n = 1024
        w = 32
        prev_rl = 0
        for num_blocks in [1, 2, 4, 8, 16, 32]:
            block_size = w // num_blocks
            gap = (n - w) // num_blocks
            mask = np.zeros(n, dtype=np.uint8)
            pos = 0
            for _ in range(num_blocks):
                mask[pos:pos + block_size] = 1
                pos += block_size + gap
            rl = run_length_bits(mask)
            assert rl >= prev_rl, f"{num_blocks} blocks: rl={rl} < prev={prev_rl}"
            prev_rl = rl


# ──────────────────────────────────────────────────────────────────────
# F. Score Convergence / Stabilization
# ──────────────────────────────────────────────────────────────────────


class TestScoreStabilization:
    """Verify that NML scores have the right asymptotic structure."""

    def test_nll_scales_linearly(self):
        """NLL should grow linearly with T for random spacetimes."""
        D = 8
        rng = np.random.RandomState(42)
        nll_per_site = []
        for T in [50, 100, 200]:
            spacetime = rng.randint(0, 2, size=(T, D)).astype(np.uint8)
            fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
            nll_per_site.append(fit.nll_bits / (T * D))

        # For random data, per-site NLL should be close to 1 bit (H(0.5) = 1)
        for nps in nll_per_site:
            assert 0.8 < nps < 1.2, f"Per-site NLL = {nps}, expected ~1.0"

    def test_complexity_scales_logarithmically(self):
        """NML complexity should grow as O(k * log T)."""
        D = 4
        rng = np.random.RandomState(42)
        comp_values = []
        for T in [50, 100, 200, 400]:
            spacetime = rng.randint(0, 2, size=(T, D)).astype(np.uint8)
            fit = fit_relative_periodic_background(spacetime, shift=0, period=2)
            comp_values.append(fit.nml_complexity)

        # Complexity should grow slower than linearly
        # comp[i+1] / comp[i] should be close to log(T[i+1]) / log(T[i])
        for i in range(len(comp_values) - 1):
            ratio = comp_values[i + 1] / comp_values[i]
            assert ratio < 1.5, f"Complexity ratio {ratio} too large (should be ~1.1-1.3)"

    def test_template_bits_bic_formula(self):
        """Verify template_bits_nml matches the claimed formula (k/2)*log2(T/p)."""
        p = 3
        D = 10
        T = 90
        k = p * D
        n_obs = T // p  # = 30
        expected = (k / 2.0) * math.log2(n_obs)
        actual = template_bits_nml(p, (D,), T)
        assert abs(actual - expected) < 1e-10


# ──────────────────────────────────────────────────────────────────────
# G. Label Consistency Checks
# ──────────────────────────────────────────────────────────────────────


class TestLabelConsistency:
    """Verify orbit label assignments are correct."""

    def test_velocity_matched_labels_refine(self):
        """When s2 = m*s1 mod D, p2-labels refine p1-labels."""
        D = 6
        T = 12
        s1, p1 = 1, 1
        s2, p2 = 2, 2  # velocity matched: 2 = 2*1 mod 6

        labels_p1 = component_labels((T, D), shift=s1, period=p1)
        labels_p2 = component_labels((T, D), shift=s2, period=p2)

        n_p2_classes = p2 * D
        for j in range(n_p2_classes):
            p2_mask = labels_p2 == j
            if not p2_mask.any():
                continue
            p1_labels_in_class = set(labels_p1[p2_mask].ravel())
            assert len(p1_labels_in_class) == 1, (
                f"p2-class {j} maps to multiple p1-classes: {p1_labels_in_class}"
            )

    def test_non_velocity_matched_labels_dont_refine(self):
        """When s2 != m*s1 mod D, refinement may fail."""
        D = 4
        T = 4
        s1, p1 = 1, 1
        s2, p2 = 1, 2  # NOT velocity matched: 1 != 2*1 mod 4

        labels_p1 = component_labels((T, D), shift=s1, period=p1)
        labels_p2 = component_labels((T, D), shift=s2, period=p2)

        n_p2_classes = p2 * D
        found_multi = False
        for j in range(n_p2_classes):
            p2_mask = labels_p2 == j
            if not p2_mask.any():
                continue
            p1_labels_in_class = set(labels_p1[p2_mask].ravel())
            if len(p1_labels_in_class) > 1:
                found_multi = True
                break
        assert found_multi, "Expected to find a p2-class spanning multiple p1-classes"


# ──────────────────────────────────────────────────────────────────────
# H. RL Rate Convergence (Theorem G)
# ──────────────────────────────────────────────────────────────────────


class TestRLConvergence:
    """Theorem G: L_RL/N converges for eventually periodic sequences
    and for finite deterministic CA (under no-ties assumption)."""

    def test_eventually_periodic_sequence_converges(self):
        """Lemma G.1: L_RL/N converges for eventually periodic binary sequences."""
        transient = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 0], dtype=np.uint8)
        period = np.array([1, 1, 0, 1, 0, 0, 1, 0], dtype=np.uint8)

        # Compute theoretical limit from long periodic sequence
        very_long = np.tile(period, 10000)
        rl_limit = run_length_bits(very_long) / len(very_long)

        # Check that L_RL/N converges to limit
        rates = []
        for M in [10, 50, 100, 200]:
            seq = np.concatenate([transient] + [period] * M)
            N = len(seq)
            rl = run_length_bits(seq)
            rates.append(rl / N)

        # Last rate should be close to limit
        assert abs(rates[-1] - rl_limit) < 0.01, (
            f"L_RL/N = {rates[-1]:.6f} not close to limit {rl_limit:.6f}"
        )
        # Rates should be converging (decreasing distance to limit)
        for i in range(1, len(rates)):
            assert abs(rates[i] - rl_limit) <= abs(rates[i-1] - rl_limit) + 0.001

    def test_nll_converges_unconditionally(self):
        """Corollary G.3: NLL/N converges even with exact ties."""
        # Spacetime with orbit class at exactly 50% frequency
        width = 4
        nll_rates = []
        for T in [50, 100, 200, 500, 1000]:
            st = np.zeros((T, width), dtype=np.uint8)
            for t in range(T):
                st[t, 0] = t % 2  # exact 50%
                st[t, 1] = 0
                st[t, 2] = 1
                st[t, 3] = 0
            fit = fit_relative_periodic_background(st, shift=0, period=1)
            nll_rates.append(fit.nll_bits / (T * width))

        # NLL/N should be exactly 0.25 = (1/4) * H(0.5) for all T
        for rate in nll_rates:
            assert abs(rate - 0.25) < 1e-10, f"NLL/N = {rate}, expected 0.25"

    def test_rl_converges_rule110(self):
        """For Rule 110 (transient defects only), L_RL/N -> 0."""
        from relative_symmetry_repair.eca import random_initial_state, simulate_eca

        width = 16
        initial = random_initial_state(width=width, density=0.5, seed=11)
        st = simulate_eca(rule=110, initial=initial, steps=2000)

        rates = []
        for T in [200, 500, 1000, 2000]:
            fit = fit_relative_periodic_background(st[:T], shift=-2, period=4)
            rates.append(fit.run_length_bits / (T * width))

        # Should decrease toward 0
        for i in range(1, len(rates)):
            assert rates[i] < rates[i-1], (
                f"RL/N not decreasing: {rates[i]:.6f} >= {rates[i-1]:.6f}"
            )
        # Last rate should be very small
        assert rates[-1] < 0.05, f"RL/N = {rates[-1]:.6f}, expected < 0.05"

    def test_rl_converges_rule30_width11(self):
        """For Rule 30 width 11 (persistent defects, no ties), L_RL/N converges."""
        from relative_symmetry_repair.eca import random_initial_state, simulate_eca

        width = 11
        initial = random_initial_state(width=width, density=0.5, seed=11)
        st = simulate_eca(rule=30, initial=initial, steps=5000)

        p, s = 1, 0
        rates = []
        for T in [500, 1000, 2000, 3000, 5000]:
            fit = fit_relative_periodic_background(st[:T], shift=s, period=p)
            rates.append(fit.run_length_bits / (T * width))

        # All rates should be close to each other (converged)
        spread = max(rates) - min(rates)
        assert spread < 0.01, (
            f"RL/N spread = {spread:.6f}, expected < 0.01 (rates: {rates})"
        )

    def test_mask_prefix_stability(self):
        """After majority vote stabilizes, mask prefix doesn't change."""
        from relative_symmetry_repair.eca import random_initial_state, simulate_eca

        width = 11
        initial = random_initial_state(width=width, density=0.5, seed=11)
        st = simulate_eca(rule=30, initial=initial, steps=3000)

        p, s = 1, 0
        fit_1000 = fit_relative_periodic_background(st[:1000], shift=s, period=p)
        fit_2000 = fit_relative_periodic_background(st[:2000], shift=s, period=p)
        fit_3000 = fit_relative_periodic_background(st[:3000], shift=s, period=p)

        # Mask prefix should be stable (majority vote already locked)
        assert np.array_equal(
            fit_1000.defect_mask, fit_2000.defect_mask[:1000]
        ), "Mask prefix changed between T=1000 and T=2000"
        assert np.array_equal(
            fit_2000.defect_mask, fit_3000.defect_mask[:2000]
        ), "Mask prefix changed between T=2000 and T=3000"
