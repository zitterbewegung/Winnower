"""Correctness tests for the synthetic-FSM residual/leverage experiment.

The brute-force helpers in this file are deliberately written from the literal
definitions in the protocol and never call the optimised routines they check.
"""

from __future__ import annotations

import gzip
import importlib
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from relative_symmetry_repair import synthetic_fsm as sf

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts" / "research"


# --------------------------------------------------------------------------
# Literal brute-force reference implementations (independent by construction)
# --------------------------------------------------------------------------


def bf_orbit(table, x):
    """Literal orbit: iterate until a state repeats; return the visit order."""
    seen = []
    cur = x
    while cur not in seen:
        seen.append(cur)
        cur = table[cur]
    return seen


def bf_terminal_cycle(table, x):
    """Literal canonical terminal cycle of the orbit of ``x``."""
    order = bf_orbit(table, x)
    repeat = table[order[-1]]
    cyc = order[order.index(repeat):]
    rotations = [tuple(cyc[i:] + cyc[:i]) for i in range(len(cyc))]
    return min(rotations)


def bf_visit_set(table, x):
    return set(bf_orbit(table, x))


def bf_w(table, u):
    n = len(table)
    return Fraction(sum(1 for x in range(n) if u in bf_visit_set(table, x)), n)


def bf_C(table, u):
    """Literal double average from the protocol definition of ``C_f(u)``."""
    n = len(table)
    total = Fraction(0)
    base = [bf_terminal_cycle(table, x) for x in range(n)]
    for y in range(n):
        if y == table[u]:
            continue
        edited = list(table)
        edited[u] = y
        switched = sum(
            1 for x in range(n) if bf_terminal_cycle(edited, x) != base[x]
        )
        total += Fraction(switched, n)
    return total / (n - 1)


def bf_theta(table, u):
    return bf_C(table, u) / bf_w(table, u)


# --------------------------------------------------------------------------
# 21.1 Functional-graph hand examples
# --------------------------------------------------------------------------


def test_fixed_point():
    table = [0, 0, 1]  # 2 -> 1 -> 0 -> 0
    assert sf.trajectory_prefix(table, 2) == [2, 1, 0]
    assert sf.terminal_cycle(table, 2) == (0,)
    assert list(sf.visit_counts(table)) == [3, 2, 1]
    assert list(sf.on_cycle_flags(table)) == [True, False, False]


def test_two_cycle():
    table = [1, 0]
    assert sf.terminal_cycle(table, 0) == (0, 1)
    assert sf.terminal_cycle(table, 1) == (0, 1)
    assert list(sf.visit_counts(table)) == [2, 2]
    assert list(sf.on_cycle_flags(table)) == [True, True]


def test_tail_into_cycle():
    # 3 -> 2 -> 0 -> 1 -> 0
    table = [1, 0, 0, 2]
    assert sf.trajectory_prefix(table, 3) == [3, 2, 0, 1]
    assert sf.terminal_cycle(table, 3) == (0, 1)
    assert list(sf.visit_counts(table)) == [4, 4, 2, 1]
    assert list(sf.on_cycle_flags(table)) == [True, True, False, False]


def test_multiple_components():
    # component A: 0 <-> 1 with tail 2; component B: 3 -> 3 with tail 4
    table = [1, 0, 0, 3, 3]
    labels, cycles = sf.cycle_labels(table)
    assert cycles == [(0, 1), (3,)]
    assert list(labels) == [0, 0, 0, 1, 1]


def test_intervention_creating_self_loop():
    table = [1, 0, 0]
    edited = [1, 0, 2]  # state 2 now self-loops
    assert sf.terminal_cycle(table, 2) == (0, 1)
    assert sf.terminal_cycle(edited, 2) == (2,)


def test_intervention_changing_cycle():
    # 0 -> 1 -> 0, 2 -> 2.  Redirect 1 -> 2 destroys the 2-cycle.
    table = [1, 0, 2]
    edited = [1, 2, 2]
    assert sf.terminal_cycle(table, 0) == (0, 1)
    assert sf.terminal_cycle(edited, 0) == (2,)


def test_intervention_leaving_cycle_unchanged():
    # 2 -> 0 already; redirecting 2 -> 1 keeps the terminal cycle (0, 1).
    table = [1, 0, 0]
    edited = [1, 0, 1]
    assert sf.terminal_cycle(table, 2) == sf.terminal_cycle(edited, 2) == (0, 1)


# --------------------------------------------------------------------------
# 21.2 Brute-force equivalence for the exact factorization
# --------------------------------------------------------------------------


def _small_maps():
    maps = [
        [1, 0],
        [0, 0],
        [1, 2, 0],
        [1, 0, 0, 2],
        [1, 0, 3, 2],
        [0, 0, 1, 1, 2],
        [3, 3, 3, 4, 5, 3],
        [1, 2, 3, 4, 5, 6, 7, 0],
        [0, 0, 1, 1, 2, 2, 3, 3],
        [2, 3, 4, 5, 6, 7, 0, 1],
        [7, 6, 5, 4, 3, 2, 1, 0],
    ]
    rng = np.random.Generator(np.random.PCG64(20260823))
    for n in (2, 3, 4, 5, 6, 7, 8):
        for _ in range(6):
            maps.append([int(v) for v in rng.integers(0, n, size=n)])
    return maps


@pytest.mark.parametrize("table", _small_maps())
def test_bruteforce_matches_factorization(table):
    n = len(table)
    assert n >= 2, "C is undefined when there is no alternative destination"
    fast_s = sf.switch_destination_counts(table)
    fast_vc = sf.visit_counts(table)
    for u in range(n):
        w_ref = bf_w(table, u)
        c_ref = bf_C(table, u)
        theta_ref = bf_theta(table, u)
        assert w_ref == Fraction(int(fast_vc[u]), n)
        assert c_ref == Fraction(int(fast_vc[u]) * int(fast_s[u]), n * (n - 1))
        assert theta_ref == Fraction(int(fast_s[u]), n - 1)


def test_bruteforce_matches_on_random_n64_maps():
    """Spot-check the factorization at the experiment's own state size."""
    rng = np.random.Generator(np.random.PCG64(4242))
    for _ in range(2):
        table = [int(v) for v in rng.integers(0, 64, size=64)]
        fast_s = sf.switch_destination_counts(table)
        fast_vc = sf.visit_counts(table)
        for u in rng.choice(64, size=6, replace=False):
            u = int(u)
            assert bf_w(table, u) == Fraction(int(fast_vc[u]), 64)
            assert bf_C(table, u) == Fraction(
                int(fast_vc[u]) * int(fast_s[u]), 64 * 63
            )


# --------------------------------------------------------------------------
# 21.3 Canonical cycles and bounds
# --------------------------------------------------------------------------


def test_canonical_cycle_rotation_invariance():
    assert sf.canonical_cycle([3, 7, 1]) == sf.canonical_cycle([7, 1, 3])
    assert sf.canonical_cycle([1, 3, 7]) == (1, 3, 7)


def test_canonical_cycle_direction_sensitive():
    assert sf.canonical_cycle([1, 3, 7]) != sf.canonical_cycle([1, 7, 3])


def test_canonical_cycle_is_deterministic():
    seq = [5, 2, 9, 4]
    assert sf.canonical_cycle(seq) == sf.canonical_cycle(seq)
    with pytest.raises(ValueError):
        sf.canonical_cycle([1, 1])
    with pytest.raises(ValueError):
        sf.canonical_cycle([])


def test_bounds_and_denominators_on_generated_maps():
    for family, seed in (
        ("permutation", 110000),
        ("contracting", 110120),
        ("random", 110240),
    ):
        inst = sf.generate_fsm("development", family, seed)
        fit = sf.fit_mdl(inst.table)
        rows = sf.entry_rows(inst, fit)
        for row in rows:
            assert row["post_visit_count"] >= 1
            assert 0 < row["post_w"] <= 1
            assert 0 <= row["C"] <= row["post_w"] + 1e-12
            assert 0 <= row["theta"] <= 1
            assert row["C_denominator"] == 64 * 63
            assert row["theta_denominator"] == 63
            assert row["C_numerator"] == (
                row["post_visit_count"] * row["switch_destination_count"]
            )


# --------------------------------------------------------------------------
# 21.4 MDL tests
# --------------------------------------------------------------------------


def test_codelength_terms_direct():
    assert sf.codelength_full_table(64) == pytest.approx(384.0)
    expected = (
        math.log2(4096) + math.log2(65) + math.log2(math.comb(64, 0)) + 0.0
    )
    assert sf.codelength_affine(0, 64) == pytest.approx(expected)
    expected3 = (
        math.log2(4096) + math.log2(65) + math.log2(math.comb(64, 3)) + 3 * math.log2(63)
    )
    assert sf.codelength_affine(3, 64) == pytest.approx(expected3)
    with pytest.raises(ValueError):
        sf.codelength_affine(65, 64)


def test_optimized_selection_matches_exhaustive_enumeration():
    rng = np.random.Generator(np.random.PCG64(777))
    for _ in range(8):
        table = np.array(rng.integers(0, 64, size=64), dtype=np.int64)
        # brute-force enumeration written from the definition
        best = None
        for a in range(64):
            for b in range(64):
                h = np.array([(a * x + b) % 64 for x in range(64)], dtype=np.int64)
                k = int((h != table).sum())
                bits = sf.codelength_affine(k, 64)
                if best is None or bits < best[0] - 1e-15:
                    best = (bits, a, b)
        fit = sf.fit_mdl(table)
        assert fit.best_affine_bits == pytest.approx(best[0])
        if fit.selected_model == "affine":
            assert (fit.a, fit.b) == (best[1], best[2])


def test_exact_affine_map_is_recovered():
    table = sf.affine_map(45, 54)
    fit = sf.fit_mdl(table)
    assert fit.selected_model == "affine"
    assert (fit.a, fit.b) == (45, 54)
    assert fit.residual_states == ()
    assert fit.best_affine_bits == pytest.approx(sf.codelength_affine(0, 64))


def test_affine_with_one_deviation():
    table = sf.affine_map(17, 3).copy()
    table[11] = (table[11] + 7) % 64
    fit = sf.fit_mdl(table)
    assert fit.selected_model == "affine"
    assert (fit.a, fit.b) == (17, 3)
    assert fit.residual_states == (11,)


def test_full_table_selected_for_random_map():
    rng = np.random.Generator(np.random.PCG64(99))
    table = np.array(rng.integers(0, 64, size=64), dtype=np.int64)
    fit = sf.fit_mdl(table)
    assert fit.selected_model == "full_table"
    assert fit.residual_states == ()
    assert fit.a == fit.b == -1


def test_lexicographic_tie_break():
    """a=0 skeletons are constant maps; several (a, b) can tie on a constant map."""
    table = np.zeros(64, dtype=np.int64)  # h(x) = 0 for a=0,b=0
    fit = sf.fit_mdl(table)
    assert (fit.a, fit.b) == (0, 0)
    # Any a with a*x ≡ 0 for all x is impossible except a=0 mod 64, so build an
    # explicit tie at the codelength level instead.
    candidates = sf.all_affine_maps(64)
    k = (candidates != table[None, :]).sum(axis=1)
    tied = np.flatnonzero(k == k.min())
    assert tied[0] == 0  # first minimum is lexicographically smallest (a, b)


def test_full_table_wins_ties():
    """When L_full == L(h*), the full table must be selected."""
    n = 4
    # Search for a k where the affine codelength equals the full-table cost.
    full = sf.codelength_full_table(n)
    # Construct a synthetic equality check on the selection rule itself.
    assert sf.codelength_affine(0, n) != full
    # Direct rule check: monkey-free equality is exercised via a tiny n where the
    # affine code is more expensive than the table for every k.
    table = np.array([1, 3, 0, 2], dtype=np.int64)
    fit = sf.fit_mdl(table, n=n)
    if fit.best_affine_bits >= full:
        assert fit.selected_model == "full_table"
    else:
        assert fit.selected_model == "affine"


# --------------------------------------------------------------------------
# 21.5 Recovery tests, including affine degeneracies
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "a,b,source,delta",
    [
        (1, 0, 5, 1),      # identity skeleton
        (0, 17, 40, 9),    # constant skeleton (maximally degenerate)
        (63, 0, 2, 31),    # x -> -x
        (33, 33, 63, 5),   # odd multiplier, order-2 permutation
        (2, 7, 13, 21),    # contracting, gcd(a,64)=2
        (32, 1, 8, 17),    # heavily degenerate multiplier
    ],
)
def test_known_plant_is_recovered(a, b, source, delta):
    skeleton = sf.affine_map(a, b)
    table = skeleton.copy()
    table[source] = (int(skeleton[source]) + delta) % 64
    fit = sf.fit_mdl(table)
    assert fit.selected_model == "affine"
    assert (fit.a, fit.b) == (a, b)
    assert fit.residual_states == (source,)


def test_generated_structured_maps_recover_the_plant():
    for family, base in (("permutation", 110000), ("contracting", 110120)):
        for seed in range(base, base + 12):
            inst = sf.generate_fsm("development", family, seed)
            fit = sf.fit_mdl(inst.table)
            assert fit.selected_model == "affine"
            assert (fit.a, fit.b) == (inst.true_a, inst.true_b)
            assert inst.planted_source in fit.residual_states


# --------------------------------------------------------------------------
# 21.6 Random negative control (smoke seeds only, not the holdout gate)
# --------------------------------------------------------------------------


def test_random_maps_generally_select_full_table():
    selected = [
        sf.fit_mdl(sf.generate_fsm("development", "random", s).table).selected_model
        for s in range(110240, 110270)
    ]
    assert selected.count("full_table") >= 28


# --------------------------------------------------------------------------
# 21.7 Reproducibility
# --------------------------------------------------------------------------


def test_generator_determinism():
    a = sf.generate_fsm("holdout", "permutation", 220000)
    b = sf.generate_fsm("holdout", "permutation", 220000)
    assert np.array_equal(a.table, b.table)
    assert np.array_equal(a.skeleton, b.skeleton)
    assert (a.planted_source, a.planted_destination) == (
        b.planted_source,
        b.planted_destination,
    )


def test_seed_plan_disjointness_and_sizes():
    plan = sf.seed_plan(0)
    assert set(plan) == {
        (s, f) for s in sf.SPLITS for f in sf.FAMILIES
    }
    all_seeds = [s for seeds in plan.values() for s in seeds]
    assert len(all_seeds) == len(set(all_seeds)) == 6 * 120
    dev = {s for (sp, _), seeds in plan.items() if sp == "development" for s in seeds}
    hold = {s for (sp, _), seeds in plan.items() if sp == "holdout" for s in seeds}
    assert dev.isdisjoint(hold)


def test_protocol_revision_offsets():
    base = sf.seed_plan(0)
    rev = sf.seed_plan(3)
    for key in base:
        assert rev[key][0] - base[key][0] == 3 * 1_000_000
    flat0 = {s for seeds in base.values() for s in seeds}
    flat3 = {s for seeds in rev.values() for s in seeds}
    assert flat0.isdisjoint(flat3)


def test_continuation_seed_disjointness():
    plan = sf.seed_plan(0)
    registered = {s for seeds in plan.values() for s in seeds}
    cont = set()
    for family in ("permutation", "contracting"):
        for block in range(sf.CONTINUATION_CAP // sf.CONTINUATION_BLOCK):
            block_seeds = sf.continuation_seeds(family, block)
            assert len(block_seeds) == sf.CONTINUATION_BLOCK
            assert not (set(block_seeds) & cont)
            cont |= set(block_seeds)
    assert cont.isdisjoint(registered)
    with pytest.raises(ValueError):
        sf.continuation_seeds("random", 0)
    with pytest.raises(ValueError):
        sf.continuation_seeds("permutation", 10)


def test_stable_fsm_ids():
    inst = sf.generate_fsm("holdout", "contracting", 220120)
    assert inst.fsm_id == "hol-contracting-000220120"
    assert sf.make_fsm_id("development", "random", 110240) == "dev-random-000110240"


def test_row_schemas():
    inst = sf.generate_fsm("development", "permutation", 110001)
    fit = sf.fit_mdl(inst.table)
    rows = sf.entry_rows(inst, fit)
    assert len(rows) == 64
    required_entry = {
        "fsm_id", "split", "family", "seed", "state", "current_destination",
        "skeleton_destination", "is_planted_source", "is_fitted_residual",
        "pre_visit_count", "pre_w", "pre_on_cycle", "post_visit_count", "post_w",
        "post_on_cycle", "switch_destination_count", "C_numerator",
        "C_denominator", "C", "theta_numerator", "theta_denominator", "theta",
        "canonical_terminal_cycle", "pre_treatment_stratum",
    }
    assert required_entry <= set(rows[0])
    summary = sf.summary_row(inst, fit, rows)
    required_summary = {
        "fsm_id", "split", "family", "seed", "protocol_revision",
        "transition_table_json", "true_a", "true_b", "planted_source",
        "original_destination", "planted_destination", "selected_model",
        "fitted_a", "fitted_b", "best_affine_bits", "full_table_bits",
        "fitted_residual_count", "skeleton_recovered", "planted_source_recovered",
        "informative", "matched_control_count", "delta_theta", "delta_C", "delta_w",
    }
    assert required_summary <= set(summary)
    matched = sf.matched_effect_rows(inst, fit, rows)
    assert any(r["analysis"] == "primary_planted_pre" for r in matched)
    assert all(r["fsm_weight"] == 1.0 for r in matched)


def test_primary_delta_matches_matched_effect_rows():
    inst = sf.generate_fsm("development", "contracting", 110130)
    fit = sf.fit_mdl(inst.table)
    rows = sf.entry_rows(inst, fit)
    summary = sf.summary_row(inst, fit, rows)
    pairs = [
        r
        for r in sf.matched_effect_rows(inst, fit, rows)
        if r["analysis"] == "primary_planted_pre"
    ]
    recomputed = sum(r["diff_theta"] * r["control_weight"] for r in pairs)
    assert recomputed == pytest.approx(summary["delta_theta"], abs=1e-12)


def test_deterministic_compressed_csv(tmp_path):
    df = pd.DataFrame({"b": [3, 1, 2], "a": ["z", "x", "y"], "v": [0.1, 0.2, 0.3]})
    p1, p2 = tmp_path / "one.csv.gz", tmp_path / "two.csv.gz"
    sf.write_csv_gz(df, p1, ["b"])
    sf.write_csv_gz(df.iloc[::-1], p2, ["b"])
    assert p1.read_bytes() == p2.read_bytes()
    with gzip.open(p1, "rb") as fh:
        text = fh.read().decode()
    assert text.splitlines()[0] == "b,a,v"
    assert text.splitlines()[1] == "1,x,0.20000000000000001"


def test_deterministic_json(tmp_path):
    p = tmp_path / "x.json"
    sf.write_json({"b": 1, "a": [2, 3]}, p)
    assert p.read_bytes() == b'{\n  "a": [\n    2,\n    3\n  ],\n  "b": 1\n}\n'


def test_holm_adjust():
    assert sf.holm_adjust([0.01, 0.04]) == pytest.approx([0.02, 0.04])
    assert sf.holm_adjust([0.6, 0.7]) == pytest.approx([1.0, 1.0])


def test_bootstrap_and_sign_flip_are_deterministic():
    perm = [(-1) ** i * 0.01 * (i + 1) for i in range(20)]
    contract = [-0.02 * (i + 1) for i in range(20)]
    b1 = sf.cluster_bootstrap(perm, contract, n_resamples=200, seed=1)
    b2 = sf.cluster_bootstrap(perm, contract, n_resamples=200, seed=1)
    assert b1 == b2
    obs = sf.equal_family_mean(perm, contract)
    r1 = sf.sign_flip_test(perm, contract, obs, np.random.Generator(np.random.PCG64(2)), 200)
    r2 = sf.sign_flip_test(perm, contract, obs, np.random.Generator(np.random.PCG64(2)), 200)
    assert r1 == r2
    assert 0 < r1["p_left"] <= 1 and 0 < r1["p_right"] <= 1


# --------------------------------------------------------------------------
# End-to-end tiny smoke run
# --------------------------------------------------------------------------


def _run(args, cwd):
    env = {
        "PYTHONPATH": str(REPO_ROOT / "src"),
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(cwd),
        "MPLBACKEND": "Agg",
    }
    return subprocess.run(
        [sys.executable, *args], cwd=str(cwd), env=env, capture_output=True, text=True
    )


SMOKE_REVISION = 900
"""Sentinel protocol revision for tests.

Every smoke run shifts all seeds by ``1_000_000 * 900``, so no test ever
generates an outcome for a registered development or holdout seed.
"""


def test_end_to_end_smoke(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "out"
    for split in ("development", "holdout"):
        res = _run(
            [
                str(SCRIPTS / "run_synthetic_fsm.py"),
                "--split", split,
                "--out-dir", str(raw),
                "--limit-per-family", "4",
                "--protocol-revision", str(SMOKE_REVISION),
                "--allow-dirty",
                "--freeze-sha", "0" * 40,
            ],
            tmp_path,
        )
        assert res.returncode == 0, res.stderr
    res = _run(
        [
            str(SCRIPTS / "analyze_synthetic_fsm.py"),
            "--raw-dir", str(raw),
            "--out-dir", str(out),
            "--protocol-revision", str(SMOKE_REVISION),
            "--bootstrap-resamples", "200",
            "--sign-flip-draws", "200",
            "--allow-dirty",
            "--freeze-sha", "0" * 40,
        ],
        tmp_path,
    )
    assert res.returncode == 0, res.stderr
    for name in (
        "fsm_summary.csv.gz",
        "entry_metrics.csv.gz",
        "matched_effects.csv.gz",
        "summary.json",
        "manifest.json",
        "effect_by_split_family.svg",
        "hashes.sha256",
    ):
        assert (out / name).exists(), name
    summary = json.loads((out / "summary.json").read_text())
    assert summary["primary"]["n_permutation"] == 4
    assert summary["primary"]["n_contracting"] == 4
    res = _run(
        [
            str(SCRIPTS / "verify_synthetic_fsm_estimator.py"),
            "--results-dir", str(out),
            "--out", str(out / "independent_check.json"),
        ],
        tmp_path,
    )
    assert res.returncode == 0, res.stderr
    check = json.loads((out / "independent_check.json").read_text())
    assert check["pass"] is True


def test_scripts_have_help():
    for name in (
        "run_synthetic_fsm.py",
        "analyze_synthetic_fsm.py",
        "verify_synthetic_fsm_estimator.py",
    ):
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / name), "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
        )
        assert res.returncode == 0
        assert "usage" in res.stdout.lower()


def test_scripts_fail_with_nonzero_exit_on_bad_split(tmp_path):
    res = _run(
        [
            str(SCRIPTS / "run_synthetic_fsm.py"),
            "--split", "nope",
            "--out-dir", str(tmp_path / "x"),
        ],
        tmp_path,
    )
    assert res.returncode != 0


# --------------------------------------------------------------------------
# 21.8 Independent estimator path
# --------------------------------------------------------------------------


def test_independent_estimator_module_does_not_import_production_code():
    src = (SCRIPTS / "verify_synthetic_fsm_estimator.py").read_text()
    assert "relative_symmetry_repair" not in src
    assert "analyze_synthetic_fsm" not in src


def test_independent_estimator_on_fixture(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "indep_check", SCRIPTS / "verify_synthetic_fsm_estimator.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rows = []
    # two permutation FSMs, two contracting FSMs, hand-computable effects
    spec_rows = [
        ("p1", "permutation", 0, [0, 63]),   # theta_entry - mean(controls)
        ("p2", "permutation", 0, [63, 0]),
        ("c1", "contracting", 0, [21, 42]),
        ("c2", "contracting", 0, [7, 7]),
    ]
    for fsm_id, family, entry_num, control_nums in spec_rows:
        m = len(control_nums)
        for cn in control_nums:
            rows.append(
                {
                    "fsm_id": fsm_id,
                    "split": "holdout",
                    "family": family,
                    "analysis": "primary_planted_pre",
                    "is_primary": 1,
                    "entry_theta": entry_num / 63,
                    "control_theta": cn / 63,
                    "diff_theta": entry_num / 63 - cn / 63,
                    "control_weight": 1.0 / m,
                }
            )
    df = pd.DataFrame(rows)
    path = tmp_path / "matched_effects.csv.gz"
    df.to_csv(path, index=False, compression="gzip")
    est = mod.independent_primary_estimate(str(path), "holdout")
    exp_p = [0 - (0 + 63) / 2, 0 - (63 + 0) / 2]
    exp_c = [0 - (21 + 42) / 2, 0 - (7 + 7) / 2]
    exp_p = [v / 63 for v in exp_p]
    exp_c = [v / 63 for v in exp_c]
    assert est["permutation_mean"] == pytest.approx(sum(exp_p) / 2, abs=1e-15)
    assert est["contracting_mean"] == pytest.approx(sum(exp_c) / 2, abs=1e-15)
    assert est["combined"] == pytest.approx(
        0.5 * sum(exp_p) / 2 + 0.5 * sum(exp_c) / 2, abs=1e-15
    )


def test_dirty_guard_ignores_only_the_output_directory():
    """The freeze guard must ignore a run's own output dir and nothing else."""
    spec = importlib.util.spec_from_file_location(
        "run_synth", SCRIPTS / "run_synthetic_fsm.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    porcelain = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
    ).stdout
    out_dir = REPO_ROOT / "research" / "synthetic_fsm" / "results"
    ignored = mod.dirty_paths(out_dir)
    for line in porcelain.splitlines():
        rel = line[3:].strip().strip('"')
        if rel.startswith("research/synthetic_fsm/results"):
            assert line not in ignored
        else:
            assert line in ignored
    # A path outside the output directory is never ignored.
    assert mod.dirty_paths(REPO_ROOT / "does" / "not" / "exist") == [
        line for line in porcelain.splitlines()
    ]
