"""Ground-truth tests built on catalogued CA patterns.

Every other experiment in this project starts from a random soup, where the
correct period and displacement are unknown and the selector's output can only
be compared against itself. ``relative_symmetry_repair.patterns`` catalogues
orbits of ``3d-life`` (S4-5/B5) whose answer is known exactly: each is a
configuration satisfying ``U[t+p, x+s] = U[t, x]`` with no transient, so the
correct fit is ``(p, s)`` at a defect rate of exactly zero.

These tests do three things:

1. re-verify the catalogue itself, so no entry is taken on trust --- constant
   population, exact translation across the whole run, minimal period;
2. check the *scan* against that ground truth: the true candidate must appear
   with a defect rate of exactly 0.0, and must be the smallest-period
   zero-defect candidate;
3. characterize what the *selector* then does with it --- which is not always
   to pick the truth at a short horizon, and that is the interesting part.

On (3): a single glider in a large lattice is missed at T=32 and recovered at
a longer T, at unchanged occupancy. The complexity gap between p=1 and the
true period scales with the spatial volume and does not depend on T, while
the defect-bits the p=1 fit leaves accumulate with T, so the horizon has to
grow roughly linearly with the volume (measured: T ~ 0.3 x V). There is no
occupancy floor below which the period stops being recoverable -- only a
horizon budget, which is the paper's stabilization property measured against
a known answer rather than argued.
"""

import numpy as np
import pytest

from relative_symmetry_repair.experiment_core import (
    DEFAULT_SEARCH_3D,
    period_first_selection_from_frame,
)
from relative_symmetry_repair.patterns import (
    PATTERNS_3D,
    Pattern,
    pattern_spacetime,
    patterns_for_rule,
)
from relative_symmetry_repair.repair_nd import scan_relative_periodicity_nd

ALL_PATTERNS = sorted(PATTERNS_3D)


def roll3(volume: np.ndarray, shift) -> np.ndarray:
    for axis, amount in enumerate(shift):
        volume = np.roll(volume, amount, axis=axis)
    return volume


def scan(spacetime):
    frame, _ = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=DEFAULT_SEARCH_3D.shift_ranges,
        periods=DEFAULT_SEARCH_3D.periods,
        nml_mode="hybrid",
    )
    return frame


def zero_defect_rows(frame):
    return frame[frame["defect_rate"] == 0.0]


def shift_of(row):
    return (int(row["shift_0"]), int(row["shift_1"]), int(row["shift_2"]))


# --- The catalogue is what it claims to be ------------------------------------


@pytest.mark.parametrize("name", ALL_PATTERNS)
def test_pattern_has_constant_population(name):
    pattern = PATTERNS_3D[name]
    spacetime = pattern_spacetime(pattern, size=20, steps=80)
    populations = spacetime.reshape(len(spacetime), -1).sum(axis=1)
    assert (populations == pattern.n_cells).all()


@pytest.mark.parametrize("name", ALL_PATTERNS)
def test_pattern_translates_exactly_at_its_catalogued_period(name):
    """The defining identity, checked on every frame rather than sampled."""
    pattern = PATTERNS_3D[name]
    spacetime = pattern_spacetime(pattern, size=20, steps=80)
    period, displacement = pattern.period, pattern.displacement
    for t in range(len(spacetime) - period):
        assert np.array_equal(roll3(spacetime[t], displacement), spacetime[t + period]), (
            f"{name} broke its own identity at t={t}"
        )


@pytest.mark.parametrize("name", ALL_PATTERNS)
def test_catalogued_period_is_minimal(name):
    """A non-minimal period would make the 'true' answer ambiguous."""
    pattern = PATTERNS_3D[name]
    if pattern.period == 1:
        return
    spacetime = pattern_spacetime(pattern, size=20, steps=40)
    for shorter in range(1, pattern.period):
        scaled = tuple(
            int(round(value * shorter / pattern.period)) for value in pattern.displacement
        )
        repeats = all(
            np.array_equal(roll3(spacetime[t], scaled), spacetime[t + shorter])
            for t in range(10, 30)
        )
        assert not repeats, f"{name} actually has period {shorter}, not {pattern.period}"


def test_the_glider_is_the_only_translating_pattern_catalogued():
    kinds = {name: PATTERNS_3D[name].kind for name in ALL_PATTERNS}
    assert kinds["glider"] == "spaceship"
    assert kinds["still-life"] == "still_life"
    assert kinds["blinker"] == "oscillator"
    assert kinds["oscillator-4"] == "oscillator"
    assert [n for n, k in kinds.items() if k == "spaceship"] == ["glider"]


def test_the_glider_moves_diagonally_at_quarter_light_speed():
    glider = PATTERNS_3D["glider"]
    assert glider.period == 4
    assert glider.displacement == (1, 1, 0)
    assert glider.speed == (0.25, 0.25, 0.0)
    assert glider.n_cells == 10
    assert glider.bounding_box == (3, 2, 4)


@pytest.mark.parametrize("name", ALL_PATTERNS)
def test_volume_places_every_cell(name):
    pattern = PATTERNS_3D[name]
    volume = pattern.volume(16)
    assert volume.shape == (16, 16, 16)
    assert int(volume.sum()) == pattern.n_cells
    assert volume.dtype == np.uint8


def test_volume_rejects_a_lattice_smaller_than_the_pattern():
    with pytest.raises(ValueError):
        PATTERNS_3D["glider"].volume(2)


def test_volume_rejects_a_size_of_the_wrong_dimension():
    with pytest.raises(ValueError):
        PATTERNS_3D["glider"].volume((16, 16))


def test_patterns_for_rule_selects_by_rule():
    assert {p.name for p in patterns_for_rule("3d-life")} == set(ALL_PATTERNS)
    assert list(patterns_for_rule("crystal")) == []


# --- Ground truth for the scan ------------------------------------------------


@pytest.mark.parametrize("name", ALL_PATTERNS)
def test_the_true_candidate_scores_exactly_zero_defects(name):
    """The known answer must be reachable, and exactly exact.

    Not "small" -- zero. The pattern satisfies the relative-periodicity
    relation identically, so any nonzero residual at the true candidate would
    be a defect in the fitting code, not in the data.
    """
    pattern = PATTERNS_3D[name]
    frame = scan(pattern_spacetime(pattern, size=12, steps=24))
    match = frame[
        (frame["period"] == pattern.period)
        & (frame["shift_0"] == pattern.displacement[0])
        & (frame["shift_1"] == pattern.displacement[1])
        & (frame["shift_2"] == pattern.displacement[2])
    ]
    assert len(match) == 1
    assert float(match.iloc[0]["defect_rate"]) == 0.0


@pytest.mark.parametrize("name", ALL_PATTERNS)
def test_the_true_candidate_is_the_smallest_zero_defect_period(name):
    """Multiples of a true period also fit exactly; the minimum is the answer."""
    pattern = PATTERNS_3D[name]
    frame = scan(pattern_spacetime(pattern, size=12, steps=24))
    zero = zero_defect_rows(frame)
    assert len(zero) >= 1
    best = zero.sort_values("period").iloc[0]
    assert int(best["period"]) == pattern.period
    assert shift_of(best) == pattern.displacement


def test_a_static_pattern_fits_exactly_at_every_scanned_period():
    """A still life is relative-periodic at p=1, hence at every multiple."""
    zero = zero_defect_rows(scan(pattern_spacetime(PATTERNS_3D["still-life"], size=12, steps=24)))
    assert set(zero["period"]) == set(DEFAULT_SEARCH_3D.periods)
    assert all(shift_of(row) == (0, 0, 0) for _, row in zero.iterrows())


def test_the_glider_has_a_unique_exact_fit():
    """Its period is 4 and the grid stops at 4, so exactly one candidate fits."""
    zero = zero_defect_rows(scan(pattern_spacetime(PATTERNS_3D["glider"], size=12, steps=24)))
    assert len(zero) == 1
    assert int(zero.iloc[0]["period"]) == 4
    assert shift_of(zero.iloc[0]) == (1, 1, 0)


def test_a_wrong_displacement_at_the_true_period_does_not_fit():
    """Guards the shift convention: (1,1,0) is not interchangeable with (-1,-1,0)."""
    frame = scan(pattern_spacetime(PATTERNS_3D["glider"], size=12, steps=24))
    wrong = frame[
        (frame["period"] == 4)
        & (frame["shift_0"] == -1) & (frame["shift_1"] == -1) & (frame["shift_2"] == 0)
    ]
    assert len(wrong) == 1
    assert float(wrong.iloc[0]["defect_rate"]) > 0.0


# --- What the selector does with the ground truth ------------------------------


def test_the_selector_recovers_the_glider_when_the_run_is_long_enough():
    """At 6^3 the horizon T=32 already clears what the volume costs."""
    frame = scan(pattern_spacetime(PATTERNS_3D["glider"], size=6, steps=32))
    selection = period_first_selection_from_frame(frame)
    assert selection.selected_period == 4
    assert tuple(int(v) for v in selection.selected_shift) == (1, 1, 0)
    assert selection.selected_defect_rate == 0.0


def test_a_run_too_short_for_its_volume_misses_an_exact_fit():
    """Pins the trade-off, on a case where the right answer is known.

    At 16^3 with T=32 a zero-defect candidate is in the grid, but coding four
    times as many orbit classes costs more than the defects that p=1 leaves,
    so the selector takes p=1 -- and labels it a stable winner.

    This is a statement about the *horizon*, not about how sparse the glider
    is: see ``test_a_longer_horizon_recovers_the_period_at_fixed_occupancy``,
    where the same occupancy recovers the true period once T is large enough.
    The complexity gap between p=1 and p=4 scales with the spatial volume and
    is independent of T, while the defect-bits p=1 leaves accumulate with T,
    so every occupancy is recoverable given a long enough run.
    """
    spacetime = pattern_spacetime(PATTERNS_3D["glider"], size=16, steps=32)
    frame = scan(spacetime)
    assert len(zero_defect_rows(frame)) == 1          # the truth is available
    selection = period_first_selection_from_frame(frame)
    assert selection.selected_period == 1             # and is not chosen
    assert selection.status == "stable_winner"        # with no hint of doubt
    assert 0.0 < selection.selected_defect_rate < 0.01


def test_the_defect_mask_carries_the_glider_when_the_period_is_missed():
    """What p=1 leaves behind is exactly the moving structure."""
    spacetime = pattern_spacetime(PATTERNS_3D["glider"], size=16, steps=32)
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=DEFAULT_SEARCH_3D.shift_ranges,
        periods=DEFAULT_SEARCH_3D.periods,
        nml_mode="hybrid",
    )
    fit = fits[((0, 0, 0), 1)]
    mask = np.asarray(fit.defect_mask)
    per_frame = mask.reshape(len(mask), -1).sum(axis=1)
    # The background is empty, so every live cell is a defect: the mask is the
    # glider itself, at constant population.
    assert set(np.unique(per_frame)) == {PATTERNS_3D["glider"].n_cells}


@pytest.mark.parametrize("name", ["blinker", "oscillator-4"])
def test_a_stationary_structure_needs_the_same_horizon_budget(name):
    """Not specific to motion: a stationary period-p structure behaves the same."""
    frame = scan(pattern_spacetime(PATTERNS_3D[name], size=16, steps=24))
    assert len(zero_defect_rows(frame)) >= 1
    assert period_first_selection_from_frame(frame).selected_period == 1


def test_a_longer_horizon_recovers_the_period_at_fixed_occupancy():
    """The stabilization property, on a case with a known answer.

    Occupancy is held fixed (same lattice, same single glider) and only the
    horizon changes. T=32 misses the true period; T=128 recovers it. So the
    earlier miss is a horizon budget, not a sensitivity floor -- there is no
    occupancy below which the period becomes unrecoverable.

    Measured recovery horizons: 7^3 and 8^3 at T=128, 10^3 at T=256, 12^3 at
    T=512 -- roughly T ~ 0.3 x V, i.e. the horizon has to grow about linearly
    with the spatial volume, which is what the scaling of the two terms
    predicts.
    """
    short = scan(pattern_spacetime(PATTERNS_3D["glider"], size=7, steps=32))
    assert period_first_selection_from_frame(short).selected_period == 1

    long = scan(pattern_spacetime(PATTERNS_3D["glider"], size=7, steps=128))
    selection = period_first_selection_from_frame(long)
    assert selection.selected_period == 4
    assert tuple(int(v) for v in selection.selected_shift) == (1, 1, 0)
    assert selection.selected_defect_rate == 0.0
