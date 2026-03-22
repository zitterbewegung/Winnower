# Submission Checklist

## Before Resubmitting

- Use the prompts in `RESUBMIT_PROMPTS.md`
- Submit `Verify/Theorem1.lean` and `Verify/Theorem2.lean` separately
- Specify:
  - Lean `4.28.0`
  - Mathlib `v4.28.0`
  - module path under `Verify/`
- Require:
  - no `sorry`
  - no `admit`
  - no `exact?`
  - no `?_`
  - no duplicate theorem variants
  - no internal reasoning comments

## When You Get The Files Back

- Replace:
  - `Verify/Theorem1.lean`
  - `Verify/Theorem2.lean`
- Do not touch `Verify/Theorem3.lean`
- Keep the package config as-is:
  - `lakefile.toml`
  - `lean-toolchain`
  - `lake-manifest.json`

## Local Checks

- Run:
  - `lake env lean Verify/Theorem1.lean`
  - `lake env lean Verify/Theorem2.lean`
- Search for placeholders:
  - `rg -n "\bsorry\b|exact\?|admit|\?_" Verify/Theorem1.lean Verify/Theorem2.lean`

## After They Compile

- Import them in `Verify.lean`
- Then run:
  - `lake env lean Verify.lean`
  - `lake env lean Main.lean`

## If Theorem 2 Still Comes Back Messy

- Resubmit `Verify/Theorem2.lean` again rather than trying to salvage a heavily duplicated draft
- Ask for one final theorem chain only, ending in `Theorem2_Final`

