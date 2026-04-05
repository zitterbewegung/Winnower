# Theorem 4: Nonidentifiability of Background Period

## Prompt for "Direct Aristotle in English"

Formalize and prove Theorem 4 from the attached paper (Section 2.6).

The setting: For any period p₀ and shift s, construct a binary spacetime U and integer q > 1 such that the candidate c₁ = (q·p₀, q·s mod D) is eventually preferred over c₀ = (p₀, s) by Bernoulli NML.

Prove that there exist q > 1 and U such that:

(i) λ_{c₀} > 0
(ii) λ_{c₁} = 0
(iii) NML(c₁, T) < NML(c₀, T) for all sufficiently large T.

PROVIDED SOLUTION:

Construction: Let B be an exactly (p₀, s)-periodic binary field. Choose q > 1 and a second (p₀, s)-periodic field B' ≠ B. Define U[t, x] = B[t, x] when ⌊t/p₀⌋ ≢ 0 (mod q), and U[t, x] = B'[t, x] otherwise.

(i): Under c₀ = (p₀, s), the template must choose one value per orbit class. At least one (p₀, s)-orbit class mixes B and B' values with asymptotic frequencies 1/q and (q-1)/q. Since 0 < 1/q < 1, H_b(1/q) > 0, so λ_{c₀} > 0.

(ii): Under c₁ = (q·p₀, q·s mod D), the orbit classes separate the q residue classes of ⌊t/p₀⌋ mod q. Each layer sees a single periodic pattern (either B or B'), so all orbit classes are pure: λ_{c₁} = 0.

(iii): By Theorem 3(ii), since λ_{c₁} < λ_{c₀}, NML(c₁, T) < NML(c₀, T) for all sufficiently large T.

This depends on Theorem 3's pairwise comparison result.
