# Theorem 3: Rate-Based Elimination and Stabilization

## Prompt for "Direct Aristotle in English"

Formalize Theorem 3 from the attached paper (Section 2.5). This is the hardest theorem to formalize because it involves asymptotic analysis. Consider formalizing only the algebraic core and treating limits as hypotheses.

The setting: A fixed finite candidate set C = {(p₁, s₁), ..., (p_m, s_m)}. Each candidate c has k_c = p_c · ∏D_i orbit classes. Assume (A1): for each candidate c and orbit class j, the empirical frequency θ̂_j(T) → θ*_j as T → ∞.

Define the per-site NLL rate λ_c = (1/k_c) · Σ H_b(θ*_j), and λ* = min_c λ_c.

Prove:

(i) NML(c, T) = λ_c · N(T) + (k_c/2)·log₂ T + o(N(T)).

(ii) If λ_{c₁} < λ_{c₂}, then NML(c₁, T) < NML(c₂, T) for all sufficiently large T.

(iii) Every candidate c with λ_c > λ* is eventually excluded.

(iv) If λ* is achieved by a unique candidate c*, then NML selection stabilizes to c* for all sufficiently large T.

PROVIDED SOLUTION:

(i): Under (A1), H_b(θ̂_j(T)) = H_b(θ*_j) + o(1). Each orbit class has n_j(T) = T/p_c + O(1), so n_j·H_b(θ̂_j) = (T/p_c)·H_b(θ*_j) + o(T). Sum over k_c classes: NLL = λ_c·N(T) + o(N(T)). Complexity: Σ (1/2)·log₂ n_j = (k_c/2)·log₂ T + O(1).

(ii): NML(c₂,T) - NML(c₁,T) = (λ_{c₂} - λ_{c₁})·N(T) + o(N(T)). Since the coefficient is positive and N(T) → ∞, this is eventually positive.

(iii): If λ_c > λ*, pick c' with λ_{c'} = λ*. By (ii), NML(c',T) < NML(c,T) eventually.

(iv): Apply (ii) to c* vs each competitor. Take max over finitely many thresholds.

NOTE: This theorem is a specialization of standard BIC/MDL consistency (Schwarz 1978, Barron-Rissanen-Yu 1998, Grünwald Ch.16) to the orbit-class Bernoulli model family. The proof technique is not novel. Formal verification adds less value here than for Theorem 2. Consider formalizing parts (ii)-(iv) as consequences of (i), taking (i) as an axiom if the asymptotic analysis is too painful in Lean.
