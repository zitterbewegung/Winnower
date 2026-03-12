# Final Cleanup Notes: v10 → v11

## Changes by Task

### TASK 1 — Selector Definition
- Added **Definition 6 (Period-first selector)** after Definition 4 in Section 2.4
- Explicit formula: $\text{Score}(p) = \min_{\mathbf{s}} \text{NML}(p, \mathbf{s})$, then $p^* = \arg\min_p \text{Score}(p)$
- Documents tie-breaking: smaller period first, then lexicographic on shift
- Notes that `select_period` / `select_period_nd` implement this exactly

### TASK 2 — Candidate Search Space
- Added **Section 3.0 "Candidate Search Space"** with parameter table
- All values pulled from experiment scripts (not guessed)
- Covers 1D ECA, 1D stabilization, 2D LifeWiki, 2D range-threshold, 2D stabilization, 3D stabilization, baseline comparison
- Explains why ranges decrease with dimensionality (orbit-class count grows multiplicatively)

### TASK 3 — Robustness Statement
- Added paragraph in Section 3.0 about extending candidate ranges
- Tagged `[AUTHOR VERIFY]` — no evidence of expanded-range testing in the repo
- Provides theoretical justification (Theorem 3's Θ(T) gap)

### TASK 4 — ECA-110 Pipeline Difference
- Section 3.1 already says "shift=0 only" in table header and explanation; now references Definition 6
- Section 3.6 already has full explanation; now references Definition 6
- No duplication; both cross-reference each other

### TASK 5 — Numerical Consistency
- Verified 34,686 from `results/stabilization_results.csv` (ECA-110, T=200, nml_bits=34686.037)
- Verified 35,885 from `outputs/convergence/convergence_1d.csv` (ECA-110, T=200, nml_bits=35885.4)
- Both round correctly to the values in the text. No change needed.

### TASK 6 — Empirical Framing
- Section 5.5 rewritten to open with "An empirical observation about the sampled rule families"
- Added sentence: "whether it extends to other rule families ... is an open question"
- Removed "broad by the standards of systematic CA surveys" (redundant with Section 1.1)

### TASK 7 — Prior-Work Positioning
- Added sentence in Section 1.2 explicitly distinguishing local causal states [4] from our approach (cost, expressiveness tradeoff)
- All four distinctions now clearly present:
  - Computational mechanics [1,2] — paragraph 1 + comparison table
  - Local causal states [4] — new sentence after table
  - Coherent-structure filters [7] — existing paragraph
  - Compression-based classification [8] — existing paragraph

### TASK 8 — Reproducibility Section
- Appendix A already has: repo URL (filled), commit hash (filled), all script names, result file paths, figure paths, key parameters
- No changes needed — already complete from v10

### TASK 9 — [AUTHOR VERIFY] Tags
- **Resolved**: Li & Packard citation — verified vol. 4, no. 3, pp. 281–297 via Complex Systems website. Tag removed, issue number added.
- **Remaining**: Robustness to search range (Section 3.0) — `[AUTHOR VERIFY]`, requires running experiments with expanded ranges

### TASK 10 — Language Conventions
- Scanned for "proves empirically", "guarantees stabilization" — none found
- Existing language already uses "consistent with", "stabilizes over the observed range", "finite data cannot prove this definitively"
- No changes needed

## Summary

| Task | Status | Changes |
|------|--------|---------|
| 1. Selector definition | Done | Definition 6 added |
| 2. Candidate search space | Done | Section 3.0 added |
| 3. Robustness statement | Done | Paragraph added with [AUTHOR VERIFY] |
| 4. ECA-110 pipeline | Done | Refined to reference Definition 6 |
| 5. Numerical consistency | Done | Verified, no change needed |
| 6. Empirical framing | Done | Section 5.5 reworded |
| 7. Prior-work positioning | Done | Local causal states sentence added |
| 8. Reproducibility | Done | Already complete |
| 9. [AUTHOR VERIFY] scan | Done | Li & Packard resolved; 1 tag remains |
| 10. Language conventions | Done | Already correct |
