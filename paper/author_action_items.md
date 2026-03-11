# Author Action Items for paper_v8.md

Only items requiring manual verification or decision. Items marked [AUTHOR VERIFY] in the manuscript are listed here.

---

## 1. Theorem 3 Assumption Verification
**Location**: Section 2.5, Assumption (A1)
**Issue**: Theorem 3(ii) requires that per-site NLL rates λ_c = lim NLL_c(T)/N(T) exist. The proof that finite deterministic CA satisfy this is in Appendix D but relies on eventual periodicity of the CA state. Verify this holds for all rules in the experimental section, or add a sentence noting which rules have been verified.
**Action**: Run convergence diagnostic (rate vs T plot) for each tested rule and confirm rates stabilize.

## 2. Theorem 3 Part (iii) — Uniqueness of Rate-Minimizer
**Location**: Section 2.5, Theorem 3(iii)
**Issue**: Full stabilization to a unique winner requires the rate-minimizer to be unique. The paper states "which holds in all cases we test." Verify this claim by checking that the margin between best and second-best rates is strictly positive for all reported experiments.
**Action**: Confirm margin > 0 for all rules in Tables 1–3.

## 3. 3D Margin Non-Monotonicity
**Location**: Section 3.3
**Issue**: v7 implied margins are monotonically increasing. v8 corrects this for 3D (margins drop T=10→T=20). Verify the exact T values and margin magnitudes from the experimental output.
**Action**: Re-run 3D analysis and confirm the stated margin trajectory.

## 4. Section 3.1 — "Best Across All Scanned Shifts"
**Location**: Section 3.1 heading and description
**Issue**: Changed from "shift = 0" to "best across all scanned shifts." Verify that the 1D experiments actually scan multiple shifts (not just s=0).
**Action**: Check `cli.py analyze` to confirm shift scanning range for 1D.

## 5. Appendix C Horizon Markers
**Location**: Appendix C
**Issue**: Placeholders for "[AUTHOR VERIFY: horizon T_0 for rule X]" need to be filled with actual stabilization horizons from experimental output.
**Action**: Fill in T_0 values from convergence traces.

## 6. Reference [10] — Shtarkov Citation
**Location**: Definition 4
**Issue**: Added reference to Shtarkov (1987) for the NML normalizing constant. Verify the exact citation: "Yu. M. Shtarkov. Universal sequential coding of single messages. *Problems of Information Transmission*, 23(3):3–17, 1987."
**Action**: Confirm bibliographic details.

## 7. Survey Scope — "773 Non-Trivial Candidates"
**Location**: Abstract, Section 3.2
**Issue**: v8 states "773 non-trivial candidates" (changed from "458 non-trivial from 621"). Verify the exact count from `outputs/survey_2d_rules.csv`.
**Action**: Count rows in survey CSV with non-trivial evolution.

## 8. S37/B11 Scaling — Grid Sizes
**Location**: Abstract, Section 4.2
**Issue**: Claims "grid sizes up to 192×192." Verify this from the strengthen_v2.py output.
**Action**: Check `outputs/` for S37/B11 scaling data.

## 9. Appendix D — RL Convergence "No Ties" Assumption
**Location**: Appendix D, Theorem D.1
**Issue**: The RL convergence proof assumes no orbit class has exact frequency ties (θ_j = 0.5). While generically true, verify no tested rule triggers this edge case.
**Action**: Check orbit-class frequencies for all reported rules.
