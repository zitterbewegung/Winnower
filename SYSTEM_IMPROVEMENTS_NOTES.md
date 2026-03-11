# System Improvements Notes

## What Changed

### 1. Period-First Selection (Priority 1) — Implemented
- New module `src/relative_symmetry_repair/selection.py` with:
  - `select_period()` for 1D and `select_period_nd()` for N-D
  - `PeriodScore` dataclass: period is primary, shift is secondary
  - `SelectionResult` with selected period, runner-up, margin, status
  - `selection_summary()` for structured JSON output
- Period-level scoring: `Score(period) = min over shifts of NML(period, shift)`
- CLI updated: all three `analyze` commands now use period-first selection
- CLI outputs structured `_selection.json` alongside existing CSVs
- Exports added to `__init__.py`

### 2. Finite-Sample Corrected NML (Priority 2) — Implemented
- `coding.py` now computes exact Bernoulli NML for orbit classes with n ≤ 200 observations
- Exact computation: `C(n) = Σ_{k=0}^{n} binom(n,k) * (k/n)^k * ((n-k)/n)^(n-k)` (Shtarkov normalizer)
- LRU cache (4096 entries) avoids recomputation
- Cutoff at n=200: asymptotic error < 0.01 bits/class there
- `nml_score_bits()` and `nml_complexity_bits()` accept `exact=True` (default) / `exact=False`
- Backward compatible: `exact=False` gives legacy asymptotic behavior

### 3. Two-Stage Pipeline (Priority 3) — Implemented
- Stage A: `select_period()` / `select_period_nd()` — NML-based selection
- Stage B: `ResidualDiagnostics` dataclass with RL bits, LZ4 bits, connected components
- `analyze_residual()` can be called independently with different parameters
- Residual diagnostics do not influence the selection criterion

### 4. Ambiguity Reporting (Secondary 4) — Implemented
- `SelectionStatus` enum: `STABLE_WINNER`, `NEAR_TIE`, `UNRESOLVED`
- Margin threshold: 2 bits (configurable via `NEAR_TIE_THRESHOLD`)
- Status included in CLI output and structured JSON

### 5-9. Secondary Goals — Partially Addressed
- **Residual modeling outputs (7)**: Connected-component analysis with size filtering, summaries
- **Stability diagnostics (8)**: Runner-up period, margin, all period scores in structured output
- **Reproducibility (9)**: JSON selection output, README updated

## What Was Intentionally NOT Changed

### Refinement / Reuse (Goal 5)
Not implemented. Would require rewriting the scan loop to share orbit statistics between divisibility-compatible periods. The current scan loop (grid over all period×shift pairs) is simple and correct. Optimization is worthwhile for large surveys but would be a separate PR.

### Velocity-Aware Search (Goal 6)
Not implemented. The current code scans all shift values independently per period. Grouping by velocity class (shift/period) and pruning redundant raw shifts would reduce the search space but requires restructuring `scan_relative_periodicity[_nd]` internals. Documented as future work.

### Existing `repair.py` / `repair_nd.py` Interfaces
Preserved unchanged. The new `selection.py` composes on top of existing scan functions. All existing call sites, test files, and scripts work as before.

### Legacy `mdl_bits` Score
Retained in fit dataclasses for backward compatibility. Not used in the new selection pipeline.

## Assumptions and Cutoffs

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `EXACT_NML_CUTOFF` | 200 | At n=200, asymptotic error ≈ 0.01 bits/class. Below this, exact computation matters for small-T / high-period scenarios. |
| `NEAR_TIE_THRESHOLD` | 2.0 bits | Below 2 bits, the winner could flip with small data perturbations. Chosen as ~2× the per-class O(1) constant. |
| LRU cache size | 4096 | Covers typical orbit-class size distributions (max period × max spatial size). |

## Behavioral Change: Finite-Sample NML and Rule 54

With exact NML, the complexity penalty for period 4 is higher than asymptotic at small T. For Rule 54 (width=32, T≤500), period 2 may be selected instead of period 4. This is correct behavior: the NLL improvement from period 4 over period 2 is marginal (~33 bits) while the complexity cost difference is substantial (~241 bits). At larger T, the NLL gap grows linearly while complexity grows logarithmically, so period 4 will eventually win. This is consistent with Theorem 3 (stabilization).

## Follow-Up Work

1. **Velocity-aware candidate pruning**: Group shifts by velocity class, skip redundant candidates
2. **Incremental orbit statistics**: Share bincount arrays between compatible period multiples
3. **Horizon sweep**: Run selection at multiple T values to visualize stabilization trajectory
4. **Manuscript update**: Section 2.4 should mention finite-sample NML correction
5. **Benchmark**: Compare exact vs asymptotic NML on the full 2D survey

## Modified Files

| File | Change |
|------|--------|
| `src/relative_symmetry_repair/coding.py` | Added `_exact_bernoulli_regret()`, `bernoulli_nml_complexity_single()`, `EXACT_NML_CUTOFF`. Updated `nml_complexity_bits()` and `nml_score_bits()` with `exact` parameter. |
| `src/relative_symmetry_repair/selection.py` | **New file**. Period-first selection, two-stage pipeline, ambiguity reporting. |
| `src/relative_symmetry_repair/__init__.py` | Added selection API exports. |
| `src/relative_symmetry_repair/cli.py` | Updated all three `analyze` commands to use period-first selection. Added JSON output. |
| `tests/test_selection.py` | **New file**. 23 tests covering finite-sample NML, period-first selection, ties, residual separation, structured output, N-D, and ECA integration. |
| `README.md` | Updated selection criterion and two-stage pipeline documentation. |
| `paper/revision_notes.md` | **New file**. Change log for paper_v7→v8 revision. |
| `paper/author_action_items.md` | **New file**. Author verification items for paper_v8. |
