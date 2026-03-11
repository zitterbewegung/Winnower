```text
Formalize and prove Theorem 1 from the attached paper `paper_v8.md`.

Please work in a finite combinatorial setting only. You do not need to formalize the CA update rule; only formalize the finite binary data and the orbit partition induced by a fixed candidate symmetry class.

Target mathematical content:

- We have a finite binary dataset U on a finite set of sites.
- A fixed candidate model induces a finite partition of the sites into orbit classes.
- A candidate background B is constrained to be constant on each orbit class.
- Hamming distance d(U,B) is the number of sites where U and B disagree.

Target claim:

For each orbit class O_j, let n_j^(1) be the number of 1s of U on that class and n_j^(0) the number of 0s. Then:

1. The Hamming distance decomposes as a sum over orbit classes.
2. A Hamming-optimal orbit-constant background is obtained by choosing, independently on each orbit class, the majority bit.
3. The minimum residual count is the sum over orbit classes of min(n_j^(0), n_j^(1)).
4. The minimizer is unique if and only if no orbit class has exactly equal numbers of 0s and 1s.

Instructions:

1. State the theorem in Lean in the cleanest finite form.
2. Make all assumptions explicit.
3. Prove it without `sorry`, `admit`, or extra `axiom`.
4. If the manuscript wording is underspecified, produce the weakest corrected formal statement and explain exactly what changed.
5. Prefer a formulation that is easy to compare line-by-line with `paper_v8.md`.
```
