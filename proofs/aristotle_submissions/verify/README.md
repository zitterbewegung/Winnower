# verify

Lean package layout:

- `Verify.lean`: root library module
- `Verify/Basic.lean`: minimal package scaffold
- `Verify/Corollary.lean`: generated corollary draft not yet included in the default build
- `Verify/Theorem1.lean`: generated draft for theorem 1
- `Verify/Theorem2.lean`: generated draft for theorem 2
- `Verify/Theorem3.lean`: Mathlib-backed theorem module now included in the library build
- `Main.lean`: executable entry point

The package is now configured with Mathlib for Lean `4.28.0`.

`Verify/Theorem3.lean` is imported by the root library module and builds as part
of the package. `Verify/Corollary.lean`, `Verify/Theorem1.lean`, and
`Verify/Theorem2.lean` remain standalone drafts until their proof holes are
repaired.
