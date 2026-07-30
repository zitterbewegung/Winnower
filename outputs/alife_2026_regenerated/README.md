# Regenerated outputs — current code, 2026-07-30

`outputs/alife_2026/` holds the numbers the **accepted ALIFE 2026 paper** was
written from, and must keep reproducing it. This directory holds what the
**current code** produces, so the two can be compared without either being
lost.

Only files that actually changed are here. Anything absent regenerated
byte-identically and can be read straight from `outputs/alife_2026/`.

Produced by:

```bash
PYTHONPATH=src python scripts/alife/alife_run_all.py \
    --output-root outputs/alife_2026 --paper-dir paper --no-resume --workers 0
```

## Summary: the delta is two tables

| verdict | files | meaning |
|---|---|---|
| **identical** | 10 CSVs | current code reproduces the accepted numbers exactly |
| **noise only** | 3 CSVs | differ by ≤ 2.6e-13 relative — float round-trip, not a result change |
| **material** | 4 CSVs | genuinely different: `null_controls`, `seed_stability` |

Reproduced exactly, byte for byte, including the complete 6400-row ECA atlas:

```
eca_atlas/eca_atlas_runs.csv             eca_atlas/eca_atlas_summary.csv
survey_3d/alife_3d_survey_runs.csv       survey_3d/alife_3d_survey_summary.csv
ground_truth/ground_truth_runs.csv       ground_truth/ground_truth_summary.csv
mask_structure/mask_structure_runs.csv   mask_structure/mask_structure_summary.csv
candidate_range_robustness/candidate_range_robustness_summary.csv
lifewiki_horizon_sweep/lifewiki_horizon_final_period_distribution.csv
```

## The material differences, and why

`null_controls_rule_level.csv` and `seed_stability_runs.csv` were last
recomputed on **2026-03-22**. Every later re-run skipped them, because the
suite resumes by default and their keys were already present — so they alone
predate the 3D initial-density fix of **2026-04-02**, while every other table
was refreshed on 04-05. (That silent-skip is fixed: runs now print a resume
report and `make data-fresh` forces a full recompute. See `REPRODUCING.md`.)

What changed as a result:

- **3D initial densities.** The accepted rows ran every 3D rule at density
  0.5; the current code uses the tuned per-rule values
  (`3d-life` 0.2, `clouds` 0.6, `crystal` 0.1, `diamoeba3d` 0.5). This moves
  the 3D rows and flips `crystal`'s original from period 1 to period 2.
- **`selected_complexity`** is ~6.8–7.5% higher on rows whose fit is otherwise
  unchanged — four scoring commits, including "Fix all 12 documented bugs",
  landed after 2026-03-22. `selected_nll_bits` is unchanged on 36 of 48
  null-control rows, i.e. simulation and fitting reproduce exactly and only
  the complexity term moved.
- **`control_seed`** semantics changed: `original` now records no control
  seed, and each control records its own. The accepted rows were offset by
  one slot.
- **`seed_stability_runs.csv`** grew from 210 to 680 rows: the sweep's scope
  widened after the accepted file was written, and resume never backfilled it.
  On the 210 shared keys the *selections* are stable — only NML/complexity
  values move, on ~20% of rows.

### One divergence worth knowing about

In the regenerated tree, `crystal`'s **space-shuffled control selects period
2**. Every control run in the accepted data selects period 1, which is what
the paper states, and that statement remains true of the accepted numbers.
This is a consequence of the density fix (crystal now starts at 0.1 rather
than 0.5) and is recorded here rather than in the paper.

## Noise-only files

`candidate_range_robustness_runs.csv` (worst 1.7e-14),
`lifewiki_horizon_runs.csv` (2.6e-13) and
`lifewiki_horizon_transition_summary.csv` (2.0e-16) differ only in the last
bits of some floats. This comes from resume re-serialising a loaded table
rather than from any recomputation — the values are identical to double
precision. They are included for completeness, not because anything changed.

## Manifests, figures and paper reports

`manifest.json` files and PNGs differ in every suite because they embed
runtimes and regeneration timestamps. `paper/alife_experiment_summary.md` and
`paper/alife_table_snippets.md` are the suite-generated report files, included
here so the accepted copies in `paper/` stay untouched.

**Nothing in this directory feeds the paper, the review site, or the
in-browser demo.** All three read `outputs/alife_2026/`.
