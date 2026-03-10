# Claim Ledger

Every major claim in paper_v6.md, classified and assessed.

---

## Theorem 1 (Optimal Hamming Projection) — Section 2.2

**Claim:** Majority vote on each orbit class minimizes Hamming distance to B(p,s). Minimum is sum_j min(n_j^(0), n_j^(1)). Unique iff no ties.

**Status:** CORRECT AS STATED

**Proof status:** Complete. The decomposition over orbit classes is additive because orbit classes partition spacetime, and B is constant on each class. Each class contributes independently. QED.

**Abstract/intro update needed:** No.

---

## Theorem 2 (Monotonicity) — Section 2.3

**Claim:** If p2 = m * p1 with the same shift s, then the orbit partition under p2 refines the partition under p1, and d*(p2,s) <= d*(p1,s).

**Status:** FALSE AS STATED

**Counterexample:** D=4 (width 4), T=4, p1=1, s=1, p2=2, s=1.
Spacetime = checkerboard (diagonal stripes):
```
0 1 0 1
1 0 1 0
0 1 0 1
1 0 1 0
```
- Under (p1=1, s=1): 4 orbit classes (diagonals). Spacetime is exactly periodic. d*(1,1) = 0.
- Under (p2=2, s=1): 8 orbit classes. Each spans TWO different p1-diagonals. The p2-orbit of (0,0) contains {(0,0)=0, (2,1)=1}, which are from different p1-classes with different values. d*(2,1) = 4.

So d*(2,1) = 4 > 0 = d*(1,1). Monotonicity fails.

**Root cause:** The map tau_2: (t,x) -> (t+2, (x+1) mod 4) is NOT a power of tau_1: (t,x) -> (t+1, (x+1) mod 4). The 2nd power of tau_1 is (t+2, (x+2) mod 4), which has shift 2, not 1. So the p2 partition is transverse to, not a refinement of, the p1 partition.

**Strongest corrected replacement:**

**Theorem 2 (Corrected Monotonicity).** If p2 = m * p1 and s2^(i) = m * s1^(i) (mod D_i) for each spatial dimension i, then the orbit partition under (p2, s2) refines the partition under (p1, s1), and d*(p2, s2) <= d*(p1, s1).

*Proof:* The (p2,s2) periodicity map tau_2(t,x) = (t + m*p1, (x + m*s1) mod D) = tau_1^m(t,x). So the tau_2-orbit of any point is a subset of its tau_1-orbit. Hence the tau_2-partition refines tau_1. By Theorem 1, optimizing over a finer partition can only reduce Hamming distance. QED.

**Special cases where the original "same shift" statement holds:**
- s = 0: Then m*0 = 0 for all m. Monotonicity along {p, 2p, 3p, ...} with shift 0 is valid.
- D_i | (m-1)*s_i for all i: Then m*s_i = s_i mod D_i.

**Abstract/intro update needed:** Yes. The abstract says "higher periods monotonically more expressive." This must be qualified: "along constant-velocity chains" or "with proportionally scaled shifts."

---

## Corollary (Overcapacity) — Section 2.3

**Claim:** Along any divisibility chain p, 2p, 3p, ..., defect rate is monotonically non-increasing.

**Status:** FALSE AS STATED (inherits Theorem 2 bug)

**Corrected:** "Along any constant-velocity divisibility chain (mp, ms mod D) for m = 1, 2, 3, ..., defect rate is monotonically non-increasing." For shift 0, the original statement holds.

**Abstract/intro update needed:** Yes.

---

## Definition 3 (Two-Part MDL Criterion) — Section 2.4

**Claim:** MDL(p,s) = (k/2) log2(T/p) + L_RL(M*). First term is "asymptotic parametric complexity for k Bernoulli parameters." "It approximates NML stochastic complexity but is not exact NML."

**Status:** CORRECT AFTER EDIT

**Issues:**
1. The term (k/2) log2(T/p) is the BIC approximation (or Rissanen's asymptotic stochastic complexity), not NML. The paper correctly disclaims exact NML, but should use the term "BIC-type penalty" or "asymptotic stochastic complexity."
2. The paper says "each estimated from floor(T/p) observations." This is the number of repetitions per orbit class, which is correct.
3. CRITICAL MISMATCH: The code's CLI and convergence scripts actually use `nml_bits` (NLL + NML complexity), not `mdl_bits` (BIC penalty + RL bits). The paper's Theorem 3 is stated for `mdl_bits`, but the reported experiments may use `nml_bits`.

**Strongest corrected replacement:** Keep the definition but rename: "BIC-type parametric penalty" instead of "asymptotic NML parametric complexity."

---

## Proposition 1 (Run-Length Separation) — Section 2.4

**Claim:** Two masks of same size and Hamming weight can have RL codelengths differing by factor Omega(log n).

**Status:** CORRECT AS STATED

**Proof status:** Adequate sketch. Clustered mask: O(log n) bits. Scattered mask with w = Theta(log n) isolated defects: Omega(w * log(n/w)) = Omega((log n)^2) bits. Ratio: Omega(log n).

**Abstract/intro update needed:** No.

---

## Remark (No convergence to "true" period) — Section 2.5

**Claim:** If defects have periodic structure, a larger period can absorb them and win for all large T.

**Status:** CORRECT AS STATED

This is an important honesty statement. Should be promoted to a formal proposition (see THEORY_NOTE.md).

---

## Theorem 3 (MDL Consistency) — Section 2.5

**Claim:** Under (A1) ergodic defect rates and (A2) Omega(T) runs, MDL-selected candidate stabilizes to the unique minimizer of asymptotic per-site RL rate.

**Status:** CORRECT AFTER EDIT

**Issues:**
1. **Proof gap:** The claim that (A2) implies L_RL(T)/T converges is asserted but not proved. Having Omega(T) runs does NOT by itself guarantee convergence of the per-site RL rate. A counterexample: a mask where half the runs have length 1 and one run has length T/2. This has Theta(T) runs, but the RL cost depends on the specific run-length distribution, not just the count.

2. **Assumption (A2) is insufficient:** You need convergence of the empirical run-length distribution, which is a stronger ergodic condition. Or: replace RL with the NML score, for which convergence follows directly from (A1) alone.

3. **Code/paper mismatch:** The convergence experiments use `nml_bits`, not `mdl_bits`. Theorem 3 should either be restated for the NML score, or the experiments should be re-run with `mdl_bits`.

**Strongest corrected replacement (Option 1 — NML score, recommended):**

**Theorem 3 (Model Selection Stabilization).** Let C be a finite candidate set. For each candidate c, define:
  NML(c, T) = NLL_c(T) + COMP_c(T)
where NLL_c(T) = sum_j n_j H(theta_hat_j) is the Bernoulli NLL over orbit classes, and COMP_c(T) = (k_c/2) log2(T/p_c) + O(k_c) is the asymptotic NML complexity.

Assume (A1): for each candidate c, the per-site entropy h_c = lim_{T->inf} NLL_c(T)/T exists.

Then the NML-selected candidate stabilizes: there exists T_0 such that c*(T) = c*(T_0) for all T > T_0. The limit minimizes h_c, with ties broken by k_c (fewer parameters preferred).

*Proof:* NML(c,T) = h_c * T + (k_c/2) log T + O(1). Pairwise differences are dominated by the linear term when h values differ, and by the log term when they agree. Since |C| is finite, all comparisons stabilize. QED.

**Strongest corrected replacement (Option 2 — keep RL but fix assumptions):**

Add assumption (A2'): The per-site RL rate ell_c = lim_{T->inf} L_RL(M*_c(T))/T exists for each candidate c.

This is a direct assumption, not derived from Omega(T) runs.

**Abstract/intro update needed:** Yes — "MDL consistency" should say "model selection stabilization" and specify which score.

---

## Corollary (Dimension-agnostic) — Section 2.5

**Claim:** Theorem 3 applies identically to 1D, 2D, 3D.

**Status:** CORRECT AS STATED (given Theorem 3 is corrected)

---

## Empirical Claims — Section 3

### "MDL-selected periods stabilize" (Section 3.4)

**Status:** HEURISTIC / EMPIRICAL ONLY

The data shows empirical stabilization over the tested range [T=50..800]. This is consistent with the (corrected) theorem but does not prove convergence. The paper correctly uses "stabilize" rather than "converge" in most places.

**Issue:** Section 3.2.3 shows S24/B11 selected period jumping 2→4→6 as T increases, and S11/B37 jumping 2→4→8. The paper says these "then lock with growing margins." But at T=800, how do we know the period won't jump again at T=1600? We don't. The data supports "stabilization over the tested range."

### "Known complexity hierarchy recovered" (Section 3.1)

**Status:** EMPIRICAL ONLY

The paper observes Rule 54 < Rule 110 < Rule 30 by MDL ranking. This is an observation, not a theorem.

### "Extensive defect scaling in S37/B11" (Section 4.2)

**Status:** EMPIRICAL ONLY

Defect density ~0.011 across grid sizes 32-192 is consistent with extensive scaling. But 5 grid sizes is not a proof of asymptotic behavior.

---

## Code vs Paper Alignment

| Code entity | Paper claim | Match? |
|---|---|---|
| `template_bits_nml` | BIC-type penalty | Name says "NML", paper says "approximates NML" — MISLEADING NAME |
| `nml_score_bits` | Not in Theorem 3 | Code uses this for selection; paper's theorem is about mdl_bits — MISMATCH |
| `nml_complexity_bits` | "exact NML" in docstring | Asymptotic, not exact — OVERCLAIMED |
| `mdl_total_bits` | Definition 3 | Matches — but labelled "legacy" in code |
| Tie-breaking: `2*ones >= totals` | "either" in Theorem 1 | Code breaks ties toward 1; paper says "either" — MINOR |

---

## Summary of Changes Required

| Claim | Status | Action |
|---|---|---|
| Theorem 1 | CORRECT | No change |
| Theorem 2 | FALSE | Restate with velocity condition |
| Overcapacity Cor. | FALSE | Restate with velocity condition |
| Proposition 1 | CORRECT | No change |
| Theorem 3 | CORRECT AFTER EDIT | Fix assumptions; align with NML score |
| Dim-agnostic Cor. | CORRECT | No change (follows from corrected Thm 3) |
| No true-period Remark | CORRECT | Promote to formal proposition |
| NML terminology | OVERSTATED | Rename in code, clarify in paper |
| Empirical claims | HEURISTIC/EMPIRICAL | Clarify language |
