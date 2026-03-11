# Aristotle Prompts For `paper_v7.md`

## Recommended Submission Workflow

Use Aristotle in `Mode [3] Direct Aristotle in English` first.

For each theorem:

1. Press `Ctrl+T` and paste one prompt from this file.
2. Press `Ctrl+F` and attach `/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_v7.md` as English context.
3. If you already have a Lean stub file, press `Ctrl+L` and attach it as Lean context.
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

If a theorem is underspecified or false as written, Aristotle should be asked to formalize the weakest corrected statement and explain the change.

## Prompt 1: Theorem 1

```text
Formalize and prove Theorem 1 from the attached paper `paper_v7.md`.

Please work from a finite setting only. You do not need to formalize the full CA dynamics; only formalize the combinatorial structure needed for the theorem.

Target mathematical content:

- We have a finite binary spacetime window U.
- A fixed relative-periodic model induces a finite partition of the sites into orbit classes.
- A candidate background B is constrained to be constant on each orbit class.
- The Hamming distance d(U,B) is the number of sites where U and B disagree.

Target claim:

For each orbit class O_j, let n_j^(1) be the number of 1s of U on that class and n_j^(0) the number of 0s. Then:

1. The Hamming distance decomposes as a sum over orbit classes.
2. The minimum over all orbit-constant backgrounds is obtained by choosing, independently on each orbit class, the majority bit.
3. The minimum defect count is the sum over orbit classes of min(n_j^(0), n_j^(1)).
4. The minimizer is unique if and only if no orbit class has exactly equal numbers of 0s and 1s.

Instructions:

1. State the theorem in Lean in the cleanest finite form.
2. Make every hidden assumption explicit.
3. Prove it without `sorry`, `admit`, or extra `axiom`.
4. If the theorem as written is underspecified, produce the weakest corrected formal statement and explain exactly what changed.
5. Prefer a formulation that is easy to compare line-by-line with the manuscript theorem.
```

## Prompt 2: Theorem 2

```text
Formalize and prove the monotonicity theorem corresponding to Theorem 2 from the attached paper `paper_v7.md`.

Please avoid unnecessary CA-specific machinery. Work with finite sets, finite partitions, and refinement.

Target mathematical content:

- A candidate relative-periodic model induces a partition of spacetime sites into orbit classes.
- If model C2 is a refinement of model C1, then every orbit class of C2 is contained in an orbit class of C1.
- For each partition, define the optimal Hamming defect count as the minimum over binary fields that are constant on each block of that partition.

Target claim:

If partition P2 refines partition P1, then the optimal Hamming defect count under P2 is less than or equal to the optimal Hamming defect count under P1.

After proving that abstract refinement theorem, if convenient, instantiate it to the paper's relative-periodic setting under the paper's velocity-matching compatibility condition:

- p2 = m * p1
- s2 is congruent to m * s1 modulo each spatial period

and show that this induces partition refinement, hence monotonicity of the optimal defect count.

Instructions:

1. Separate clearly the abstract partition-refinement statement from the relative-periodic corollary.
2. Make the compatibility condition precise.
3. Do not prove a stronger statement than is justified.
4. If the manuscript theorem needs to be weakened, provide the corrected theorem and explain the exact gap.
5. Prove everything without `sorry`, `admit`, or extra `axiom`.
```

## Prompt 3: Theorem 3

```text
Formalize as much of Theorem 3 from the attached paper `paper_v7.md` as is realistically supportable in Lean, and prove the strongest correct version.

This theorem is about eventual stabilization of model selection over a finite candidate set, where each score has asymptotic form

score_c(T) = lambda_c * T + alpha_c * log(T) + O(1).

The manuscript claims that if the candidate set is finite, then the argmin stabilizes for all sufficiently large T, with ties broken by the lower-complexity model.

Target tasks:

1. Decide on a precise finite-dimensional formal statement that captures the stabilization argument.
2. Make all asymptotic assumptions explicit. If necessary, replace informal O(1) language by a concrete bounded remainder hypothesis.
3. Prove that for any two candidates, the sign of the score difference eventually stabilizes.
4. Derive an eventual global winner over a finite candidate set, under whatever explicit assumptions are actually needed.

Important:

- Be very careful about tie cases and uniqueness of argmin.
- If the paper's theorem is too informal to formalize directly, state the weakest corrected version that is true.
- If the proof requires stronger assumptions than the manuscript states, identify them clearly.
- If some part is too cumbersome to formalize fully, prioritize the exact pairwise stabilization lemma and then the finite-candidate corollary.

Please return:

1. A Lean theorem statement for the strongest correct version.
2. A full proof with no `sorry`, `admit`, or extra `axiom`.
3. A short English note explaining how the formal theorem differs from the manuscript statement, if it does.
```

## Prompt 4: Theorem 4

```text
Formalize and prove a rigorous version of the nonidentifiability result corresponding to Theorem 4 from the attached paper `paper_v7.md`.

The manuscript-level idea is:

- There is a baseline model with period p0.
- Its residual has its own periodic structure of period k > 1.
- A richer model with period k * p0 can absorb that residual structure.
- Because the score has linear-in-T data-fit gain but only logarithmic complexity cost, the richer model eventually wins.

Please do not overcommit to the full prose theorem if it is underspecified. Instead:

1. Build a concrete finite family of candidate score functions that captures this phenomenon.
2. State a precise theorem showing that a model with a strictly better asymptotic linear rate eventually beats the original model despite a larger logarithmic penalty.
3. If helpful, phrase the theorem as an abstract comparison lemma, then explain how it yields the paper's nonidentifiability interpretation.

If possible, also formalize a simple constructive example schema, but only if it can be done cleanly.

Requirements:

- Make all assumptions explicit.
- Avoid hidden appeals to intuition about residual absorption.
- If the full manuscript theorem is too strong, provide the weakest corrected theorem that still supports the intended interpretation.
- Prove the result without `sorry`, `admit`, or extra `axiom`.
```

## Prompt 5: Theorem 5

```text
Formalize and prove a rigorous version of the identifiability-under-aperiodic-residuals result corresponding to Theorem 5 from the attached paper `paper_v7.md`.

The intended manuscript claim is:

- Under the true period p0, the orbit classes are asymptotically pure.
- Passing to a strict multiple p = m * p0 does not improve the asymptotic NLL, because splitting a pure class into smaller pure classes keeps entropy zero.
- The higher-period model has strictly larger complexity.
- Therefore the lower-period model is eventually preferred.

Please convert this into a precise finite or asymptotic theorem with explicit assumptions.

Tasks:

1. Decide the cleanest formal level: either an abstract score comparison theorem, or a theorem stated directly in terms of pure orbit classes and complexity growth.
2. Make explicit what "pure" means in the formal statement.
3. Prove that the data-fit terms are equal under the stated purity hypothesis.
4. Prove that the higher-complexity model is eventually worse.
5. State clearly whether the manuscript theorem needs stronger assumptions than currently written.

Requirements:

- No `sorry`, `admit`, or extra `axiom`.
- If the manuscript statement is not formalizable as written, return the weakest corrected formal statement and explain the changes.
- Keep the theorem easy to compare back to the paper.
```

## After Aristotle Returns

For each theorem, record these five things before updating the manuscript:

1. The exact Lean theorem statement.
2. Whether Lean accepted it without gaps.
3. Which assumptions were added that do not appear explicitly in the paper.
4. Whether the result is weaker or stronger than the paper prose.
5. What sentence in `paper_v7.md` must change to match the formal result.
