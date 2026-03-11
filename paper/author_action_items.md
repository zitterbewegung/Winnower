# Author Action Items for paper_v8.md

Only items requiring manual verification or decision.

---

## 1. [AUTHOR INSERT REPO URL] and [AUTHOR INSERT COMMIT HASH]
**Location**: Appendix A
**Action**: Fill with repository URL and commit hash before submission.

## 2. [AUTHOR VERIFY HORIZON] in Appendix C
**Location**: Appendix C
**Issue**: Verify NML vs MDL comparison horizons (T=800 for 1D/2D, T=80 for 3D).

## 3. Theorem 3 Assumption (A1) — Wording
**Location**: Section 2.5
**Issue**: v8 uses "convergent orbit-class frequencies" (vs "ergodic" in v7). Confirm this is the intended, weaker statement.

## 4. Theorem 3(iii) — Unique Rate-Minimizer
**Location**: Section 2.5
**Issue**: Claims uniqueness "holds in all cases we test." Verify margin > 0 for all reported experiments.

## 5. 3D Margin Non-Monotonicity
**Location**: Section 3.3
**Issue**: Margins drop T=10→T=20 before period switches. Verify exact values from experimental output.

## 6. Shtarkov Citation
**Location**: Definition 4, Reference [10]
**Issue**: Verify: "Yu. M. Shtarkov. Universal sequential coding of single messages. *Problems of Information Transmission*, 23(3):3–17, 1987."

## 7. Fredkin Period-8 Interpretation
**Location**: Section 3.2.1b
**Issue**: Fredkin (B1357/S02468) produces exact negation every step (period-2 for cell states), but NML selects period 8. Verify whether this is due to torus geometry interaction or a genuine period-8 orbit-class structure.

## 8. Diamoeba Margin at T=400
**Location**: Section 3.2.1b, Table
**Issue**: Margin is 369 bits — smallest among all stable_winner rules at T=400. Confirm correct and note significance.

## 9. Serviettes Transition Direction
**Location**: Section 3.2.1b
**Issue**: Serviettes goes p=2→p=1 at T=400. Verify interpretation: transient signal eliminated vs genuine dynamics change.

## 10. Two Rules Became Trivial at T=400
**Location**: Section 3.2.1b
**Issue**: Iceballs (B25678/S5678→all_ones) and Lifeguard 2 (B3/S4567→dead) became trivial at T=400 but were nontrivial at T=100. This explains the nontrivial count drop from 105 to 103. Currently mentioned only in passing — consider adding explicit note.

## 11. Appendix D — RL No-Ties Assumption
**Location**: Appendix D
**Issue**: RL convergence proof assumes θ_j ≠ 0.5. Verify no tested rule triggers this edge case.

## Items Already Resolved
- Period count consistency: 105 nontrivial at T=100 (97+7+1), 103 at T=400 (94+7+1+1). ✓
- "Three vs four rules changed": fixed to "four" in paper_v8.md. ✓
- All selections stable_winner at both horizons. ✓
