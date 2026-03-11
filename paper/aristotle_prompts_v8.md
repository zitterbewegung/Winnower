# Aristotle Prompts For `paper_v8.md`

## Recommended Submission Workflow

Use Aristotle in `Mode [3] Direct Aristotle in English` first.

For each theorem:

1. Press `Ctrl+T` and paste one prompt from this file.
2. Press `Ctrl+F` and attach `/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_v8.md` as English context.
3. If you already have a Lean skeleton file, press `Ctrl+L` and attach it as Lean context.
4. Press `Ctrl+S` to submit.
5. When Aristotle returns, check:
   - the Lean file compiles,
   - there is no `sorry`,
   - there is no `admit`,
   - there is no extra `axiom`,
   - the formal theorem statement matches the manuscript claim.

Recommended order:

1. Theorem 1
2. Theorem 2
3. Theorem 3
4. Theorem 4
5. Theorem 5
6. Appendix D, if needed

`paper_v8.md` is more formal than `paper_v7.md`, especially in Theorem 3. The main thing to test is whether the revised statement really matches what Lean can prove, not whether Aristotle can paraphrase it confidently.

## Prompt 1: Theorem 1

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

## Prompt 2: Theorem 2

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

## Prompt 3: Theorem 3

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

## Prompt 4: Theorem 4

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

## Prompt 5: Theorem 5

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

## Prompt 6: Appendix D.2

```text
Formalize and prove the strongest correct Lean version of Theorem D.2 from Appendix D of the attached paper `paper_v8.md`.

The theorem claims:

- U is the spacetime of a deterministic CA on a finite spatial domain
- for a fixed candidate model c = (p, s), assume no exact frequency ties, meaning each orbit class limit frequency theta_j* is not equal to 1/2
- then the run-length codelength per site of the Hamming-optimal residual mask converges as T -> infinity

The manuscript proof sketch factors this through:

1. the CA state sequence is eventually periodic on a finite state space
2. orbit-class empirical frequencies converge, and under the no-ties assumption the majority choice stabilizes
3. after that, the residual mask becomes eventually periodic
4. run-length rate convergence follows from eventual periodicity of a binary sequence

Please structure the formalization in the cleanest way available.

Suggested strategy:

- First formalize and prove the analogue of Lemma D.1 for eventually periodic binary sequences and run-length codelength.
- Then state a separate theorem saying that, under eventual periodicity of the source sequence and stable majority choices, the residual mask sequence is eventually periodic.
- Finally derive convergence of the RL rate.

Requirements:

- Make all assumptions explicit.
- If the full CA formalization is too heavy, isolate an abstract theorem about eventually periodic source data plus stable majority projection.
- If the manuscript theorem needs weakening, say exactly how.
- Prove everything without `sorry`, `admit`, or extra `axiom`.
```

## Optional Prompt 7: Corollary D.3

```text
Formalize and prove the strongest correct Lean version of Corollary D.3 from the attached paper `paper_v8.md`.

Target idea:

- for deterministic CA on a finite spatial domain, orbit-class empirical frequencies converge because the state sequence is eventually periodic
- continuity of binary entropy implies convergence of the per-site NLL
- exact 1/2 ties do not obstruct NLL convergence, even though they may obstruct stabilization of the majority-vote residual mask

Please formalize only the mathematical content actually needed for the corollary. If full CA formalization is too heavy, an abstract theorem about eventually periodic binary observations along finitely many orbit classes is acceptable.

Requirements:

- State the weakest correct theorem supporting the manuscript claim.
- Make explicit whether CA determinism and finite state space are used directly or abstracted away.
- Prove it without `sorry`, `admit`, or extra `axiom`.
```

## After Aristotle Returns

For each theorem, record these five things before updating the manuscript:

1. The exact Lean theorem statement.
2. Whether Lean accepted it without gaps.
3. Which assumptions were added that do not appear explicitly in the paper.
4. Whether the result is weaker or stronger than the paper prose.
5. What sentence in `paper_v8.md` must change to match the formal result.
