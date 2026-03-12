import itertools

import numpy as np

from relative_symmetry_repair.repair import component_labels, fit_relative_periodic_background


def _enumerate_orbit_constant_backgrounds(shape, *, shift: int, period: int):
    labels = component_labels(shape, shift=shift, period=period)
    n_labels = period * shape[1]
    for template_bits in itertools.product([0, 1], repeat=n_labels):
        template = np.array(template_bits, dtype=np.uint8)
        yield template[labels]


def _minority_sum(spacetime: np.ndarray, *, shift: int, period: int) -> int:
    labels = component_labels(spacetime.shape, shift=shift, period=period)
    n_labels = period * spacetime.shape[1]
    total = 0
    for label in range(n_labels):
        values = spacetime[labels == label]
        ones = int(values.sum())
        zeros = int(values.size - ones)
        total += min(ones, zeros)
    return total


def test_all_zero_and_all_one_spacetimes_have_zero_defects():
    for fill in [0, 1]:
        spacetime = np.full((6, 4), fill, dtype=np.uint8)
        fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
        assert fit.defect_sites == 0
        assert fit.defect_rate == 0.0
        assert np.array_equal(fit.background, spacetime)


def test_exact_translated_background_has_zero_defects():
    row0 = np.array([1, 0, 1, 0], dtype=np.uint8)
    spacetime = np.vstack([np.roll(row0, t) for t in range(6)]).astype(np.uint8)
    fit = fit_relative_periodic_background(spacetime, shift=1, period=1)
    assert fit.defect_sites == 0
    assert fit.defect_rate == 0.0


def test_tie_break_is_deterministic_and_prefers_one():
    spacetime = np.array([[0], [1], [0], [1]], dtype=np.uint8)
    fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
    assert np.array_equal(fit.background, np.ones_like(spacetime))
    assert fit.defect_sites == 2
    assert fit.defect_rate == 0.5


def test_defect_count_equals_sum_of_per_class_minorities_explicit_case():
    spacetime = np.array(
        [
            [0, 1],
            [0, 1],
            [1, 0],
            [1, 0],
        ],
        dtype=np.uint8,
    )
    fit = fit_relative_periodic_background(spacetime, shift=0, period=1)
    assert fit.defect_sites == _minority_sum(spacetime, shift=0, period=1)


def test_projection_is_hamming_optimal_against_bruteforce_templates():
    spacetime = np.array(
        [
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 1, 1],
        ],
        dtype=np.uint8,
    )
    fit = fit_relative_periodic_background(spacetime, shift=1, period=2)
    brute_force_min = min(
        int((spacetime != background).sum())
        for background in _enumerate_orbit_constant_backgrounds(
            spacetime.shape,
            shift=1,
            period=2,
        )
    )
    assert fit.defect_sites == brute_force_min
    assert fit.defect_sites == _minority_sum(spacetime, shift=1, period=2)
