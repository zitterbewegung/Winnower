import itertools

import numpy as np

from relative_symmetry_repair.coding import nml_score_bits
from relative_symmetry_repair.repair import component_labels, fit_relative_periodic_background
from relative_symmetry_repair.selection import select_period


def _brute_force_templates(shape, *, shift: int, period: int):
    labels = component_labels(shape, shift=shift, period=period)
    n_labels = period * shape[1]
    for template_bits in itertools.product([0, 1], repeat=n_labels):
        template = np.array(template_bits, dtype=np.uint8)
        yield template[labels]


def _brute_force_min_hamming(spacetime: np.ndarray, *, shift: int, period: int) -> int:
    return min(
        int((spacetime != background).sum())
        for background in _brute_force_templates(
            spacetime.shape,
            shift=shift,
            period=period,
        )
    )


def _brute_force_period_first_selection(
    spacetime: np.ndarray,
    *,
    shifts,
    periods,
    nml_mode: str,
) -> tuple[int, int]:
    best_period_scores = {}
    for period in periods:
        for shift in shifts:
            labels = component_labels(spacetime.shape, shift=shift, period=period)
            n_labels = period * spacetime.shape[1]
            _, _, total = nml_score_bits(spacetime, labels, n_labels, mode=nml_mode)
            key = (float(total), int(period), int(shift))
            if period not in best_period_scores or key < best_period_scores[period][0]:
                best_period_scores[period] = (key, int(shift))
    best = sorted(
        (score_key[0], period, best_shift)
        for period, (score_key, best_shift) in best_period_scores.items()
    )[0]
    return best[1], best[2]


def test_hamming_projection_matches_bruteforce_for_all_4x3_spacetimes():
    for bits in itertools.product([0, 1], repeat=12):
        spacetime = np.array(bits, dtype=np.uint8).reshape(4, 3)
        for period in [1, 2]:
            for shift in [-1, 0, 1]:
                fit = fit_relative_periodic_background(spacetime, shift=shift, period=period)
                brute = _brute_force_min_hamming(spacetime, shift=shift, period=period)
                assert fit.defect_sites == brute


def test_period_first_exact_nml_selection_matches_bruteforce_on_tiny_sample():
    shifts = [-1, 0, 1]
    periods = [1, 2]
    for bits in itertools.islice(itertools.product([0, 1], repeat=16), 512):
        spacetime = np.array(bits, dtype=np.uint8).reshape(4, 4)
        brute_period, brute_shift = _brute_force_period_first_selection(
            spacetime,
            shifts=shifts,
            periods=periods,
            nml_mode="exact",
        )
        result = select_period(spacetime, shifts=shifts, periods=periods, nml_mode="exact")
        assert result.selected.period == brute_period
        assert result.selected.best_shift == brute_shift


def test_period_first_selection_is_independent_of_shift_and_period_iteration_order():
    spacetime = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 1, 1],
        ],
        dtype=np.uint8,
    )
    forward = select_period(
        spacetime,
        shifts=[-1, 0, 1],
        periods=[1, 2, 3],
        nml_mode="exact",
    )
    reverse = select_period(
        spacetime,
        shifts=[1, 0, -1],
        periods=[3, 2, 1],
        nml_mode="exact",
    )
    assert forward.selected.period == reverse.selected.period
    assert forward.selected.best_shift == reverse.selected.best_shift
    assert forward.margin == reverse.margin
