-- This module serves as the root of the `Verify` library.
-- Import modules here that should be built as part of the library.
import Verify.Basic
import Verify.Theorem1
import Verify.Theorem3

-- Standalone theorem drafts that are not yet part of the default build live in:
--   Verify/Corollary.lean
--   Verify/Theorem2.lean
--   Verify/Theorem5.lean
--
-- They are not imported here yet because they are generated drafts that still
-- need Mathlib/project setup and proof cleanup before being part of the
-- default build.
