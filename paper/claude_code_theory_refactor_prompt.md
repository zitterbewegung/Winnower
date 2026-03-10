Refactor this project from an empirically led CA survey paper into a theorem-forward paper with empirical validation in a supporting role.

You are working in:
- `/Users/r2q2/Projects/Experiments/relative_symmetry_repair`

Start by reading only the files that matter:
- `paper/paper_v5.md`
- `paper/orbitwise_mdl_presentation.tex`
- `src/relative_symmetry_repair/repair_nd.py`
- `src/relative_symmetry_repair/coding.py`
- `scripts/survey_persistent_defects.py`
- `scripts/strengthen_v2.py`
- `outputs/best_relative_periodic_fits.csv`
- `outputs/reflection_repair_comparison.csv`
- `outputs/survey_2d_rules.csv`
- `outputs/survey_persistent_defects.csv`
- `outputs/strengthening_v2/verification_400step.csv`
- `outputs/strengthening_v2/multi_seed_mdl.csv`
- `outputs/strengthening_v2/multiseed_scaling.csv`
- `outputs/strengthening_v2/autocorrelation_mdl.csv`
- `outputs/strengthening_v2/period_convergence.csv`

Primary objective:
- Produce a new draft at `paper/paper_v6_theory.md` that pivots the paper toward clean mathematics, precise model-selection language, and a much smaller empirical core.

Secondary objective:
- Produce `paper/paper_v6_theory_notes.md` with:
  - theorem candidates you considered and kept/dropped
  - claims from `paper_v5.md` that were removed or softened
  - what still needs proof or more literature support

Non-negotiable corrections:
1. Do not claim exact NML unless you actually derive and implement an exact NML code. The current code uses an MDL-motivated two-part score with an asymptotic parametric-complexity penalty plus run-length defect coding.
2. Do not keep the current monotonicity theorem in its fixed-shift form. It is false as stated. Replace it only with statements you can actually justify from the implemented model.
3. Do not present the paper as mainly a 2D rule survey. The survey should become validation or motivation, not the paper's center of gravity.
4. Do not oversell “persistent structured defects” as particle theory. Keep that language modest unless you introduce actual component tracking or symbolic-dynamics machinery that supports it.

Preferred strongest version of the paper:
- Theory framed at the level of partitions: optimal Hamming projection and monotonicity under refinement.
- Model selection done with an exact code:
  - either exact NML for an orbitwise Bernoulli model,
  - or an exact two-part deterministic template code plus combinatorial defect code.
- Run-length and LZ4 residual compression used only as secondary geometry diagnostics unless you label them explicitly as heuristic selectors.
- Identifiability made explicit: include a short impossibility result explaining why a “true background period” is not recoverable without assumptions on the defects.
- Add a stronger positive control on Rule 54 and Rule 110 by comparing the residual masks to known domain/particle or local-causal-state structure where possible.
- Make the empirical message crisp: this is a fast screening tool that finds rules with persistent residual structure worth deeper computational-mechanics analysis.
- For the 2D highlights, include not just defect counts, but component persistence, scaling fits, and visual evidence.

Recommended target framing:
- The cleanest pivot is to reinterpret the fitted background class as a fixed-point subspace, or equivalently an orbit-constant code, induced by a cyclic spacetime symmetry action.
- Then the key theorem becomes: nearest background fitting under Hamming loss is exact nearest-codeword decoding in a direct sum of orbitwise repetition codes, solved by majority vote on each orbit.
- Model selection then becomes a separate layer: ideally an exact code over a nested or partially nested family of symmetry classes, with heuristic residual coders clearly demoted to diagnostics.
- The empirical section becomes a sanity/validation section showing the framework is not vacuous on canonical ECA and selected 2D rules.

Theory directions to explore in this order:

1. Partition / fixed-point / coding-theory formulation
- Define the induced partition of the spacetime window directly and make that partition, not the rule survey, the conceptual centerpiece.
- Define the permutation action on the observed spacetime window induced by temporal period and spatial shift.
- Show that the admissible background class is the fixed-point set of that action.
- Formalize the class as a binary linear subspace, ideally as a direct sum of repetition codes over orbit classes.
- Prove exact nearest-codeword decoding under Hamming loss by orbitwise majority vote.
- Make clear when one partition refines another and what that implies for optimal Hamming projection.
- If clean, generalize to:
  - q-ary alphabets
  - weighted Hamming loss
  - ties and non-uniqueness conditions
- If possible, derive exact dimension / number of free binary parameters and computational complexity.

2. Correct monotonicity / capacity statement
- Replace the false theorem with one of these, if valid:
  - partition-refinement monotonicity at the partition level
  - scaled-shift refinement: a refinement result when both period and cumulative shift scale compatibly
  - candidate-set monotonicity: enlarging the scanned model family cannot worsen the best achievable defect rate
  - any stronger statement you can prove directly from the implemented labeling scheme
- Be explicit about what fails for fixed shift with changing period.

3. Exact coding / selector theory
- Try to refactor the selector away from heuristic RL-first language.
- Preferred options, in order:
  - exact NML for an orbitwise Bernoulli model, if the model class and normalization can be made explicit cleanly
  - exact two-part deterministic template code plus exact combinatorial defect-mask code
  - asymptotic or heuristic MDL only if the exact routes prove unwieldy
- If you keep RL or LZ4 in the main text, demote them to geometry diagnostics or heuristic alternatives and say so plainly.
- Separate:
  - the theoremically justified selector
  - the geometry-sensitive diagnostics

4. Identifiability / impossibility
- Add a short proposition or remark showing that the “true background period” is not identifiable from the full spacetime without assumptions on defect sparsity, stochasticity, or non-periodicity.
- Good target:
  - if defects can themselves be periodic or be absorbed into a refined template, then multiple background/defect decompositions are observationally equivalent or asymptotically preferred under richer models
- Use this to justify why the paper estimates the best descriptive symmetry class, not a metaphysically unique hidden background.

5. L2 / harmonic-analysis relaxation
- Check whether there is a useful companion theorem for real-valued fields:
  - L2 projection onto the fixed-point subspace equals orbit averaging
  - binary fitting is then a thresholded or discretized analogue of an exact projector
- Keep this only if it materially clarifies the theory; otherwise make it a short remark.

6. Symbolic-dynamics / defect refactor
- Recast the background as a finite-window approximation to a periodic spacetime factor or invariant subshift viewpoint.
- Use symbolic-dynamics language only where it buys real conceptual leverage.
- A good target is: “defects as departures from an invariant language/background class”, not “we solved particle theory”.

7. Empirical refactor
- Make the empirical message: the method is a fast screening tool, not the last word on coherent structures.
- Use the autocorrelation comparison as a baseline for selector quality.
- Add a stronger positive control on Rule 54 and Rule 110:
  - compare fitted residual masks and known periodic domains / particles qualitatively
  - if possible, compare to local-causal-state or computational-mechanics descriptions from the literature
- For 2D highlights, include:
  - defect counts
  - connected-component persistence
  - size-scaling fits
  - visual evidence
- Compress the broad survey; emphasize selected exemplars and what they demonstrate theoretically.

Strong candidate theorem list:
- Theorem A: Fixed-point / orbit-constant characterization of the background class.
- Theorem B: Exact Hamming projection by orbitwise majority vote, with uniqueness iff no orbit ties.
- Theorem C: q-ary or weighted generalization of Theorem B.
- Theorem D: Partition-refinement monotonicity or a correct refinement theorem.
- Proposition E: Identifiability impossibility or non-identifiability of “true background period” without defect assumptions.
- Proposition F: L2 projector by orbit averaging.
- Proposition G: Exact-code or MDL-type overfitting control / finite-candidate stabilization under explicit assumptions.

What to demote from the current paper:
- Large survey rhetoric in the abstract and introduction.
- Exact-rank claims that are not auditable from checked-in artifacts.
- Any claim that period margins increase monotonically with observation length.
- Any claim that S11/B37 is clearly sub-extensive unless you prove it from scaling analysis.

What to keep, but move into validation:
- 1D ECA sanity check:
  - `outputs/best_relative_periodic_fits.csv`
  - `outputs/reflection_repair_comparison.csv`
- 1D stronger positive control:
  - qualitative comparison against known Rule 54 / Rule 110 domains and particles from the literature
- 2D validation:
  - strongest low-defect rules from `outputs/survey_2d_rules.csv`
  - persistent-defect candidates from `outputs/survey_persistent_defects.csv`
  - 400-step verification and size scaling from `outputs/strengthening_v2/*`
- baseline comparison:
  - `outputs/strengthening_v2/autocorrelation_mdl.csv`

Make the persistent-defect section more principled:
- Surface the actual targeted-search criteria from `scripts/survey_persistent_defects.py`:
  - nontrivial end density
  - defect-rate window
  - late defect count threshold
  - ranking by `defect_rate * (run_length_bits / defect_sites)`
- Explain why the paper focuses on S24/B11, S11/B37, and S37/B11 rather than pretending they emerged uniquely from a single ranking.

Preferred new outline:
1. Introduction
2. Partitions, symmetry classes, and orbit codes
3. Exact projection theorems
4. Exact or MDL-style model selection
5. Identifiability limits
6. Relation to symbolic dynamics and computational mechanics
7. Validation on canonical examples and selected 2D rules
8. Limitations and open theory problems
9. Conclusion

Tone requirements:
- Make the paper sound mathematically honest and modest.
- Prefer exact statements over expansive novelty language.
- If something is heuristic, say heuristic.
- If something is conditional, state the condition.
- If something is only empirical, say empirical.

Literature anchors to use and verify:
- Peter Grünwald, *The Minimum Description Length Principle*:
  - https://mitpress.mit.edu/9780262529631/the-minimum-description-length-principle/
  - Use for MDL language and exact-versus-asymptotic model-selection framing.
- Adam Rupe and James P. Crutchfield, “Local Causal States and Discrete Coherent Structures”:
  - https://arxiv.org/abs/1801.00515
  - Use to position against local predictive/state-space reconstructions.
- J. E. Hanson and J. P. Crutchfield, “The Attractor-Basin Portrait of a Cellular Automaton”:
  - https://csc.ucdavis.edu/~cmg/compmech/pubs/ABPoaCATitlePage.htm
  - Use for domains/dislocations and computational-mechanics context.
- Marcus Pivato, “Defect Particle Kinematics in One-Dimensional Cellular Automata”:
  - https://arxiv.org/abs/math/0506417
  - Use for symbolic-dynamics defect language and for sharpening the limits of particle claims.
- Marcus Pivato, “Spectral domain boundaries in cellular automata”:
  - https://arxiv.org/abs/math/0507091
  - Use if partition/domain-boundary framing helps.
- Nino Boccara and Michel Roger, “Totalistic two-dimensional cellular automata exhibiting global periodic behavior”:
  - https://arxiv.org/abs/adap-org/9904002
  - Use to contextualize the low-period 2D rules.
- Cosma Shalizi et al., “Automatic Filters for the Detection of Coherent Structure in Spatiotemporal Systems”:
  - https://arxiv.org/abs/nlin/0508001
  - Use as another contrast class for coherent-structure extraction.

Specific deliverables:
1. Write `paper/paper_v6_theory.md`.
2. Write `paper/paper_v6_theory_notes.md`.
3. In the notes file, list:
   - which theorem became the paper’s centerpiece
   - whether the selector is exact NML, exact two-part, or only MDL-motivated
   - which empirical sections were compressed
   - which claims remain unproved
   - which additional experiments would still help but are no longer central
4. Keep the old paper untouched.

Success criterion:
- After the rewrite, the paper should read like a theory paper with a validation section, not like a survey paper with a few theorems attached.
