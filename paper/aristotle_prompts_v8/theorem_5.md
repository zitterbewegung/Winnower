```text
Formalize and prove a rigorous version of Theorem 5 from the attached paper `paper_v8.md`.

The manuscript's target statement is now:

- p0 is the smallest period whose orbit classes are asymptotically pure
- p = m * p0 is a velocity-matched strict multiple
- both models have per-site NLL rate 0
- the NLL difference is bounded by O(1), coming only from finitely many transient defects
- the complexity difference is ((m - 1) * k_p0 / 2) * log(T) + O(1)
- therefore the higher-period model is eventually worse and NML selects p0 over p

Please convert this into a precise formal theorem.

Tasks:

1. Decide whether to formalize it as an abstract score comparison theorem or directly in terms of pure orbit classes and candidate scores.
2. Make explicit what "true background period" and "asymptotically pure" mean in the formal statement.
3. Prove that the per-site rates are both 0.
4. Prove the bounded NLL-difference claim under the transient-defect hypothesis actually used by the manuscript.
5. Prove that the logarithmic complexity term eventually dominates.

Important:

- Be careful about what is genuinely assumed versus what the prose only hints at.
- If the O(1) NLL-difference claim needs stronger hypotheses than the manuscript states, identify them clearly.
- If needed, weaken the theorem and explain the changes.

Requirements:

- No `sorry`, `admit`, or extra `axiom`.
- Keep the result easy to compare back to `paper_v8.md`.
```
