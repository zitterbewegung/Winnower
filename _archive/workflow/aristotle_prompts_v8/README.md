# Aristotle Prompts For `paper_v8.md`

## Recommended Mode

Start in Aristotle `Mode [3] Direct Aristotle in English`.

Use this mode first because the main job is still theorem discovery and theorem tightening:

- extract the exact formal statement from the manuscript,
- force hidden assumptions to become explicit,
- see whether the theorem survives formalization at all.

Do **not** start with `fill sorries` unless you already have a Lean file whose definitions and theorem statements you trust.

## Phase 1: Prompt Mode

For each theorem:

1. Press `Ctrl+T` and paste one prompt from the matching file in this directory.
2. Press `Ctrl+F` and attach `/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_v8.md` as English context.
3. If you already have a Lean skeleton file, press `Ctrl+L` and attach it as Lean context. Otherwise skip this step.
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

## Why This Order

- `theorem_1.md` and `theorem_2.md` are the cleanest and should be the easiest to formalize.
- `theorem_3.md` should be treated as:
  1. per-site NLL convergence,
  2. pairwise eventual comparison,
  3. elimination of non-rate-minimizers,
  4. stabilization only under a unique rate-minimizer.
- `theorem_4.md` depends on the comparison logic from Theorem 3.
- `theorem_5.md` should be formalized using the manuscript's revised hypothesis: eventual exact periodicity after a finite transient.
- `appendix_d2.md` and `corollary_d3.md` are secondary; do them only after the main theorem block is stable.

## What To Record After Each Run

After Aristotle returns for any item, record:

1. The exact Lean theorem statement.
2. Whether Lean accepted it without gaps.
3. Which assumptions were added that do not appear explicitly in the paper.
4. Whether the result is weaker or stronger than the paper prose.
5. What sentence in `paper_v8.md` must change to match the formal result.

Use `/Users/r2q2/Projects/Experiments/relative_symmetry_repair/CLAIM_LEDGER.md` as the running checklist for what is already solid, what has been narrowed, and where the manuscript still relies on proof sketches.

## Phase 2: Switch To `Fill Sorries`

Once Aristotle gives you a theorem statement you trust, move to Aristotle's Lean-project mode.

Use `Fill sorries in a Lean file` when:

- you have a local Lean file,
- the definitions are stable,
- the theorem statement is the one you actually want,
- and you want Aristotle to prove that exact statement rather than reinterpret the paper again.

The recommended workflow is:

1. Use prompt mode to settle the statement.
2. Create a Lean file with the relevant definitions and theorem statement.
3. Put `sorry` in the proof body.
4. If helpful, add an English header comment tagged `PROVIDED SOLUTION`.
5. Run Aristotle in `fill sorries` mode on that file.

## Practical Rule

- `Direct Aristotle in English`: use it to discover and pressure-test the right formal theorem.
- `Fill sorries in a Lean file`: use it to prove the finalized theorem you have already chosen.
