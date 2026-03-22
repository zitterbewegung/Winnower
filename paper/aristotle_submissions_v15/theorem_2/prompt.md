# Theorem 2: Exact Characterization of Universal Refinement and Monotonicity (Six-Way Equivalence)

## Prompt for "Direct Aristotle in English"

Formalize and prove Theorem 2 from the attached paper (Section 2.3).

The setting: a binary spacetime U on a torus with spatial dimensions D = (D₁, ..., Dₙ) and temporal length T. Two relative-periodic candidates c₁ = (p₁, s₁) and c₂ = (p₂, s₂) define spacetime translations τᵢ(t, x) := (t + pᵢ, x + sᵢ mod D). Each τᵢ induces an orbit partition Πᵢ. The model class B(pᵢ, sᵢ) consists of all binary fields constant on Πᵢ-classes. For a binary spacetime U, d*_U(cᵢ) is the minimum Hamming distance from U to any field in B(pᵢ, sᵢ), and NLL_U(cᵢ) is the Bernoulli negative log-likelihood (sum of n_j · H_b(θ̂_j) over orbit classes).

Prove that the following six conditions are equivalent:

(i) There exists m ≥ 1 such that p₂ = m·p₁ and s₂ ≡ m·s₁ (mod D) componentwise.
(ii) τ₂ = τ₁ᵐ for some integer m ≥ 1.
(iii) The orbit partition Π₂ refines Π₁.
(iv) The model classes are nested: B₁ ⊆ B₂.
(v) For every binary spacetime U, d*_U(c₂) ≤ d*_U(c₁).
(vi) For every binary spacetime U, NLL_U(c₂) ≤ NLL_U(c₁).

PROVIDED SOLUTION for each direction:

(i)↔(ii): Immediate from definitions. τ₁ᵐ advances time by m·p₁ and space by m·s₁ mod D.

(ii)→(iii): If τ₂ = τ₁ᵐ, every τ₂-orbit is contained in a τ₁-orbit.

(iii)→(iv): B consists of fields constant on orbit classes. Finer partition ⟹ larger model class.

(iv)→(v): Minimizing Hamming distance over a larger set cannot give a worse optimum.

(iii)→(vi): Each coarse orbit class O ∈ Π₁ splits into finer classes O_α ∈ Π₂. Coarse NLL contribution is n·H_b(θ), refined is Σ n_α·H_b(θ_α). By concavity of H_b (Jensen's inequality), n·H_b(θ) ≥ Σ n_α·H_b(θ_α). Sum over all coarse classes.

(v)→(iii) [NECESSITY]: Suppose Π₂ does NOT refine Π₁. Then some Π₂-class intersects two distinct Π₁-classes. Construct U ∈ B₁ (constant on Π₁-classes) with value 0 on one chosen class and 1 on the other. Then d*_U(c₁) = 0 (since U ∈ B₁) but d*_U(c₂) > 0 (the Π₂-class contains both 0 and 1).

(vi)→(iii) [NECESSITY]: Same construction. U ∈ B₁ gives NLL_U(c₁) = 0, but the mixed Π₂-class gives NLL_U(c₂) > 0.

Combining: (i)↔(ii)→(iii)→(iv)→(v)→(iii) and (iii)→(vi)→(iii), closing the loop.
