```text
Formalize and prove the strongest correct Lean version of Theorem 3 from the attached paper `paper_v8.md`.

The revised theorem in `paper_v8.md` is intentionally weaker than the earlier draft. It does not claim unconditional unique winner stabilization in all tie cases. Instead it claims:

- each candidate c has an asymptotic score of the form
  NML(c,T) = lambda_c * N(T) + (k_c / 2) * log(T) + o(N(T))
- every candidate with lambda_c strictly larger than the minimum lambda* is eventually excluded
- if the minimizer of lambda_c is unique, then the selected candidate stabilizes to that unique minimizer

Please choose a precise formal statement that captures this elimination-plus-unique-minimizer argument.

Target tasks:

1. Decide on a precise finite-candidate theorem statement.
2. Replace informal asymptotic notation by explicit assumptions whenever helpful.
3. Prove a pairwise exclusion lemma: if lambda_a > lambda_b and score_a(T) - score_b(T) = (lambda_a - lambda_b) * N(T) + o(N(T)), then score_a(T) > score_b(T) eventually.
4. Derive the finite-candidate elimination result.
5. Derive the unique-rate-minimizer stabilization corollary.

Important:

- Be careful about `argmin` definitions and uniqueness.
- Do not try to prove logarithmic tie-breaking unless it follows from stronger assumptions that you state explicitly.
- If the manuscript theorem is still too informal, give the weakest corrected version that Lean can support and explain the difference.

Please return:

1. A Lean theorem statement for the strongest correct version.
2. A full proof with no `sorry`, `admit`, or extra `axiom`.
3. A short English note explaining any differences from the manuscript theorem.
```
