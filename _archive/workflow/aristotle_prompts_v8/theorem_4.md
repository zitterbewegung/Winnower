```text
Formalize and prove a rigorous version of Theorem 4 from the attached paper `paper_v8.md`.

The manuscript theorem is now explicitly about Bernoulli NML, not a generic MDL-type criterion. The target idea is:

- fix a baseline period p0 and shift s
- choose an integer q > 1
- choose two distinct exactly (p0, s)-periodic binary fields B and B'
- build a spacetime U that alternates between B and B' on residue classes of floor(t / p0) mod q
- under the baseline candidate c0 = (p0, s), some orbit classes mix B and B' values, so the asymptotic per-site NLL rate is positive
- under the higher-period candidate (q * p0, q * s mod D), the q layers separate and all orbit classes are pure, so the asymptotic per-site NLL rate is 0
- therefore the higher-period candidate c1 eventually wins by Theorem 3's pairwise comparison result

Tasks:

1. State a precise theorem capturing this construction, either directly or through an abstract comparison lemma plus a concrete instance.
2. Make explicit why B != B' implies lambda_c0 > 0 for the lower-period candidate.
3. Prove that lambda_c1 = 0 for the higher-period candidate.
4. Prove the eventual defeat of c0 by c1.
5. If the full constructive statement is too cumbersome, at minimum prove the abstract comparison theorem and then formalize the construction assumptions clearly.

Requirements:

- Make all assumptions explicit.
- Avoid hidden appeals to intuition about residual absorption.
- If the manuscript statement is too strong, provide the weakest corrected theorem that still supports the intended interpretation.
- Prove the result without `sorry`, `admit`, or extra `axiom`.
```
