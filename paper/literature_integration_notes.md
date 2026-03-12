# Literature Integration Notes: v8 → v9

## Source
Research report: `outputs/conclusions.md` (novelty/prior-art assessment)
Supporting reviews: `VERDICT.md`, `paper/chatgpt_review_prompt.md`

---

## Novelty Positioning

### Changes made
- **Introduction rewritten** to lead with the global model-selection framing: "which relative-periodic template best describes the data?" is the core question, positioned against the local-model tradition from the start
- **Contributions list** reframed to emphasize method + theory + broad empirical validation as the three pillars, matching the research report's assessment
- Added explicit framing sentence: this is a *framework and method paper* with theorem-level analysis, not a claim to discover new CA phenomenology
- Removed implicit claims of discovering new dynamical phenomena; reframed 2D persistent-defect rules as "identified by the framework" rather than "discovered"

### Claims softened
- "central problem in CA theory" → "longstanding question in CA analysis" (less grandiose)
- Removed any remaining "novel" language; replaced with specific descriptions of what the paper provides
- Added qualifying language that the 2D survey scale is "broad by CA standards" rather than implying exhaustiveness
- Discussion now states explicitly: "The broader empirical pattern suggested by these surveys is that most rules do not justify a global periodic background more complex than period 1 under complexity-penalized selection, unless the likelihood gain from genuine periodic structure is strong enough to overcome the penalty"

### Claims strengthened (where justified by report)
- Made the unified N-dimensional framework more prominent — the report identifies this as clearly novel
- Emphasized that the stabilization theorem (Theorem 3) has no prior analogue in the periodic CA template selection literature
- Baseline selector comparison (Section 3.5) now explicitly connected to Theorem 2 motivation

---

## Prior-Work Additions

### New references added
- [11] S. Wolfram, *A New Kind of Science*, Wolfram Media, 2002. — Standard reference for CA classification and surveys; gives context for the 2D survey contribution
- [12] W. Li and N. Packard, "The structure of the elementary cellular automata rule space," *Complex Systems*, vol. 4, pp. 281–297, 1990. — Early systematic CA rule-space survey; positions our 2D survey in context

### Enhanced discussion of existing references
- [1,2] Crutchfield/Hanson: expanded comparison paragraph explaining bottom-up (local epsilon-machines) vs top-down (global projection) approaches, and why they are complementary rather than competing
- [4] Rupe/Crutchfield: noted that local causal states generalize to arbitrary dimensions but at higher computational cost; our dimension-agnostic framework is cheaper but less expressive
- [7] Shalizi et al.: noted that coherent-structure filters identify spatial features through local statistical models, while our method identifies temporal periodicity through global template fitting — different decomposition targets
- [8] Zenil: clarified that compression-based CA classification operates on raw spacetimes, while our compression diagnostics operate on projection residuals after template selection — different stage of the analysis pipeline

### New Section 1.2 structure
- Comparison table retained but column headers clarified
- Added prose paragraph below the table explaining the local-vs-global distinction more precisely
- Added paragraph on compression-based and survey-based CA analysis (Zenil, Wolfram, Li/Packard) as a separate tradition, distinct from computational mechanics

---

## Claims Softened

| Location | Old phrasing | New phrasing | Reason |
|----------|-------------|-------------|---------|
| Abstract | "The theory applies identically to 1D, 2D, and 3D automata" | Unchanged (factual) | — |
| Intro | "central problem in CA theory" | "longstanding question in CA analysis" | Overly strong scope claim |
| Section 3.4 | "3 rules change period" | "4 rules change period" | Already fixed in v8; retained |
| Section 5.3 | "does not recover domain/particle structure" | Added: "nor does it claim to — the outputs are projection residual masks, not particles in the computational-mechanics sense" | Sharper disclaimer per report |
| Discussion | (implicit that surveys are comprehensive) | Added: "broad by the standards of systematic CA surveys" with caveat about single-seed limitation | Per report's "what would strengthen" |

## Claims Strengthened

| Location | Change | Justification |
|----------|--------|---------------|
| Intro | "stabilization theorem ... has no direct analogue in prior periodic-structure analysis of CA" | Report finds no prior stabilization proof for this setting |
| Contributions | "cross-dimensional experiments spanning 1D, 2D, and 3D" made more prominent | Report identifies unified N-d framework as clearly novel |
| Section 3.5 | Baseline comparison explicitly motivates NML | Report: codelength-based quality metric is clearly novel |
| Discussion | New sentence on broader empirical pattern (most rules select p=1) | Report: systematic survey findings are novel |

---

## New References Added

| # | Reference | Why added |
|---|-----------|-----------|
| [11] | Wolfram, *A New Kind of Science* (2002) | Standard CA survey/classification context |
| [12] | Li & Packard, "Structure of ECA rule space" (1990) | Positions 1D results relative to prior systematic surveys |

---

## Unresolved Verification Items

Items moved to `author_action_items.md`:
1. Li & Packard (1990) exact citation — verify volume/pages [AUTHOR VERIFY]
2. Wolfram (2002) — confirm this is the right edition to cite [AUTHOR VERIFY]
3. Direct computational-mechanics comparison on Rule 54 — listed as future work, not attempted
4. Fredkin period-8 interpretation — carried forward from v8 action items
