You are working in the `zitterbewegung/relative_symmetry_repair` repository.

Goal:
Integrate an ALIFE experiment suite into the existing codebase without breaking current workflows. Reuse the existing library and script structure as much as possible.

Important repo facts:
- The repo already has `scripts/`, `paper/`, `tests/`, and `src/relative_symmetry_repair/`.
- Core modules include `eca.py`, `ca2d.py`, `ca3d.py`, `repair.py`, `repair_nd.py`, `coding.py`, and `cli.py`.
- The existing CLI already exposes 1D / 2D / 3D analysis commands and uses `scan_relative_periodicity` / `scan_relative_periodicity_nd`.
- The N-dimensional repair objects already expose `nll_bits`, `nml_complexity`, and `nml_bits`.
- The repo already contains experiment-style scripts such as convergence, survey, persistent-defect, and counterexample utilities under `scripts/`.

Implement the following.

## 1. Add a small shared experiment utility layer

Create a new module, preferably `src/relative_symmetry_repair/experiment_suite.py`, with reusable helpers for:

- deterministic seed iteration
- period-first selection from an existing result frame:
  - for each period, minimize over shifts by `nml_bits`
  - then choose the period with minimal score
  - compute a runner-up margin in bits
- writing summary CSVs
- writing a small JSON manifest
- creating output directories safely
- optional caching / resume behavior

Do not duplicate selection logic across scripts.

## 2. Add the ALIFE experiment scripts under `scripts/`

Create these scripts.

### `scripts/alife_null_controls.py`
Run the specificity / null-controls panel.

Requirements:
- support 1D, 2D, and 3D representative rules
- for each original spacetime, create:
  - time-shuffled control
  - space-shuffled control
  - density-matched i.i.d. Bernoulli control
- compute:
  - selected period
  - selected shift
  - winner margin
  - defect rate
  - `nml_bits`
- save:
  - rule-level CSV
  - aggregated summary CSV
  - at least two publication-ready plots
  - optional decomposition PNGs for a small representative subset

### `scripts/alife_seed_stability.py`
Run multi-seed robustness on the representative panel.

Requirements:
- use the rule panel already emphasized in the manuscript:
  - 1D: ECA 30, 54, 110
  - 2D: Diamoeba, Maze with Mice, S24/B11, S11/B37, S37/B11
  - 3D: every named 3D rule already present, or at minimum diamoeba3d
- default to 10 seeds for the representative panel
- horizons should match the existing stabilization sweeps where possible
- output:
  - per-run CSV
  - per-rule summary CSV
  - stability metrics such as modal period frequency, number of transitions, mean/median margin, and defect-rate CV
  - one summary figure

### `scripts/alife_candidate_range_robustness.py`
Check whether enlarging the candidate search space changes the winner.

Requirements:
- compare at least three nested search ranges per dimension
- record:
  - whether selected period changes
  - whether selected shift changes
  - winner margin under each range
- produce a summary CSV and a concise plot

### `scripts/alife_lifewiki_horizon_sweep.py`
Run the named Life-like rule survey across multiple horizons.

Requirements:
- horizons default to something like `100, 200, 400, 800`
- 5 seeds by default
- save:
  - per-rule per-seed per-horizon CSV
  - transition summary CSV
  - final period-distribution CSV
  - one transition plot or heatmap

### `scripts/alife_eca_atlas.py`
Build a complete 1D ECA atlas.

Requirements:
- run all 256 ECA rules
- 5 seeds
- horizons `50, 100, 200, 400, 800`
- candidate range should match the existing 1D defaults unless overridden
- outputs:
  - per-run CSV
  - per-rule summary CSV
  - atlas figure(s) showing selected period class and stabilization behavior

### `scripts/alife_3d_survey.py`
Run the breadth-oriented 3D survey.

Requirements:
- iterate over every named 3D rule already defined in the codebase
- 5 seeds by default
- use the existing 3D defaults as the baseline search range
- outputs:
  - per-run CSV
  - per-rule summary CSV
  - one compact summary plot

### `scripts/alife_counterexample_stress.py`
Search for cases that would weaken over-strong claims.

Requirements:
- detect:
  - non-unique winners
  - very small margins
  - candidate-range instability
  - null-control false positives
  - suspicious repeated ties
- emit a machine-readable report and a human-readable markdown summary
- do not fabricate counterexamples; only report actual observed cases

### `scripts/alife_run_all.py`
A single orchestrator that runs the whole suite with reasonable defaults and resume support.

Requirements:
- flags to enable / disable individual experiment blocks
- write all outputs under `outputs/alife_2026/`
- create a top-level `results_manifest.json`

## 3. Add paper-facing summary helpers

Create a markdown report generator, ideally in the shared utility module or as a dedicated script, that reads the experiment CSVs and produces:

- `paper/alife_experiment_summary.md`
- `paper/alife_table_snippets.md`

These should contain compact tables and plain-language summaries that can be pasted into the manuscript.

## 4. Add lightweight CLI integration

Update `src/relative_symmetry_repair/cli.py` to expose a small number of non-invasive commands, such as:

- `alife-null-controls`
- `alife-seed-stability`
- `alife-run-all`

Keep current commands unchanged.

## 5. Add tests

Add smoke tests under `tests/` that:
- run tiny versions of the new experiment helpers on very small grids / horizons
- verify that summary CSVs are produced
- verify that period-first selection works correctly
- verify that the null controls preserve shape and binary dtype

Tests must be fast.

## 6. Update documentation

Update `README.md` with:
- a short section describing the ALIFE experiment suite
- example commands
- output directory layout

## 7. Implementation constraints

- Reuse existing simulation and repair functions instead of reimplementing them.
- Keep the code type-annotated where practical.
- Use `matplotlib`, not seaborn.
- Keep plots simple and publication-oriented.
- Avoid introducing heavyweight dependencies.
- Preserve existing APIs unless you have a strong reason to extend them.
- Prefer small pure helpers and composable functions.
- Make resume behavior deterministic and safe.

## 8. Output contract

At the end, the repo should be able to generate:
- experiment CSVs
- summary CSVs
- summary markdown for the paper
- publication-ready PNG figures
- a manifest file
- smoke-test coverage

Implement the code, tests, and README updates directly in the repository.
