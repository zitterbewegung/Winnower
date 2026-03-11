```text
Formalize and prove a rigorous version of Theorem 4 from the attached paper `paper_v8.md`.

The manuscript now gives an explicit construction rather than only an informal nonidentifiability slogan. The target idea is:

- fix a baseline period p0 and shift s
- choose two distinct exactly (p0, s)-periodic binary fields B and B'
- build a spacetime U that alternates between B and B' on residue classes of floor(t / p0) mod q
- under the baseline candidate (p0, s), some orbit classes mix B and B' values, so the asymptotic per-site NLL rate is positive
- under the higher-period candidate (q * p0, q * s mod D), the q layers separate and all orbit classes are pure, so the asymptotic per-site NLL rate is 0
- therefore the higher-period candidate eventually wins because it improves the linear term while only paying logarithmic complexity cost

Tasks:

1. State a precise theorem capturing this construction, either directly or through an abstract comparison lemma plus a concrete instance.
2. Make explicit what assumptions on B and B' are needed to ensure the lower-period candidate has positive asymptotic rate.
3. Prove the eventual defeat of the lower-period candidate.
4. If the full constructive statement is too cumbersome, at minimum prove the abstract comparison theorem and then formalize the construction assumptions clearly.

Requirements:

- Make all assumptions explicit.
- Avoid hidden appeals to intuition about residual absorption.
- If the manuscript statement is too strong, provide the weakest corrected theorem that still supports the intended interpretation.
- Prove the result without `sorry`, `admit`, or extra `axiom`.
```
