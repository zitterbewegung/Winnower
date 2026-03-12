# Author Action Items for paper_v11.md

Only items requiring manual verification or decision.

---

## Open Items

### 1. Stabilization theorem novelty claim
**Location**: Section 1, last sentence of Introduction
**Issue**: The text states "This is, to the extent we are aware, the first stabilization theorem for periodic template selection in CA spacetimes." Verify against computational mechanics literature. Crutchfield et al. have consistency results for epsilon-machines but for a different model class.
**Status**: Requires literature search. Likely correct but unverified.

### ~~2. [RESOLVED] Fredkin Period-8 Interpretation~~
Explanatory note added to Section 3.2.1b: Fredkin is NOT exact negation on the 64×64 torus (match rate ~50%). Period-8 wins because 32,768 fine-grained orbit classes capture temporal structure that coarser periods miss (NML drops from 415,361 to 396,557). Noted as possible finite-size effect.

### 3. Appendix D — RL No-Ties Assumption
**Location**: Appendix D
**Finding**: Exact θ_j = 0.5 ties occur in ALL tested rules: ECA-30 (4 classes), ECA-54 (9), ECA-110 (9), S24/B11 (11), S11/B37 (22), S37/B11 (3), Diamoeba (3), Maze w/ Mice (7), Fredkin (12,388). The no-ties assumption in Theorem D.2 is violated.
**Action**: Add a remark to Appendix D noting that exact ties occur in practice but affect only a small fraction of orbit classes (except Fredkin). For these classes, majority vote does not stabilize, but the NML score is unaffected (the NLL contribution is symmetric). The RL convergence statement should be qualified accordingly.

---

## Resolved Items

- ~~Robustness to search range~~ — verified: expanding to P={1..16}, S={-10..10} matches default results for all 18 test cases (3 rules × 6 horizons). [AUTHOR VERIFY] tag removed from paper.
- ~~Diamoeba margin at T=400~~ — confirmed: 369 bits from `outputs/lifewiki_survey_T400.csv`, smallest of 103 stable_winners (next smallest: 2,910 bits).
- ~~Serviettes transition~~ — confirmed transient elimination: the period-2 NLL advantage (~14,800 bits) does not grow with T, while complexity cost grows from 11,409 to 16,716 bits, so p=1 correctly overtakes p=2 between T=200 and T=400.
- ~~Shtarkov citation~~ — verified: vol. 23, no. 3, pp. 3–17, 1987 (confirmed via multiple academic databases).
- ~~Li & Packard citation~~ — verified: vol. 4, no. 3, pp. 281–297 (Complex Systems website).
- ~~Repo URL and commit hash~~ — filled (`afd832ef`)
- ~~Wolfram (2002) citation~~ — verified via wolframscience.com
- ~~LifeWiki URL~~ — confirmed canonical
- ~~Appendix C horizons~~ — verified T=800 for 1D/2D, T=80 for 3D
- ~~Computational-mechanics comparison~~ — entropy-rate analysis added (Section 5.3)
- ~~ECA-110 discrepancy~~ — explained (shift=0 vs joint optimization)
- ~~Stabilization sweep parameters~~ — verified match script defaults
- ~~ECA-54 selected period~~ — both pipelines agree on p=4
