"""Search rule spaces for rules worth running the selector on.

Picking the rules a paper reports is usually done by hand, and by hand it is
easy to pick one that does not survive its own horizon -- ``3d-life``
(S4-5/B5) is extinct by t=49 at the tuned density, so the last third of its
observed window is an empty lattice, which is exactly relative-periodic under
``p=1, s=0`` at zero defect rate and flatters the fit it contributes to.

This module makes that check mechanical. It enumerates a rule family, screens
each rule cheaply for whether anything is still happening at the horizon, and
then runs the *real* selector on the survivors, so "useful" means what it
means everywhere else in this project: the rule sustains activity, and the
pipeline finds a domain template with a sparse defect mask.

Two consumers share this core. ``webdemo/bootstrap.py`` exposes it to the
in-browser reproduction under a rule budget, so a reviewer can search
interactively; ``scripts/surveys/search_useful_rules.py`` sweeps a whole
family offline. Both get identical verdicts because both call this code.

Nothing here defines its own simulator or selector: rules become
:class:`~relative_symmetry_repair.experiment_core.ALifeCase` objects and go
through ``simulate_case`` and ``scan_case_spacetime`` like every other
experiment in the suite.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
import math
from typing import Any, Callable, Iterable, Iterator, Literal, Sequence

import numpy as np

from .experiment_core import (
    DEFAULT_SEARCH_1D,
    DEFAULT_SEARCH_2D,
    DEFAULT_SEARCH_3D,
    ALifeCase,
    SearchConfig,
    eca_case,
    life_range_case,
    life_rulestring_case,
    rule3d_case,
    rule3d_general_case,
    scan_case_spacetime,
    simulate_case,
    _lifewiki_rules_path,
)

__all__ = [
    "ACTIVITY_FLOOR",
    "SATURATED_DENSITY",
    "DEFAULT_SCREEN",
    "RuleEvaluation",
    "RuleScreen",
    "RuleSpec",
    "ScreenSettings",
    "Verdict",
    "count_rule_space",
    "evaluate_rule",
    "iter_eca_rules",
    "iter_life_range_rules",
    "iter_lifewiki_rules",
    "iter_rule3d_rules",
    "rule_space",
    "screen_rule",
    "search_rules",
]

Verdict = Literal["extinct", "saturated", "frozen", "active"]

#: A lattice at or above this live fraction is saturated: the rule has filled
#: space and there is no figure left against the ground.
SATURATED_DENSITY = 0.99

#: Mean fraction of sites changing per step, below which nothing is happening.
#: A still life sits here; a blinker does not.
ACTIVITY_FLOOR = 1e-4


@dataclass(frozen=True, slots=True)
class ScreenSettings:
    """Lattice, horizon and seeds for one screening pass.

    The defaults are deliberately small: screening is a filter, not a
    measurement, and the rules that pass get re-run at full size.

    ``densities`` is a ladder, not a single value, because initial density is
    a per-rule tuning knob rather than a property of the family: ``clouds``
    (S13-26/B13-14) needs a dense start to reach its birth threshold and dies
    at 0.3, while ``crystal`` (S1/B1-3) is smothered above 0.2. Screening at
    one density would reject rules the paper already ships. Each rule is
    screened at every density and keeps its best outcome.
    """

    size: int
    horizon: int
    densities: tuple[float, ...]
    seed: int = 11
    chunk: int = 10
    tail_frames: int = 10


#: Verdict preference when a rule behaves differently at different densities.
_VERDICT_RANK: dict[str, int] = {"extinct": 0, "saturated": 1, "frozen": 2, "active": 3}


#: Per-dimension screening defaults, sized so a single screen is milliseconds.
#: The 3D ladder spans the four tuned densities in ``RULES_3D_DENSITY``, and
#: the 3D horizon matches ``max(DEFAULT_HORIZONS_3D)``.
#:
#: The horizon matters more than it looks. A verdict is only ever a statement
#: about the window it was measured on: ``3d-life`` screens as *active* over 30
#: frames and is extinct by frame 49, so a screen shorter than the horizon you
#: intend to report at will happily recommend a rule that dies later.
#: :func:`search_rules` therefore screens over at least its evaluation horizon.
DEFAULT_SCREEN: dict[int, ScreenSettings] = {
    1: ScreenSettings(size=96, horizon=200, densities=(0.3, 0.5)),
    2: ScreenSettings(size=32, horizon=100, densities=(0.2, 0.35, 0.5)),
    3: ScreenSettings(size=12, horizon=80, densities=(0.1, 0.2, 0.3, 0.45, 0.6)),
}


@dataclass(frozen=True, slots=True)
class RuleSpec:
    """One candidate rule, independent of the lattice it will be run on."""

    dimension: int
    label: str
    family: str
    rule_number: int | None = None
    survive: tuple[int, int] | None = None
    birth: tuple[int, int] | None = None
    rulestring: str | None = None

    def to_case(
        self,
        *,
        size: int,
        density: float,
        horizons: Sequence[int],
        search: SearchConfig | None = None,
    ) -> ALifeCase:
        """Build the ordinary experiment case for this rule."""
        horizons = tuple(int(value) for value in horizons)
        if self.family == "eca":
            return eca_case(
                int(self.rule_number),
                width=size,
                density=density,
                horizons=horizons,
                search=search or DEFAULT_SEARCH_1D,
            )
        if self.family == "life_range":
            return life_range_case(
                self.label,
                survive=self.survive,
                birth=self.birth,
                width=size,
                height=size,
                density=density,
                horizons=horizons,
                search=search or DEFAULT_SEARCH_2D,
            )
        if self.family == "life_rulestring":
            return life_rulestring_case(
                self.label,
                rulestring=str(self.rulestring),
                width=size,
                height=size,
                density=density,
                horizons=horizons,
                search=search or DEFAULT_SEARCH_2D,
            )
        if self.family == "rule3d":
            return rule3d_case(
                self.label,
                survive=self.survive,
                birth=self.birth,
                size=size,
                density=density,
                horizons=horizons,
                search=search or DEFAULT_SEARCH_3D,
            )
        if self.family == "rule3d_general":
            return rule3d_general_case(
                self.label,
                rulestring=str(self.rulestring),
                size=size,
                density=density,
                horizons=horizons,
                search=search or DEFAULT_SEARCH_3D,
            )
        raise ValueError(f"Unsupported family: {self.family!r}")

    def to_payload(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "label": self.label,
            "family": self.family,
            "rule_number": self.rule_number,
            "survive": list(self.survive) if self.survive else None,
            "birth": list(self.birth) if self.birth else None,
            "rulestring": self.rulestring,
        }


# --- Rule spaces --------------------------------------------------------------


def _ranges(max_count: int) -> list[tuple[int, int]]:
    """Every contiguous ``lo <= hi`` neighbor-count window on ``0..max_count``."""
    return [(lo, hi) for lo in range(max_count + 1) for hi in range(lo, max_count + 1)]


def iter_eca_rules() -> Iterator[RuleSpec]:
    """All 256 elementary cellular automata."""
    for rule in range(256):
        yield RuleSpec(dimension=1, label=f"ECA-{rule}", family="eca", rule_number=rule)


def iter_life_range_rules() -> Iterator[RuleSpec]:
    """2D contiguous survive/birth windows on a 8-neighbor Moore neighborhood."""
    for survive in _ranges(8):
        for birth in _ranges(8):
            yield RuleSpec(
                dimension=2,
                label=f"S{survive[0]}-{survive[1]}/B{birth[0]}-{birth[1]}",
                family="life_range",
                survive=survive,
                birth=birth,
            )


def iter_rule3d_rules() -> Iterator[RuleSpec]:
    """3D contiguous survive/birth windows on a 26-neighbor Moore neighborhood.

    This is the family ``RULES_3D`` is drawn from, so a sweep of it is a
    complete answer to "is there a better 3D rule than the four we ship?".
    """
    for survive in _ranges(26):
        for birth in _ranges(26):
            yield RuleSpec(
                dimension=3,
                label=f"S{survive[0]}-{survive[1]}/B{birth[0]}-{birth[1]}",
                family="rule3d",
                survive=survive,
                birth=birth,
            )


def iter_lifewiki_rules() -> Iterator[RuleSpec]:
    """The named Life-like rules catalogued in ``data/lifewiki_rules.json``."""
    with open(_lifewiki_rules_path()) as handle:
        for entry in json.load(handle):
            yield RuleSpec(
                dimension=2,
                label=str(entry.get("name") or entry["rulestring"]),
                family="life_rulestring",
                rulestring=str(entry["rulestring"]),
            )


#: Named rule spaces the demo and the sweep script both offer.
RULE_SPACES: dict[str, Callable[[], Iterator[RuleSpec]]] = {
    "eca": iter_eca_rules,
    "life_range": iter_life_range_rules,
    "lifewiki": iter_lifewiki_rules,
    "rule3d": iter_rule3d_rules,
}

#: Exact size of each space, so a caller can report a budget as a fraction.
RULE_SPACE_SIZES: dict[str, int] = {
    "eca": 256,
    "life_range": len(_ranges(8)) ** 2,
    "rule3d": len(_ranges(26)) ** 2,
}


def rule_space(name: str) -> Iterator[RuleSpec]:
    try:
        factory = RULE_SPACES[name]
    except KeyError:
        raise ValueError(f"Unknown rule space {name!r}; choose from {sorted(RULE_SPACES)}") from None
    return factory()


def count_rule_space(name: str) -> int:
    if name in RULE_SPACE_SIZES:
        return RULE_SPACE_SIZES[name]
    return sum(1 for _ in rule_space(name))


# --- Stage 1: is anything still happening? ------------------------------------


@dataclass(frozen=True, slots=True)
class RuleScreen:
    spec: RuleSpec
    verdict: Verdict
    frames: int
    extinct_at: int | None
    final_density: float
    mean_density: float
    activity: float
    #: The initial density this verdict was reached at -- the rule's own
    #: tuning, carried forward so the full evaluation re-uses it.
    density: float

    @property
    def passed(self) -> bool:
        return self.verdict == "active"

    def to_payload(self) -> dict[str, Any]:
        return {
            "rule": self.spec.to_payload(),
            "verdict": self.verdict,
            "frames": self.frames,
            "extinct_at": self.extinct_at,
            "final_density": _finite(self.final_density),
            "mean_density": _finite(self.mean_density),
            "activity": _finite(self.activity),
            "density": _finite(self.density),
        }


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def screen_rule(spec: RuleSpec, settings: ScreenSettings | None = None) -> RuleScreen:
    """Cheaply decide whether a rule is worth the selector's time.

    Screens the rule at every density in the ladder and returns its best
    outcome, so a rule is only called dead if it dies at *all* of them. The
    density that produced the verdict is carried on the result.
    """
    settings = settings or DEFAULT_SCREEN[spec.dimension]
    best: RuleScreen | None = None
    for density in settings.densities:
        screen = _screen_at_density(spec, settings, float(density))
        # Best = liveliest verdict; then longest survival (so a rule that dies
        # everywhere reports the density it lasted longest at); then activity.
        if best is None or (
            _VERDICT_RANK[screen.verdict],
            screen.frames,
            screen.activity,
        ) > (_VERDICT_RANK[best.verdict], best.frames, best.activity):
            best = screen
        if best.verdict == "active" and best.activity > 0.05:
            break  # clearly alive; no need to try the rest of the ladder
    assert best is not None  # settings.densities is never empty
    return best


def _screen_at_density(
    spec: RuleSpec, settings: ScreenSettings, density: float
) -> RuleScreen:
    """One screening pass.

    Simulates in chunks and stops as soon as the lattice dies or fills, which
    is what most rules do: in a sample of the 3D contiguous space a third are
    extinct within five steps, so the early exit dominates the runtime of any
    sweep.
    """
    case = spec.to_case(
        size=settings.size,
        density=density,
        horizons=(settings.horizon,),
    )

    frames: list[np.ndarray] = []
    state = None
    remaining = int(settings.horizon)
    extinct_at: int | None = None
    saturated = False

    while remaining > 0:
        steps = min(int(settings.chunk), remaining) + (1 if state is not None else 0)
        if state is None:
            block = simulate_case(case, steps=steps, seed=settings.seed)
        else:
            block = _continue(case, state, steps)[1:]
        if block.size == 0:
            break
        frames.append(block)
        remaining -= len(block)
        state = block[-1]

        flat = block.reshape(len(block), -1)
        sums = flat.sum(axis=1)
        if sums[-1] == 0:
            dead = int(np.flatnonzero(sums == 0)[0])
            extinct_at = sum(len(f) for f in frames[:-1]) + dead
            break
        if flat.mean(axis=1)[-1] >= SATURATED_DENSITY:
            saturated = True
            break

    spacetime = np.concatenate(frames, axis=0) if frames else np.zeros((0, 1), dtype=np.uint8)
    n_frames = int(len(spacetime))
    flat = spacetime.reshape(n_frames, -1) if n_frames else np.zeros((0, 1), dtype=np.uint8)
    densities = flat.mean(axis=1) if n_frames else np.zeros(0)

    tail = flat[-int(settings.tail_frames) :] if n_frames else flat
    if len(tail) >= 2:
        activity = float((tail[1:] != tail[:-1]).mean())
    else:
        activity = 0.0

    if extinct_at is not None:
        verdict: Verdict = "extinct"
    elif saturated:
        verdict = "saturated"
    elif activity < ACTIVITY_FLOOR:
        verdict = "frozen"
    else:
        verdict = "active"

    return RuleScreen(
        spec=spec,
        verdict=verdict,
        frames=n_frames,
        extinct_at=extinct_at,
        final_density=float(densities[-1]) if n_frames else 0.0,
        mean_density=float(densities.mean()) if n_frames else 0.0,
        activity=activity,
        density=float(density),
    )


def _continue(case: ALifeCase, state: np.ndarray, steps: int) -> np.ndarray:
    """Continue a case's dynamics from ``state`` for ``steps`` frames.

    Re-uses the case's own family dispatch so the screen and the full run are
    the same dynamics, rather than a second simulator written for speed.
    """
    from .ca2d import parse_rulestring, simulate_2d, simulate_2d_general
    from .ca3d import parse_rulestring_3d, simulate_3d, simulate_3d_general
    from .eca import simulate_eca

    if case.family == "eca":
        return simulate_eca(int(case.rule_number), state, int(steps))
    if case.family == "life_range":
        return simulate_2d(state, steps=int(steps), rule="custom", survive=case.survive, birth=case.birth)
    if case.family == "life_rulestring":
        birth, survive = parse_rulestring(str(case.rulestring))
        return simulate_2d_general(state, steps=int(steps), birth=birth, survive=survive)
    if case.family == "rule3d":
        return simulate_3d(state, steps=int(steps), rule="custom", survive=case.survive, birth=case.birth)
    if case.family == "rule3d_general":
        birth, survive = parse_rulestring_3d(str(case.rulestring))
        return simulate_3d_general(state, steps=int(steps), birth=birth, survive=survive)
    raise ValueError(f"Unsupported family: {case.family}")


# --- Stage 2: what does the selector make of it? ------------------------------


@dataclass(frozen=True, slots=True)
class RuleEvaluation:
    spec: RuleSpec
    screen: RuleScreen
    horizon: int
    size: int
    density: float
    selected_period: int
    selected_shift: tuple[int, ...]
    defect_rate: float
    margin_bits: float
    status: str
    bits_per_site: float
    n_candidates: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "rule": self.spec.to_payload(),
            "screen": self.screen.to_payload(),
            "horizon": self.horizon,
            "size": self.size,
            "density": _finite(self.density),
            "selected_period": self.selected_period,
            "selected_shift": list(self.selected_shift),
            "defect_rate": _finite(self.defect_rate),
            "margin_bits": _finite(self.margin_bits),
            "status": self.status,
            "bits_per_site": _finite(self.bits_per_site),
            "n_candidates": self.n_candidates,
        }


def evaluate_rule(
    spec: RuleSpec,
    screen: RuleScreen,
    *,
    size: int,
    horizon: int,
    density: float,
    seed: int = 11,
    search: SearchConfig | None = None,
) -> RuleEvaluation:
    """Run the shipped selector on a rule that passed screening."""
    case = spec.to_case(size=size, density=density, horizons=(horizon,), search=search)
    spacetime = simulate_case(case, steps=horizon, seed=seed)
    outcome = scan_case_spacetime(case, spacetime)
    selection = outcome.selection
    n_sites = int(np.prod(spacetime.shape))
    shift = selection.selected_shift
    shift = (int(shift),) if isinstance(shift, (int, np.integer)) else tuple(int(v) for v in shift)
    return RuleEvaluation(
        spec=spec,
        screen=screen,
        horizon=int(horizon),
        size=int(size),
        density=float(density),
        selected_period=int(selection.selected_period),
        selected_shift=shift,
        defect_rate=float(selection.selected_defect_rate),
        margin_bits=float(selection.margin_bits),
        status=str(selection.status),
        bits_per_site=float(selection.selected_nml_bits) / n_sites if n_sites else float("inf"),
        n_candidates=int(len(outcome.frame)),
    )


# --- The search ---------------------------------------------------------------


def usefulness_key(evaluation: RuleEvaluation) -> tuple[float, float]:
    """Rank order: a sparse mask first, then a cheap code.

    This is the paper's own target signature -- a domain template that covers
    most of the run with a small set of localized departures -- so ranking by
    defect rate ranks by how well the rule exhibits the thing being studied.
    """
    return (evaluation.defect_rate, evaluation.bits_per_site)


def search_rules(
    space: str | Iterable[RuleSpec],
    *,
    limit: int | None = None,
    screen_settings: ScreenSettings | None = None,
    evaluate: bool = True,
    max_evaluations: int | None = None,
    eval_size: int | None = None,
    eval_horizon: int | None = None,
    eval_density: float | None = None,
    seed: int = 11,
    shuffle_seed: int | None = None,
    progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    """Screen a rule space and evaluate the survivors.

    ``limit`` caps how many rules are *screened*, which is what bounds the
    runtime; pass ``shuffle_seed`` to take a representative sample of a large
    space rather than its first ``limit`` entries in enumeration order.

    ``max_evaluations`` caps the second stage separately, because screening
    costs ~16 ms per rule and the selector ~0.9 s: a caller that wants to
    scan widely but only wants a handful of fully-scored results (the browser
    demo) screens everything and evaluates a bounded, unbiased prefix of the
    survivors. The returned payload always reports both counts, so a capped
    run never reads as an exhaustive one.
    """
    specs = list(rule_space(space) if isinstance(space, str) else space)
    total_space = len(specs)
    if shuffle_seed is not None:
        rng = np.random.default_rng(int(shuffle_seed))
        rng.shuffle(specs)
    if limit is not None:
        specs = specs[: int(limit)]
    if not specs:
        return {
            "space": space if isinstance(space, str) else "custom",
            "screened": 0, "space_size": total_space,
            "counts": {}, "results": [], "rejected": [],
        }

    settings = screen_settings or DEFAULT_SCREEN[specs[0].dimension]
    counts: dict[str, int] = {"extinct": 0, "saturated": 0, "frozen": 0, "active": 0}
    # A verdict only describes the window it was measured on, so never screen
    # over a shorter window than the one results are reported for -- otherwise
    # a rule that dies inside the evaluation horizon can still pass screening.
    if eval_horizon is not None and int(eval_horizon) > settings.horizon:
        settings = replace(settings, horizon=int(eval_horizon))
    evaluations: list[RuleEvaluation] = []
    screens: list[RuleScreen] = []

    dimension = specs[0].dimension
    size = int(eval_size if eval_size is not None else settings.size)
    horizon = int(eval_horizon if eval_horizon is not None else settings.horizon)

    for index, spec in enumerate(specs):
        screen = screen_rule(spec, settings)
        screens.append(screen)
        counts[screen.verdict] += 1
        room = max_evaluations is None or len(evaluations) < int(max_evaluations)
        if screen.passed and evaluate and room:
            # Evaluate at the density the rule actually survived at, not a
            # family-wide default -- that default is what killed 3d-life.
            density = float(eval_density if eval_density is not None else screen.density)
            evaluations.append(
                evaluate_rule(
                    spec, screen, size=size, horizon=horizon, density=density, seed=seed
                )
            )
        if progress is not None:
            progress(
                (index + 1) / len(specs),
                f"screened {index + 1}/{len(specs)} — {counts['active']} active",
            )

    evaluations.sort(key=usefulness_key)
    return {
        "space": space if isinstance(space, str) else "custom",
        "dimension": dimension,
        "space_size": total_space,
        "screened": len(specs),
        "counts": counts,
        "screen_settings": {
            "size": settings.size,
            "horizon": settings.horizon,
            "densities": list(settings.densities),
            "seed": settings.seed,
        },
        "evaluation_settings": {
            "size": size,
            "horizon": horizon,
            # Per-rule unless the caller pinned one; see each result's density.
            "density": _finite(eval_density) if eval_density is not None else "per-rule",
            "seed": seed,
        },
        "evaluated": len(evaluations),
        # Screened, alive, but never scored -- either the caller asked for a
        # screen-only run or max_evaluations was reached. Reported so a capped
        # run is never mistaken for a complete one.
        "active_not_evaluated": max(0, counts["active"] - len(evaluations)),
        "max_evaluations": int(max_evaluations) if max_evaluations is not None else None,
        "results": [evaluation.to_payload() for evaluation in evaluations],
        "active_screens": [
            screen.to_payload() for screen in screens if screen.passed
        ][: 200],
    }
