# Winnower: Relative-Periodic Decomposition for Cellular Automata

[![Tests](https://img.shields.io/badge/tests-363%20passing-brightgreen)]()

Fits relative-periodic backgrounds to cellular automaton spacetimes and analyzes the structured residual masks that remain. Uses Normalized Maximum Likelihood (NML) for principled model selection across shift and period candidates.

**Paper:** *Winnower: A Fast Tool for Splitting Cellular Automaton Spacetimes into a Periodic Background and a Residual Mask* — see `paper/paper_alife2026.pdf` and the [reviewer site](https://zitterbewegung.github.io/Winnower/).

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
# Generate all survey data (takes a while)
python scripts/alife/alife_run_all.py

# Generate all figures
python scripts/alife/alife_rule_diagrams.py

# Run tests
pytest tests/
```

See [REPRODUCING.md](REPRODUCING.md) for the full reproduction pipeline.

## Reviewer / evaluation interface

A self-contained web page for evaluating the paper — abstract, claim-by-claim
audit ledger, all figures with their generating scripts, sortable result
tables, and reproduction steps.

The hosted version additionally includes a **live in-browser reproduction**
(`reproduce.html`): WebAssembly Python (Pyodide) runs the actual
`relative_symmetry_repair` pipeline — simulate → scan candidates →
Bernoulli-NML selection — for any ECA rule, any 2D B/S rulestring, arbitrary
3D birth/survive count sets (e.g. `B5-7,9/S4,6-8`, non-contiguous allowed),
or the paper's representative 2D/3D rules, and compares
the result against the committed row of `eca_atlas_runs.csv` /
`seed_stability_runs.csv`, column by column (integers and strings exactly,
floats at 1e-9 relative tolerance; max observed deviation 9×10⁻¹³). Results
are inspectable interactively: full spacetime diagrams in 1D, frame
scrubbing plus a rotatable 3D world-tube view of the residual mask in 2D,
and fully rotatable linked voxel views of spacetime, background, and
residual in 3D. The browser code path (numba stubbed, vectorized simulator
kernels) is verified against the committed CSVs by:

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

The site is published via GitHub Pages from the `gh-pages` branch at
`https://<owner>.github.io/Winnower/`. Pushes to `main` that touch the paper,
outputs, or the site generator trigger
`.github/workflows/deploy-review-site.yml`, which builds a standalone copy
(figures embedded, paper PDF included) and force-pushes it to `gh-pages`.
To host elsewhere, build the same folder locally and upload it to any static
host (Netlify, Vercel, S3, …):

```bash
python scripts/build_review_site.py --pages _site
```

Note for double-blind review: the paper is anonymized, but a GitHub Pages URL
under your account is not. For reviewer-facing links, prefer an anonymized
mirror (e.g. https://anonymous.4open.science) or share the portable
single-file HTML directly.

## Project structure

```
src/relative_symmetry_repair/   Core library
  eca.py, ca2d.py, ca3d.py      CA simulators (1D, 2D, 3D)
  repair.py, repair_nd.py       Relative-periodic background fitting
  coding.py                     NML scoring, codelength metrics
  selection.py                  Period-first model selection
  cli.py                        Command-line interface

scripts/                        Experiment and survey scripts
  alife/                        ALIFE paper figure and data generation
  surveys/                      Rule surveys (LifeWiki, ECA atlas, 2D range)
  analysis/                     Convergence, baselines, stabilization

paper/                          Paper (LaTeX + compiled PDF)
poster/                         Conference poster
proofs/                         Lean 4 artifacts (see proofs/README.md for per-file status)
tests/                          Test suite (363 tests)
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
