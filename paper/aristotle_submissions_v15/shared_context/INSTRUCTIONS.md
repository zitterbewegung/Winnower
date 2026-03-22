# Aristotle Verification Workflow for `paper_v15.md`

## Overview

This directory contains prompts and workflow guidance for formally verifying Theorems 1–5 from `paper_v15.md` using Aristotle. The previous Lean file (generated against `paper_v8.md`) has been deleted; start fresh.

## Plain-English Quick Start

If you choose **"Direct Aristotle in English"**, do this:

1. Open Aristotle and select **"Direct Aristotle in English"**.
2. Paste the English prompt from this folder, for example [theorem_2.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/aristotle_prompts_v15/theorem_2.md).
3. Optionally attach [paper_v15.md](/Users/r2q2/Projects/Experiments/relative_symmetry_repair/paper/paper_v15.md) as English context.
4. Optionally attach an existing Lean file as **context only**. In this mode Aristotle can read that Lean file, but it is not the main thing you are editing.
5. Submit. Aristotle should return a **new Lean output file**.

If you already have a Lean file and want Aristotle to work **inside that file**, do **not** use "Direct Aristotle in English". Use **"Fill sorries in Lean file"** instead.

Short rule:

- **No Lean file yet** or you want Aristotle to invent the formal statement: use **Direct Aristotle in English**.
- **You already have a Lean file** and want proofs filled in: use **Fill sorries in Lean file**.

### Aristotle Environment

- Lean: `v4.24.0`
- Mathlib commit: `f897ebcf72cd16f89ab4577d0c826cd14afaafc7`

## Aristotle Modes

There are three relevant Aristotle modes. Use them in this order:

### Mode 1: "Direct Aristotle in English" (Ctrl+T)

**Use this first.** This is the bootstrapping mode. You describe a theorem in English, optionally attach the paper and/or a Lean file as context, and Aristotle generates a complete Lean file with definitions, theorem statements, and proofs.

**When to use:** When you don't yet have a Lean file, or when you want Aristotle to discover the right formal statement from the manuscript.

**Workflow:**
1. Press `Ctrl+T` and paste the prompt from the matching file in this directory.
2. Press `Ctrl+F` and attach `paper/paper_v15.md` as English context.
3. If you already have a Lean file with definitions, press `Ctrl+L` to attach it as Lean context (Aristotle sees it but won't modify it).
4. Press `Ctrl+S` to submit.

### Mode 2: "Prove and Formalize"

**Use this for single claims.** Similar to "Direct in English" but more structured for formalizing individual mathematical statements rather than full papers. Good for isolated lemmas or corollaries.

### Mode 3: "Fill sorries in Lean file"

**Use this second, after you have a Lean file with correct definitions and theorem statements but incomplete proofs.** You mark unproven theorems with `sorry`, add `PROVIDED SOLUTION` sketches in header comments, and Aristotle fills in the proofs.

**When to use:** Once Mode 1 has given you a file with correct *statements* that you've verified against the manuscript, but some proofs are missing or have `sorry`.

**Workflow:**
1. Take the Lean file from Mode 1.
2. Replace proof bodies you want filled with `sorry`.
3. Add an English sketch in the theorem header comment tagged `PROVIDED SOLUTION`.
4. Replace proofs you do NOT want Aristotle to touch with `admit` (Aristotle will not modify `admit` terms).
5. Run Aristotle in "Fill sorries" mode on that file.

## Verification Order

### Priority 1: Theorem 2 (Six-Way Equivalence)

This is the strongest theorem-level novelty claim (the necessity direction). Formalize first.

**Key change from v8:** Theorem 2 is now a *six-way* equivalence. Condition (vi) — universal NLL monotonicity — was added. The necessity directions (v)→(iii) and (vi)→(iii) use the same adversarial construction.

**What to verify:**
- Forward chain: (i)↔(ii)→(iii)→(iv)→(v) and (iii)→(vi)
- Necessity: (v)→(iii) and (vi)→(iii)
- The full six-way iff

### Priority 2: Theorem 5 (Identifiability)

Clean finite-transient argument. Should formalize well.

**What to verify:**
- Equal rates λ_p = λ_{p₀} = 0
- NLL difference O(1)
- NML difference (m-1)k/2 · log T + O(1) → +∞
- Therefore NML selects p₀ over p

### Priority 3: Theorem 1 (Optimal Hamming Projection)

Straightforward finite combinatorics. Easy target.

### Priority 4: Theorem 3 (Stabilization)

**Hardest to formalize.** Asymptotic analysis with o(N(T)) terms is painful in Lean. This theorem is a specialization of standard BIC/MDL consistency — formal verification adds less value here since the proof technique is well-established. Consider formalizing only the algebraic core (NML decomposition) and treating the asymptotic argument as a proof sketch.

**If you do formalize, break it into:**
1. Per-site NLL convergence (part i)
2. Pairwise comparison (part ii)
3. Elimination (part iii)
4. Stabilization under unique minimizer (part iv)

### Priority 5: Theorem 4 (Nonidentifiability)

Depends on Theorem 3's comparison logic. The explicit construction (MixedSpacetime) is the interesting part.

### Low Priority: Appendix D

- Theorem D.2 (RL rate convergence) — only a proof sketch in the manuscript
- Corollary D.3 (unconditional NML convergence) — good formalization target but secondary

## After Each Aristotle Run

Check the following:

1. `lake build` succeeds (or Lean compiles with no errors)
2. `grep -n 'sorry\|admit' output.lean` — no `sorry` or `admit` remaining
3. `grep -n 'axiom' output.lean` — no extra `axiom` beyond standard Mathlib
4. **Compare the formal theorem statement to the manuscript claim line by line.** The main risk is silent weakening or added assumptions during formalization.
5. Record results in `CLAIM_LEDGER.md`

## What To Record

After Aristotle returns for any item, record:

1. The exact Lean theorem statement.
2. Whether Lean accepted it without gaps.
3. Which assumptions were added that do not appear explicitly in the paper.
4. Whether the result is weaker or stronger than the paper prose.
5. What sentence in `paper_v15.md` must change to match the formal result (if any).

## Practical Rules

- **"Direct Aristotle in English"**: use it to discover and pressure-test the right formal theorem statement.
- **"Fill sorries in a Lean file"**: use it to prove the finalized theorem you have already chosen.
- **"Prove and Formalize"**: use it for single isolated claims.
- Trust Lean's kernel, not Aristotle's prose.
- Aristotle will not modify definitions/data by default.
- Aristotle will not add imports on its own; it only edits the target file.
- In project mode, Aristotle sees the specified Lean file plus its transitive imports.
