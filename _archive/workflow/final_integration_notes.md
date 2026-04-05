# Final Integration Notes: v9 → v10

## Source Materials
- `paper_v9.md`: base manuscript with literature/novelty positioning from research report
- `results/baseline_selector_summary.csv`: baseline selector comparison (3 datasets × 3 selectors)
- `results/baseline_selector_rule_level.csv`: per-rule selector comparison (112 rows)
- `results/stabilization_results.csv`: finite-horizon stabilization sweep (54 rows, 9 rules × 6 horizons)
- `figures/period_stabilization_*.png`: 9 stabilization figures

---

## Literature Positioning (carried from v9)
- Introduction rewritten to lead with global model-selection framing
- Two CA analysis traditions presented: computational mechanics [1,2,4,7] and compression/survey [8,11,12]
- Comparison table in Section 1.2 clarified
- Claims softened: "longstanding question" not "central problem"; "broad by CA standards" not exhaustive
- Claims strengthened: stabilization theorem novelty, unified N-d framework prominence

## Experiment Integration (new in v10)

### Abstract
- Added sentences on baseline comparison and stabilization sweep findings
- Conservative language: "consistent with the stabilization prediction", "at most 2 period transitions before locking"

### Section 3.5 — Baseline Selector Comparison
- Already present in v9 (from v8); no structural changes needed
- Section 5.1 now references this evidence explicitly

### Section 3.6 — Stabilization Sweep
- Enhanced summary table with "Final Margin" column populated from CSV data
- Added actual margin values: ECA-54 681→2319, ECA-110 262→2356, Diamoeba 3687→12193
- Added `[AUTHOR VERIFY]` note about discrepancy between Section 3.1 (ECA-110 locked at p=7) and Section 3.6 (p=1→p=7→p=4 transitions, locks at p=4)
- Added reference to figure files in `figures/`

### Section 5.1 — Stabilization Discussion
- Added sentence connecting baseline comparison evidence to Theorem 3 motivation

### Section 5.4 — Broader Empirical Pattern
- Enhanced with stabilization sweep findings
- Added caveats: "over the observed horizons", "is consistent with", "supports the practical relevance"
- Notes all rules achieve stable_winner status, post-lock margins grow monotonically

### Appendix A — Reproducibility
- Expanded with experiment scripts, result file paths, figure paths
- Added detailed parameters for both experiments (grid sizes, horizons, seeds)

---

## Claims Softened (v10-specific)

| Location | Change | Reason |
|----------|--------|--------|
| Abstract | "consistent with the stabilization prediction" | Not proof of convergence |
| Section 3.6 | "over the observed horizons" | Finite data caveat |
| Section 5.4 | "supports the practical relevance of Theorem 3" | Empirical support, not proof |

## Claims Strengthened (v10-specific)

| Location | Change | Justification |
|----------|--------|---------------|
| Abstract | Mentions baseline comparison and stabilization sweep | New empirical evidence |
| Section 3.6 | Concrete margin values from CSV | Quantitative stabilization data |
| Section 5.1 | Baseline comparison isolates NML's role | Experiment directly tests overfitting |

---

## New Tables/Figures Added
- Section 3.6 summary table: "Final Margin" column added
- 9 stabilization figures referenced: `figures/period_stabilization_*.png`

## References Added/Updated
- No new references in v10 (all additions were in v9: [11] Wolfram, [12] Li & Packard, [13] LifeWiki)

---

## Resolved Verification Items (v10)
1. **ECA-110 discrepancy (Section 3.1 vs 3.6)**: Section 3.1 uses shift=0 only → p=7. Section 3.6 uses joint (shift, period) optimization → p=4 (shift=−2) at lower NML. Both sections now document the shift constraint. Explanatory text added.
2. **Appendix C horizons**: Verified T=800 for 1D/2D, T=80 for 3D. [AUTHOR VERIFY] tags removed.
3. **ECA-54 period**: Both pipelines agree on p=4. No discrepancy.
4. **Appendix A parameters**: All match `experiments/stabilization_analysis.py` defaults exactly.

## Remaining Verification Items
Carried forward to `author_action_items.md` (9 open items):
- Repo URL and commit hash (item #1)
- Li & Packard citation pages (item #3)
- Stabilization theorem novelty claim (item #4)
- Fredkin period-8 interpretation (item #5)
- Diamoeba margin significance (item #6)
- Serviettes transition direction (item #7)
- Shtarkov, Wolfram, LifeWiki citations (items #8–10)
- RL no-ties assumption (item #11)
- Computational mechanics comparison (item #12)
