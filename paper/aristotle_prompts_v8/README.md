# Aristotle Prompts For `paper_v8.md`

Use Aristotle in `Mode [3] Direct Aristotle in English` first.

For each theorem:

1. Press `Ctrl+T` and paste one prompt from the matching file in this directory.
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

1. `theorem_1.md`
2. `theorem_2.md`
3. `theorem_3.md`
4. `theorem_4.md`
5. `theorem_5.md`
6. `appendix_d2.md`, if needed
7. `corollary_d3.md`, optional

`paper_v8.md` is more formal than `paper_v7.md`, especially in Theorem 3. The main thing to test is whether the revised statement really matches what Lean can prove, not whether Aristotle can paraphrase it confidently.

After Aristotle returns for any item, record:

1. The exact Lean theorem statement.
2. Whether Lean accepted it without gaps.
3. Which assumptions were added that do not appear explicitly in the paper.
4. Whether the result is weaker or stronger than the paper prose.
5. What sentence in `paper_v8.md` must change to match the formal result.
