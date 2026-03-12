# Paper Traceability Report

## Table Sources

| Paper Quantity | CSV Source | Notes |
|---|---|---|
| 1D/2D/3D stabilization tables | `results/stabilization_results.csv` + `results/stabilization_period_scores.csv` + `results/stabilization_candidates.csv` | Joint period/shift selector. |
| Shift-zero stabilization tables | `results/stabilization_shift_zero_results.csv` + `results/stabilization_shift_zero_period_scores.csv` | Dedicated fixed-shift-zero exports for manuscript-facing tables. |
| Baseline selector comparison | `results/baseline_selector_rule_level.csv` + `results/baseline_selector_summary.csv` + `results/baseline_selector_candidates.csv` | Candidate-level selector definitions are explicit in metadata sidecars. |
| LifeWiki named-rule survey | `outputs/lifewiki_survey.csv` and `outputs/lifewiki_survey_T400.csv` | Named-rule transitions checked directly. |
| 2D range-threshold survey counts | `outputs/survey_2d_rules_large.csv` | Content checks and metadata sidecar now both exist. |

## Validation Results

- `PASS` [stabilization] Found source file `results/stabilization_results.csv`.
- `PASS` [stabilization] Found source file `results/stabilization_period_scores.csv`.
- `PASS` [stabilization] Found source file `results/stabilization_candidates.csv`.
- `PASS` [stabilization] Found source file `results/stabilization_shift_zero_results.csv`.
- `PASS` [stabilization] Found source file `results/stabilization_shift_zero_period_scores.csv`.
- `PASS` [stabilization] Metadata present with selector `period_first_nml_joint_hybrid` and boundary `periodic`.
- `PASS` [stabilization] Selection rows, grouped period scores, and candidate flags are internally consistent.
- `WARN` [traceability] Shift-zero stabilization CSV for ECA-110 does not match the manuscript-facing sequence [7, 7, 7, 7, 7, 7]; actual sequence is [1, 7, 7, 7, 7, 7].
- `PASS` [baseline] Found source file `results/baseline_selector_rule_level.csv`.
- `PASS` [baseline] Found source file `results/baseline_selector_summary.csv`.
- `PASS` [baseline] Found source file `results/baseline_selector_candidates.csv`.
- `PASS` [baseline] Metadata present with 3 explicit selector variants.
- `PASS` [baseline] Summary rows reconcile exactly after restoring the missing `p=3` bucket.
- `PASS` [baseline] Rule-level winners match the saved candidate tables for all three selectors.
- `PASS` [lifewiki] Found source file `outputs/lifewiki_survey.csv`.
- `PASS` [lifewiki] Found source file `outputs/lifewiki_survey_T400.csv`.
- `PASS` [lifewiki] Both LifeWiki survey outputs contain all 106 named rules.
- `PASS` [lifewiki] Named-rule checks match manuscript-facing claims: Diamoeba 1→2, Fredkin 8, Serviettes 2→1.
- `PASS` [range_threshold] Range-threshold survey output supports the paper counts: 773 non-trivial rules and 172 with nonzero shift.
- `PASS` [range_threshold] Range-threshold survey CSV now has a metadata sidecar, so that paper count is metadata-validated as well as content-validated.

## Unresolved Gaps

- Exact LaTeX table parsing is not automated here; the validator checks the underlying CSV sources and derived counts instead.
