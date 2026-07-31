"""Tests for the structured reading of a selected relative-periodic template.

``relative_symmetry_repair.reading`` is what the in-browser reproduction demo
shows a reader after the comparison table: which kind of domain won, what the
margin is worth, and what the defect mask did over time. Before it existed
that logic lived in ``webdemo/reproduce.html`` as page JavaScript, with the
pipeline's tie thresholds restated as JS literals and no test anywhere.

These tests pin two things: that the module's decisions are the ones the prose
claims, branch by branch, and that its thresholds are the *same* values
``experiment_core`` selects with, so the page and the paper's tables cannot
drift apart.
"""

import json
import math
import re
from pathlib import Path

import pytest

from relative_symmetry_repair import experiment_core, reading
from relative_symmetry_repair.reading import (
    DEFECT_BADGES,
    DENSE_MASK_SHARE,
    MIN_TREND_FRAMES,
    NEAR_EXACT_SITES_PER_FRAME,
    TREND_BAND,
    build_reading,
    check_defect_rate,
    classify_defect_dynamics,
    parse_shift,
    read_complexity,
    read_confidence,
    read_cost,
    read_template,
    thresholds,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REPRODUCE_HTML = REPO_ROOT / "webdemo" / "reproduce.html"


def make_record(**overrides):
    """A selection record shaped like one row of the suite's run-level CSVs."""
    record = {
        "rule": "ECA-110",
        "seed": 11,
        "horizon": 200,
        "selected_period": 4,
        "selected_shift_str": "-2",
        "selected_nml_bits": 25000.0,
        "selected_nll_bits": 24000.0,
        "selected_complexity": 1000.0,
        "selected_defect_rate": 0.2,
        "runner_up_period": 8,
        "runner_up_nml_bits": 25600.0,
        "margin_bits": 600.0,
        "status": "stable_winner",
        "period_tie_count": 1,
        "selected_shift_tie_count": 1,
    }
    record.update(overrides)
    return record


# --- Single source of truth ---------------------------------------------------


def test_thresholds_are_experiment_core_values_not_copies():
    """The whole point of the module: one definition of "near tie" per project."""
    published = thresholds()
    assert published["near_tie_bits"] == experiment_core.NEAR_TIE_THRESHOLD_BITS
    assert published["very_small_margin_bits"] == experiment_core.VERY_SMALL_MARGIN_BITS
    assert published["tie_tolerance_bits"] == experiment_core.TIE_TOLERANCE_BITS


def test_reading_does_not_redefine_the_selection_thresholds():
    """A local re-declaration would silently decouple the page from the suite."""
    source = (REPO_ROOT / "src" / "relative_symmetry_repair" / "reading.py").read_text()
    body = source.split('"""', 2)[-1]  # skip the module docstring
    for name in ("NEAR_TIE_THRESHOLD_BITS", "VERY_SMALL_MARGIN_BITS", "TIE_TOLERANCE_BITS"):
        assert not re.search(rf"^{name}\s*=", body, re.M), f"{name} is redefined in reading.py"


def test_mask_thresholds_are_exported_so_the_page_need_not_restate_them():
    published = thresholds()
    assert published["dense_mask_share"] == DENSE_MASK_SHARE
    assert published["trend_band"] == TREND_BAND
    assert published["min_trend_frames"] == MIN_TREND_FRAMES
    assert published["near_exact_sites_per_frame"] == NEAR_EXACT_SITES_PER_FRAME


def test_every_defect_kind_has_a_badge():
    """Guards adding a classification that reaches the page with no badge."""
    kinds = {
        "no_series", "exact", "transient", "near_exact",
        "growing", "decaying", "too_short", "dense", "persistent",
    }
    assert set(DEFECT_BADGES) == kinds
    for badge_class, label in DEFECT_BADGES.values():
        assert badge_class.startswith("text-bg-")
        assert label == label.upper()


# --- Displacement parsing -----------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("0", (0,)),
        ("-3", (-3,)),
        ("(0, 0)", (0, 0)),
        ("(-1, 2)", (-1, 2)),
        ("(1, -2, 3)", (1, -2, 3)),
        ((4, 5), (4, 5)),
    ],
)
def test_parse_shift_reads_both_csv_forms(value, expected):
    assert parse_shift(value) == expected


# --- Which template won -------------------------------------------------------


def test_static_period_1_template():
    t = read_template(make_record(selected_period=1, selected_shift_str="0"))
    assert t.kind == "static_period_1"
    assert t.moving is False
    assert t.shift_identified is True


def test_rigid_drift_is_period_1_with_an_identified_nonzero_shift():
    t = read_template(make_record(selected_period=1, selected_shift_str="3"))
    assert t.kind == "rigid_drift"
    assert t.moving is True
    assert t.velocity == (3.0,)


def test_static_periodic_domain():
    t = read_template(make_record(selected_period=4, selected_shift_str="(0, 0)"))
    assert t.kind == "static_periodic"
    assert t.moving is False


def test_drifting_periodic_domain_reports_velocity():
    t = read_template(make_record(selected_period=4, selected_shift_str="-2"))
    assert t.kind == "drifting_periodic"
    assert t.moving is True
    assert t.velocity == (-0.5,)


def test_a_tied_displacement_is_never_read_as_motion():
    """A shift that only won a tie-break carries no information about drift."""
    tied = read_template(
        make_record(selected_period=4, selected_shift_str="-2", selected_shift_tie_count=5)
    )
    assert tied.shift_identified is False
    assert tied.moving is False
    assert tied.kind == "static_periodic"  # not "drifting_periodic"


def test_a_tied_displacement_at_period_1_stays_a_period_1_template():
    tied = read_template(
        make_record(selected_period=1, selected_shift_str="3", selected_shift_tie_count=13)
    )
    assert tied.kind == "static_period_1"
    assert tied.moving is False


# --- What the margin is worth -------------------------------------------------


def test_stable_winner_confidence():
    c = read_confidence(make_record())
    assert c.kind == "stable_winner"
    assert c.below_very_small_margin is False


def test_near_tie_confidence():
    c = read_confidence(make_record(margin_bits=1.2, status="near_tie"))
    assert c.kind == "near_tie"
    assert c.below_very_small_margin is False


def test_very_small_margin_is_flagged_inside_the_near_tie_band():
    c = read_confidence(make_record(margin_bits=0.25, status="near_tie"))
    assert c.kind == "near_tie"
    assert c.below_very_small_margin is True


def test_unresolved_confidence():
    c = read_confidence(make_record(margin_bits=0.0, status="unresolved", period_tie_count=3))
    assert c.kind == "unresolved"
    assert c.period_tie_count == 3


def test_no_runner_up_means_no_evidence_against_a_competitor():
    c = read_confidence(
        make_record(runner_up_period=None, margin_bits=float("inf"), status="stable_winner")
    )
    assert c.kind == "no_alternative"


def test_missing_status_is_recovered_with_experiment_cores_own_classifier():
    record = make_record(margin_bits=1.0)
    record.pop("status")
    assert read_confidence(record).kind == "near_tie"


# --- What the template cost ---------------------------------------------------


def test_cost_pays_to_name_the_winning_candidate():
    cost = read_cost(
        make_record(selected_nml_bits=1000.0),
        n_sites=2000,
        frames=100,
        defect_sites=400,
        n_candidates=256,
    )
    assert cost.index_bits == pytest.approx(8.0)
    assert cost.bits_per_site == pytest.approx((1000.0 + 8.0) / 2000)
    assert cost.compresses is True
    assert cost.cells_per_frame == 20
    assert cost.coverage == pytest.approx(0.8)


def test_cost_reports_when_the_template_does_not_pay_for_itself():
    cost = read_cost(
        make_record(selected_nml_bits=4000.0),
        n_sites=2000,
        frames=100,
        defect_sites=400,
        n_candidates=1,
    )
    assert cost.index_bits == 0.0
    assert cost.bits_per_site > 1.0
    assert cost.compresses is False


# --- What the complexity term bought ------------------------------------------


def summary_rows():
    return [
        {"period": 1, "nml_bits": 26000.0, "nll_bits": 25900.0, "best_shift_str": "0"},
        {"period": 4, "nml_bits": 25000.0, "nll_bits": 24000.0, "best_shift_str": "-2"},
        {"period": 8, "nml_bits": 25600.0, "nll_bits": 23000.0, "best_shift_str": "1"},
    ]


def test_complexity_contrasts_the_nll_ranking_with_the_penalized_one():
    x = read_complexity(make_record(), summary_rows())
    assert x.best_nll_period == 8           # fit alone prefers the longest period
    assert x.max_period == 8
    assert x.best_nll_is_max_period is True
    assert x.fit_agrees is False            # the penalty moved the winner to 4
    assert x.selected_period == 4


def test_a_clear_gain_over_the_best_period_1_template():
    x = read_complexity(make_record(), summary_rows())
    assert x.period_1_gain_bits == pytest.approx(1000.0)
    assert x.gain_kind == "clear"
    assert x.period_1_shift_str == "0"


def test_a_gain_thinner_than_the_tie_band_is_called_thin():
    rows = summary_rows()
    rows[0]["nml_bits"] = 25001.0  # only 1 bit better than the winner
    x = read_complexity(make_record(), rows)
    assert x.gain_kind == "thin"
    assert x.period_1_gain_bits == pytest.approx(1.0)


def test_a_period_1_template_that_beats_the_winner_is_flagged_not_hidden():
    """Impossible for a rank-1 winner; the page asks the reader to report it."""
    rows = summary_rows()
    rows[0]["nml_bits"] = 24000.0
    x = read_complexity(make_record(), rows)
    assert x.gain_kind == "negative"
    assert x.period_1_gain_bits < 0


def test_period_1_winner_has_no_gain_to_report():
    x = read_complexity(make_record(selected_period=1), summary_rows())
    assert x.gain_kind is None
    assert x.period_1_gain_bits is None


def test_no_period_summary_means_nothing_can_be_said():
    assert read_complexity(make_record(), []) is None


# --- What the mask did over time ----------------------------------------------


def test_no_series_is_its_own_classification():
    d = classify_defect_dynamics([], cells_per_frame=100)
    assert d.kind == "no_series"
    assert d.badge_label == "NO DEFECT SERIES"


def test_an_empty_mask_is_an_exact_domain():
    d = classify_defect_dynamics([0] * 40, cells_per_frame=100)
    assert d.kind == "exact"
    assert d.last_defect_index is None


def test_defects_that_die_out_are_transient():
    series = [5] * 5 + [0] * 35
    d = classify_defect_dynamics(series, cells_per_frame=100)
    assert d.kind == "transient"
    assert d.last_defect_index == 4
    assert d.peak == 5
    assert d.peak_at == 0


def test_a_mask_that_all_but_empties_is_near_exact():
    series = [5] * 30 + [0] * 5 + [1] + [0] * 4
    d = classify_defect_dynamics(series, cells_per_frame=100)
    assert d.kind == "near_exact"
    assert d.end_level < NEAR_EXACT_SITES_PER_FRAME


def test_a_monotone_rise_beyond_the_band_is_growing():
    series = [0] * 20 + [10] * 6 + [20] * 6 + [30] * 8
    d = classify_defect_dynamics(series, cells_per_frame=100)
    assert d.kind == "growing"
    assert d.rising is True
    assert d.change > TREND_BAND


def test_a_monotone_fall_beyond_the_band_is_decaying():
    series = [0] * 20 + [30] * 6 + [20] * 6 + [10] * 8
    d = classify_defect_dynamics(series, cells_per_frame=100)
    assert d.kind == "decaying"
    assert d.falling is True
    assert d.change < -TREND_BAND


def test_a_monotone_move_inside_the_band_is_not_called_a_trend():
    """The band is the whole guard against reading noise as a direction."""
    series = [0] * 20 + [100] * 6 + [105] * 6 + [110] * 8
    d = classify_defect_dynamics(series, cells_per_frame=1000)
    assert d.rising is True
    assert 0 < d.change < TREND_BAND
    assert d.kind != "growing"


def test_a_large_but_non_monotone_move_is_not_called_a_trend():
    series = [0] * 20 + [10] * 6 + [90] * 6 + [50] * 8
    d = classify_defect_dynamics(series, cells_per_frame=1000)
    assert d.rising is False
    assert d.falling is False
    assert d.kind not in {"growing", "decaying"}


def test_a_short_window_refuses_to_call_a_trend():
    d = classify_defect_dynamics([10] * 16, cells_per_frame=100)
    assert d.enough_frames is False
    assert d.window_frames < MIN_TREND_FRAMES
    assert d.kind == "too_short"


def test_a_mask_covering_much_of_each_frame_is_dense_not_particles():
    d = classify_defect_dynamics([10] * 40, cells_per_frame=50)
    assert d.tail_share >= DENSE_MASK_SHARE
    assert d.kind == "dense"


def test_a_sparse_steady_mask_is_a_persistent_population():
    d = classify_defect_dynamics([10] * 40, cells_per_frame=1000)
    assert d.tail_share < DENSE_MASK_SHARE
    assert d.kind == "persistent"


def test_an_unbounded_rise_is_json_safe():
    """A window that opens empty gives an infinite ratio, which JSON cannot hold."""
    series = [0] * 20 + [0] * 6 + [5] * 6 + [10] * 8
    d = classify_defect_dynamics(series, cells_per_frame=100)
    assert math.isinf(d.change)
    assert d.to_payload()["change"] is None


# --- The mask on the page is the mask that was scored -------------------------


def test_consistency_check_passes_when_the_mask_matches_the_record():
    check = check_defect_rate(
        make_record(selected_defect_rate=0.25), defect_sites=250, n_sites=1000
    )
    assert check.ok is True
    assert check.implied_rate == pytest.approx(0.25)


def test_consistency_check_fails_when_the_fields_disagree_with_the_record():
    """A mismatch means the fields and the record came from different fits."""
    check = check_defect_rate(
        make_record(selected_defect_rate=0.25), defect_sites=260, n_sites=1000
    )
    assert check.ok is False


# --- The assembled payload ----------------------------------------------------


def full_reading(**record_overrides):
    series = [10] * 200
    return build_reading(
        record=make_record(selected_defect_rate=2000 / 200_000, **record_overrides),
        period_summary=summary_rows(),
        defects_per_frame=series,
        shape=(200, 1000),
        n_candidates=130,
        dimension=1,
    )


def test_build_reading_has_every_section_the_page_renders():
    payload = full_reading()
    assert set(payload) == {
        "dimension", "template", "confidence", "cost", "complexity",
        "defects", "consistency", "grid", "thresholds",
    }
    assert payload["consistency"]["ok"] is True
    assert payload["grid"] == {"min_period": 1, "max_period": 8, "n_candidates": 130}


def test_build_reading_is_strictly_json_safe():
    """The payload crosses to the page as json.dumps -> JSON.parse.

    Python emits a bare ``Infinity``/``NaN`` for non-finite floats and
    ``JSON.parse`` rejects both, so a non-finite value anywhere in the reading
    would break the page rather than degrade it.
    """
    payload = full_reading(runner_up_period=None, margin_bits=float("inf"))
    encoded = json.dumps(payload)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
    assert json.loads(encoded)["confidence"]["kind"] == "no_alternative"


def test_build_reading_counts_every_observed_site_including_the_transient():
    payload = full_reading()
    assert payload["cost"]["n_sites"] == 200_000
    assert payload["cost"]["frames"] == 200
    assert payload["cost"]["cells_per_frame"] == 1000
    assert payload["cost"]["defect_sites"] == 2000


# --- The page must not re-derive any of this ----------------------------------


def test_the_demo_page_renders_the_payload_instead_of_recomputing_it():
    """Regression guard for the drift this module exists to prevent."""
    html = REPRODUCE_HTML.read_text()
    assert "res.reading" in html, "the page no longer reads the Python reading payload"
    for stale in ("const NEAR_TIE_BITS", "const VERY_SMALL_MARGIN_BITS", "const DENSE_MASK_SHARE"):
        assert stale not in html, f"the page restates a pipeline threshold: {stale}"


def test_the_demo_page_takes_its_badges_from_the_payload():
    html = REPRODUCE_HTML.read_text()
    assert "badge_class" in html and "badge_label" in html
    # The classifier owns the labels; the page should not spell them itself.
    assert "PERSISTENT DEFECTS" not in html
    assert "DENSE DEFECT MASK" not in html


# --- The demo's expected rows must come from the reproducible table -----------


def test_demo_expected_rows_prefer_the_atlas_over_the_stale_table():
    """eca_atlas and seed_stability overlap and disagree; the atlas must win.

    seed_stability_runs.csv was last recomputed on 2026-03-22 and predates
    later scoring fixes; eca_atlas_runs.csv does not. Later entries overwrite
    earlier ones, so seed_stability has to be read FIRST. Loading it last made
    the live demo quote stale values and flag correct browser results as
    mismatches on 32 of 6400 comparison rows.
    """
    import re

    source = (REPO_ROOT / "scripts" / "build_review_site.py").read_text()
    body = source.split("def _demo_expected_rows")[1].split("def ")[0]
    seed_at = body.index("seed_stability/seed_stability_runs.csv")
    atlas_at = body.index("eca_atlas/eca_atlas_runs.csv")
    assert seed_at < atlas_at, "eca_atlas must be loaded after seed_stability"
