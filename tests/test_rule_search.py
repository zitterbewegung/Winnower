"""Tests for the rule search.

``relative_symmetry_repair.rule_search`` exists because two of the four
hard-coded 3D rules do not sustain activity over their own observed horizon:
``3d-life`` (S4-5/B5) is extinct from t=49 and ``clouds`` (S13-26/B13-14)
freezes into a static blob from t=10 at every initial density. A dead or
frozen lattice is exactly relative-periodic under ``p=1, s=0`` at zero defect
rate, so both flatter the fits they contribute to.

The tests below pin the classifier on cases whose behaviour is known
analytically (ECA 0 dies, 255 fills, 204 is the identity), pin the two
degenerate 3D rules as characterization tests so a future change to
``RULES_3D_DENSITY`` cannot quietly re-break them, and check that a budgeted
search reports what it skipped instead of presenting a capped run as a
complete one.
"""

import json

import pytest

from relative_symmetry_repair.rule_search import (
    ACTIVITY_FLOOR,
    DEFAULT_SCREEN,
    SATURATED_DENSITY,
    RuleSpec,
    ScreenSettings,
    count_rule_space,
    evaluate_rule,
    iter_eca_rules,
    iter_life_range_rules,
    iter_rule3d_rules,
    rule_space,
    screen_rule,
    search_rules,
    usefulness_key,
)

ECA_SCREEN = ScreenSettings(size=64, horizon=30, densities=(0.5,))
# The shipped 3D screening configuration, so these characterize what the
# search actually does rather than a lattice chosen for the test.
D3_SCREEN = DEFAULT_SCREEN[3]


def eca(rule: int) -> RuleSpec:
    return RuleSpec(dimension=1, label=f"ECA-{rule}", family="eca", rule_number=rule)


def rule3d(label, survive, birth) -> RuleSpec:
    return RuleSpec(dimension=3, label=label, family="rule3d", survive=survive, birth=birth)


# --- Rule spaces --------------------------------------------------------------


def test_rule_space_sizes_are_exact():
    """The reported size is what the page shows as the search denominator."""
    assert count_rule_space("eca") == 256
    assert count_rule_space("life_range") == 45 ** 2 == 2025      # 9 counts -> 45 windows
    assert count_rule_space("rule3d") == 378 ** 2 == 142_884      # 27 counts -> 378 windows
    assert count_rule_space("lifewiki") == 106


def test_rule_space_iterators_match_their_advertised_size():
    assert sum(1 for _ in iter_eca_rules()) == 256
    assert sum(1 for _ in iter_life_range_rules()) == 2025
    assert len({spec.label for spec in iter_life_range_rules()}) == 2025


def test_rule3d_space_covers_the_full_neighbour_count_range():
    labels = {spec.label for spec in iter_rule3d_rules()}
    assert "S4-5/B5-5" in labels        # 3d-life
    assert "S13-26/B13-14" in labels    # clouds
    assert "S0-26/B0-26" in labels      # the extremes are present


def test_unknown_rule_space_is_rejected():
    with pytest.raises(ValueError):
        list(rule_space("no-such-family"))


@pytest.mark.parametrize(
    "spec, dimension",
    [
        (eca(110), 1),
        (RuleSpec(2, "S2-3/B3-3", "life_range", survive=(2, 3), birth=(3, 3)), 2),
        (RuleSpec(2, "B36/S23", "life_rulestring", rulestring="B36/S23"), 2),
        (rule3d("S4-5/B5-5", (4, 5), (5, 5)), 3),
        (RuleSpec(3, "B5,7/S4,6", "rule3d_general", rulestring="B5,7/S4,6"), 3),
    ],
)
def test_every_family_builds_an_ordinary_experiment_case(spec, dimension):
    """The search must run the same cases as the rest of the suite."""
    case = spec.to_case(size=8, density=0.3, horizons=(20,))
    assert case.dimension == dimension
    assert case.density == pytest.approx(0.3)
    assert len(case.size) == dimension


def test_unsupported_family_is_rejected():
    with pytest.raises(ValueError):
        RuleSpec(1, "bogus", "nonsense").to_case(size=8, density=0.5, horizons=(10,))


# --- The screen, on cases with known behaviour --------------------------------


def test_eca_0_is_extinct():
    """Rule 0 maps every neighbourhood to 0: dead after one step."""
    screen = screen_rule(eca(0), ECA_SCREEN)
    assert screen.verdict == "extinct"
    assert screen.extinct_at == 1
    assert screen.final_density == 0.0


def test_eca_255_is_saturated():
    """Rule 255 maps every neighbourhood to 1: the lattice fills."""
    screen = screen_rule(eca(255), ECA_SCREEN)
    assert screen.verdict == "saturated"
    assert screen.final_density >= SATURATED_DENSITY


def test_eca_204_is_frozen():
    """Rule 204 is the identity: alive, but nothing ever changes."""
    screen = screen_rule(eca(204), ECA_SCREEN)
    assert screen.verdict == "frozen"
    assert screen.activity < ACTIVITY_FLOOR


def test_eca_110_is_active():
    screen = screen_rule(eca(110), ECA_SCREEN)
    assert screen.verdict == "active"
    assert screen.passed is True
    assert screen.activity > ACTIVITY_FLOOR


def test_the_screen_exits_early_when_a_rule_dies():
    """Most rules die immediately; not simulating past that is the whole budget."""
    screen = screen_rule(eca(0), ECA_SCREEN)
    assert screen.frames < ECA_SCREEN.horizon


def test_an_active_rule_is_simulated_to_the_horizon():
    screen = screen_rule(eca(110), ECA_SCREEN)
    assert screen.frames == ECA_SCREEN.horizon


# --- The two degenerate 3D rules (characterization) ---------------------------


def test_3d_life_does_not_survive_screening_at_any_density():
    """S4-5/B5 dies at every density in the ladder — the caveat, pinned.

    Extinction is lattice-dependent: at 10^3 it happens to survive at
    density 0.2, which is the same size-and-seed luck that made a 5-seed
    sweep look like density 0.16 rescued it. This asserts the shipped
    screening configuration, where it dies at every density.
    """
    screen = screen_rule(rule3d("3d-life", (4, 5), (5, 5)), D3_SCREEN)
    assert screen.verdict == "extinct"


def test_clouds_freezes_rather_than_sustaining_activity():
    """S13-26/B13-14 either dies (sparse) or sets into a static blob (dense).

    It never sustains activity, so the search must not report it as useful.
    """
    screen = screen_rule(rule3d("clouds", (13, 26), (13, 14)), D3_SCREEN)
    assert screen.verdict in {"frozen", "saturated", "extinct"}
    assert screen.passed is False


@pytest.mark.parametrize("label, survive, birth", [("crystal", (1, 1), (1, 3)), ("diamoeba3d", (5, 8), (5, 8))])
def test_the_two_healthy_3d_rules_pass_screening(label, survive, birth):
    screen = screen_rule(rule3d(label, survive, birth), D3_SCREEN)
    assert screen.verdict == "active"


def test_the_screen_reports_the_density_its_verdict_came_from():
    """Density is a per-rule knob; the evaluation stage re-uses this value."""
    screen = screen_rule(rule3d("crystal", (1, 1), (1, 3)), D3_SCREEN)
    assert screen.density in D3_SCREEN.densities


def test_a_single_density_ladder_would_reject_a_rule_a_wider_one_keeps():
    """Why the ladder exists: crystal is smothered at 0.6 and fine at 0.1."""
    dense_only = ScreenSettings(size=D3_SCREEN.size, horizon=D3_SCREEN.horizon, densities=(0.6,))
    sparse_only = ScreenSettings(size=D3_SCREEN.size, horizon=D3_SCREEN.horizon, densities=(0.1,))
    crystal = rule3d("crystal", (1, 1), (1, 3))
    assert screen_rule(crystal, sparse_only).verdict == "active"
    assert screen_rule(crystal, dense_only).verdict != "active"
    # The ladder recovers it.
    assert screen_rule(crystal, D3_SCREEN).verdict == "active"


# --- The selector stage -------------------------------------------------------


def test_evaluate_rule_agrees_with_running_the_selector_directly():
    from relative_symmetry_repair.experiment_core import scan_case_spacetime, simulate_case

    spec = eca(110)
    screen = screen_rule(spec, ECA_SCREEN)
    evaluation = evaluate_rule(spec, screen, size=64, horizon=40, density=0.5, seed=11)

    case = spec.to_case(size=64, density=0.5, horizons=(40,))
    outcome = scan_case_spacetime(case, simulate_case(case, steps=40, seed=11))
    assert evaluation.selected_period == outcome.selection.selected_period
    assert evaluation.defect_rate == pytest.approx(outcome.selection.selected_defect_rate)
    assert evaluation.n_candidates == len(outcome.frame)


def test_usefulness_ranks_a_sparser_mask_first():
    """The ranking is the paper's target signature, not an arbitrary score."""
    spec = eca(110)
    screen = screen_rule(spec, ECA_SCREEN)
    sparse = evaluate_rule(spec, screen, size=64, horizon=40, density=0.5, seed=11)
    dense = evaluate_rule(eca(30), screen, size=64, horizon=40, density=0.5, seed=11)
    ranked = sorted([dense, sparse], key=usefulness_key)
    assert ranked[0].defect_rate <= ranked[1].defect_rate


# --- The search ---------------------------------------------------------------


def test_search_respects_its_screening_budget():
    result = search_rules("eca", limit=12, screen_settings=ECA_SCREEN, evaluate=False)
    assert result["screened"] == 12
    assert result["space_size"] == 256
    assert sum(result["counts"].values()) == 12


def test_search_caps_the_selector_stage_and_says_what_it_skipped():
    """A capped run must never read as an exhaustive one."""
    result = search_rules(
        "eca", limit=40, screen_settings=ECA_SCREEN, evaluate=True, max_evaluations=3
    )
    assert result["evaluated"] == 3
    assert len(result["results"]) == 3
    assert result["counts"]["active"] > 3
    assert result["active_not_evaluated"] == result["counts"]["active"] - 3
    assert result["max_evaluations"] == 3


def test_search_results_are_ranked_by_defect_rate():
    result = search_rules(
        "eca", limit=40, screen_settings=ECA_SCREEN, evaluate=True, max_evaluations=6
    )
    rates = [row["defect_rate"] for row in result["results"]]
    assert rates == sorted(rates)


def test_search_sampling_is_deterministic_for_a_given_shuffle_seed():
    kwargs = dict(limit=8, screen_settings=ECA_SCREEN, evaluate=False, shuffle_seed=5)
    first = search_rules("eca", **kwargs)
    second = search_rules("eca", **kwargs)
    assert first["counts"] == second["counts"]
    labels = lambda r: [s["rule"]["label"] for s in r["active_screens"]]
    assert labels(first) == labels(second)


def test_search_sampling_differs_between_shuffle_seeds():
    a = search_rules("eca", limit=8, screen_settings=ECA_SCREEN, evaluate=False, shuffle_seed=1)
    b = search_rules("eca", limit=8, screen_settings=ECA_SCREEN, evaluate=False, shuffle_seed=2)
    assert [s["rule"]["label"] for s in a["active_screens"]] != [
        s["rule"]["label"] for s in b["active_screens"]
    ]


def test_search_reports_progress():
    seen = []
    search_rules(
        "eca", limit=5, screen_settings=ECA_SCREEN, evaluate=False,
        progress=lambda frac, text: seen.append((frac, text)),
    )
    assert len(seen) == 5
    assert seen[-1][0] == pytest.approx(1.0)


def test_search_payload_survives_the_json_bridge():
    result = search_rules(
        "eca", limit=20, screen_settings=ECA_SCREEN, evaluate=True, max_evaluations=3
    )
    encoded = json.dumps(result)
    assert "Infinity" not in encoded and "NaN" not in encoded
    json.loads(encoded)


def test_an_empty_rule_list_is_handled():
    result = search_rules([], evaluate=False)
    assert result["screened"] == 0
    assert result["results"] == []


def test_default_screens_exist_for_every_dimension():
    for dimension in (1, 2, 3):
        settings = DEFAULT_SCREEN[dimension]
        assert settings.densities, f"dimension {dimension} has an empty density ladder"
        assert settings.size > 0 and settings.horizon > 0
