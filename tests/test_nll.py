import math

import numpy as np

from relative_symmetry_repair.coding import nml_complexity_bits, nml_score_bits, orbit_nll_bits


def test_orbit_nll_is_zero_for_pure_classes():
    spacetime = np.array(
        [
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
        ],
        dtype=np.uint8,
    )
    labels = np.array(
        [
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
        ],
        dtype=np.int32,
    )
    assert orbit_nll_bits(spacetime, labels, n_labels=2) == 0.0


def test_orbit_nll_matches_hand_computed_fifty_fifty_case():
    spacetime = np.array(
        [
            [0, 1],
            [1, 1],
            [0, 1],
            [1, 1],
        ],
        dtype=np.uint8,
    )
    labels = np.array(
        [
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
        ],
        dtype=np.int32,
    )
    # Class 0 has values [0,1,0,1] so theta=1/2 and contributes 4 * H(1/2)=4 bits.
    # Class 1 is pure ones and contributes 0.
    assert orbit_nll_bits(spacetime, labels, n_labels=2) == 4.0


def test_asymptotic_complexity_is_half_log_sum_of_class_sizes():
    labels = np.array(
        [
            [0, 0, 1, 2],
            [0, 0, 1, 2],
        ],
        dtype=np.int32,
    )
    # Class sizes are [4, 2, 2].
    expected = 0.5 * (math.log2(4) + math.log2(2) + math.log2(2))
    actual = nml_complexity_bits(labels, n_labels=3, mode="asymptotic")
    assert abs(actual - expected) < 1e-12


def test_nml_score_splits_into_nll_plus_complexity():
    spacetime = np.array(
        [
            [0, 0],
            [1, 0],
            [0, 0],
            [1, 0],
        ],
        dtype=np.uint8,
    )
    labels = np.array(
        [
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
        ],
        dtype=np.int32,
    )
    nll, complexity, total = nml_score_bits(spacetime, labels, n_labels=2, mode="exact")
    assert nll == 4.0
    assert abs(total - (nll + complexity)) < 1e-12
