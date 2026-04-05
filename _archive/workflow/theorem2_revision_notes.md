# Theorem 2 Revision Notes

## What was replaced

**Old Theorem 2** ("Monotonicity under Velocity-Matched Refinement"): A sufficient condition — if velocity-matched divisibility holds, then the orbit partition refines and Hamming residual counts are monotone non-increasing. The proof was a short forward implication. An accompanying remark showed the condition is necessary via a counterexample, but this was informal. The corollary addressed overcapacity only at the Hamming level.

**New Theorem 2** ("Exact Characterization of Universal Refinement and Monotonicity"): A six-way equivalence proving that velocity-matched divisibility (i), translation power (ii), orbit partition refinement (iii), model nesting (iv), universal Hamming monotonicity (v), and universal NLL monotonicity (vi) are all equivalent. The proof includes both forward and reverse implications, with an explicit adversarial construction for necessity. The corollary now addresses overcapacity at both the Hamming and likelihood levels.

## What surrounding prose was updated

1. **Abstract** (line 5): Updated description of Theorem 2 from "partition refinement along constant-velocity chains makes higher periods monotonically more expressive" to the exact characterization language including both Hamming and NLL monotonicity.

2. **Contributions list** (Section 1.1, item 2): Rewritten from "higher periods achieve lower residual counts" to "velocity-matched divisibility is proved equivalent to partition refinement, model nesting, and universal monotonicity of both Hamming residuals and Bernoulli NLL."

3. **Section 5.1** ("What the Theory Provides", item 2): Changed from "A formal explanation of overcapacity" to "An exact characterization of overcapacity" with both Hamming and NLL language.

4. **Section 5.1** (key insight paragraph): Added explicit connection between Theorem 2's exact characterization and why NLL-only selection overfits.

5. **Section 3.5** (Baseline Selector Comparison, interpretive paragraph): Connected the observed NLL overfitting directly to Theorem 2's monotonicity guarantee. Final sentence now references overcapacity "at both the Hamming and likelihood levels."

6. **Section 5.6** (Limitations, item 0): Changed from "Monotonicity requires velocity matching" to "Monotonicity is exactly velocity matching," noting that Theorem 2 now proves necessity (not just sufficiency).

## Notation

No notation conflicts were found. The new theorem uses:
- $c_i = (p_i, \mathbf{s}_i)$ — consistent with existing notation
- $\tau_i$ for translation maps — newly introduced, not conflicting
- $\Pi_i$ for orbit partitions — newly introduced, not conflicting
- $\mathcal{B}_i$ for model classes — consistent with existing usage
- $d_U^*(c_i)$ for Hamming residuals — consistent with Theorem 1's $d^*$ notation
- $\mathrm{NLL}_U(c_i)$ — consistent with Definition 3

The theorem references Definition 3 (orbit-class Bernoulli model) and Theorem 1 explicitly, which are both present and unchanged.

## Optional remark

**Included.** The remark appears after the proof and before the corollary, stating that failure of condition (i) implies existence of a spacetime violating both monotonicity inequalities. This replaces the old counterexample-based remark with the stronger contrapositive statement derived from the necessity proof.

## Experiment tables

No experiment tables were modified. All empirical results are preserved exactly.
