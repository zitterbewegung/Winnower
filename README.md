# Winnower: Relative-Periodic Decomposition for Cellular Automata

[![Tests](https://img.shields.io/badge/tests-543%20passing-brightgreen)]()

This algorithm fits relative-periodic backgrounds to cellular automaton spacetimes and analyzes the structured residual masks that remain. Uses Normalized Maximum Likelihood (NML) for principled model selection across shift and period candidates.

**Paper:** *Winnower: A Fast Tool for Splitting Cellular Automaton Spacetimes into a Periodic Background and a Residual Mask* — see `paper/paper_alife2026.pdf` and the [reviewer site](https://zitterbewegung.github.io/Winnower/). Accepted at ALIFE 2026.

## Quick start

```bash
pip install -e .

# Analyze a 1D elementary CA
python -m relative_symmetry_repair analyze --rule 110

# Analyze a 2D Life-like rule
python -m relative_symmetry_repair analyze2d --rule life

# Analyze a 3D rule
python -m relative_symmetry_repair analyze3d --rule diamoeba3d
```

## Reproduce paper results

```bash
make data-fresh    # recompute every table from scratch (this is the one you want)
make figures       # regenerate figures
make test          # run the suite
```

> **`make data` resumes; `make data-fresh` does not.**
> The suite reuses any row already present in the output CSVs. That is right
> for continuing an interrupted sweep, and wrong for verifying reproducibility:
> on a fresh clone `outputs/alife_2026/` arrives populated from git, so
> `make data` completes successfully having recomputed almost nothing. Every
> run now ends with a **resume report** naming any sub-suite that recomputed
> nothing, and the same breakdown is stored under `resume_summary` in
> `results_manifest.json`.

The two expensive sweeps parallelise across independent `(rule, seed)` units:

```bash
python scripts/alife/alife_run_all.py --workers 0    # 0 = CPU count - 2
```

Results are identical to a serial run, not merely equivalent — `Executor.map`
yields in submission order and the result tables are key-sorted on flush. On an
18-core machine this takes the full regeneration from hours to minutes.

See [REPRODUCING.md](REPRODUCING.md) for the full pipeline.

### Two output trees

| directory | contents |
|---|---|
| `outputs/alife_2026/` | the numbers the **accepted paper** was written from — the paper, review site and demo all read these |
| `outputs/alife_2026_regenerated/` | what **current code** produces, for the files where that differs, with a README explaining each difference |

They diverge in exactly two tables (`null_controls`, `seed_stability`), which
were last recomputed on 2026-03-22 and were skipped by every later resumed run,
leaving them older than a 3D initial-density fix. Everything else — including
the complete 6400-row ECA atlas — regenerates byte-identically. See
`outputs/alife_2026_regenerated/README.md`.

## Reviewer / evaluation interface


This hosted version additionally includes a **live in-browser reproduction**
(`reproduce.html`): WebAssembly Python (Pyodide) runs the actual
`relative_symmetry_repair` pipeline — simulate → scan candidates →
Bernoulli-NML selection — for any ECA rule, any 2D B/S rulestring, arbitrary
3D birth/survive count sets (e.g. `B5-7,9/S4,6-8`, non-contiguous allowed), or
the paper's representative 2D/3D rules, and compares the result against the
committed row of `eca_atlas_runs.csv` / `seed_stability_runs.csv`, column by
column.

Results are inspectable interactively: full spacetime diagrams in 1D, frame
scrubbing plus a rotatable 3D world-tube view of the residual mask in 2D, and
fully rotatable linked voxel views in 3D. The page also **reads back what the
selected template means** — which kind of domain won, what the margin is worth,
and what the defect mask did over time. Every threshold and classification
behind that comes from `relative_symmetry_repair.reading` in Python, against
the same constants `experiment_core` uses for the paper's own tables, so the
page cannot drift from the pipeline.

A **rule search** panel screens a rule family for rules that still sustain
activity at the horizon (each at its own best initial density), runs the real
selector on the survivors, and ranks them by defect rate.

The browser code path (numba stubbed, vectorized simulator kernels) is verified
against the committed CSVs by:

```bash
make verify-webdemo    # or: python scripts/verify_webdemo_bootstrap.py --block-numba
```

```bash
# Just open the committed page (no server, no dependencies needed):
open review_site/index.html          # macOS
xdg-open review_site/index.html      # Linux

# Rebuild it from the current outputs:
make review

# Build a portable single-file version (figures embedded, ~14 MB):
python scripts/build_review_site.py --embed-images
```

### Hosting

Published via GitHub Pages from the `gh-pages` branch at
`https://zitterbewegung.github.io/Winnower/`.

## Project structure

```
src/relative_symmetry_repair/   Core library
  eca.py, ca2d.py, ca3d.py      CA simulators (1D, 2D, 3D)
  repair.py, repair_nd.py       Relative-periodic background fitting
  coding.py                     NML scoring, codelength metrics
  selection.py                  Period-first model selection
  experiment_core.py            Cases, sweeps, resume tables, parallel units
  experiment_suite.py           The ALIFE experiment suite
  reading.py                    Structured reading of a selected template
  rule_search.py                Search a rule family for rules worth running
  patterns.py                   Catalogued orbits with a known period/displacement
  cli.py                        Command-line interface

scripts/                        Experiment and survey scripts
  alife/                        ALIFE paper figure and data generation
  surveys/                      Rule surveys (LifeWiki, ECA atlas, rule search)
  analysis/                     Convergence, baselines, stabilization

webdemo/                        In-browser reproduction (Pyodide)
paper/                          Paper (LaTeX + compiled PDF)
poster/                         Conference poster
proofs/                         Lean 4 artifacts (see proofs/README.md)
tests/                          Test suite (543 tests)
notebooks/                      Demo and paper companion notebooks
outputs/                        Generated CSVs, figures, survey results
docs/                           Theory notes and claim audit trail
data/                           Input data (LifeWiki rules JSON)
```

## How it works

For a binary spacetime `U[t, x]` and a candidate `(shift s, period p)`, the algorithm:

1. **Partitions** cells into orbit equivalence classes under the shift-period symmetry
2. **Majority-votes** within each class to build the optimal background `B`
3. **Scores** the fit with Bernoulli NML = data-fit (NLL) + model complexity
4. **Selects** the smallest period whose NML score beats alternatives

The residual mask `M = U ⊕ B*` captures what the periodic background cannot explain — gliders, domain walls, and other structured residuals.

### Ground truth

`patterns.py` catalogues orbits of `3d-life` (S4-5/B5) whose correct answer is
known analytically rather than planted: a 10-cell period-4 glider travelling
diagonally at c/4, a still life, and two oscillators. Each satisfies
`U[t+p, x+s] = U[t, x]` identically with no transient, so the true fit is
`(p, s)` at a defect rate of exactly zero, and the scan is checked against it.

Used this way, the selector shows that recovering a localized structure's period
is a **horizon budget**, not a sensitivity floor: at fixed occupancy a long
enough run always recovers it (7³ and 8³ at T=128, 10³ at T=256, 12³ at T=512,
i.e. T ≳ 0.3 × V). The complexity gap between period 1 and the true period
scales with spatial volume and does not depend on T, while the defect-bits a
period-1 fit leaves accumulate with T.

## Key dependencies

- `numpy`, `numba` — simulation and array ops
- `scipy` — connected components, stable combinatorics
- `pandas` — tabular results
- `matplotlib` — visualization
- `lz4` — compression-based codelength proxy
- `typer` — CLI

## Citation

```bibtex
@misc{winnower2026,
  title={Winnower: A Fast Tool for Splitting Cellular Automaton Spacetimes
         into a Periodic Background and a Residual Mask},
  author={Herman, Joshua},
  year={2026},
  howpublished={\url{https://github.com/zitterbewegung/Winnower}}
}
```

## License

See [LICENSE](LICENSE) for details.
