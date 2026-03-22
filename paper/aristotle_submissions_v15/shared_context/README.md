# Aristotle Quick Start for the `v15` Theorem Package

Use [paper_v15.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_v15.md) as the source of truth for Aristotle.
Use [paper_alife2026.tex](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_alife2026.tex) only to compare the current submission wording.

## Default Workflow

1. Run `python scripts/prepare_aristotle_submissions.py --zip`.
2. Open the bundle for the claim you want, for example [theorem_2](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_submissions_v15/theorem_2).
3. In Aristotle, choose `Direct Aristotle in English`.
4. Paste that bundle's `prompt.md`.
5. Attach `shared_context/paper_v15.md`.
6. Submit.
7. Save the returned Lean file locally.
8. Run `lake build` or compile the file directly.
9. Check for `sorry`, `admit`, and unexpected `axiom`.
10. Record the result in [CLAIM_LEDGER.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/CLAIM_LEDGER.md).

## Submission Order

1. `theorem_2`
2. `theorem_5`
3. `theorem_1`
4. `theorem_3`
5. `theorem_4`
6. `corollary_d3` if you still want the appendix claim

## Claim Notes

- `theorem_2`: highest-value target; do this first.
- `theorem_5`: usually cleaner than `theorem_3` or `theorem_4`.
- `theorem_1`: easy sanity check.
- `theorem_3`: hardest; if needed, formalize only the pairwise-comparison core.
- `theorem_4`: best attempted after `theorem_3` yields a usable comparison lemma.
- `corollary_d3`: appendix-level and optional.

## When to Use `Fill sorries in Lean file`

Use it only after you already have a Lean file whose theorem statement you trust.

That means:

- first run `Direct Aristotle in English` to get the statement
- then, if the statement is right but the proof is incomplete, switch to `Fill sorries in Lean file`

## Files That Matter

- [SUBMISSION_CHECKLIST.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/SUBMISSION_CHECKLIST.md): compact run checklist
- [CLAIM_LEDGER.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/CLAIM_LEDGER.md): what Aristotle and Lean actually established
- [INSTRUCTIONS.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/INSTRUCTIONS.md): older detailed notes, only if you need more context
