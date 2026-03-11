```text
Formalize and prove the strongest correct Lean version of Theorem D.2 from Appendix D of the attached paper `paper_v8.md`.

The theorem claims:

- U is the spacetime of a deterministic CA on a finite spatial domain
- for a fixed candidate model c = (p, s), assume no exact frequency ties, meaning each orbit class limit frequency theta_j* is not equal to 1/2
- then the run-length codelength per site of the Hamming-optimal residual mask converges as T -> infinity

The manuscript proof sketch factors this through:

1. the CA state sequence is eventually periodic on a finite state space
2. orbit-class empirical frequencies converge, and under the no-ties assumption the majority choice stabilizes
3. after that, the residual mask becomes eventually periodic
4. run-length rate convergence follows from eventual periodicity of a binary sequence

Please structure the formalization in the cleanest way available.

Suggested strategy:

- First formalize and prove the analogue of Lemma D.1 for eventually periodic binary sequences and run-length codelength.
- Then state a separate theorem saying that, under eventual periodicity of the source sequence and stable majority choices, the residual mask sequence is eventually periodic.
- Finally derive convergence of the RL rate.

Requirements:

- Make all assumptions explicit.
- If the full CA formalization is too heavy, isolate an abstract theorem about eventually periodic source data plus stable majority projection.
- If the manuscript theorem needs weakening, say exactly how.
- Prove everything without `sorry`, `admit`, or extra `axiom`.
```
