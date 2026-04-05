# Prior-Art Search for Theorems 1-5

Date: 2026-03-12

Scope: fresh explicit prior-art search against the current theorem statements in `paper/paper_v11.md`, using primary sources where possible.

Method:
- Started from the current manuscript statements in `paper/paper_v11.md`.
- Searched theorem-by-theorem across CA literature, periodicity/string-algorithm literature, and MDL/NML literature.
- Treated the following as primary sources: journal papers, conference proceedings, and official publisher/DOI pages.
- This was a targeted search, not an exhaustive proof that no earlier analogue exists.

Representative queries:
- `"Testing periodicity" Algorithmica 2011`
- `"Computational mechanics of cellular automata: An example"`
- `"A Mathematical Theory of Communication" 1948 entropy`
- `"The minimum description length principle in coding and modeling"`
- `"Model selection and the principle of minimum description length"`
- `"Mining periodic patterns with a MDL criterion"`
- `"Nested periodic matrices and dictionaries" period estimation`

## Bottom Line

| Theorem | Search outcome | Positioning recommendation |
|---|---|---|
| Theorem 1 | Direct prior art found | Do not claim novelty for the majority-vote lemma itself |
| Theorem 2 | No direct match found; ingredients are classical | Defensible as a new exact characterization in this model class |
| Theorem 3 | No direct CA-template analogue found; generic MDL/NML background is classical | Claim novelty only at the level of this model family / application |
| Theorem 4 | No direct prior analogue found in the searched literature | Defensible as novel in this setting |
| Theorem 5 | No direct prior theorem found, but conceptually close to generic MDL behavior for nested exact-fit models | Treat as a complementary corollary/result, not a headline novelty claim |

## Theorem 1

Statement in current paper: Hamming-optimal projection onto a fixed orbit partition is obtained by majority vote on each orbit class.

Search result:
- Direct prior art exists for the core optimization pattern.
- The closest match found is Lachish and Newman, who formulate distance to periodicity by grouping positions into residue classes modulo the candidate period and optimizing classwise.
- The manuscript's current prior-art remark is directionally correct.

Primary sources:
- Oded Lachish and Ilan Newman, "Testing Periodicity," *Algorithmica* 60(2), 401-420 (2011). https://doi.org/10.1007/s00453-009-9351-y

Assessment:
- The majority-vote / per-class minimization lemma is not novel.
- The new part is its use as the front end of the relative-periodic CA pipeline and theorems built on top of it.

Recommended wording:
- Keep the current "prior art" remark.
- Avoid presenting Theorem 1 itself as an original theorem.

## Theorem 2

Statement in current paper: velocity-matched divisibility is equivalent to translation-power identity, orbit-partition refinement, model nesting, and universal monotonicity of both Hamming residuals and Bernoulli NLL.

Search result:
- No direct prior theorem matching the full six-way equivalence was found in the targeted search.
- The ingredients appear classical:
  - residue-class / divisibility structure for periodicity,
  - refinement/nesting under coarser vs finer classes,
  - monotonicity of entropy-based likelihood under refinement via entropy concavity / conditioning.
- CA prior art discusses exact periodic domains and local structure, but not this global equivalence for relative-periodic candidate families.

Primary sources consulted:
- Oded Lachish and Ilan Newman, "Testing Periodicity," *Algorithmica* 60(2), 401-420 (2011). https://doi.org/10.1007/s00453-009-9351-y
- Claude E. Shannon, "A Mathematical Theory of Communication," *Bell System Technical Journal* 27(3), 379-423 (1948). https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
- J.E. Hanson and J.P. Crutchfield, "The attractor-basin portrait of a cellular automaton," *Journal of Statistical Physics* 66, 1415-1462 (1992). https://doi.org/10.1007/BF01054429
- J.P. Crutchfield and J.E. Hanson, "Computational mechanics of cellular automata: An example," *Physica D* 103, 169-189 (1997). https://doi.org/10.1016/S0167-2789(96)00259-X
- A. Rupe and J.P. Crutchfield, "Local causal states and discrete coherent structures," *Chaos* 28, 075312 (2018). https://doi.org/10.1063/1.5021130
- M. Redeker, "A Language for Particle Interactions in Rule 54 and Other Cellular Automata," *Complex Systems* 26(1), 39-60 (2017). https://doi.org/10.25088/ComplexSystems.26.1.39

Assessment:
- Theorem 2 looks defensible as a new exact characterization for this relative-periodic CA model class.
- However, it is assembled from standard mathematical ingredients, so the safe claim is not that every implication is new, but that the exact equivalence and its CA-model-selection interpretation appear to be new.

Recommended wording:
- "Exact characterization" is supportable.
- Avoid stronger wording like "entirely new monotonicity principle" without qualification.

## Theorem 3

Statement in current paper: for a fixed finite candidate set with convergent orbit-class frequencies, Bernoulli NML asymptotically eliminates all non-rate-minimizers and stabilizes when the rate-minimizer is unique.

Search result:
- No direct prior theorem applying this to relative-periodic CA template selection was found.
- But the underlying phenomenon is not new in the abstract: it sits on classical MDL/NML asymptotics and model-selection consistency.
- The novelty is therefore at the level of:
  - the orbit-class Bernoulli model family,
  - the reduction from relative-periodic CA fitting to that family,
  - the explicit stabilization statement for this setting.

Primary sources:
- Andrew R. Barron, Jorma Rissanen, and Bin Yu, "The Minimum Description Length Principle in Coding and Modeling," *IEEE Transactions on Information Theory* 44(6), 2743-2760 (1998). https://doi.org/10.1109/18.720554
- Peter D. Grunwald, "Model Selection and the Principle of Minimum Description Length," *Journal of the American Statistical Association* 96(454), 746-774 (2001). https://doi.org/10.1198/016214501753168398
- Jorma Rissanen, "Model Selection using the Minimum Description Length Principle," *The American Statistician* 54(3), 209-217 (2000). https://doi.org/10.1080/00031305.2000.10474558

Assessment:
- Theorem 3 should not be sold as a new discovery about MDL/NML in general.
- It remains defensible as a new theorem for periodic CA template selection, because the search did not surface a direct predecessor in that literature.

Recommended wording:
- Good: "a stabilization theorem for Bernoulli NML over relative-periodic CA candidates."
- Safer than: "the first stabilization theorem of this kind in all MDL contexts."

## Theorem 4

Statement in current paper: there exist spacetime / candidate pairs for which the smaller-period background has positive asymptotic NLL rate, a higher-period velocity-matched candidate has zero rate, and NML eventually prefers the higher-period candidate.

Search result:
- No direct prior theorem with this NML nonidentifiability construction was found in the targeted search.
- Related literatures exist:
  - periodic pattern mining under MDL,
  - signal-processing representations with nested periodic dictionaries,
  - CA domain/particle work where finer temporal structure matters.
- None of the searched sources stated the manuscript's result: nonidentifiability of "background period" under Bernoulli NML for nested relative-periodic CA models.

Primary sources:
- A. Galbrun, T. N. Pham, and A. Termier, "Mining Periodic Patterns with a MDL Criterion," in *Advances in Intelligent Data Analysis XVII*, LNCS 11191 (2019). https://doi.org/10.1007/978-3-030-10928-8_32
- P. P. Vaidyanathan and B. V. Veen, "Nested Periodic Matrices and Dictionaries: New Signal Representations for Period Estimation," *IEEE Transactions on Signal Processing* 63(14), 3736-3750 (2015). https://doi.org/10.1109/TSP.2015.2434318
- J.E. Hanson and J.P. Crutchfield, "The attractor-basin portrait of a cellular automaton," *Journal of Statistical Physics* 66, 1415-1462 (1992). https://doi.org/10.1007/BF01054429
- J.P. Crutchfield and J.E. Hanson, "Computational mechanics of cellular automata: An example," *Physica D* 103, 169-189 (1997). https://doi.org/10.1016/S0167-2789(96)00259-X

Assessment:
- Theorem 4 appears novel in the searched literature.
- The claim should still stay scoped to the Bernoulli NML selector and the relative-periodic candidate family actually analyzed in the paper.

Recommended wording:
- "An explicit nonidentifiability construction for Bernoulli NML over relative-periodic CA backgrounds" is supportable.

## Theorem 5

Statement in current paper: if a spacetime is eventually exactly relative-periodic with minimal period `p0`, then any strict velocity-matched multiple has the same zero asymptotic NLL rate but larger asymptotic complexity, so NML eventually prefers `p0`.

Search result:
- No direct prior theorem in the searched CA literature was found.
- Conceptually, this looks like a standard nested-model MDL consequence:
  - both candidates fit asymptotically perfectly,
  - the smaller model wins because the complexity penalty differs by `Theta(log T)`.
- That makes Theorem 5 more of a clean specialization / complement than a strong standalone novelty claim.

Primary sources:
- Andrew R. Barron, Jorma Rissanen, and Bin Yu, "The Minimum Description Length Principle in Coding and Modeling," *IEEE Transactions on Information Theory* 44(6), 2743-2760 (1998). https://doi.org/10.1109/18.720554
- Peter D. Grunwald, "Model Selection and the Principle of Minimum Description Length," *Journal of the American Statistical Association* 96(454), 746-774 (2001). https://doi.org/10.1198/016214501753168398
- Oded Lachish and Ilan Newman, "Testing Periodicity," *Algorithmica* 60(2), 401-420 (2011). https://doi.org/10.1007/s00453-009-9351-y

Assessment:
- Theorem 5 is probably new as an explicit statement for this model class.
- It does not look like the right place to make a strong novelty pitch; it reads more naturally as the complementary identifiability corollary to Theorem 4.

Recommended wording:
- Keep it as the complement to Theorem 4.
- Do not present it as an independent flagship contribution.

## Practical Positioning for the Paper

Recommended contribution hierarchy after this search:

1. Theorem 1: prior art acknowledged; not a novelty claim.
2. Theorem 2: new exact characterization in the paper's model class, but built from classical ingredients.
3. Theorem 3: strongest defensible theory novelty, but phrase it as a CA-template/NML theorem, not as a general MDL breakthrough.
4. Theorem 4: strongest clean novelty claim after Theorem 3.
5. Theorem 5: complementary result; useful, but not a headline novelty claim.

Suggested high-level wording:
- "The paper's main theorem-level novelties are the exact monotonicity characterization for relative-periodic candidates (Theorem 2), the specialization of Bernoulli NML stabilization to this CA model family (Theorem 3), and the nonidentifiability/identifiability pair for background period recovery (Theorems 4-5), with Theorem 4 carrying the stronger standalone novelty."

## Residual Risk

This search did not uncover a direct predecessor for Theorems 2-5 in the targeted literatures. The remaining risk is not that the exact statements are obviously preempted, but that a reviewer may regard Theorems 2, 3, or 5 as specializations of broader known facts rather than deep standalone novelties. The safest response is careful positioning, not overclaiming.
