import numpy as np

from relative_symmetry_repair.eca import simulate_eca
from relative_symmetry_repair.repair import component_labels, fit_reflection_symmetric_state, fit_relative_periodic_background


def test_component_labels_respect_relative_periodicity():
    labels = component_labels((8, 10), shift=2, period=3)
    for t in range(8 - 3):
        expected = np.roll(labels[t], 2)
        assert np.array_equal(labels[t + 3], expected)


def test_reflection_fit_is_exact_on_symmetric_input():
    state = np.array([0, 1, 0, 1, 1, 0, 1, 0], dtype=np.uint8)
    fit = fit_reflection_symmetric_state(state)
    assert fit.defect_sites == 0
    assert np.array_equal(fit.target, state)


def test_relative_periodic_fit_returns_same_shape():
    initial = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=np.uint8)
    spacetime = simulate_eca(rule=110, initial=initial, steps=12)
    fit = fit_relative_periodic_background(spacetime, shift=0, period=4, rule=110)
    assert fit.background.shape == spacetime.shape
    assert fit.defect_mask.shape == spacetime.shape
