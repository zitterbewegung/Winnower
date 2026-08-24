"""Synthetic finite-state-machine residual/leverage experiment primitives.

This module implements the exact dynamical, model-selection, generation and
matching machinery for the registered study described in
``research/synthetic_fsm/PROTOCOL.md``.

The system family is deterministic maps ``f: S -> S`` on ``S = {0, ..., 63}``.
Everything here is computed exactly with integer counts; floating point appears
only in codelengths and in derived convenience columns.

Nothing in this module is specific to cellular automata: the point of the study
is to strip spatial geometry, locality, neighbourhoods and parallel update out
of the residual/leverage question.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from math import gcd
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

__all__ = [
    "N_STATES",
    "N_ALTERNATIVES",
    "PROTOCOL_ID",
    "FAMILIES",
    "SPLITS",
    "FSMInstance",
    "MDLFit",
    "affine_map",
    "all_affine_maps",
    "canonical_cycle",
    "cluster_bootstrap",
    "codelength_affine",
    "codelength_full_table",
    "cycle_labels",
    "entry_rows",
    "fit_mdl",
    "generate_fsm",
    "holm_adjust",
    "matched_effect_rows",
    "on_cycle_flags",
    "reachability_matrix",
    "residual_destination_type",
    "seed_plan",
    "sha256_bytes",
    "sha256_path",
    "sign_flip_test",
    "summary_row",
    "switch_destination_counts",
    "terminal_cycle",
    "trajectory_prefix",
    "visit_counts",
    "write_csv_gz",
    "write_json",
]

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

N_STATES = 64
"""Size of the state set ``S = {0, ..., 63}``."""

N_ALTERNATIVES = N_STATES - 1
"""Number of alternative destinations for one outgoing transition (63)."""

PROTOCOL_ID = "winnower.synthetic-fsm-residual-leverage"

FAMILIES = ("permutation", "contracting", "random")
SPLITS = ("development", "holdout")

BIT_GENERATOR = "PCG64"

# Base seed blocks for protocol revision 0 (see PROTOCOL.md section "Seeds").
_BASE_SEEDS: dict[tuple[str, str], int] = {
    ("development", "permutation"): 110000,
    ("development", "contracting"): 110120,
    ("development", "random"): 110240,
    ("holdout", "permutation"): 220000,
    ("holdout", "contracting"): 220120,
    ("holdout", "random"): 220240,
}
_BASE_CONTINUATION_SEEDS: dict[str, int] = {
    "permutation": 221000,
    "contracting": 222000,
}
REVISION_SEED_STRIDE = 1_000_000
N_PER_FAMILY = 120
CONTINUATION_BLOCK = 40
CONTINUATION_CAP = 400
INFORMATIVE_TARGET = 100

ANALYSIS_SEED_BOOTSTRAP = 330000
ANALYSIS_SEED_SIGN_FLIP = 330001
N_BOOTSTRAP = 10_000
N_SIGN_FLIP = 10_000


# --------------------------------------------------------------------------
# Affine candidate family
# --------------------------------------------------------------------------


def affine_map(a: int, b: int, n: int = N_STATES) -> np.ndarray:
    """Return the transition table of ``h(x) = (a*x + b) mod n``."""
    if not (0 <= a < n and 0 <= b < n):
        raise ValueError(f"affine parameters out of range: a={a}, b={b}, n={n}")
    x = np.arange(n, dtype=np.int64)
    return (a * x + b) % n


@lru_cache(maxsize=4)
def all_affine_maps(n: int = N_STATES) -> np.ndarray:
    """All ``n**2`` affine candidate tables, row ``a*n + b``.

    Row order is lexicographic in ``(a, b)``, which is exactly the tie-break
    order the frozen MDL rule requires.
    """
    a = np.arange(n, dtype=np.int64)[:, None, None]
    b = np.arange(n, dtype=np.int64)[None, :, None]
    x = np.arange(n, dtype=np.int64)[None, None, :]
    table = (a * x + b) % n
    out = table.reshape(n * n, n)
    out.flags.writeable = False
    return out


def permutation_multipliers(n: int = N_STATES) -> tuple[int, ...]:
    """Multipliers ``a`` with ``gcd(a, n) == 1`` (bijective skeletons)."""
    return tuple(a for a in range(n) if gcd(a, n) == 1)


def contracting_multipliers(n: int = N_STATES) -> tuple[int, ...]:
    """Multipliers ``a`` with ``gcd(a, n) == 2`` (2-to-1 skeletons)."""
    return tuple(a for a in range(n) if gcd(a, n) == 2)


# --------------------------------------------------------------------------
# Exact functional-graph dynamics
# --------------------------------------------------------------------------


def _as_table(f: Sequence[int] | np.ndarray) -> np.ndarray:
    table = np.asarray(f, dtype=np.int64)
    if table.ndim != 1:
        raise ValueError("transition table must be one-dimensional")
    n = table.shape[0]
    if n < 1:
        raise ValueError("transition table must be non-empty")
    if table.min() < 0 or table.max() >= n:
        raise ValueError("transition table entries must lie in range(n)")
    return table


def trajectory_prefix(f: Sequence[int] | np.ndarray, x: int) -> list[int]:
    """Distinct pre-repeat trajectory prefix ``V_f(x) = [x_0, ..., x_{tau-1}]``.

    ``tau_f(x) = min{t >= 1 : x_t in {x_0, ..., x_{t-1}}}``.  The returned list
    is exactly the set of states reachable from ``x`` under ``f``, in visit
    order.
    """
    table = _as_table(f)
    n = table.shape[0]
    if not (0 <= x < n):
        raise ValueError(f"state {x} out of range for n={n}")
    seen = np.full(n, -1, dtype=np.int64)
    order: list[int] = []
    cur = int(x)
    while seen[cur] < 0:
        seen[cur] = len(order)
        order.append(cur)
        cur = int(table[cur])
    return order


def terminal_cycle(f: Sequence[int] | np.ndarray, x: int) -> tuple[int, ...]:
    """Canonical directed terminal cycle reached from ``x``.

    The cycle is returned as the lexicographically smallest rotation of its
    directed state sequence.  Reversal is *not* an equivalence: edge direction
    matters.
    """
    table = _as_table(f)
    order = trajectory_prefix(table, x)
    repeat = int(table[order[-1]])
    start = order.index(repeat)
    return canonical_cycle(order[start:])


def canonical_cycle(seq: Iterable[int]) -> tuple[int, ...]:
    """Lexicographically smallest rotation of a directed cycle sequence."""
    cyc = tuple(int(v) for v in seq)
    if not cyc:
        raise ValueError("cycle sequence must be non-empty")
    if len(set(cyc)) != len(cyc):
        raise ValueError(f"cycle sequence has repeated states: {cyc}")
    k = min(range(len(cyc)), key=lambda i: cyc[i:] + cyc[:i])
    return cyc[k:] + cyc[:k]


def reachability_matrix(f: Sequence[int] | np.ndarray) -> np.ndarray:
    """Boolean matrix ``R`` with ``R[x, u] == (u in V_f(x))``."""
    table = _as_table(f)
    n = table.shape[0]
    reach = np.zeros((n, n), dtype=bool)
    for x in range(n):
        for u in trajectory_prefix(table, x):
            reach[x, u] = True
    return reach


def visit_counts(f: Sequence[int] | np.ndarray) -> np.ndarray:
    """``visitCount_f(u) = |{x in S : u in V_f(x)}|`` for every ``u``."""
    return reachability_matrix(f).sum(axis=0).astype(np.int64)


def cycle_labels(
    f: Sequence[int] | np.ndarray,
) -> tuple[np.ndarray, list[tuple[int, ...]]]:
    """Terminal-cycle label per state plus the sorted canonical cycle list.

    ``labels[x]`` indexes into the returned list; the list is sorted so labels
    are a deterministic function of ``f`` alone.
    """
    table = _as_table(f)
    n = table.shape[0]
    cycles = sorted({terminal_cycle(table, x) for x in range(n)})
    index = {c: i for i, c in enumerate(cycles)}
    labels = np.array(
        [index[terminal_cycle(table, x)] for x in range(n)], dtype=np.int64
    )
    return labels, cycles


def on_cycle_flags(f: Sequence[int] | np.ndarray) -> np.ndarray:
    """``True`` exactly for states lying on their component's terminal cycle."""
    table = _as_table(f)
    n = table.shape[0]
    flags = np.zeros(n, dtype=bool)
    for cyc in cycle_labels(table)[1]:
        for u in cyc:
            flags[u] = True
    return flags


def switch_destination_counts(f: Sequence[int] | np.ndarray) -> np.ndarray:
    """Exact ``s_f(u)`` for every state ``u``.

    ``s_f(u) = |{y != f(u) : cycle_{f^{u->y}}(u) != cycle_f(u)}|``.

    This uses the closed form justified in the protocol.  Editing only the
    outgoing edge of ``u`` and starting the walk at ``u`` gives ``u -> y ->
    ...``; the tail of that walk is a plain ``f``-walk from ``y`` until (and
    unless) it returns to ``u``.  Hence:

    * if ``y`` reaches ``u`` under ``f`` then the edited walk closes a new
      directed cycle through ``u`` whose successor of ``u`` is ``y != f(u)``,
      so the canonical terminal cycle necessarily differs from ``cycle_f(u)``;
    * otherwise the edited walk never revisits ``u``, so it lands in
      ``cycle_f(y)``, and the cycle changes exactly when
      ``cycle_f(y) != cycle_f(u)``.

    ``tests/test_synthetic_fsm.py`` checks this against a literal enumeration.
    """
    table = _as_table(f)
    n = table.shape[0]
    reach = reachability_matrix(table)
    labels, _ = cycle_labels(table)
    out = np.zeros(n, dtype=np.int64)
    for u in range(n):
        ancestors = reach[:, u].copy()  # y reaches u
        cur = int(table[u])
        excluded_is_ancestor = bool(ancestors[cur])
        n_anc = int(ancestors.sum()) - (1 if excluded_is_ancestor else 0)
        non_anc = ~ancestors
        if not excluded_is_ancestor:
            non_anc = non_anc.copy()
            non_anc[cur] = False
        n_other = int(np.count_nonzero(non_anc & (labels != labels[u])))
        out[u] = n_anc + n_other
    return out


@dataclass(frozen=True)
class Dynamics:
    """Exact integer dynamical summary of one transition table."""

    table: np.ndarray
    visit_count: np.ndarray
    on_cycle: np.ndarray
    cycle_label: np.ndarray
    cycles: tuple[tuple[int, ...], ...]
    switch_count: np.ndarray

    @property
    def n(self) -> int:
        return int(self.table.shape[0])

    def canonical_cycle_strings(self) -> list[str]:
        return ["-".join(str(v) for v in self.cycles[i]) for i in self.cycle_label]

    def cycle_lengths(self) -> np.ndarray:
        return np.array(
            [len(self.cycles[i]) for i in self.cycle_label], dtype=np.int64
        )


def analyse_dynamics(f: Sequence[int] | np.ndarray) -> Dynamics:
    """Compute every exact dynamical quantity for one map."""
    table = _as_table(f)
    labels, cycles = cycle_labels(table)
    return Dynamics(
        table=table,
        visit_count=visit_counts(table),
        on_cycle=on_cycle_flags(table),
        cycle_label=labels,
        cycles=tuple(cycles),
        switch_count=switch_destination_counts(table),
    )


# --------------------------------------------------------------------------
# Frozen static MDL fit
# --------------------------------------------------------------------------


def codelength_full_table(n: int = N_STATES) -> float:
    """``L_full = n * log2(n)``."""
    return n * math.log2(n)


def codelength_affine(k: int, n: int = N_STATES) -> float:
    """Frozen exception codelength for an affine model with ``k`` deviations.

    ``L = log2(n^2) + log2(n + 1) + log2(C(n, k)) + k * log2(n - 1)``.
    """
    if not (0 <= k <= n):
        raise ValueError(f"deviation count out of range: k={k}, n={n}")
    return (
        math.log2(n * n)
        + math.log2(n + 1)
        + math.log2(math.comb(n, k))
        + k * math.log2(n - 1)
    )


@dataclass(frozen=True)
class MDLFit:
    """Result of the frozen static MDL model selection."""

    selected_model: str  # "affine" | "full_table"
    a: int
    b: int
    best_affine_bits: float
    full_table_bits: float
    residual_states: tuple[int, ...]

    @property
    def residual_count(self) -> int:
        return len(self.residual_states)


def fit_mdl(f: Sequence[int] | np.ndarray, n: int = N_STATES) -> MDLFit:
    """Select between the affine family and the full transition table.

    Only the complete static transition table is consulted.  No trajectory,
    occupancy, cycle, attractor, planted-label or family information enters.
    Ties in codelength break lexicographically on ``(a, b)``; the full table
    wins ties against the best affine model.
    """
    table = _as_table(f)
    if table.shape[0] != n:
        raise ValueError("table size does not match n")
    candidates = all_affine_maps(n)
    k = (candidates != table[None, :]).sum(axis=1)
    bits = np.array([codelength_affine(int(kk), n) for kk in k], dtype=np.float64)
    best = int(np.argmin(bits))  # argmin returns the first minimum => lex (a, b)
    best_a, best_b = divmod(best, n)
    best_bits = float(bits[best])
    full_bits = codelength_full_table(n)
    if full_bits <= best_bits:
        return MDLFit(
            selected_model="full_table",
            a=-1,
            b=-1,
            best_affine_bits=best_bits,
            full_table_bits=full_bits,
            residual_states=(),
        )
    skeleton = candidates[best]
    residuals = tuple(int(u) for u in np.flatnonzero(table != skeleton))
    return MDLFit(
        selected_model="affine",
        a=int(best_a),
        b=int(best_b),
        best_affine_bits=best_bits,
        full_table_bits=full_bits,
        residual_states=residuals,
    )


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class FSMInstance:
    """One generated FSM together with its pre-treatment skeleton."""

    fsm_id: str
    split: str
    family: str
    seed: int
    protocol_revision: int
    table: np.ndarray
    skeleton: np.ndarray
    true_a: int
    true_b: int
    planted_source: int
    original_destination: int
    planted_destination: int
    skeleton_resamples: int

    @property
    def is_structured(self) -> bool:
        return self.family in ("permutation", "contracting")


def _new_generator(seed: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(seed))


def _eligible_sources(skeleton: np.ndarray) -> np.ndarray:
    """States whose exact pre-treatment stratum contains at least two states."""
    vc = visit_counts(skeleton)
    oc = on_cycle_flags(skeleton)
    keys = vc * 2 + oc.astype(np.int64)
    _, inverse, counts = np.unique(keys, return_inverse=True, return_counts=True)
    return np.flatnonzero(counts[inverse] >= 2)


def make_fsm_id(split: str, family: str, seed: int) -> str:
    return f"{split[:3]}-{family}-{seed:09d}"


def generate_fsm(
    split: str,
    family: str,
    seed: int,
    protocol_revision: int = 0,
    n: int = N_STATES,
) -> FSMInstance:
    """Generate one FSM exactly as registered.

    For the two structured families the seeded stream draws, in this fixed
    order: multiplier ``a``, offset ``b``, (repeating both if the skeleton has
    no eligible planted source), then the planted source ``u*``, then the
    replacement destination ``y* != h(u*)``.  Resampling is driven *only* by
    source eligibility, never by any post-plant property.

    For the random family the stream draws 64 iid uniform destinations and
    nothing else; random maps are never conditioned or resampled.
    """
    if split not in SPLITS:
        raise ValueError(f"unknown split: {split}")
    if family not in FAMILIES:
        raise ValueError(f"unknown family: {family}")
    rng = _new_generator(seed)
    fsm_id = make_fsm_id(split, family, seed)

    if family == "random":
        table = rng.integers(0, n, size=n, endpoint=False).astype(np.int64)
        return FSMInstance(
            fsm_id=fsm_id,
            split=split,
            family=family,
            seed=seed,
            protocol_revision=protocol_revision,
            table=table,
            skeleton=table.copy(),
            true_a=-1,
            true_b=-1,
            planted_source=-1,
            original_destination=-1,
            planted_destination=-1,
            skeleton_resamples=0,
        )

    multipliers = (
        permutation_multipliers(n)
        if family == "permutation"
        else contracting_multipliers(n)
    )
    resamples = 0
    while True:
        a = int(multipliers[int(rng.integers(0, len(multipliers)))])
        b = int(rng.integers(0, n))
        skeleton = affine_map(a, b, n)
        eligible = _eligible_sources(skeleton)
        if eligible.size > 0:
            break
        resamples += 1

    source = int(eligible[int(rng.integers(0, eligible.size))])
    original = int(skeleton[source])
    alternatives = np.array([y for y in range(n) if y != original], dtype=np.int64)
    planted = int(alternatives[int(rng.integers(0, alternatives.size))])
    table = skeleton.copy()
    table[source] = planted
    return FSMInstance(
        fsm_id=fsm_id,
        split=split,
        family=family,
        seed=seed,
        protocol_revision=protocol_revision,
        table=table,
        skeleton=skeleton,
        true_a=a,
        true_b=b,
        planted_source=source,
        original_destination=original,
        planted_destination=planted,
        skeleton_resamples=resamples,
    )


def seed_plan(protocol_revision: int = 0) -> dict[tuple[str, str], list[int]]:
    """Registered seeds per ``(split, family)`` for a protocol revision."""
    offset = REVISION_SEED_STRIDE * protocol_revision
    return {
        key: list(range(base + offset, base + offset + N_PER_FAMILY))
        for key, base in _BASE_SEEDS.items()
    }


def continuation_seeds(
    family: str, block_index: int, protocol_revision: int = 0
) -> list[int]:
    """Deterministic continuation seeds for one 40-FSM extension block."""
    if family not in _BASE_CONTINUATION_SEEDS:
        raise ValueError(f"no continuation block registered for family {family}")
    if block_index < 0 or block_index * CONTINUATION_BLOCK >= CONTINUATION_CAP:
        raise ValueError(f"continuation block index out of range: {block_index}")
    base = (
        _BASE_CONTINUATION_SEEDS[family]
        + REVISION_SEED_STRIDE * protocol_revision
        + block_index * CONTINUATION_BLOCK
    )
    return list(range(base, base + CONTINUATION_BLOCK))


# --------------------------------------------------------------------------
# Row construction
# --------------------------------------------------------------------------


def residual_destination_type(
    inst: FSMInstance, source: int, destination: int
) -> str:
    """Classify a residual edge relative to the pre-treatment skeleton.

    Categories are mutually exclusive and checked in this order: ``self_loop``,
    ``pre_ancestor_of_source`` (destination reaches the source under the
    skeleton, so the edit closes a new cycle), ``same_terminal_cycle``,
    ``different_terminal_cycle``.
    """
    if destination == source:
        return "self_loop"
    reach = reachability_matrix(inst.skeleton)
    if reach[destination, source]:
        return "pre_ancestor_of_source"
    labels, _ = cycle_labels(inst.skeleton)
    if labels[destination] == labels[source]:
        return "same_terminal_cycle"
    return "different_terminal_cycle"


def stratum_key(visit_count: int, on_cycle: bool) -> str:
    return f"vc{int(visit_count)}|oc{int(bool(on_cycle))}"


def entry_rows(inst: FSMInstance, fit: MDLFit) -> list[dict]:
    """One row per state of one FSM.

    Pre-treatment columns come from the skeleton ``h``.  For the random family
    no deviation is planted, so the pre-treatment map *is* the observed map and
    the pre/post columns coincide by construction.
    """
    n = inst.table.shape[0]
    post = analyse_dynamics(inst.table)
    pre_vc = visit_counts(inst.skeleton)
    pre_oc = on_cycle_flags(inst.skeleton)
    post_cycles = post.canonical_cycle_strings()
    residual_set = set(fit.residual_states)
    rows: list[dict] = []
    for u in range(n):
        s = int(post.switch_count[u])
        vc = int(post.visit_count[u])
        rows.append(
            {
                "fsm_id": inst.fsm_id,
                "split": inst.split,
                "family": inst.family,
                "seed": inst.seed,
                "state": u,
                "current_destination": int(inst.table[u]),
                "skeleton_destination": int(inst.skeleton[u]),
                "is_planted_source": int(u == inst.planted_source),
                "is_fitted_residual": int(u in residual_set),
                "pre_visit_count": int(pre_vc[u]),
                "pre_w": int(pre_vc[u]) / n,
                "pre_on_cycle": int(bool(pre_oc[u])),
                "post_visit_count": vc,
                "post_w": vc / n,
                "post_on_cycle": int(bool(post.on_cycle[u])),
                "switch_destination_count": s,
                "C_numerator": vc * s,
                "C_denominator": n * (n - 1),
                "C": (vc * s) / (n * (n - 1)),
                "theta_numerator": s,
                "theta_denominator": n - 1,
                "theta": s / (n - 1),
                "canonical_terminal_cycle": post_cycles[u],
                "pre_treatment_stratum": stratum_key(int(pre_vc[u]), bool(pre_oc[u])),
                "post_cycle_length": int(post.cycle_lengths()[u]),
            }
        )
    _assert_entry_bounds(rows, n)
    return rows


def _assert_entry_bounds(rows: list[dict], n: int) -> None:
    for row in rows:
        w = row["post_w"]
        c = row["C"]
        theta = row["theta"]
        if not (0 < w <= 1):
            raise AssertionError(f"w out of bounds: {row}")
        if not (0 <= c <= w + 1e-12):
            raise AssertionError(f"C exceeds w: {row}")
        if not (0 <= theta <= 1):
            raise AssertionError(f"theta out of bounds: {row}")
        if row["C_denominator"] != n * (n - 1):
            raise AssertionError("unexpected C denominator")
        if row["theta_denominator"] != n - 1:
            raise AssertionError("unexpected theta denominator")


def _matched_delta(
    rows: list[dict], target: int, stratum_field: str, stratum_value
) -> tuple[float, float, float, int]:
    controls = [
        r
        for r in rows
        if r["state"] != target and r[stratum_field] == stratum_value
    ]
    if not controls:
        return (float("nan"), float("nan"), float("nan"), 0)
    tgt = rows[target]
    m = len(controls)
    d_theta = tgt["theta"] - sum(r["theta"] for r in controls) / m
    d_c = tgt["C"] - sum(r["C"] for r in controls) / m
    d_w = tgt["post_w"] - sum(r["post_w"] for r in controls) / m
    return (d_theta, d_c, d_w, m)


def summary_row(inst: FSMInstance, fit: MDLFit, rows: list[dict]) -> dict:
    """One row per FSM: model recovery plus the primary matched effect."""
    skeleton_recovered = int(
        fit.selected_model == "affine"
        and fit.a == inst.true_a
        and fit.b == inst.true_b
    )
    planted_recovered = int(
        inst.planted_source >= 0 and inst.planted_source in fit.residual_states
    )
    if inst.is_structured:
        stratum = rows[inst.planted_source]["pre_treatment_stratum"]
        d_theta, d_c, d_w, m = _matched_delta(
            rows, inst.planted_source, "pre_treatment_stratum", stratum
        )
        informative = int(m >= 1 and all(math.isfinite(v) for v in (d_theta, d_c, d_w)))
        dest_type = residual_destination_type(
            inst, inst.planted_source, inst.planted_destination
        )
    else:
        d_theta = d_c = d_w = float("nan")
        m = 0
        informative = 0
        dest_type = ""
    return {
        "fsm_id": inst.fsm_id,
        "split": inst.split,
        "family": inst.family,
        "seed": inst.seed,
        "protocol_revision": inst.protocol_revision,
        "transition_table_json": json.dumps([int(v) for v in inst.table]),
        "skeleton_table_json": json.dumps([int(v) for v in inst.skeleton]),
        "true_a": inst.true_a,
        "true_b": inst.true_b,
        "planted_source": inst.planted_source,
        "original_destination": inst.original_destination,
        "planted_destination": inst.planted_destination,
        "planted_destination_type": dest_type,
        "skeleton_resamples": inst.skeleton_resamples,
        "selected_model": fit.selected_model,
        "fitted_a": fit.a,
        "fitted_b": fit.b,
        "best_affine_bits": fit.best_affine_bits,
        "full_table_bits": fit.full_table_bits,
        "fitted_residual_count": fit.residual_count,
        "fitted_residual_states_json": json.dumps(list(fit.residual_states)),
        "skeleton_recovered": skeleton_recovered,
        "planted_source_recovered": planted_recovered,
        "informative": informative,
        "matched_control_count": m,
        "delta_theta": d_theta,
        "delta_C": d_c,
        "delta_w": d_w,
    }


def matched_effect_rows(inst: FSMInstance, fit: MDLFit, rows: list[dict]) -> list[dict]:
    """Every entry/control pair consumed by any registered estimator.

    ``analysis`` values:

    ``primary_planted_pre``
        planted source vs. non-planted controls in the same exact
        pre-treatment stratum (the confirmatory estimand);
    ``secondary_fitted_pre``
        fitted residual entries vs. non-residual controls in the same exact
        pre-treatment stratum;
    ``secondary_fitted_post``
        fitted residual entries vs. non-residual controls matched on exact
        *post*-treatment integer visit count (observational sensitivity).
    """
    out: list[dict] = []
    family_weight = 0.5 if inst.is_structured else 0.0

    def emit(analysis: str, primary: int, entry: int, controls: list[dict],
             stratum_field: str, matching_version: str, entry_weight: float) -> None:
        tgt = rows[entry]
        m = len(controls)
        for ctl in controls:
            out.append(
                {
                    "fsm_id": inst.fsm_id,
                    "split": inst.split,
                    "family": inst.family,
                    "seed": inst.seed,
                    "analysis": analysis,
                    "is_primary": primary,
                    "entry_state": entry,
                    "control_state": ctl["state"],
                    "matching_stratum": str(tgt[stratum_field]),
                    "matching_version": matching_version,
                    "entry_weight": entry_weight,
                    "control_weight": 1.0 / m,
                    "fsm_weight": 1.0,
                    "family_weight": family_weight,
                    "entry_theta": tgt["theta"],
                    "control_theta": ctl["theta"],
                    "diff_theta": tgt["theta"] - ctl["theta"],
                    "entry_C": tgt["C"],
                    "control_C": ctl["C"],
                    "diff_C": tgt["C"] - ctl["C"],
                    "entry_w": tgt["post_w"],
                    "control_w": ctl["post_w"],
                    "diff_w": tgt["post_w"] - ctl["post_w"],
                }
            )

    if inst.is_structured:
        u = inst.planted_source
        stratum = rows[u]["pre_treatment_stratum"]
        controls = [
            r for r in rows if r["state"] != u and r["pre_treatment_stratum"] == stratum
        ]
        if controls:
            emit(
                "primary_planted_pre", 1, u, controls,
                "pre_treatment_stratum", "exact_pre_visit_count_and_pre_on_cycle", 1.0,
            )

    residuals = list(fit.residual_states)
    if inst.is_structured and residuals:
        n_res = len(residuals)
        for r_state in residuals:
            stratum = rows[r_state]["pre_treatment_stratum"]
            controls = [
                rr
                for rr in rows
                if rr["is_fitted_residual"] == 0
                and rr["pre_treatment_stratum"] == stratum
            ]
            if controls:
                emit(
                    "secondary_fitted_pre", 0, r_state, controls,
                    "pre_treatment_stratum",
                    "exact_pre_visit_count_and_pre_on_cycle",
                    1.0 / n_res,
                )
            post_controls = [
                rr
                for rr in rows
                if rr["is_fitted_residual"] == 0
                and rr["post_visit_count"] == rows[r_state]["post_visit_count"]
            ]
            if post_controls:
                emit(
                    "secondary_fitted_post", 0, r_state, post_controls,
                    "post_visit_count",
                    "exact_post_visit_count_observational",
                    1.0 / n_res,
                )
    return out


# --------------------------------------------------------------------------
# Frozen statistics
# --------------------------------------------------------------------------


def equal_family_mean(
    perm: Sequence[float], contract: Sequence[float]
) -> float:
    """``0.5 * mean(permutation) + 0.5 * mean(contracting)``."""
    if len(perm) == 0 or len(contract) == 0:
        return float("nan")
    return 0.5 * float(np.mean(perm)) + 0.5 * float(np.mean(contract))


def cluster_bootstrap(
    perm: Sequence[float],
    contract: Sequence[float],
    n_resamples: int = N_BOOTSTRAP,
    seed: int = ANALYSIS_SEED_BOOTSTRAP,
) -> dict:
    """Stratified cluster bootstrap over per-FSM effects.

    Each resample draws permutation FSMs and contracting FSMs with replacement
    at their observed family sample sizes, averages within family and combines
    the two family means with equal weight.  Percentile interval at 2.5/97.5.
    """
    p = np.asarray(perm, dtype=np.float64)
    c = np.asarray(contract, dtype=np.float64)
    rng = np.random.Generator(np.random.PCG64(seed))
    combined = np.empty(n_resamples, dtype=np.float64)
    p_means = np.empty(n_resamples, dtype=np.float64)
    c_means = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        pm = p[rng.integers(0, p.size, size=p.size)].mean()
        cm = c[rng.integers(0, c.size, size=c.size)].mean()
        p_means[i] = pm
        c_means[i] = cm
        combined[i] = 0.5 * pm + 0.5 * cm
    return {
        "combined_lo": float(np.percentile(combined, 2.5)),
        "combined_hi": float(np.percentile(combined, 97.5)),
        "permutation_lo": float(np.percentile(p_means, 2.5)),
        "permutation_hi": float(np.percentile(p_means, 97.5)),
        "contracting_lo": float(np.percentile(c_means, 2.5)),
        "contracting_hi": float(np.percentile(c_means, 97.5)),
        "n_resamples": int(n_resamples),
        "seed": int(seed),
    }


def sign_flip_test(
    perm: Sequence[float],
    contract: Sequence[float] | None,
    observed: float,
    rng: np.random.Generator,
    n_draws: int = N_SIGN_FLIP,
) -> dict:
    """Cluster sign-flip Monte Carlo test.

    Every FSM effect is independently sign-flipped and the same
    equal-family-weighted statistic recomputed.  ``p_left`` is the registered
    one-sided p-value for the negative alternative.
    """
    p = np.asarray(perm, dtype=np.float64)
    stats = np.empty(n_draws, dtype=np.float64)
    if contract is None:
        for i in range(n_draws):
            signs = rng.choice(np.array([-1.0, 1.0]), size=p.size)
            stats[i] = float(np.mean(signs * p))
    else:
        c = np.asarray(contract, dtype=np.float64)
        for i in range(n_draws):
            sp = rng.choice(np.array([-1.0, 1.0]), size=p.size)
            sc = rng.choice(np.array([-1.0, 1.0]), size=c.size)
            stats[i] = 0.5 * float(np.mean(sp * p)) + 0.5 * float(np.mean(sc * c))
    n_le = int(np.count_nonzero(stats <= observed))
    n_ge = int(np.count_nonzero(stats >= observed))
    p_left = (1 + n_le) / (n_draws + 1)
    p_right = (1 + n_ge) / (n_draws + 1)
    return {
        "p_left": float(p_left),
        "p_right": float(p_right),
        "p_two_sided": float(min(1.0, 2 * min(p_left, p_right))),
        "n_draws": int(n_draws),
    }


def holm_adjust(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjustment preserving input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * pvalues[idx])
        running = max(running, val)
        adjusted[idx] = running
    return adjusted


# --------------------------------------------------------------------------
# Deterministic serialization
# --------------------------------------------------------------------------


def write_csv_gz(df, path: str | Path, sort_keys: Sequence[str]) -> None:
    """Write a deterministically sorted, deterministically gzipped CSV.

    Rows are sorted by ``sort_keys`` with a stable mergesort, floats are
    formatted with ``%.17g`` (exact float64 round-trip), newlines are ``\\n``
    and the gzip header carries ``mtime=0`` with no embedded filename.
    """
    path = Path(path)
    ordered = df.sort_values(list(sort_keys), kind="mergesort").reset_index(drop=True)
    csv_bytes = ordered.to_csv(index=False, lineterminator="\n", float_format="%.17g")
    raw = csv_bytes.encode("utf-8")
    buf = io.BytesIO()
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0, compresslevel=9)
    gz.write(raw)
    gz.close()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buf.getvalue())


def read_csv_gz(path: str | Path):
    """Read a gzipped CSV with an exactly round-tripping float parser.

    pandas' default ``float_precision="high"`` parser is fast but not exact;
    it loses up to a few ULP, which would silently degrade the integer-derived
    columns this study writes.  ``round_trip`` restores byte-exact values.
    """
    import pandas as pd

    return pd.read_csv(path, compression="gzip", float_precision="round_trip")


def write_json(obj, path: str | Path) -> None:
    """Write JSON with sorted keys, two-space indent and a trailing newline."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n"
    path.write_bytes(text.encode("utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def sha256_csv_gz_content(path: str | Path) -> str:
    """SHA-256 of the *decompressed* CSV bytes (gzip-implementation agnostic)."""
    with gzip.open(path, "rb") as fh:
        return sha256_bytes(fh.read())
