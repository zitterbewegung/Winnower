# Claim Ledger

Status of every formal claim in the project's long-form theory notes (the
internal `paper_v8`/`paper_v15` lineage, preserved under `_archive/paper_drafts/`
and `proofs/aristotle_submissions/shared_context/`). Section numbers below
refer to those notes, not to the conference manuscript.

**How this maps to the current manuscript** (`paper/paper_alife2026.tex`):
the manuscript deliberately keeps formal machinery out of the main text and
states only three things — a proposition that majority vote is the optimal
orbit-class fit, and two informal properties ("why the penalty is necessary"
and "why selections stabilize"). Their formal counterparts here are:

| Manuscript statement | Ledger entry |
|---|---|
| Proposition (majority vote is optimal) | Theorem 1 (Optimal Hamming Projection) |
| Property: penalty necessary (velocity-matched refinement only improves fit) | Theorem 2 (Monotonicity under Velocity-Matched Refinement) + Corollary (Overcapacity) |
| Property: selections stabilize | Theorem 3 (Rate-Based Elimination and Stabilization) |

Everything else in this ledger (Theorems 4–5, Proposition 1 on run-length
codelength, Appendix D) supports the longer-form notes only and is **not
claimed in the manuscript**. The manuscript's experimental claims rest on the
reproducible pipeline, not on these theorems.

**Score-definition note.** Definition 4 below states the complexity term as
the asymptotic Σ (1/2)·log2 n_j. The shipped implementation
(`nml_mode="hybrid"`) computes the exact Shtarkov complexity for classes with
n ≤ 200 and (1/2)·log2(π·n/2) above. Exact regret = (1/2)·log2(π·n/2) + o(1),
so hybrid and asymptotic scores differ by O(k_c) per candidate — constant in
T — and every asymptotic conclusion in this ledger transfers to the hybrid
score unchanged.

---

## Theorem 1 (Optimal Hamming Projection) — Section 2.2

**Claim:** For a fixed orbit partition, the Hamming-optimal orbit-constant background is obtained by majority vote on each orbit class. The minimum residual count is `sum_j min(n_j^(0), n_j^(1))`. The minimizer is unique iff no orbit class has an exact tie.

**Status:** CORRECT AS STATED

**Why:** The Hamming objective decomposes additively over orbit classes, and each class is an independent one-bit optimization.

**Residual caution:** None beyond finite-set formalization details.

---

## Theorem 2 (Monotonicity under Velocity-Matched Refinement) — Section 2.3

**Claim:** If `p2 = m * p1` and `s2^(i) = m * s1^(i) mod D_i` for each spatial dimension, then the `(p2, s2)` orbit partition refines the `(p1, s1)` partition, hence the optimal residual count cannot increase.

**Status:** CORRECT AS STATED

**Why:** Under the velocity-matching condition, the second periodicity map is the `m`-fold iterate of the first, so every fine orbit is contained in a coarse orbit.

**Residual caution:** The theorem must not be generalized back to “same shift, larger period” without the scaling condition. That statement is false.

---

## Corollary (Overcapacity) — Section 2.3

**Claim:** Along constant-velocity divisibility chains, residual count is monotonically non-increasing, so naive residual minimization overfits toward higher-capacity models.

**Status:** CORRECT AS STATED

**Residual caution:** The scope is exactly the velocity-matched chain, not arbitrary period scans.

---

## Definition 4 (Bernoulli NML Score) — Section 2.4

**Claim:** The score used for selection is orbit-class Bernoulli NLL plus the asymptotic per-class complexity term `sum_j (1/2) log_2 n_j`.

**Status:** CORRECT AFTER CLARIFICATION

**Why:** This is an asymptotic Bernoulli NML-style score, not exact finite-sample NML.

**Residual caution:** The paper now says this explicitly. Any future Lean formalization should treat exact NML and asymptotic NML as different objects.

---

## Theorem 3 (Rate-Based Elimination and Stabilization) — Section 2.5

**Claim:** Under convergent orbit-class frequencies:

1. `NLL(c,T) / N(T) -> lambda_c`.
2. `NML(c,T) = lambda_c * N(T) + (k_c / 2) log_2 T + o(N(T))`.
3. If `lambda_a < lambda_b`, then candidate `a` eventually beats candidate `b`.
4. Every candidate whose rate exceeds `lambda*` is eventually excluded.
5. If the rate-minimizer is unique, selection stabilizes to that unique candidate.

**Status:** CORRECT AFTER EDIT

**Why:** The current version is the strongest theorem that the draft honestly supports from the asymptotic expansion. It no longer overclaims tie-breaking among equal-rate candidates. The theory note's E.1 has been restated to match: E.1a (elimination + unique-rate-minimizer stabilization, the Lean-checked core) plus E.1b (complexity tie-breaking under an explicit bounded-NLL-gap hypothesis, discharged for eventually-exactly-periodic data), plus an explicit non-conclusion for equal-period shift ties.

**What changed from earlier drafts:** The theorem is now built around pairwise eventual ordering and elimination, with full stabilization only as a corollary under a unique rate-minimizer.

**Residual caution:**
- The theorem does not resolve equal-rate ties.
- Logarithmic tie-breaking needs a stronger remainder hypothesis such as `o(log T)`.
- Same-period different-shift candidates share the same complexity term, so even logarithmic tie-breaking will not separate them without extra rules.

---

## Theorem 4 (Nonidentifiability for Bernoulli NML) — Section 2.6

**Claim:** For any baseline period `p0` and shift `s`, there exists a spacetime and a higher-period velocity-matched candidate such that:

1. the baseline candidate has positive asymptotic NLL rate,
2. the higher-period candidate has zero asymptotic NLL rate,
3. the higher-period candidate eventually wins under Bernoulli NML.

**Status:** CORRECT AFTER EDIT

**Why:** The current manuscript theorem is now matched to the proof sketch. It is an existence theorem for the Bernoulli NML selector, proved by explicit construction.

**What changed from earlier drafts:** The claim is no longer phrased for a generic “MDL-type criterion” that the proof did not actually instantiate. It is now explicitly about Bernoulli NML and the two concrete candidates in the construction.

**Residual caution:** The proof in the paper is still a proof sketch. The key formal burden for Aristotle/Lean is showing precisely why `B != B'` forces `lambda_c0 > 0`.

---

## Definition 5 (True Background Period) — Section 2.7

**Claim:** The true background period is the smallest period such that, after some finite transient time, the spacetime becomes exactly relative-periodic.

**Status:** CORRECT AFTER EDIT

**Why:** This is the right hypothesis for the proof that follows. The older “asymptotically pure orbit classes” formulation was too weak for the manuscript’s `O(1)` NLL-difference argument.

---

## Theorem 5 (Identifiability for Eventually Exactly Periodic Backgrounds) — Section 2.7

**Claim:** If the spacetime is eventually exactly relative-periodic with minimal period `p0`, then for any velocity-matched strict multiple `p = m * p0`:

1. both candidates have per-site NLL rate `0`,
2. their NLL difference is `O(1)`,
3. the complexity gap is `((m - 1) * k_p0 / 2) log_2 T + O(1)`,
4. therefore the higher-period model is eventually worse and NML selects `p0`.

**Status:** CORRECT AFTER EDIT

**Why:** The theorem now assumes exactly what the proof uses: only finitely many transient rows contribute nonzero NLL, so the NLL gap stays bounded while complexity diverges.

**What changed from earlier drafts:** The theorem no longer tries to derive the `O(1)` NLL difference from mere asymptotic purity. It uses eventual exact periodicity after a finite transient.

**Residual caution:** The theorem is intentionally narrower than the old prose intuition. If you want a theorem under weaker asymptotic assumptions, that will need a different argument.

---

## Proposition 1 (Run-Length Separation) — Section 2.8

**Claim:** Two same-size binary masks with the same Hamming weight can have run-length codelengths differing by an `Omega(log n)` factor.

**Status:** CORRECT AS STATED

**Residual caution:** None, beyond keeping it clearly marked as a geometric diagnostic rather than a model-selection theorem.

---

## Theorem D.2 (RL Rate Convergence for Finite CA) — Appendix D

**Claim:** For deterministic CA on a finite spatial domain, under the no-exact-frequency-ties condition, the run-length codelength per site of the Hamming-optimal residual mask converges.

**Status:** CORRECT — FULL WRITE-UP IN THEORY_NOTE G.2

**Why:** The proof route, now written out in full (THEORY_NOTE G.1/G.2 with completing remarks covering per-horizon refitting, finite-sample tie-breaks, multidimensional shift periods, seam runs, and the constant-mask edge case of Lemma G.1):

1. finite deterministic CA implies eventual periodicity of the state sequence,
2. no exact ties implies majority decisions stabilize,
3. stabilized residual mask becomes eventually periodic,
4. eventual periodicity implies RL-rate convergence.

**Residual caution:** Now proved at prose level with a computational verification test (`tests/test_theory.py::TestRLConvergence`); Lean formalization remains an open Aristotle target.

---

## Corollary D.3 (Unconditional NLL Convergence for Finite CA) — Appendix D

**Claim:** For deterministic finite-domain CA, per-site Bernoulli NLL converges without any no-ties assumption.

**Status:** CORRECT IN SUBSTANCE

**Why:** NLL depends on orbit-class frequencies through binary entropy, and entropy is continuous even at the exact `1/2` case. Tie-breaking affects the majority-vote residual mask, not the NLL itself.

**Residual caution:** Best formalized as an abstract orbit-frequency convergence statement, with CA eventual periodicity used only to discharge the convergence assumption.

---

## Empirical Claims — Section 3 and Section 4

### Period stabilization in experiments

**Status:** EMPIRICAL ONLY

**Claim:** The selected period locks over the tested horizon and margins grow after locking.

**Assessment:** Supported over the observed `T` ranges. This is consistent with Theorem 3 but does not prove asymptotic behavior beyond the tested windows.

### Rule rankings and highlighted rules

**Status:** EMPIRICAL ONLY

**Claim:** Rule 54 < Rule 110 < Rule 30 under NML, Diamoeba/Fredkin behavior in LifeWiki survey, and the selected 2D persistent-residual rules.

**Assessment:** These are observational results, not theorem-level claims.

### Extensive scaling in S37/B11

**Status:** EMPIRICAL ONLY

**Claim:** Approximately constant defect density across tested system sizes is consistent with extensive scaling.

**Assessment:** Reasonable empirical interpretation, but not an asymptotic proof.

---

## Code vs Paper Alignment

| Code entity | Paper claim | Match? |
|---|---|---|
| `nml_score_bits` | Bernoulli NML selector | YES |
| `mdl_bits` | Legacy RL-based criterion | YES, now clearly secondary |
| tie break `2 * ones >= totals` | deterministic projection tie-break | YES, manuscript now says ties are broken deterministically |
| asymptotic complexity term | asymptotic, not exact NML | YES, with explicit manuscript caveat |

---

## Current Bottom Line

| Claim | Status | What remains |
|---|---|---|
| Theorem 1 | CORRECT | Lean formalization should be straightforward |
| Theorem 2 | CORRECT | Lean formalization should be straightforward |
| Theorem 3 | CORRECT AFTER EDIT | Lean should target pairwise comparison first |
| Theorem 4 | CORRECT AFTER EDIT | Lean needs the construction details made explicit |
| Theorem 5 | CORRECT AFTER EDIT | Lean should use eventual exact periodicity, not asymptotic purity |
| Proposition 1 | CORRECT | Optional to formalize |
| Theorem D.2 | CORRECT (full write-up in THEORY_NOTE G.2) | Lean formalization open |
| Corollary D.3 | CORRECT IN SUBSTANCE | Good appendix formalization target |
| Experimental claims | EMPIRICAL ONLY | Keep language modest |
