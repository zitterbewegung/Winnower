import numpy as np
import pandas as pd
import pandas.testing as pdt

from relative_symmetry_repair._orbit_scoring import (
    class_sizes_1d,
    class_sizes_nd,
    reduce_binary_spacetime_by_orbits,
)
from relative_symmetry_repair.repair import (
    _fit_relative_periodic_background_reference,
    _scan_relative_periodicity_reference,
    component_labels,
    fit_relative_periodic_background,
    scan_relative_periodicity,
)
from relative_symmetry_repair.repair_nd import (
    _fit_relative_periodic_background_nd_reference,
    _scan_relative_periodicity_nd_reference,
    component_labels_nd,
    fit_relative_periodic_background_nd,
    scan_relative_periodicity_nd,
)
from relative_symmetry_repair.selection import (
    select_period,
    select_period_from_scan,
    select_period_nd,
    select_period_nd_from_scan,
)


def _assert_fit_equal(actual, expected) -> None:
    assert actual.shift == expected.shift
    assert actual.period == expected.period
    assert np.array_equal(actual.background, expected.background)
    assert np.array_equal(actual.defect_mask, expected.defect_mask)
    assert actual.defect_sites == expected.defect_sites
    assert actual.total_sites == expected.total_sites
    assert actual.defect_rate == expected.defect_rate
    assert actual.combinatorial_bits == expected.combinatorial_bits
    assert actual.run_length_bits == expected.run_length_bits
    assert actual.lz4_bits == expected.lz4_bits
    assert actual.template_bits == expected.template_bits
    assert actual.mdl_bits == expected.mdl_bits
    assert actual.nll_bits == expected.nll_bits
    assert actual.nml_complexity == expected.nml_complexity
    assert actual.nml_bits == expected.nml_bits
    assert actual.nml_mode == expected.nml_mode
    assert actual.rule_error == expected.rule_error


def test_fast_reduction_matches_hand_checked_tie_case():
    spacetime = np.array(
        [
            [0, 1],
            [1, 0],
            [0, 1],
            [1, 0],
        ],
        dtype=np.uint8,
    )
    labels = component_labels(spacetime.shape, shift=0, period=1)
    reduction = reduce_binary_spacetime_by_orbits(
        spacetime.ravel(),
        labels.ravel(),
        class_sizes_1d(spacetime.shape, period=1),
        nml_mode="exact",
    )

    assert np.array_equal(reduction.class_sizes, np.array([4, 4], dtype=np.int64))
    assert np.array_equal(reduction.ones_per_class, np.array([2.0, 2.0]))
    assert np.array_equal(reduction.majority_bits, np.array([1, 1], dtype=np.uint8))
    assert np.array_equal(reduction.background_flat.reshape(spacetime.shape), np.ones_like(spacetime))
    assert np.array_equal(
        reduction.defect_flat.reshape(spacetime.shape),
        np.array(
            [
                [1, 0],
                [0, 1],
                [1, 0],
                [0, 1],
            ],
            dtype=np.uint8,
        ),
    )
    assert reduction.defect_sites == 4


def test_class_size_helpers_match_public_label_bincounts():
    labels_1d = component_labels((7, 5), shift=1, period=3)
    sizes_1d = np.bincount(labels_1d.ravel(), minlength=15)
    assert np.array_equal(sizes_1d, class_sizes_1d((7, 5), period=3))

    labels_nd = component_labels_nd((6, 3, 4), shift=(1, -1), period=2)
    sizes_nd = np.bincount(labels_nd.ravel(), minlength=24)
    assert np.array_equal(sizes_nd, class_sizes_nd((6, 3, 4), period=2))


def test_randomized_1d_candidates_match_reference_path():
    rng = np.random.default_rng(1234)
    shifts = [-1, 0, 1]
    periods = [1, 2, 3]

    for _ in range(10):
        spacetime = rng.integers(0, 2, size=(6, 5), dtype=np.uint8)
        for period in periods:
            for shift in shifts:
                actual = fit_relative_periodic_background(
                    spacetime,
                    shift=shift,
                    period=period,
                    nml_mode="exact",
                )
                expected = _fit_relative_periodic_background_reference(
                    spacetime,
                    shift=shift,
                    period=period,
                    nml_mode="exact",
                )
                _assert_fit_equal(actual, expected)

        actual_frame, actual_fits = scan_relative_periodicity(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode="exact",
        )
        expected_frame, expected_fits = _scan_relative_periodicity_reference(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode="exact",
        )
        pdt.assert_frame_equal(actual_frame, expected_frame)
        for key, expected_fit in expected_fits.items():
            _assert_fit_equal(actual_fits[key], expected_fit)

        actual_selection = select_period(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode="exact",
        )
        expected_selection = select_period_from_scan(
            expected_frame,
            expected_fits,
            nml_mode="exact",
        )
        assert actual_selection.selected.period == expected_selection.selected.period
        assert actual_selection.selected.best_shift == expected_selection.selected.best_shift
        assert actual_selection.selected.nml_bits == expected_selection.selected.nml_bits
        assert actual_selection.margin == expected_selection.margin
        assert actual_selection.status == expected_selection.status


def test_randomized_nd_candidates_match_reference_path():
    rng = np.random.default_rng(5678)
    shift_values = [-1, 0, 1]
    periods = [1, 2]

    for _ in range(6):
        spacetime = rng.integers(0, 2, size=(5, 3, 4), dtype=np.uint8)
        for period in periods:
            for shift_y in shift_values:
                for shift_x in shift_values:
                    shift = (shift_y, shift_x)
                    actual = fit_relative_periodic_background_nd(
                        spacetime,
                        shift=shift,
                        period=period,
                        nml_mode="exact",
                    )
                    expected = _fit_relative_periodic_background_nd_reference(
                        spacetime,
                        shift=shift,
                        period=period,
                        nml_mode="exact",
                    )
                    _assert_fit_equal(actual, expected)

        actual_frame, actual_fits = scan_relative_periodicity_nd(
            spacetime,
            shift_ranges=[shift_values, shift_values],
            periods=periods,
            nml_mode="exact",
        )
        expected_frame, expected_fits = _scan_relative_periodicity_nd_reference(
            spacetime,
            shift_ranges=[shift_values, shift_values],
            periods=periods,
            nml_mode="exact",
        )
        pdt.assert_frame_equal(actual_frame, expected_frame)
        for key, expected_fit in expected_fits.items():
            _assert_fit_equal(actual_fits[key], expected_fit)

        actual_selection = select_period_nd(
            spacetime,
            shift_ranges=[shift_values, shift_values],
            periods=periods,
            nml_mode="exact",
        )
        expected_selection = select_period_nd_from_scan(
            expected_frame,
            expected_fits,
            nml_mode="exact",
        )
        assert actual_selection.selected.period == expected_selection.selected.period
        assert actual_selection.selected.best_shift == expected_selection.selected.best_shift
        assert actual_selection.selected.nml_bits == expected_selection.selected.nml_bits
        assert actual_selection.margin == expected_selection.margin
        assert actual_selection.status == expected_selection.status


def test_fast_path_preserves_tie_break_background_bits_nd():
    spacetime = np.array(
        [
            [[0, 1], [1, 0]],
            [[1, 0], [0, 1]],
        ],
        dtype=np.uint8,
    )
    labels = component_labels_nd(spacetime.shape, shift=(0, 0), period=1)
    reduction = reduce_binary_spacetime_by_orbits(
        spacetime.ravel(),
        labels.ravel(),
        class_sizes_nd(spacetime.shape, period=1),
        nml_mode="exact",
    )

    assert np.array_equal(reduction.ones_per_class, np.ones(4, dtype=np.float64))
    assert np.array_equal(reduction.majority_bits, np.ones(4, dtype=np.uint8))
    assert np.array_equal(reduction.background_flat.reshape(spacetime.shape), np.ones_like(spacetime))
