```text
Formalize and prove the monotonicity theorem corresponding to Theorem 2 from the attached paper `paper_v8.md`.

Please avoid unnecessary CA-specific machinery. Work with finite sets, finite partitions, and refinement first.

Target mathematical content:

- A candidate model induces a partition of the finite site set.
- If partition P2 refines partition P1, then every block of P2 is contained in a block of P1.
- For each partition, define the optimal Hamming residual count as the minimum over binary functions that are constant on each block.

Target claim:

If partition P2 refines partition P1, then the optimal Hamming residual count under P2 is less than or equal to the optimal Hamming residual count under P1.

After proving that abstract refinement theorem, if convenient, instantiate it to the paper's relative-periodic setting under the compatibility condition:

- p2 = m * p1
- s2^(i) is congruent to m * s1^(i) modulo each spatial period D_i

and show that this implies orbit-partition refinement.

Instructions:

1. Separate clearly the abstract partition-refinement theorem from the relative-periodic corollary.
2. Make the compatibility condition precise.
3. Do not claim monotonicity beyond the velocity-matched case justified in the manuscript.
4. If the manuscript theorem needs weakening, provide the corrected theorem and explain the gap.
5. Prove everything without `sorry`, `admit`, or extra `axiom`.
```
