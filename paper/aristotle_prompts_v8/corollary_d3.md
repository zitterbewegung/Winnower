```text
Formalize and prove the strongest correct Lean version of Corollary D.3 from the attached paper `paper_v8.md`.

Target idea:

- for deterministic CA on a finite spatial domain, orbit-class empirical frequencies converge because the state sequence is eventually periodic
- continuity of binary entropy implies convergence of the per-site NLL
- exact 1/2 ties do not obstruct NLL convergence, even though they may obstruct stabilization of the majority-vote residual mask

Please formalize only the mathematical content actually needed for the corollary. If full CA formalization is too heavy, an abstract theorem about eventually periodic binary observations along finitely many orbit classes is acceptable.

Requirements:

- State the weakest correct theorem supporting the manuscript claim.
- Make explicit whether CA determinism and finite state space are used directly or abstracted away.
- Prove it without `sorry`, `admit`, or extra `axiom`.
```
