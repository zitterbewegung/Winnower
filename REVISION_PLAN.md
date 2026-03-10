# Revision Plan

Prioritized list of changes to transform the manuscript into the strongest
correct version. Each item tagged with priority (P1 = must fix, P2 = should fix,
P3 = nice to have).

---

## P1: Critical Corrections (blocks acceptance)

### 1. Fix Theorem 2 (Monotonicity)
**Current:** "If p2 = m * p1 with the same shift s, then..."
**Problem:** FALSE. Counterexample: D=4, p1=1, s=1, p2=2, s=1 on checkerboard.
**Fix:** Replace with velocity-matched condition: p2 = m*p1 AND s2 = m*s1 (mod D_i).
**Impact:** Theorem statement, proof, Overcapacity Corollary, abstract, intro.

### 2. Fix Theorem 3 Proof Gap
**Current:** Claims L_RL(T)/T converges under assumptions (A1)+(A2).
**Problem:** (A2) "Omega(T) runs" does not imply per-site RL rate convergence.
**Fix:** Either:
  (a) RECOMMENDED: Restate Theorem 3 for the Bernoulli NML score, where convergence
      of NLL/T follows directly from (A1). This also aligns with the code.
  (b) Add explicit assumption that L_RL(T)/T converges.
**Impact:** Theorem 3 statement, proof, and all references to "MDL consistency."

### 3. Align Paper and Code on Which Score Is Used
**Current:** Paper's Theorem 3 is about MDL = BIC penalty + RL bits.
**Code:** CLI and convergence scripts use NML = NLL + NML complexity.
**Fix:** Choose one. Recommend NML (cleaner theory, already in code).
**Impact:** Definition 3, Theorem 3, all experimental sections, code comments.

### 4. Fix "NML" Terminology
**Current:** Code and paper mix "exact NML," "asymptotic NML," and "BIC-like penalty."
**Fix:**
  - Rename `template_bits_nml` → `template_bits_bic` in code
  - Remove "exact" from `nml_complexity_bits` docstring (it's asymptotic)
  - In paper: use "asymptotic Bernoulli NML" or "BIC-type penalty" consistently
  - Never call the combined score "exact NML"
**Impact:** coding.py, repair.py, repair_nd.py, all docstrings, paper Definition 3.

---

## P2: Important Improvements (strengthens paper significantly)

### 5. Promote Nonidentifiability Remark to Formal Proposition
**Current:** A remark in Section 2.5.
**Fix:** State as Proposition/Theorem D with proof. This is a genuine contribution.
**Impact:** Section 2.5, possibly abstract.

### 6. Add Abstract Partition Theorems
**Current:** Theorems stated only for relative-periodic partitions.
**Fix:** State the abstract partition projection (Theorem A) and partition-refinement
  monotonicity (Theorem B) first, then specialize. This makes the paper cleaner
  and the proofs more transparent.
**Impact:** Section 2.1-2.3.

### 7. Clarify Empirical vs Theoretical Claims
**Current:** "convergence confirmed empirically" (Section 3.4).
**Fix:** Use "empirical stabilization over the tested range [T_min, T_max]."
  Do not use "confirmed" for finite data. The theory predicts eventual stabilization;
  the data is consistent with the prediction.
**Impact:** Section 3, conclusion.

### 8. Fix Terminology: "Defects" vs "Projection Residuals"
**Current:** Uses "defects" throughout, which implies physical interpretation.
**Fix:** Use "projection residuals" or "residual mask" in formal sections.
  "Defect" is acceptable in informal discussion with a clear disclaimer.
**Impact:** Throughout paper.

---

## P3: Polish (nice to have, not blocking)

### 9. Add Tie-Breaking Documentation
**Current:** Code breaks ties toward 1; paper says "either."
**Fix:** Document the tie-breaking choice and note it doesn't affect asymptotic results.
**Impact:** Theorem 1 remark, code comments.

### 10. Verify RL Proposition Numbers
**Current:** Proposition 1 claims Omega(log n) factor.
**Fix:** The proof sketch is correct. Add the full proof from THEORY_NOTE.md.
**Impact:** Section 2.4.

### 11. Add Constant-Omission Remark for NML
**Current:** Code omits (1/2) log(pi/2) per orbit class.
**Fix:** Note that this constant (≈ 0.326 bits per class) is omitted but does not
  affect asymptotic model selection since it's O(k) = O(1) relative to T.
**Impact:** Definition 3 or a footnote.

### 12. Discuss Combinatorial Score Alternative
**Current:** Only BIC+RL and NML scores discussed.
**Fix:** Note that raw template bits (k bits) + log2(binom(N,w)) fails to prevent
  overcapacity because the template cost is O(1) relative to T.
**Impact:** Discussion section.

---

## Implementation Order

1. Fix Theorem 2 statement and proof (P1.1) — purely textual
2. Choose NML as primary score (P1.3) — aligns code and paper
3. Rewrite Theorem 3 for NML (P1.2) — cleaner proof, fewer assumptions
4. Rename code functions (P1.4) — mechanical
5. Add abstract partition theorems (P2.6) — strengthens theory
6. Promote nonidentifiability (P2.5) — genuine contribution
7. Fix empirical language (P2.7) — throughout
8. Polish (P3) — final pass

---

## Files to Modify

| File | Changes |
|------|---------|
| `paper/paper_v7.md` | New version with all fixes |
| `src/relative_symmetry_repair/coding.py` | Rename functions, fix docstrings |
| `src/relative_symmetry_repair/repair.py` | Update comments, aliases |
| `src/relative_symmetry_repair/repair_nd.py` | Update comments |
| `src/relative_symmetry_repair/cli.py` | Update if function names change |
| `tests/test_theory.py` | Already written (this session) |
| `scripts/find_counterexamples.py` | Already written (this session) |
| `scripts/compare_scores.py` | Already written (this session) |
