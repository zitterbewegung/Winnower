import numpy as np

from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d, rule_consistency_mask_2d
from relative_symmetry_repair.ca3d import random_initial_volume, simulate_3d
from relative_symmetry_repair.repair_nd import (
    component_labels_nd,
    fit_relative_periodic_background_nd,
    extract_components_nd,
)


def test_simulate_2d_shape():
    grid = random_initial_grid(16, 16, seed=42)
    st = simulate_2d(grid, steps=10, rule="life")
    assert st.shape == (10, 16, 16)
    assert st.dtype == np.uint8


def test_simulate_2d_deterministic():
    grid = random_initial_grid(16, 16, seed=42)
    st1 = simulate_2d(grid, steps=10, rule="life")
    st2 = simulate_2d(grid, steps=10, rule="life")
    assert np.array_equal(st1, st2)


def test_rule_consistency_2d_on_actual_run():
    grid = random_initial_grid(16, 16, seed=42)
    st = simulate_2d(grid, steps=10, rule="life")
    mask = rule_consistency_mask_2d(st, survive=(2, 3), birth=(3, 3))
    assert mask.sum() == 0, "Actual Life run should have zero rule violations"


def test_simulate_3d_shape():
    vol = random_initial_volume(8, 8, 8, seed=42)
    st = simulate_3d(vol, steps=5, rule="3d-life")
    assert st.shape == (5, 8, 8, 8)
    assert st.dtype == np.uint8


def test_component_labels_nd_2d_periodicity():
    shape = (8, 10, 12)  # steps=8, H=10, W=12
    shift = (1, 2)
    period = 3
    labels = component_labels_nd(shape, shift=shift, period=period)
    assert labels.shape == shape
    # Check relative-periodic invariance: label[t+p, y, x] == label[t, (y-s0)%H, (x-s1)%W]
    for t in range(shape[0] - period):
        expected = np.roll(np.roll(labels[t], shift[0], axis=0), shift[1], axis=1)
        assert np.array_equal(labels[t + period], expected)


def test_component_labels_nd_3d_periodicity():
    shape = (6, 5, 5, 5)
    shift = (1, -1, 0)
    period = 2
    labels = component_labels_nd(shape, shift=shift, period=period)
    assert labels.shape == shape
    for t in range(shape[0] - period):
        expected = np.roll(
            np.roll(np.roll(labels[t], shift[0], axis=0), shift[1], axis=1), shift[2], axis=2
        )
        assert np.array_equal(labels[t + period], expected)


def test_fit_2d_returns_correct_shape():
    grid = random_initial_grid(12, 12, seed=7)
    st = simulate_2d(grid, steps=8, rule="life")
    fit = fit_relative_periodic_background_nd(st, shift=(0, 0), period=2)
    assert fit.background.shape == st.shape
    assert fit.defect_mask.shape == st.shape
    assert 0.0 <= fit.defect_rate <= 1.0


def test_extract_components_nd_3d():
    mask = np.zeros((4, 4, 4), dtype=np.uint8)
    mask[1, 1, 1] = 1
    mask[1, 1, 2] = 1
    mask[3, 3, 3] = 1
    labels, n = extract_components_nd(mask)
    assert n == 2  # two separate components
