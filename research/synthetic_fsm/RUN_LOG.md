# RUN LOG — synthetic FSM residual/leverage

Chronological. Nothing here is rewritten to make the run look cleaner than it
was.

All times are 2026-08-23, America/Chicago.

---

## 1. Primary-worktree protection check

The session's working directory `/Users/r2q2/Projects/ishtar/fsm-winnower` was
an **empty, non-git directory**. The only local clone of
`zitterbewegung/Winnower` at the audited base is
`/Users/r2q2/Documents/GitHub/Winnower`. Recorded before touching anything:

```console
$ git -C /Users/r2q2/Documents/GitHub/Winnower rev-parse --show-toplevel
/Users/r2q2/Documents/GitHub/Winnower
$ git -C /Users/r2q2/Documents/GitHub/Winnower rev-parse HEAD
598a774abaef70236f62a5df8f312632e6cb7caa
$ git -C /Users/r2q2/Documents/GitHub/Winnower status --short --branch
## main...origin/main
$ git -C /Users/r2q2/Documents/GitHub/Winnower diff --stat
(empty)
$ git -C /Users/r2q2/Documents/GitHub/Winnower ls-files --others --exclude-standard
(empty)
$ git -C /Users/r2q2/Documents/GitHub/Winnower remote -v
origin	https://github.com/zitterbewegung/Winnower.git (fetch)
origin	https://github.com/zitterbewegung/Winnower.git (push)
```

The primary worktree was clean at the audited base and was **never modified**.
It was re-checked after worktree creation and remained `## main...origin/main`
with an empty status.

Other local clones exist (`/Users/r2q2/Documents/Projects/Winnower` on branch
`NCA`, ahead 11, with untracked `.claude/`; several `aconsapart/ruler` clones).
None were modified.

## 2. Recovery audit

```console
$ git -C <primary> fetch --all --prune
$ git -C <primary> worktree list --porcelain
$ git -C <primary> for-each-ref --sort=-committerdate \
    --format='%(committerdate:iso8601) %(objectname) %(refname)'
$ git -C <primary> reflog --all --since='2026-08-23 00:00:00'
$ git -C <primary> log --all --since='2026-08-20 00:00:00' --oneline --decorate --name-only
$ git -C <primary> fsck --full --no-reflogs --unreachable
$ git -C <primary> stash list
$ git -C <primary> grep -n -i -E 'synthetic_fsm|finite[- ]state machine|functional graph|random mapping|attractor[- ]switch'
$ find /Users/r2q2 -maxdepth 6 -type d -name 'relative_symmetry_repair'
$ find /Users/r2q2/Documents/GitHub -maxdepth 3 -type d -name .git
```

Findings:

- `origin/main` and `main` are both `598a774abaef70236f62a5df8f312632e6cb7caa`
  after fetch. `research/synthetic-fsm` did not exist locally or on the remote.
- Five unreachable commits exist (review-site deploys and a causal-control
  preflight). None of their trees contain any path matching
  `fsm|finite_state|functional_graph`.
- Stash list empty. `git grep` over tracked files found no FSM implementation.
- One pre-existing worktree,
  `.../worktrees/synthetic-fsm-residual-leverage-v1`, is checked out on branch
  `research/synthetic-fsm-residual-leverage-v1-20260823` whose tip is still the
  base `598a774`. It contains an **untracked, outcome-free protocol packet**
  (`research/synthetic_fsm_residual_leverage_v1/`, 7 markdown/JSON files):
  `README.md`, `ARCHAEOLOGY.md`, `PROTOCOL_FROZEN.md`, `CLAIM_THRESHOLDS.md`,
  `PREFREEZE_REVIEW.md`, `config.json`, `cohort_manifest.json`.
  **No implementation code, no test, no run, no result, no holdout outcome.**
  Its design is different from this protocol (block-structured generators,
  SHA-256 rank selection instead of a seeded RNG, a system-level two-sided mean
  test, equivalence margins). It was read read-only and **not modified**.
- Two adjacent completed/frozen studies were located in `aconsapart/ruler` and
  read read-only:
  `research/three-outcome/finite_state_systems` (completed at `512ee425`) and
  `research/fsm-local-disagreement-relabel-v2-20260823` (frozen at `6faca214`).
  Both are recorded in `PRIOR_ART.md` (items 8 and 9). The first is decisive
  for framing: it already reports an exact-zero incremental effect for a
  transition-exception codelength on finite maps.

### Recovery conclusion

No committed synthetic-FSM implementation, result branch, result commit or
result artifact exists in `zitterbewegung/Winnower`. No registered holdout
outcome was ever generated. Therefore **`protocol_revision = 0` and the
registered revision-0 holdout seeds remain valid.** Nothing was recomputed that
could have been recovered; there was nothing to recover.

## 3. Selected base, branch and worktree

```console
$ git -C /Users/r2q2/Documents/GitHub/Winnower worktree add \
    -b research/synthetic-fsm /Users/r2q2/Projects/ishtar/fsm-winnower \
    598a774abaef70236f62a5df8f312632e6cb7caa
Preparing worktree (new branch 'research/synthetic-fsm')
HEAD is now at 598a774 Create uv.lock
```

Verified immediately afterwards:

```console
$ pwd
/Users/r2q2/Projects/ishtar/fsm-winnower
$ git rev-parse --abbrev-ref HEAD
research/synthetic-fsm
$ git rev-parse HEAD
598a774abaef70236f62a5df8f312632e6cb7caa
$ git status --short --branch
## research/synthetic-fsm
```

**Documented deviation from the suggested layout.** The prompt suggested the
sibling path `../Winnower-synthetic-fsm`. The dedicated worktree was instead
created at the session's own empty working directory
`/Users/r2q2/Projects/ishtar/fsm-winnower`, which existed and was empty
specifically for this task. The branch name is the preferred
`research/synthetic-fsm`. No collision rule was triggered: neither the branch
nor a conflicting worktree existed.

Every edit, test, run, plot, commit and push below happened from this
dedicated worktree.

## 4. Environment

A dedicated `.venv` was created **inside the research worktree** (already
git-ignored) so that no other checkout's environment was mutated. Package
versions were pinned to match the primary clone's environment exactly.

```console
$ uv venv --python 3.12 .venv
$ uv pip install --python ./.venv/bin/python numpy==2.5.2 pandas==3.0.5 \
    scipy==1.18.0 matplotlib==3.11.1 numba==0.67.0 pytest==9.1.1 lz4 typer
$ ./.venv/bin/python -V
Python 3.12.13
```

## 5. Clean baseline (before any FSM code)

```console
$ PYTHONPATH=src ./.venv/bin/python -m pytest tests/ -q
511 passed in 95.60s (0:01:35)
```

- base SHA: `598a774abaef70236f62a5df8f312632e6cb7caa`
- Python 3.12.13; numpy 2.5.2, pandas 3.0.5, scipy 1.18.0, matplotlib 3.11.1,
  numba 0.67.0, pytest 9.1.1; uv 0.12.1; macOS Darwin 25.6.0 (arm64)
- passed 511, failed 0, skipped 0, xfailed 0, xpassed 0
- wall clock 95.60 s (97 s including process startup)
- worktree clean after the run (`git status --short` empty)

No unexpected baseline failure occurred; the historical count was not assumed.

## 6. Prior-art audit (before hypothesis freeze)

Performed before `PROTOCOL.md` was written. Queries, sources, access
limitations and the per-source overlap table are in `PRIOR_ART.md`. Two threats
to novelty were recorded and are carried into `RESULTS.md`: Zenil et al.'s
algorithmic-information perturbation analysis, and the sibling
`research/three-outcome/finite_state_systems` study whose reported
`Delta_R = 0`, `Delta_R:L = 0`, `Delta_joint = 0` (each `[0, 0]`) anticipates a
null here.

## 7. Implementation and correctness tests

Added:

- `src/relative_symmetry_repair/synthetic_fsm.py`
- `scripts/research/run_synthetic_fsm.py`
- `scripts/research/analyze_synthetic_fsm.py`
- `scripts/research/verify_synthetic_fsm_estimator.py`
- `tests/test_synthetic_fsm.py`

```console
$ PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_synthetic_fsm.py -q
96 passed in 21.02s
```

No skip, no xfail. The brute-force reference in the test file is written from
the literal double-average definition, uses exact `Fraction` arithmetic, and
never calls the optimised cycle-switch routine.

### 7.1 Disclosed near-miss: smoke test initially touched registered holdout seeds

The first version of the end-to-end smoke test ran
`run_synthetic_fsm.py --split holdout --limit-per-family 4` at
`protocol_revision 0`, which **generated** rows for 12 registered holdout seeds
(220000–220003, 220120–220123, 220240–220243) into a pytest `tmp_path`, and
computed a `summary.json` over 4+4 FSMs inside that temp directory.

The test asserted only the returncode, the presence of the artifact filenames,
`n_permutation == 4`, `n_contracting == 4`, and `independent_check["pass"] is
True`. Subprocess stdout was captured and never printed, so **no holdout effect
estimate, gate value or p-value entered the operator's view**, and no design
choice was made after it. The temporary directory was discarded by pytest.

The test was immediately hardened to run at sentinel `protocol_revision = 900`
(all seeds shifted by 900,000,000), so no test can ever generate an outcome for
a registered seed again. Recorded here in full rather than repaired silently.
This is disclosed again in `RESULTS.md` under limitations. The registered study
proceeds at `protocol_revision = 0` because no registered holdout *statistic*
was observed and no frozen choice was influenced.

### 7.2 Pre-freeze pipeline validation on a non-registered cohort

To validate the full pipeline at full size without touching registered seeds,
both splits were generated at sentinel `protocol_revision = 900` into the
session scratchpad (outside the repository) and analysed:

```console
$ PYTHONPATH=src ./.venv/bin/python scripts/research/run_synthetic_fsm.py \
    --split development --out-dir $SCRATCH/prefreeze/raw \
    --protocol-revision 900 --allow-dirty --jobs 8
development: 360 FSMs, informative={'permutation': 120, 'contracting': 120}, 1.8s
$ ... --split holdout --freeze-sha 0000...0000 ...
holdout: 360 FSMs, informative={'permutation': 120, 'contracting': 120}, 1.8s
$ PYTHONPATH=src ./.venv/bin/python scripts/research/analyze_synthetic_fsm.py \
    --raw-dir $SCRATCH/prefreeze/raw --out-dir $SCRATCH/prefreeze/out \
    --protocol-revision 900 --allow-dirty
```

This exercised every gate, the bootstrap, the sign-flip test, the plot, the
manifest and the hash record. Determinism was confirmed by re-running both the
generator and the analyser into fresh directories and comparing SHA-256 for all
six scientific artifacts (all identical), and the independent estimator agreed
to `< 3e-17`.

**These sentinel-cohort numbers are not the registered result and are not used
for any scientific claim.** They were produced before the freeze commit; the
frozen design was not altered afterwards.

## 8. First freeze commit

```console
$ git add research/synthetic_fsm/PRIOR_ART.md research/synthetic_fsm/PROTOCOL.md \
    research/synthetic_fsm/RUN_LOG.md scripts/research \
    src/relative_symmetry_repair/synthetic_fsm.py tests/test_synthetic_fsm.py
$ git commit -F - <<'MSG'
Freeze synthetic FSM residual-leverage protocol
...
MSG
```

Full repository suite immediately before this commit:

```console
$ PYTHONPATH=src ./.venv/bin/python -m pytest tests/ -q
607 passed in 83.42s (0:01:23)
```

(511 baseline + 96 new; no skip, no xfail.)  Protected trees confirmed
unchanged:

```console
$ git status --porcelain -- paper poster _archive outputs/alife_2026
(empty)
```

**First freeze SHA: `100d4a1413c1fa901677aafd0b3b3906f240a835`.**

## 9. Pre-holdout implementation bug and second freeze commit

Registered development was then run against the first freeze SHA and succeeded:

```console
$ PYTHONPATH=src ./.venv/bin/python scripts/research/run_synthetic_fsm.py \
    --split development --out-dir research/synthetic_fsm/results/raw \
    --freeze-sha 100d4a1413c1fa901677aafd0b3b3906f240a835 --jobs 8
development: 360 FSMs, informative={'permutation': 120, 'contracting': 120}, 2.0s
```

**Bug found (before any holdout outcome).** The clean-worktree guard used a
bare `git status --porcelain` check, so the run's *own* freshly written output
directory made the tree dirty and the guard would have refused the holdout run
that immediately follows the development run. The guard was therefore
unusable exactly where it mattered. A second, latent defect in the same helper:
`_git()` applied `str.strip()` to the whole porcelain output, so the first
status line lost its leading status column.

**Fix.** `dirty_paths(ignore_dir)` now reads porcelain lines without stripping
(new `_porcelain_lines()`) and excludes only entries under the run's declared
output directory; every other modified or untracked path still trips the guard.
The same guard was added to `analyze_synthetic_fsm.py`, whose `--allow-dirty`
flag had previously been inert. A new test,
`test_dirty_guard_ignores_only_the_output_directory`, checks both halves of the
behaviour against live `git status` output.

This fix touches only a run-time guard. It changes no generator, codelength,
estimand, matching, weighting, statistic or gate threshold.

Correctness tests rerun after the fix:

```console
$ PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_synthetic_fsm.py -q
97 passed in 19.54s
```

The stale development artifacts produced under the first freeze were **deleted,
not reused**, and development was regenerated against the second freeze SHA.
No holdout outcome had been generated at any point in this section.


## 10. Second pre-holdout bug and third (final) freeze commit

Development was regenerated against the second freeze SHA and then *validated*
(schemas, row counts, bounds, exactness, model recovery). The exactness check
`theta == theta_numerator / 63` **failed for 12,417 of 23,040 entry rows**.

**Diagnosis.** The written bytes were exact: `write_csv_gz` emits
`0.015873015873015872` for `1/63`. The loss was on the **read** side. pandas'
default `read_csv(float_precision="high")` uses a fast, inexact float parser
and returned `0.0158730158730158` (a few ULP low). Because
`analyze_synthetic_fsm.py` re-reads the per-split raw CSVs to build the
committed artifacts, and `verify_synthetic_fsm_estimator.py` re-reads
`matched_effects.csv.gz`, every downstream number was being derived from
slightly degraded values.

**Fix.** All three readers now pass `float_precision="round_trip"`
(`synthetic_fsm.read_csv_gz`, `analyze_synthetic_fsm.main`,
`verify_synthetic_fsm_estimator.independent_primary_estimate`). A new test,
`test_written_csv_floats_round_trip_exactly`, asserts bit-identical round trip
for `theta`, `C`, `post_w`, `pre_w`, asserts the integer-derived identities
after the round trip, and explicitly demonstrates that the default parser would
*not* have been exact.

This fix changes no generator, codelength, estimand, matching, weighting,
statistic or gate threshold. It was found **before any holdout outcome was
generated**; the development artifacts from the second freeze were deleted, not
reused.

```console
$ PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_synthetic_fsm.py -q
98 passed in 18.90s
```

## 11. Third pre-holdout bug and fourth (final) freeze commit

With the exact-read fix in place, development was regenerated against the third
freeze SHA and fully validated:

```console
$ PYTHONPATH=src ./.venv/bin/python scripts/research/run_synthetic_fsm.py \
    --split development --out-dir research/synthetic_fsm/results/raw \
    --freeze-sha 37c0b8d132b26f13f9e85b28d305e3327afdbf31 --jobs 8
development: 360 FSMs, informative={'permutation': 120, 'contracting': 120}, 1.8s
```

Validation (development, diagnostic only): 360 summary rows, 23,040 entry rows,
22,321 matched rows; all bounds hold; every integer identity
(`theta == theta_numerator/63`, `C == C_numerator/(64*63)`,
`post_w == post_visit_count/64`, `C_numerator == visit_count * switch_count`)
holds **bit-exactly**; skeleton recovery 1.000000, pooled precision 1.000000,
pooled recall 1.000000 (TP 240, FP 0, FN 0); development random-map full-table
rate 1.0; fitted residual count 1 for all 240 structured FSMs; 120/120
informative in each structured family; matched-control counts min 1, median 31,
max 63.

**Bug found (still before any holdout outcome).** The holdout run then failed:

```console
ERROR: worktree is dirty outside the output directory; commit or stash before running:
  ?? research/synthetic_fsm/results/
```

`git status --porcelain` collapses an untracked tree to its top-most directory,
so the output directory `research/synthetic_fsm/results/raw` was reported as
its new parent `research/synthetic_fsm/results/` and never matched the ignore
path. The guard was still unusable.

**Fix.** `_porcelain_lines()` now passes `--untracked-files=all` in both
scripts, so no untracked path is collapsed. Two tests cover it:
`test_dirty_guard_ignores_only_the_output_directory` (unchanged semantics,
updated to the same flag) and a new
`test_dirty_guard_sees_through_collapsed_untracked_directories`.

Again this touches only a run-time guard: no generator, codelength, estimand,
matching, weighting, statistic or gate threshold changed. The development
artifacts from the third freeze were deleted, not reused.

```console
$ PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_synthetic_fsm.py -q
99 passed in 14.53s
```
