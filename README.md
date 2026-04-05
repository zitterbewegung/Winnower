# Winnower: Relative-Periodic Decomposition for Cellular Automata

[![Tests](https://img.shields.io/badge/tests-333%20passing-brightgreen)]()

Fits relative-periodic backgrounds to cellular automaton spacetimes and analyzes the structured defect masks that remain. Uses Normalized Maximum Likelihood (NML) for principled model selection across shift and period candidates.

**Paper:** *Structure Discovery in Cellular Automata via Relative-Periodic Decomposition* — submitted to ALIFE 2026.

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

paper/                          ALIFE 2026 submission (LaTeX)
poster/                         Conference poster
proofs/                         Lean 4 verification of Theorem A
tests/                          Test suite (333 tests)
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

The defect mask `D = U ⊕ B` captures what the periodic scaffold cannot explain — gliders, domain walls, and other structured residuals.

## Key dependencies

- `numpy`, `numba` — simulation and array ops
- `scipy` — connected components, stable combinatorics
- `pandas` — tabular results
- `matplotlib` — visualization
- `lz4` — compression-based codelength proxy
- `typer` — CLI

## Citation

```bibtex
@inproceedings{winnower2026,
  title={Structure Discovery in Cellular Automata via Relative-Periodic Decomposition},
  author={...},
  booktitle={ALIFE 2026},
  year={2026}
}
```

## License

See [LICENSE](LICENSE) for details.
