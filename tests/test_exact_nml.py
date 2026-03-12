import numpy as np

from relative_symmetry_repair.coding import (
    _exact_bernoulli_regret,
    nml_complexity_bits,
)
from relative_symmetry_repair.repair import component_labels
from relative_symmetry_repair.selection import select_period


def test_exact_mode_sums_exact_regrets_over_orbit_classes():
    labels = np.array(
        [
            [0, 0, 1],
            [0, 0, 1],
        ],
        dtype=np.int32,
    )
    # Orbit sizes are 4 and 2.
    expected = _exact_bernoulli_regret(4) + _exact_bernoulli_regret(2)
    actual = nml_complexity_bits(labels, n_labels=2, mode="exact")
    assert abs(actual - expected) < 1e-12


def test_exact_and_asymptotic_nml_disagree_on_short_horizon_case():
    spacetime = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 0],
            [0, 0, 1],
        ],
        dtype=np.uint8,
    )
    exact = select_period(spacetime, shifts=[0], periods=[1, 2, 3], nml_mode="exact")
    asymptotic = select_period(
        spacetime,
        shifts=[0],
        periods=[1, 2, 3],
        nml_mode="asymptotic",
    )
    assert exact.selected.period == 3
    assert asymptotic.selected.period == 2


def test_exact_and_asymptotic_nml_agree_on_simple_large_exact_oscillator():
    row0 = np.array([0, 1, 0, 1], dtype=np.uint8)
    row1 = np.array([1, 0, 1, 0], dtype=np.uint8)
    spacetime = np.tile(np.vstack([row0, row1]), (20, 1))
    exact = select_period(spacetime, shifts=[0], periods=[1, 2, 4], nml_mode="exact")
    asymptotic = select_period(
        spacetime,
        shifts=[0],
        periods=[1, 2, 4],
        nml_mode="asymptotic",
    )
    assert exact.selected.period == 2
    assert asymptotic.selected.period == 2


def test_hybrid_mode_matches_legacy_exact_true_path_on_small_case():
    spacetime = np.array(
        [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0],
            [1, 0, 1],
        ],
        dtype=np.uint8,
    )
    labels = component_labels(spacetime.shape, shift=0, period=2)
    hybrid = nml_complexity_bits(labels, n_labels=6, mode="hybrid")
    legacy = nml_complexity_bits(labels, n_labels=6, exact=True)
    assert hybrid == legacy
