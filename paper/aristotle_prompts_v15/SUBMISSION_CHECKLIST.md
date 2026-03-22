# Aristotle Submission Checklist

Use [paper_v15.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_v15.md) as the formalization source of truth.
Treat [paper_alife2026.tex](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_alife2026.tex) as the current submission draft only.

## Do This For Every Claim

- [ ] Open the claim bundle under [paper/aristotle_submissions_v15](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_submissions_v15).
- [ ] In Aristotle, choose `Direct Aristotle in English`.
- [ ] Paste that claim's `prompt.md`.
- [ ] Attach `shared_context/paper_v15.md`.
- [ ] Submit.
- [ ] Save the returned Lean file.
- [ ] Run `lake build` or compile the file directly.
- [ ] Check that there is no `sorry`, `admit`, or unexpected `axiom`.
- [ ] Copy the exact theorem statement into [CLAIM_LEDGER.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/CLAIM_LEDGER.md).
- [ ] Note any added assumptions or weakening.

## Recommended Order

1. [theorem_2.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/theorem_2.md)
2. [theorem_5.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/theorem_5.md)
3. [theorem_1.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/theorem_1.md)
4. [theorem_3.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/theorem_3.md)
5. [theorem_4.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/theorem_4.md)
6. [corollary_d3.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/corollary_d3.md) if you want the appendix claim

## Special Cases

- `theorem_3`: if full asymptotics are too painful, accept a precise pairwise-comparison or algebraic-core result.
- `theorem_4`: do it after `theorem_3` if the proof depends on a comparison lemma.
- `corollary_d3`: optional and lower priority.
