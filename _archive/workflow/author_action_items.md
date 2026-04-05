# Author Action Items for paper_v11.md

Only items requiring manual verification or decision.

---

## Open Items

### 1. Stabilization theorem novelty claim
**Location**: Section 1 (line 53 area)
**Issue**: The text claims the stabilization theorem (Theorem 3) is the primary contribution relative to prior work. Deep research assessment (ChatGPT 5.4 Pro, March 2026) confirms: computational mechanics treats periodicity as exact symbolic structure (automata, languages, domain transducers), not as approximate Hamming-loss template selection with NML model-selection guarantees. No equivalent stabilization result exists in that literature. However, the *majority-vote lemma* (Theorem 1) is standard — now acknowledged via [14] (Lachish & Newman, 2011) with a Prior Art remark after the proof.
**Status**: Novelty claim for Theorem 3 is defensible. Theorem 1 prior art now cited. No further action needed unless a specific competing stabilization result is found during peer review.

### ~~2. [RESOLVED] Fredkin Period-8 Interpretation~~
Explanatory note added to Section 3.2.1b: Fredkin is NOT exact negation on the 64×64 torus (match rate ~50%). Period-8 wins because 32,768 fine-grained orbit classes capture temporal structure that coarser periods miss (NML drops from 415,361 to 396,557). Noted as possible finite-size effect.

### ~~3. [RESOLVED] Appendix D — RL No-Ties Assumption~~
Theorem D.2 condition reworded from "assume no exact frequency ties" to a conditional statement. New Remark added documenting empirical tie frequencies (ECA-30: 4, ECA-54: 9, ECA-110: 9, Fredkin: 12,388) and explaining that NML is unaffected because H_b(1/2) = 1 regardless of tie-breaking. Concluding remark notes θ≈1/2 classes have minimal explanatory power.

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
