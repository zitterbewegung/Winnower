# Resubmission Prompts

Use the prompts below when resubmitting the unfinished theorem files.

## General Instructions

- Match the local package environment exactly:
  - Lean `4.28.0`
  - Mathlib `v4.28.0`
- Return a clean final Lean module under `Verify/`
- Do not include placeholders:
  - no `sorry`
  - no `admit`
  - no `exact?`
  - no `?_`
- Do not include exploratory proof attempts, abandoned variants, or internal reasoning comments
- Do not include duplicate theorem variants like `*_final`, `*_v2`, `*_success`, etc. unless they are the single final theorem
- Prefer a clean compilable file over preserving every draft proof step

## Theorem 1

### Instructions

- File path: `Verify/Theorem1.lean`
- Keep the theorem intent: optimal Hamming projection onto orbit-constant binary fields over a finite setoid partition
- Preserve these main theorem names if practical:
  - `majority_vote_minimizes_hamming_dist`
  - `minimum_residual_count`
  - `unique_minimizer_iff`
- It is fine to refactor helper lemmas and definitions if needed for Lean `4.28.0` + Mathlib `v4.28.0`

### Prompt

```text
Please regenerate a complete Lean 4 file for this module:

  Verify/Theorem1.lean

Target environment:
- Lean version: 4.28.0
- Mathlib version: v4.28.0
- The file should live in a Lean package where modules are under `Verify/`
- `import Mathlib` is acceptable

What I need:
- A clean, final version of `Verify/Theorem1.lean`
- No placeholders of any kind:
  - no `sorry`
  - no `admit`
  - no `exact?`
  - no `?_`
- No exploratory attempts, failed proof sketches, or internal reasoning comments
- No duplicated “final attempt” theorems
- No scratch `#check` / `#synth` lines unless absolutely required for compilation
- Return a single self-contained file

Mathematical target:
This file formalizes Theorem 1 about optimal Hamming projection onto orbit-constant binary fields over a finite setoid partition.

It should define and prove the following ideas cleanly:
- `count_ones`
- `count_zeros`
- `hamming_dist`
- `is_constant_on`
- `ModelClass`
- `is_majority_vote`
- `hamming_dist_on`
- decomposition of Hamming distance over equivalence classes
- majority vote minimizes Hamming distance in the model class
- the minimum residual count equals the sum of minority counts over classes
- uniqueness of the minimizer iff no class has equal zero/one counts

Important:
- Please preserve the overall theorem intent and, if practical, the main theorem names:
  - `majority_vote_minimizes_hamming_dist`
  - `minimum_residual_count`
  - `unique_minimizer_iff`
- If some definitions or helper lemmas need to be refactored to make the file compile in Lean 4.28.0 + Mathlib v4.28.0, that is fine.
- Prefer a clean, compilable file over preserving every old proof step.

Deliverable:
- Output only the final Lean file contents for `Verify/Theorem1.lean`.
```

## Theorem 2

### Instructions

- File path: `Verify/Theorem2.lean`
- Keep the theorem intent: six-way equivalence for translation candidates, orbit refinement, model-class inclusion, minimum Hamming distance monotonicity, and NLL monotonicity on a torus spacetime grid
- Use the mathematically correct modular condition for shifts if needed
- The current draft should be replaced, not patched in place conceptually
- Preserve these main theorem names if practical:
  - `cond1_mod_iff_cond2`
  - `cond2_imp_cond3`
  - `cond3_imp_cond2`
  - `cond3_imp_cond4`
  - `cond4_imp_cond5`
  - `cond5_imp_cond3`
  - `cond3_imp_cond6`
  - `cond6_imp_cond3`
  - `Theorem2_Final`

### Prompt

```text
Please regenerate a complete Lean 4 file for this module:

  Verify/Theorem2.lean

Target environment:
- Lean version: 4.28.0
- Mathlib version: v4.28.0
- The file should live in a Lean package where modules are under `Verify/`
- `import Mathlib` is acceptable

What I need:
- A clean, final version of `Verify/Theorem2.lean`
- No placeholders of any kind:
  - no `sorry`
  - no `admit`
  - no `exact?`
  - no `?_`
- No exploratory attempts, abandoned variants, or internal reasoning comments
- Remove all duplicate “proof”, “final”, “v2”, “success”, etc. variants
- No scratch `#check` / `#synth` lines unless absolutely required for compilation
- Return a single self-contained file

Mathematical target:
This file formalizes Theorem 2 about a torus spacetime grid, translation candidates, orbit partitions, model classes, Hamming-optimality, and NLL monotonicity.

It should cleanly define:
- `SpacetimeGrid`
- `Candidate`
- `gridTranslate`
- `gridOrbit`
- `orbitPartition`
- `BinaryField`
- `ModelClass`
- `minHammingDist`
- `empiricalProb`
- `NLL`

It should formalize the six conditions:
- parameter multiple / modular multiple condition
- translation-as-iterate condition
- orbit partition refinement
- model-class inclusion
- monotonicity of minimum Hamming distance
- monotonicity of NLL

And it should prove the final equivalence theorem cleanly, ideally with a final theorem like:
- `Theorem2_Final`

Important:
- The current draft has many unfinished holes and many duplicate variants. I do not want patched fragments. I want a fresh, coherent final file.
- If some statements need to be slightly reformulated to make the equivalence precise in Lean and mathematically correct, that is acceptable, but keep the theorem as close as possible to the intended six-way equivalence.
- If the original condition `(i)` needs a modular formulation for time/space shifts, use the mathematically correct modular version consistently.
- Prefer one clean final chain of lemmas over many competing theorem versions.

Strong preference:
- Keep or provide clear final names for the main implications and equivalences, such as:
  - `cond1_mod_iff_cond2`
  - `cond2_imp_cond3`
  - `cond3_imp_cond2`
  - `cond3_imp_cond4`
  - `cond4_imp_cond5`
  - `cond5_imp_cond3`
  - `cond3_imp_cond6`
  - `cond6_imp_cond3`
  - `Theorem2_Final`
- But correctness and compilability matter more than preserving every draft name exactly.

Deliverable:
- Output only the final Lean file contents for `Verify/Theorem2.lean`.
```

