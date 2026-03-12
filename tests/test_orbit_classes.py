import numpy as np

from relative_symmetry_repair.repair import component_labels
from relative_symmetry_repair.repair_nd import component_labels_nd


def test_component_labels_period_one_shift_zero_are_column_classes():
    labels = component_labels((4, 3), shift=0, period=1)
    expected = np.array(
        [
            [0, 1, 2],
            [0, 1, 2],
            [0, 1, 2],
            [0, 1, 2],
        ],
        dtype=np.int32,
    )
    assert np.array_equal(labels, expected)


def test_component_labels_period_one_shift_one_follow_diagonals():
    labels = component_labels((4, 4), shift=1, period=1)
    expected = np.array(
        [
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
        ],
        dtype=np.int32,
    )
    assert np.array_equal(labels, expected)


def test_component_labels_period_two_shift_zero_split_by_time_residue():
    labels = component_labels((4, 3), shift=0, period=2)
    expected = np.array(
        [
            [0, 1, 2],
            [3, 4, 5],
            [0, 1, 2],
            [3, 4, 5],
        ],
        dtype=np.int32,
    )
    assert np.array_equal(labels, expected)


def test_component_labels_nd_manual_small_case():
    labels = component_labels_nd((3, 2, 2), shift=(1, 0), period=1)
    expected = np.array(
        [
            [[0, 2], [1, 3]],
            [[1, 3], [0, 2]],
            [[0, 2], [1, 3]],
        ],
        dtype=np.int32,
    )
    assert np.array_equal(labels, expected)
