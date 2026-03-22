# Corollary D.3: Unconditional NML Convergence

## Prompt for "Direct Aristotle in English"

Formalize and prove Corollary D.3 from the attached paper (Appendix D).

Statement: For a deterministic CA on a finite spatial domain, the per-site NLL converges unconditionally (no ties assumption needed): lim_{T→∞} NLL_c(T) / N(T) = λ_c exists.

PROVIDED SOLUTION: The per-orbit-class frequency θ̂_j(T) → θ*_j by eventual periodicity of the CA state sequence (pigeonhole on {0,1}^D), without requiring a no-ties condition. Since H_b is continuous, n_j · H_b(θ̂_j) / N(T) → (1/k_c) · H_b(θ*_j). Summing gives λ_c. When θ*_j = 1/2, the NLL contribution is n_j bits regardless of tie-breaking, so NLL does not depend on the no-ties condition. Combined with the O(log T) complexity, Theorem 3 applies.
