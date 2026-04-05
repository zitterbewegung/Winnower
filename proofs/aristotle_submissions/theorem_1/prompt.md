# Theorem 1: Optimal Hamming Projection

## Prompt for "Direct Aristotle in English"

Formalize and prove Theorem 1 from the attached paper (Section 2.2).

The setting: a binary spacetime U ∈ {0,1}^(T × D₁ × ... × Dₙ) with orbit classes {O_j} induced by a relative-periodic model (p, s). Each orbit class O_j has n_j^(1) ones and n_j^(0) = |O_j| - n_j^(1) zeros. The model class B(p, s) consists of all binary fields constant on each orbit class.

Prove: The Hamming distance d(U, B) = |{sites where U ≠ B}| is minimized over B ∈ B(p, s) by majority vote:
- b_j = 1 if n_j^(1) > n_j^(0)
- b_j = 0 if n_j^(0) > n_j^(1)
- either if tied

The minimum residual count is Σ_j min(n_j^(0), n_j^(1)).

The minimizer is unique if and only if no orbit class has n_j^(0) = n_j^(1).

PROVIDED SOLUTION: The Hamming distance decomposes additively over orbit classes: d(U,B) = Σ_j d_j. Since B is constant on each O_j, choosing b_j independently minimizes each d_j = min(n_j^(0), n_j^(1)). Uniqueness follows because each orbit class has a unique minimizer iff the counts are unequal.
