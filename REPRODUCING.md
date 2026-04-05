# Reproducing the paper results

This document describes how to reproduce every figure, table, and claim in the ALIFE 2026 paper from scratch.

## Prerequisites

```bash
pip install -e .
```

Requires Python 3.11+ with numpy, numba, scipy, pandas, matplotlib, lz4, and typer.

## Step 1: Generate survey data

```bash
# Full experiment suite: null controls, seed stability, range robustness,
# LifeWiki survey, ECA atlas, 3D survey, counterexample stress tests.
# Runtime: ~30-60 minutes depending on hardware.
PYTHONPATH=src python scripts/alife/alife_run_all.py \
    --output-root outputs/alife_2026 \
    --paper-dir paper
```

This populates `outputs/alife_2026/` with CSVs and summary statistics.

## Step 2: Generate figures

```bash
# Matplotlib figures for paper and poster (rule diagrams, mechanisms, etc.)
PYTHONPATH=src python scripts/alife/alife_rule_diagrams.py \
    --output-root outputs/alife_2026 \
    --paper-dir paper

# Algorithm flow diagram
PYTHONPATH=src python scripts/alife/alife_algorithm_figure.py

# Stabilization summary (requires Step 1 data)
PYTHONPATH=src python scripts/alife/alife_stabilization_summary.py
```

## Step 3: Compile TikZ figures

```bash
cd poster/figures
pdflatex algorithm_detailed_tikz.tex
pdflatex selector_ablation_tikz.tex
pdflatex stabilization_summary_tikz.tex
pdflatex entropy_rate_comparison_tikz.tex
cd ../..
```

## Step 4: Compile the paper

```bash
cd paper
pdflatex paper_alife2026.tex
bibtex paper_alife2026    # if using bibliography
pdflatex paper_alife2026.tex
cd ..
```

## Step 5: Run the test suite

```bash
pytest tests/
```

Expected: 333+ tests passing, 0 failures.

## Step 6: Verify Lean proofs (optional)

Requires Lean 4 (v4.24.0) and Mathlib.

```bash
cd proofs
lake build
```

This machine-checks the Partition Projection Theorem (Theorem A).

## What each script produces

| Script | Outputs | Used in |
|--------|---------|---------|
| `alife_run_all.py` | CSVs in `outputs/alife_2026/` | Tables 1-2, ablation data |
| `alife_rule_diagrams.py` | PNGs in `outputs/alife_2026/rule_diagrams/` and `paper/figures/` | Figures 1-2, poster panels |
| `alife_algorithm_figure.py` | `outputs/alife_2026/editable_figures/algorithm_detailed.*` | Figure 1 |
| `alife_stabilization_summary.py` | `outputs/alife_2026/editable_figures/stabilization_summary.*` | Poster stabilization panel |

## Seeds and reproducibility

All experiments use deterministic seeds. The diagram generation uses `--base-seed 42`. Survey scripts use `seed=11` as the primary seed with multi-seed sweeps over `[11, 42, 73, 104, 135]`.
