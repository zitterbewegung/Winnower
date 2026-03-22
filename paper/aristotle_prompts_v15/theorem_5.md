# Theorem 5: Identifiability for Eventually Exactly Periodic Backgrounds

## Prompt for "Direct Aristotle in English"

Formalize and prove Theorem 5 from the attached paper (Section 2.7).

The setting: A CA spacetime U has true background period p₀ with shift s, meaning there exists a transient time T₀ such that U[t + p₀, x + s mod D] = U[t, x] for all t ≥ T₀. Consider a velocity-matched strict multiple p = m·p₀ (m > 1) with shift m·s mod D.

Prove:

(i) The per-site NLL rates are equal: λ_p = λ_{p₀} = 0.

(ii) The NLL difference satisfies NLL(p, T) - NLL(p₀, T) = O(1).

(iii) The NML score difference satisfies NML(p, T) - NML(p₀, T) = (m-1)·k_{p₀}/2 · log₂ T + O(1) → +∞.

(iv) Therefore NML selects p₀ over p for all sufficiently large T.

PROVIDED SOLUTION:

(i): After T₀, the spacetime is exactly (p₀, s)-periodic, so every (p₀, s)-orbit class is pure outside the finite prefix t < T₀. Hence λ_{p₀} = 0. The same exact periodicity implies exact (p, m·s)-periodicity, so λ_p = 0.

(ii): Only orbit classes intersecting the finite transient prefix t < T₀ contribute nonzero NLL. There are finitely many such classes. For each, splitting from p₀ to p = m·p₀ creates m sub-classes, but the total transient disagreements stay fixed. The NLL change is bounded by a constant independent of T.

(iii): The complexity difference is COMP(p,T) - COMP(p₀,T) = (m·k_{p₀}/2)·log₂(T/(m·p₀)) - (k_{p₀}/2)·log₂(T/p₀) + O(1) = (m-1)·k_{p₀}/2 · log₂ T + O(1).

(iv): Combining (ii) and (iii), the score difference tends to +∞, so the higher-period model is eventually worse.
