# Verdict

## Current Manuscript (paper_v6.md)

The paper contains a genuine and useful theoretical contribution — the orbit-class
reduction and stabilization theorem for periodic model selection — but has three
critical mathematical errors that block publication as-is: (1) Theorem 2 (monotonicity)
is false as stated, with an explicit counterexample on D=4 checkerboard data where the
"higher period" model is *worse* (d*(2,1) = 4 > 0 = d*(1,1)); (2) Theorem 3's proof
has a gap — the assumption that defect masks have Omega(T) runs does not imply
convergence of the per-site run-length rate, and the paper's stated score (BIC + RL)
does not match the code's actual score (NLL + NML complexity); (3) "NML" terminology
is used loosely, with the code's asymptotic approximation labelled "exact NML" in
several places. The nonidentifiability remark (Section 2.5) is correct and important
but should be a formal theorem. Theorem 1 (orbit-class reduction) is fully correct.
The empirical results are sound but should use "stabilization over the tested range"
rather than "convergence confirmed."

## Strongest Corrected Manuscript

The strongest correct version would contain five theorems:

**Theorem A (Partition Projection):** Identical to current Theorem 1. Correct as stated.

**Theorem B (Partition-Refinement Monotonicity):** Abstract result: finer partitions
yield lower Hamming distance. No reference to periods or shifts. Unconditionally true.

**Theorem C (Relative-Periodic Corollary):** The orbit partition under (p2, s2) refines
that under (p1, s1) if and only if p2 = m*p1 and s2 = m*s1 (mod D_i). This is the
"constant velocity" condition. For shift-0 scanning (the empirically dominant case),
the original monotonicity holds along all divisibility chains.

**Theorem D (Nonidentifiability):** No procedure based solely on the observed spacetime
can generally recover the "true background period." Periodic defect structure can be
absorbed by higher-period templates that achieve lower total description length.

**Theorem E (Bernoulli-NML Stabilization):** For a finite candidate set, the
NML-selected model stabilizes under the single assumption that per-orbit empirical
frequencies converge. This is cleaner than the RL-based version, requires no
"Omega(T) runs" assumption, and aligns with the code's actual selection criterion.

## What Still Blocks Acceptance

1. The monotonicity theorem must be corrected (mechanical fix, counterexample is definitive).
2. The score used in Theorem 3 must match the code (switch to NML score or re-run experiments).
3. The "NML" terminology must be honest (rename to "asymptotic NML" or "BIC-type" throughout).
4. Empirical language must distinguish "stabilization over tested range" from "proved convergence."

## What Has Been Resolved Since Initial Audit

The convergence gap in Theorem 3 has been closed with a rigorous proof:
- For the NML score: convergence is *unconditional* for finite deterministic CA
  (Corollary G.3). No ergodic assumptions needed beyond finiteness.
- For the RL score: convergence holds under a "no exact ties" assumption
  (Theorem G.2), proved via: finite CA → eventually periodic states →
  stable majority vote → eventually periodic mask → convergent L_RL/N (Lemma G.1).
- Both are verified computationally (27 tests pass).

None of the remaining issues are fatal. The paper has a publishable core; it needs
surgical corrections, not a rewrite. Estimated effort: 2-3 days for a careful revision.
