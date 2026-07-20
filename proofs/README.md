# Formal proof artifacts

Lean 4 artifacts for the formal counterparts of the manuscript's
supporting statements, generated with the Aristotle prover
(https://aristotle.harmonic.fun). **Nothing in the paper depends on
these artifacts.** They back the informally-stated properties in the
Method section and the long-form theory notes audited in
`docs/CLAIM_LEDGER.md`, and they are at *different levels of
completeness* — the table below is the honest inventory.

## Per-file status

| File | Statement | Status |
|---|---|---|
| `aristotle_submissions/verify/Verify/Theorem3.lean` | Stabilization core: pairwise eventual ordering, elimination, and lock-in to a unique rate minimizer, **assuming** the NML expansion `NML = λN + (k/2)log₂T + o(N)` as a hypothesis | **Complete**: no `sorry`/`admit`/`axiom`/`exact?`; part of the default `lake build` |
| `55d8f9ef-…-output.lean` (proofs root) | Refinement ⇒ total NLL non-increasing, plus converse (the NLL half of the "penalty is necessary" property, at the abstract-partition level) | Proof text complete but contains one `exact?` placeholder and `import Mathlib` in a package with no Mathlib dependency — **not buildable in-repo as shipped** |
| `aristotle_submissions/verify/Verify/Theorem1.lean` | Majority vote optimal (Hamming projection) | **Draft**: 5 `exact?` placeholders; excluded from build |
| `aristotle_submissions/verify/Verify/Theorem2.lean` | Six-way equivalence / refinement monotonicity | **Draft**: 17 `exact?` placeholders — all implications are declared and combined, but several rest on placeholder holes; excluded from build |
| `aristotle_submissions/verify/Verify/Theorem5.lean` | Identifiability for eventually exactly periodic backgrounds | **Draft**: 6 `exact?` placeholders; excluded from build |
| `aristotle_submissions/verify/Verify/Corollary.lean` | NLL convergence support (Corollary D.3) | **Draft**: 5 `exact?` placeholders; excluded from build |

`exact?` is a proof-search placeholder tactic: a file containing it is
not a finished proof even though it contains no `sorry`. Grep for
yourself: `grep -rn "sorry\|admit\|exact?" proofs/ --include=*.lean`.

## Building

```bash
cd proofs/aristotle_submissions/verify
lake exe cache get   # fetch prebuilt Mathlib oleans (recommended)
lake build           # builds Verify/Basic.lean, Verify/Theorem3.lean, Main.lean
```

The `verify` package pins its toolchain (`lean-toolchain`) and Mathlib
(`v4.28.0` in `lakefile.toml`). Two caveats, stated plainly: the
Aristotle outputs were generated against Lean `v4.24.0`, and no build
artifacts ship in the repo — so until the root-level CI workflow
(`.github/workflows/lean-verify.yml`, which rebuilds the `verify`
package and greps the built targets for placeholders) has a public green
run on `main`, the v4.28.0 compilability of `Theorem3.lean` is asserted,
not demonstrated. That gap is now closed: the workflow's first run on
`main` completed green (build + placeholder check) — see the repository's
Actions tab, workflow "Lean proof check", run of commit `85803b0`.

The top-level `proofs/` package (`rsr`) is a minimal shell with no
Mathlib dependency; it exists to host the standalone Aristotle output
and builds trivially.

## Provenance and honesty

- `aristotle_submissions/theorem_*/` preserves the exact prompts,
  manuscript excerpts, and notes sent to Aristotle for each claim.
- The formal statements were produced against the long-form notes'
  wording, not the conference manuscript's. Before citing any file,
  compare its Lean statement against the manuscript claim line by line —
  formalization can silently weaken or add hypotheses.
- LLM assistants drafted proof sketches; Aristotle generated the Lean;
  Lean's kernel — not any model's prose — is the arbiter of what is
  proved. By that standard, exactly one statement here (the
  stabilization core, under its stated hypothesis) is machine-checked.
