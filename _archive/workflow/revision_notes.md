# Revision Notes: paper_v7.md → paper_v8.md

## Theorem-Level Changes

### Theorem 3 (Stabilization) — Rewritten
- **v7**: Claimed unique stabilization unconditionally from convergent per-site entropy rates.
- **v8**: Three-part structure: (i) NML decomposition identity, (ii) elimination of candidates with non-minimal rate (proved: Θ(T) dominates O(log T)), (iii) full stabilization **conditional** on unique rate-minimizer.
- **Reason**: The o(N(T)) remainder in NLL(c,T) = λ_c·N(T) + o(N(T)) can dominate the O(log T) complexity term, so logarithmic tie-breaking is not justified under (A1) alone.
- **Added**: Remark on logarithmic tie-breaking — holds if NLL remainder is o(log T), which finite deterministic CA satisfy (Appendix D). All tested cases have unique rate-minimizer with growing margins.

### Theorem 4 (Nonidentifiability) — Proof Added
- **v7**: Stated without proof sketch.
- **v8**: Explicit construction: given (p₀, s) with periodic residual of period k, the candidate (k·p₀, k·s mod D) absorbs residual into template, NLL drops by Θ(N(T)) while complexity grows O(log T).

### Theorem 5 (Identifiability for Exactly Periodic Backgrounds) — Strengthened
- **v7**: Stated NLL change as exactly 0 for pure orbit splits.
- **v8**: Correctly states NLL change is O(1) (not exactly 0) due to ceiling effects in orbit-class sizes. Still dominated by Θ(log T) complexity increase. Title changed from "Identifiability for Pure Backgrounds" to "Identifiability for Exactly Periodic Backgrounds."

### Theorem 1 (Orbit-Class Reduction) — Language Tightened
- **v7**: Implied unique minimizer.
- **v8**: "a Hamming-optimal projection" (not "the unique"); uniqueness conditional on no exact ties; O(|U|) per candidate model stated explicitly.

### Theorem 2 (Monotonicity) — Unchanged
- Already corrected in v7 (velocity-matching condition from MANUSCRIPT_PATCH.md).

## Claim-Scope Changes

### Abstract
- "stabilizes to a unique period" → "stabilizes as the observation window grows: every candidate whose rate exceeds the minimum is eventually excluded"
- Rate-minimizer uniqueness noted as empirical, not assumed.

### Section 1.1 Contributions
- Item 3 rewritten to match three-part Theorem 3.
- "three selected 2D totalistic rules (from a survey of 773)" replaces "458 non-trivial 2D rules."

### Section 3.1
- Heading changed from "shift = 0" to "best across all scanned shifts" (matches code behavior).

### Section 3.4 Summary / Conclusion
- Removed claim that margins are monotonically increasing for 3D (empirically false: margins drop T=10→T=20 before stabilization).
- "consistent with Theorem 3" replaces "exactly as Theorem 3 predicts."

### Section 4.2
- Added explicit definitions of Mean Rate and Defect Density metrics used in scaling analysis.

### Section 5.2
- Fixed cross-reference: Section 2.8 → Section 2.7 (Appendix C reference was wrong).

### Section 5.4 Nonzero Shifts
- Fixed contradiction: item 1 now accurately describes that case studies use specific rules, not the full survey.

## Internal Consistency Fixes

- N(T) = T·∏ᵢDᵢ defined in Section 2.1 and used consistently thereafter.
- "per-site" consistently means division by N(T), not by T.
- [10] Shtarkov reference added to Definition 4.
- Appendix C horizon verification markers added (placeholders for author verification).
- Appendix D (RL convergence) carried over from v7 LaTeX.

## Terminology Fixes (Global)

| v7 | v8 | Scope |
|----|----|-------|
| "MDL consistency" | "model selection stabilization" | throughout |
| "converges to" (re: period) | "stabilizes to" or "locks to" | throughout |
| "defects" (formal) | "projection residuals" | theorems, definitions |
| "exact NML" | "asymptotic NML" / "Bernoulli NML" | throughout |
| "NML parametric complexity" | "asymptotic parametric complexity" | Definition 4 |
| "convergence confirmed" | "empirical stabilization observed" | Section 3 |

## Presentation / Bibliography

- Limitation 0 added (velocity-matching requirement for Theorem 2).
- Limitation 5 added (finite candidate set assumption in Theorem 3).
- Future Work item 6 added (formal verification of Theorem 3 decomposition).
- Appendix A placeholders for experimental parameters.
