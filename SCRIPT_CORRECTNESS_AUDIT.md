# Script Correctness Audit

This report summarizes the scientific-correctness hardening performed for the
relative-periodic model-selection code and paper-facing experiment pipelines.

## What Was Tested

- Core orbit-class labeling on small hand-checkable 1D and N-D examples.
- Hamming-optimal projection, including explicit tie cases and brute-force
  enumeration of all orbit-constant templates on tiny instances.
- Defect count and defect rate on exact periodic, translated, pure, and tied
  orbit-class examples.
- Bernoulli NLL on exact, pure, and 50/50 orbit-class cases.
- Bernoulli NML complexity in three explicit modes:
  `exact`, `hybrid` (current practical selector), and `asymptotic`.
- Period-first selector behavior under:
  - fixed shift (`shift=0` only),
  - joint shift/period optimization,
  - exact vs asymptotic NML,
  - deterministic tie-breaking,
  - reversed candidate iteration order.
- Theorem-inspired invariants:
  - residual count equals the sum of per-class minority counts,
  - projection is Hamming-optimal,
  - monotonicity along velocity-matched divisibility chains,
  - explicit counterexamples when the velocity-matching condition fails.
- Experiment-pipeline consistency for:
  - stabilization analysis,
  - baseline selector comparison,
  - manuscript-facing LifeWiki and range-threshold survey outputs.

## Bugs and Inconsistencies Found

- `baseline_selector_summary.csv` could not reconcile to rule-level outputs
  because the script omitted the `p=3` bucket entirely.
- `baseline_selector_rule_level.csv` stored period choices but left many score
  columns empty for 1D and 3D runs, making cross-checking impossible.
- Selector definitions were ambiguous in code and outputs:
  `nml_bits` hid a hybrid exact/asymptotic mode, and result files did not
  record whether a run used joint shift optimization or `shift=0` only.
- Result-producing scripts did not save the candidate tables or grouped
  period scores needed to verify that reported winners and margins were
  actually computed from the scanned search space.
- Metadata sidecars for new experiment outputs were missing entirely.

## What Was Fixed

- Added explicit Bernoulli-NML scoring modes:
  `exact`, `hybrid`, and `asymptotic`.
- Threaded `nml_mode` through fitting, scanning, and period selection so score
  semantics are explicit and serializable.
- Added selector/metadata utilities for deterministic ranking, explicit
  tie-break recording, and JSON sidecar emission.
- Refactored stabilization and baseline experiment scripts to write:
  - main result tables,
  - candidate-level scan tables,
  - grouped period-score tables where applicable,
  - metadata sidecars describing selector type, score type, tie-break rule,
    period/shift ranges, seed, density, boundary condition, and grid size.
- Added detailed benchmark score-dump and paper-traceability validator scripts.
- Added exact small-case tests, brute-force selector validation, pipeline
  consistency tests, and benchmark regression tests.

## What Remains Uncertain

- The new dedicated shift-zero stabilization CSVs expose a manuscript-facing
  discrepancy: for ECA-110 at `T=50`, the audited fixed-shift-zero output is
  `p=1`, not `p=7`. This is now machine-visible and needs author review.
- Some paper tables are referenced through prose and filtering logic rather than
  through dedicated standalone export scripts. The validator documents those
  derivations instead of guessing.

## Strongly Verified After This Audit

- Orbit-class assignment and majority-vote projection on tiny exact cases.
- Hamming-optimality and minority-count invariants for the projection step.
- Exact-vs-asymptotic NML differences on short horizons and agreement on simple
  larger exact cases.
- Deterministic selector behavior under reordered candidate iteration.
- Internal consistency of saved experiment outputs once candidate tables and
  grouped period scores are available.
- The regenerated paper-facing artifacts pass the new validator in
  `scripts/validate_results_against_paper.py`.
- The full automated test suite passes: `94 passed`.

## Regenerated Outputs

The following result files were regenerated because the audited pipelines now
emit candidate tables, grouped period scores, and metadata sidecars:

- `results/stabilization_results.csv`
- `results/stabilization_period_scores.csv`
- `results/stabilization_candidates.csv`
- `results/stabilization_shift_zero_results.csv`
- `results/stabilization_shift_zero_period_scores.csv`
- `results/stabilization_results.csv.metadata.json`
- `results/stabilization_period_scores.csv.metadata.json`
- `results/stabilization_candidates.csv.metadata.json`
- `results/stabilization_shift_zero_results.csv.metadata.json`
- `results/stabilization_shift_zero_period_scores.csv.metadata.json`
- `results/baseline_selector_rule_level.csv`
- `results/baseline_selector_summary.csv`
- `results/baseline_selector_candidates.csv`
- `results/baseline_selector_rule_level.csv.metadata.json`
- `results/baseline_selector_summary.csv.metadata.json`
- `results/baseline_selector_candidates.csv.metadata.json`
- `results/paper_traceability_report.md`
- `outputs/survey_2d_rules_large.csv.metadata.json`
- `results/selector_score_dumps/eca54_T200.csv`
- `results/selector_score_dumps/eca110_T200.csv`
- `results/selector_score_dumps/fredkin_T100.csv`
- `results/selector_score_dumps/diamoeba_T100.csv`
- `results/selector_score_dumps/diamoeba_T400.csv`
- `results/selector_score_dumps/serviettes_T100.csv`
- `results/selector_score_dumps/serviettes_T400.csv`
- matching `.metadata.json` sidecars for each selector score dump
- updated stabilization figures in `figures/` because `experiments/stabilization_analysis.py`
  was rerun to regenerate the audited stabilization outputs

## Still Needs Author Verification

- Whether the manuscript should describe the practical default selector as
  `hybrid` NML, `exact` NML, or `asymptotic` NML in each section. The code now
  distinguishes them, but paper wording still needs author sign-off.
- Whether the manuscript’s shift-zero ECA-110 table should be corrected to
  reflect the audited fixed-shift-zero result sequence `[1, 7, 7, 7, 7, 7]`.
