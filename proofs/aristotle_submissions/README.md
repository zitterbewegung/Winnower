# Aristotle submission packet

This directory was generated automatically from `paper/aristotle_prompts_v15`.

Use `shared_context/paper_v15.md` as the source of truth for Aristotle.
Use `paper_alife2026.tex` and the per-claim `manuscript_excerpt.tex` files only to compare the current ALIFE submission wording.

## Shared context

- `shared_context/paper_v15.md`
- `shared_context/paper_alife2026.tex`
- `shared_context/README.md`
- `shared_context/INSTRUCTIONS.md`
- `shared_context/SUBMISSION_CHECKLIST.md`
- `shared_context/CLAIM_LEDGER.md`

## Claim bundles

- `theorem_2/`: Theorem 2: Six-Way Equivalence / Monotonicity (priority 1)
- `theorem_5/`: Theorem 5: Identifiability for Eventually Exact Backgrounds (priority 2)
- `theorem_1/`: Theorem 1: Optimal Hamming Projection (priority 3)
- `theorem_3/`: Theorem 3: Stabilization (priority 4)
- `theorem_4/`: Theorem 4: Nonidentifiability (priority 5)
- `corollary_d3/`: Corollary D.3: Unconditional NML Convergence (priority 6)

## Suggested workflow

1. Start with `theorem_2/`.
2. Paste that bundle's `prompt.md` into Aristotle in `Direct Aristotle in English` mode.
3. Attach `shared_context/paper_v15.md`.
4. Record every result in `shared_context/CLAIM_LEDGER.md`.
5. Regenerate this packet whenever the manuscript or prompt files change.
