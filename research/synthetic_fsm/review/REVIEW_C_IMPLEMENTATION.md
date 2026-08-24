# Review C — Implementation and Reproducibility

Independent adversarial review, 2026-08-23. The reviewer had read-only access to
the worktree and wrote scratch code outside the repository. It was asked to
audit optimised-vs-brute-force agreement, deterministic generation, artifact
completeness and map reconstruction, gzip/JSON/SVG determinism, the independent
estimator, full-suite regression and accepted-output protection, the hash
record, and manifest completeness.

## VERDICT: **PASS WITH CONCERNS**

Every substantive correctness and determinism claim survived hostile checking,
including a full independent reconstruction that agreed **exactly** (discrepancy
0.0, not merely small) and a byte-for-byte regeneration of every scientific
artifact. The concerns are custodial, not scientific: at review time the entire
results tree was untracked in git, and two manifest fields are incomplete.

---

## 1. Optimised vs brute-force agreement — VERIFIED

`tests/test_synthetic_fsm.py:33-77` defines the literal reference
implementations. `bf_C` (`:61-74`) is the literal double average from
PROTOCOL §6 — it materialises each edited table `f^{u->y}` and counts changed
terminal cycles over all `x`, accumulating in `Fraction`. `bf_w` (`:56-58`) is
exact `Fraction` too.

The reviewer did not take the docstring's word for independence. AST analysis of
every `bf_*` function body:

```
bf_orbit / bf_terminal_cycle / bf_visit_set / bf_w / bf_C / bf_theta
    external refs (sf.* or np.*): NONE
```

They touch only Python lists and `Fraction`. No path to
`sf.switch_destination_counts` (`src/relative_symmetry_repair/synthetic_fsm.py:256`).

Ran them: `59 passed, 40 deselected in 0.37s`.

**Mutation check** — proof the test is load-bearing, not decorative. Copied the
module to scratch, injected `+ (1 if u == 1 and n > 3 else 0)` into
`switch_destination_counts`, re-ran: **38 failed, 16 passed**. The test catches it.

Minor caveat: the `n=64` spot-check (`:183-194`) asserts `bf_w` and `bf_C` but
not `bf_theta`. Harmless — `theta = C/w` is implied — and the small-`n` test
(`:169-178`) does assert all three.

## 2. Deterministic generation — VERIFIED

- **Repeat calls**: 7 seeds spanning both splits and all three families, called
  twice each — table, skeleton, `true_a/true_b`, `u*`, `y*`, `skeleton_resamples`
  identical every time.
- **Seed fully determines the stream**: the reviewer re-derived the draws by hand
  from a fresh `np.random.Generator(PCG64(seed))` in the protocol's fixed order
  (`a`, `b`, repeat-while-ineligible, `u*`, `y*`), including an independent
  re-implementation of the eligibility stratification. **0 mismatches** against
  `generate_fsm` (`synthetic_fsm.py:457`) on all structured seeds tested.
- **Against the artifacts**: regenerated all **720** FSMs from seed alone in a
  fresh process and compared `transition_table_json`, `skeleton_table_json`,
  `planted_source`, `planted_destination`, `skeleton_resamples`.
  **0 mismatches / 720.**

All sampled seeds had `skeleton_resamples = 0`, so the resampling branch is
exercised by no registered seed — it is dead code in this run. That is a fact
about the seeds, not a defect.

## 3. Artifact completeness and map reconstruction — VERIFIED (max discrepancy exactly 0.0)

The reviewer wrote a standalone reconstructor importing nothing from the
project, reading the CSVs with `float_precision="round_trip"`, and exceeded the
brief: rather than sampling 60 FSMs it recomputed **all 720** from scratch —
orbits, visit counts, `on_cycle`, canonical terminal cycles (min-rotation),
cycle lengths, `s_f(u)` by **literal enumeration** of all 63 edited maps, `C`,
`theta`, pre-treatment strata, the full 4096-candidate MDL fit with its own
codelength and lexicographic tie-break, and per-FSM `delta_theta`.

| Quantity | Max discrepancy (all 720 FSMs, 46,080 rows) |
|---|---|
| `post_visit_count` | 0 |
| `pre_visit_count` | 0 |
| `post_on_cycle` / `pre_on_cycle` | 0 |
| `canonical_terminal_cycle` (string) | 0 mismatches |
| `post_cycle_length` | 0 |
| `switch_destination_count` | 0 |
| `C` | 0.0 |
| `theta` | 0.0 |
| `pre_treatment_stratum` | 0 mismatches |
| `selected_model` / `fitted_a,b` / residual set | 0 mismatches |
| `best_affine_bits` | 0.0 |
| `matched_control_count` | 0 mismatches |
| **`delta_theta`** | **0.0** |

**Map reconstruction, all 720:** `entry_metrics.current_destination` reproduces
`fsm_summary.transition_table_json` — **0 mismatches**. `skeleton_destination`
reproduces `skeleton_table_json` — **0 mismatches**.

**Exact-rational double average.** For a 72-FSM sample (12 per split × family
cell) the reviewer computed the literal
`C_f(u) = (1/63)·Σ_y (1/64)·Σ_x 1[cycle changed]` in `Fraction` for every one of
the 64 states — 4,608 exact values. Result: `C_literal == Fraction(vc·s, 64·63)`
and `theta_literal == Fraction(s, 63)` with **0 exact-rational mismatches**, and
`max|float(C_literal) − stored| = 0.0`. **The PROTOCOL §6.1 factorization is not
merely approximately right; it is exact.**

Structural invariants over all 46,080 rows: `0 < w ≤ 1`, `0 ≤ C ≤ w`,
`0 ≤ theta ≤ 1`, `C == vc·s/4032` bit-exact, `theta == s/63` bit-exact.

`matched_effects` internal consistency: `entry_theta − control_theta −
diff_theta` max residual **0.0**; same for `diff_C`, `diff_w`. `control_weight`
sums to 1 for all entry groups (0 violations); `entry_weight` sums to 1 per FSM
for both secondary analyses (0 violations — the "residual with no controls"
under-weighting edge case at `synthetic_fsm.py:800-825` never fires here).

## 4. Gzip / JSON / SVG determinism — VERIFIED

Gzip header bytes, all 9 `.csv.gz` (3 final + 6 raw), parsed with `struct`:

```
magic=8b1f CM=8 FLG=0x00 MTIME=0 XFL=2 OS=255 FNAME_bit=0 FEXTRA=0 FCOMMENT=0
```

`MTIME=0`; `FLG=0x00` (FNAME bit clear ⇒ no embedded filename); `OS=255`
(unknown, not host-dependent). Source: `synthetic_fsm.py:948`.

JSON: `summary.json`, `manifest.json`, `independent_check.json` and both
`run_meta_*.json` are **byte-identical** to
`json.dumps(obj, sort_keys=True, indent=2) + "\n"`.

`summary.json` volatile-field scan: regex over
`timestamp|generated_at|created|date|elapsed|runtime|wall|hostname|/Users/|/tmp/|20\d\d-\d\d-\d\d`
→ **zero hits**. Leaf-key scan for
`time|date|host|path|dir|platform|version|command|seconds` → **zero hits**.

SVG: the `<metadata>` block contains only `dc:type`, `dc:format` and
`dc:creator` = "Matplotlib v3.11.1". **No `<dc:date>`, no `Date` string**
(`analyze_synthetic_fsm.py:364` passes `metadata={"Date": None}`). The one
`2026` hit is a false positive — a coordinate `y="49.320264"`. `svg.hashsalt` is
fixed (`:35`); element ids are stable.

**Full clean regeneration.** The reviewer re-ran both split generators and the
analysis into scratch and byte-compared:

```
IDENTICAL  fsm_summary.csv.gz          IDENTICAL  raw/summary_development.csv.gz
IDENTICAL  entry_metrics.csv.gz        IDENTICAL  raw/entries_development.csv.gz
IDENTICAL  matched_effects.csv.gz      IDENTICAL  raw/matched_development.csv.gz
IDENTICAL  summary.json                IDENTICAL  raw/summary_holdout.csv.gz
IDENTICAL  effect_by_split_family.svg  IDENTICAL  raw/entries_holdout.csv.gz
IDENTICAL  hashes.sha256               IDENTICAL  raw/matched_holdout.csv.gz
```

Only `manifest.json` differed, in exactly two fields: the `--out-dir`/
`--allow-dirty` command string, and `runtimes_seconds.analysis`
(4.324 → 3.164). Both live in `manifest.json`, which PROTOCOL §12 explicitly
excludes from the scientific hash set. **PROTOCOL §12's byte-for-byte claim holds.**

## 5. Independent estimator — VERIFIED

`verify_synthetic_fsm_estimator.py` imports only
`argparse, hashlib, json, sys, pathlib, pandas` (`:24-30`). Grep for
`relative_symmetry_repair` and `analyze_synthetic_fsm` → **no hits**. It reads
with `float_precision="round_trip"` (`:42`).

Re-ran it: exit 0, output identical to the committed `independent_check.json`
modulo the `command` string.

**A third implementation** (different code again — `collections.defaultdict`
grouping over `itertuples`, `np.mean` per family):

```
mine:         perm 0.05259839914549211   contract 0.009639016897081416   Delta 0.031118708021286762
summary.json: perm 0.052598399145492074  contract 0.009639016897081416   Delta 0.031118708021286745
|diff|:            3.47e-17                   0.0                            1.73e-17
n = 120 / 120
```

**A fourth route**, straight from `fsm_summary.delta_theta` filtered on
`informative == 1`: `0.052598399145492074 / 0.009639016897081416 /
0.031118708021286745` — bit-identical to production. The residual ~3e-17 is
float summation-order noise.

The sign-flip RNG consumption order was verified against PROTOCOL §9.2 by
reading `analyze_synthetic_fsm.py:436-465`: splits `development→holdout`, blocks
`primary_theta → delta_C → delta_w → secondary_fitted_pre →
secondary_fitted_post`, and within `estimate_block` combined-then-permutation-
then-contracting (`:248-252`). Matches the frozen order exactly.

## 6. Full-suite regression and accepted-output protection — VERIFIED

```
610 passed in 52.50s
```

**610 passed, 0 failed, 0 skipped, 0 xfailed, 0 xpassed.** Baseline 511/0/0;
delta **+99**, and `--collect-only` on the new file collects **exactly 99**.
Nothing else moved. Pre-existing conditional `pytest.skip` guards live in
`test_comprehensive_bugs_round{3,4,6}.py`; none fired.

```
$ git diff --stat 598a774abaef70236f62a5df8f312632e6cb7caa HEAD -- paper poster _archive outputs
(empty)
```

**EMPTY. No accepted ALIFE artifact changed.** Complete changed-file list since
base: **8 files, all additions, zero modifications, zero deletions.**

## 7. `hashes.sha256` correctness — VERIFIED

All 8 lines recomputed independently; **all 8 match**. Both forms are recorded
for each of the three CSVs. The recorded values also agree with
`manifest.json.artifact_hashes`, and `independent_check.json.input_hashes`
agrees for the two files it consumed.

## 8. `manifest.json` completeness — PASS WITH CONCERNS

Present and correct: `repository`, `base_sha`, `freeze_sha`,
`protocol_revision`, `protocol_sha256`, `code_hashes` (5 files),
`result_parent_sha`, `python`, `packages`, `platform`, `bit_generator`,
`commands`, `generator_seeds` (720 total, verified equal to the registered
ranges), `resampling_seeds`, `row_counts` (720 / 46,080 / 44,876, all confirmed
against the CSVs), `informative_clusters`, `runtimes_seconds`,
`artifact_hashes`.

`code_hashes` was verified three ways — each of the five entries equals both the
working-tree file **and** the blob at freeze commit `b61e402`.

Gaps: see F2 and F4 below.

---

## Findings

### F1 — MEDIUM: the results tree was untracked at review time

At review time `git status --porcelain --untracked-files=all` showed all 17
result files as `??`, and `manifest.json.result_commit_sha` was the placeholder
string. Consequence: `hashes.sha256` and `manifest.json` were themselves
untracked, mutable and unsigned.

**Strongly mitigated** by the fact that the reviewer could regenerate every
scientific byte from the freeze-commit code plus registered seeds (§4). The
evidence is real; it was just not yet anchored to history.

**Fix: commit the results tree and record the commit SHA externally.**

> **Author response.** Resolved by the result commit, which is exactly the step
> this review preceded. The results tree, `hashes.sha256`, `manifest.json` and
> `independent_check.json` are all committed, and the result SHA is reported in
> `RUN_LOG.md` §14 and in the final report.

### F2 — LOW: generation runtimes discarded

`run_synthetic_fsm.py:260-281` — the `meta` dict omits the elapsed time computed
at `:186`/`:285`; only the analysis runtime reaches `manifest.json`.

> **Author response.** Accepted, not fixed in code. Changing
> `run_synthetic_fsm.py` after the holdout would break the byte-for-byte
> reproduction of every artifact for a purely non-scientific metadata field.
> The wall-clock figures are instead recorded in `RUN_LOG.md` §12 and
> `RESULTS.md` §18: development generation 1.6 s, holdout generation 1.6 s,
> analysis 4.3 s.

### F3 — LOW: three result files are outside the hash record

`hashes.sha256` covers 5 artifacts. `manifest.json` (correctly excluded per
PROTOCOL §12), `independent_check.json` and `hashes.sha256` itself are
uncovered. `independent_check.json` self-binds via its `input_hashes` field, so
this is largely cosmetic.

> **Author response.** Accepted. A supplementary, hand-written record
> `review/AUDIT_HASHES.sha256` now covers the three files the generated record
> cannot cover, without modifying post-holdout scientific code.

### F4 — LOW: manifest continuation-seed and development-informative gaps

`continuation_blocks` is `{development: 0, holdout: 0}` but the manifest never
names the revision-0 continuation bases (221000 / 222000);
`informative_clusters` is holdout-only.

> **Author response.** Accepted. Zero continuation blocks were used so no seed
> is unrecorded in fact. The bases are stated in PROTOCOL §4.2 and are now also
> stated explicitly in `RESULTS.md` §8, together with the development
> informative counts (120/120).

### F5 — INFO: worktree dirty at audit time, but the run was not

At audit time: ` M research/synthetic_fsm/RUN_LOG.md`,
`?? research/synthetic_fsm/RESULTS.md`,
`?? research/synthetic_fsm/review/CODEX_AUDIT.md` — write-up files being edited
concurrently with the audit. This does not contaminate the run: mtimes order it
cleanly (results 19:17:47–19:18:50, `CODEX_AUDIT.md` 19:22:53, `RESULTS.md`
19:26:10 — all write-up postdates the run). The reviewer re-verified at end of
session that all six scientific-code files are still bit-identical to their
freeze blobs, that `summary.json` still hashes to `f8d86d65…`, and that all 8
recorded hashes still match. The dirty guard also **fails closed**.

### F6 — INFO: `--allow-dirty` / `--limit-per-family` escape hatches are self-reported

The manifest's `commands` field is a bare `sys.argv` echo. The recorded commands
contain neither flag, and `run_meta_*.json` records `limit_per_family: 0`,
`continuation_blocks: 0`, `revision_note: ""`. Independently corroborated: the
full-size regeneration reproduced every byte, which is not consistent with a
truncated or tampered run.

### F7 — INFO (outside remit): the registered hypothesis is not confirmed and the sign is inverted

Both gates pass, so the null is diagnostic: the effect is significantly
positive, the opposite of the registered direction. `summary.json` records this
honestly — `FSM_H1_confirmed: false`, `family_signs_differ: false` (both
families positive). Nothing is hidden.

> **Author note.** This reviewer quoted the interval as `[0.0138, 0.0491]`,
> which does not match the committed value. The registered figure in
> `summary.json` is `[+0.009616174329122745, +0.053229401709838454]`; the
> reviewer appears to have run its own bootstrap rather than reading the frozen
> one. The committed value is authoritative and is what `RESULTS.md` reports.

---

## Reproductions run

```bash
# 1  brute force
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_synthetic_fsm.py -q \
  -k "bruteforce or exhaustive or canonical or bounds"     # 59 passed
# + AST independence proof of every bf_* body
# + mutation of switch_destination_counts in a scratch copy  -> 38 failed

# 2  determinism: repeat calls, hand-rolled PCG64 redraw, 720/720 vs CSV   -> 0 mismatches

# 3  full reconstruction, all 720 FSMs                                     -> max discrepancy 0.0
#    exact-Fraction double average, 72 FSMs, 4608 states                   -> 0 mismatches

# 4  gzip struct-unpack of 9 headers; JSON canonical round-trip; SVG metadata scan
#    full clean rerun of both splits + analysis, cmp against committed     -> all IDENTICAL

# 5  verify_synthetic_fsm_estimator.py                                     -> exit 0, agrees to 3.47e-17
#    + a third implementation, + a fourth route via fsm_summary            -> agree to 3.47e-17 / exactly

# 6  PYTHONPATH=src ./.venv/bin/python -m pytest tests/ -q                 -> 610 passed, 0 skipped, 0 xfailed
#    git diff --stat 598a774..HEAD -- paper poster _archive outputs        -> EMPTY

# 7  recomputed all 8 lines of hashes.sha256                               -> 8/8 match

# 8  manifest key audit + code_hashes vs worktree AND freeze blobs         -> 5/5 pristine, 0 missing keys
```

No repository file was modified by the reviewer.

**Bottom line (reviewer's words):** the implementation is correct and the
pipeline is genuinely deterministic — no numerical defect was found, and the
exact-rational check plus byte-identical regeneration are about as strong as
this class of evidence gets. The one thing standing between this and an
unqualified PASS is that none of it is committed.
