-- Minimal library root so `lake build` succeeds for the top-level package.
-- The substantive Lean artifacts live in `aristotle_submissions/verify/`
-- (see proofs/README.md for their per-file status) and in the standalone
-- Aristotle output file at the proofs/ root, which requires Mathlib.
def hello := "rsr"
