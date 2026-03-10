# CLAUDE.md

## Project Overview
Relative symmetry-repair analysis for cellular automata. Fits relative-periodic backgrounds to CA spacetimes and analyzes structured defect masks.

## Workflow Preferences
- When evaluating novelty/publishability, pipe conclusions and paper drafts to `codex exec` for independent review
- Return full codex conversation transcripts when asked
- Use multiple rounds of codex review (initial assessment → strengthen → re-evaluate)
- Make a git commit after each revision (paper update, experiment results, code changes)

## Key Commands
- `codex exec -` reads prompt from stdin (use for piping content)
- `jupytext --to notebook` to convert .py to .ipynb

## Project Structure
- `src/relative_symmetry_repair/` — core library (repair.py, repair_nd.py, coding.py, eca.py, ca2d.py, ca3d.py)
- `scripts/` — survey and analysis scripts
- `paper/` — paper drafts (v1, v2, v3_final)
- `notebooks/` — demo and paper companion notebooks
- `outputs/` — generated CSVs, PNGs, strengthening data

## Publication Status
- Paper v3 addresses all Codex review issues
- Best venues: ALIFE 2026 (deadline March 30), Complex Systems, Journal of Cellular Automata
- Key novel contributions: codelength metric for defect masks, 2D persistent-defect rule catalog
- Known limitations: no interaction analysis, single-seed scaling, raster-order dependent run-length metric
