You are acting as a research mathematician, referee, and code auditor for a paper on cellular automata, computational mechanics, and MDL. Work autonomously inside this repo/session and do the job end to end.

Your goal is not to preserve the current paper. Your goal is to determine the strongest publishable version that is actually true, then prove it or narrow it until every claim is correct.

Treat false theorems and overclaimed MDL language as bugs.

Inputs I will provide in this session:
- manuscript text
- source files such as `coding.py` and `repair_nd.py`
- experimental summaries / tables
- known issues from prior review

Non-negotiable requirements

1. Every theorem / proposition / corollary / important claim must be classified as exactly one of:
   - CORRECT AS STATED
   - CORRECT AFTER EDIT
   - FALSE
   - HEURISTIC / EMPIRICAL ONLY

2. For every FALSE claim, do one of:
   - give a concrete counterexample, preferably executable, or
   - prove precisely why the statement fails.

3. For every CORRECT AFTER EDIT claim, write the strongest corrected statement you can actually justify.

4. Do not call anything “NML” unless it matches Grünwald-style NML for an explicitly stated probabilistic model.

5. Do not say “convergence” unless you prove eventual stabilization under explicit assumptions.

6. Do not preserve wording that is mathematically misleading just because it sounds nicer.

7. Do not stop at a review. Produce corrected theorem statements, proofs/counterexamples, code patches, tests, and a revision plan.

Known issues you must address explicitly

A. Proposition 2 is false as stated.
Counterexample: period-1 spacetime with defects every 3rd step. Period 3 absorbs the defect structure and can win for all large T. So convergence to the “true background period” fails in general.

B. “NML parametric complexity” is overstated.
The current score `(k/2) log(T/p)` plus a run-length residual code is not strict NML in the Grünwald sense. It may be an asymptotic penalty, a BIC-like term, or an MDL-inspired heuristic, depending on the exact model.

C. The monotonicity corollary is too strong.
Monotonicity does not hold for arbitrary periods. It may hold only along actual refinement chains / model-class inclusions. Verify the exact condition.

Primary tasks

TASK 1: Build a complete claim ledger
Create a file `CLAIM_LEDGER.md` containing every major claim in the paper:
- exact quote or paraphrase
- location
- status
- proof status
- counterexample if false
- strongest corrected replacement
- whether the abstract/introduction/discussion also need updating

TASK 2: Prove the strongest correct projection theorem
Generalize the projection result to a partition theorem.

Target form:
- finite index set Ω
- partition Π = {C_1, ..., C_k}
- model class F_Π = {b in {0,1}^Ω : b is constant on each C_j}

Prove:
- the minimizer of Hamming distance d_H(x,b) over b in F_Π is obtained by majority vote on each cell
- the minimum is sum_j min(#0s in C_j, #1s in C_j)
- uniqueness holds iff no cell is tied

Then specialize this abstract theorem to the relative-periodic orbit partition used in the paper.

Be fully explicit about:
- finite observation window
- toroidal spatial dimensions
- shift vector
- period
- orbit labels / equivalence classes

If tie-breaking matters for downstream residual compression, state that and test it.

TASK 3: Fix monotonicity at the right level of abstraction
Do not start from periods. Start from partitions / model classes.

Prove the abstract theorem:
If Π_2 refines Π_1, then
  d*_Π2(x) <= d*_Π1(x),
where d*_Π(x) is the minimal Hamming distance to F_Π.

Then determine the correct relative-periodic corollary.

You must verify the exact condition under which one relative-periodic model class is included in another on a torus. Do not assume:
- same shift + p1 divides p2
unless you actually prove that it implies refinement in this setting.

Investigate whether the sufficient condition is:
  (p2, s2) = m (p1, s1)
componentwise modulo spatial sizes,
or something slightly different.

If any commonly tempting formulation is false, provide a concrete counterexample and add a regression test.

TASK 4: State and prove the nonidentifiability result
Write a clean theorem/proposition explaining why “background period recovery” is impossible in general.

Minimum requirement:
- show that if the residual/defect pattern has its own periodic structure, a larger period can absorb it and outperform the smaller period indefinitely
- generalize beyond the specific period-1 / every-3rd-step example if possible

The point should be:
the observed spacetime does not intrinsically separate into “background” plus “defect” without additional assumptions.

TASK 5: Replace the current convergence claim with the strongest true stabilization theorem
You need a theorem that is actually correct.

Candidate target:
For a fixed finite candidate set C and scores
  S_m(T) = L_m(T) + λ_m(T),
if λ_m(T) = O(log T) and L_m(T)/T -> ℓ_m for every candidate m,
then any unique minimizer of ℓ_m is eventually selected.

You must verify all assumptions for the actual score being used.
In particular:
- if the residual term is run-length code, does L_m(T)/T even converge under the assumptions you have?
- if not, do not use this theorem for RL-based selection.

If there are ties in ℓ_m, determine whether you can prove a sharper theorem with
  L_m(T) = ℓ_m T + b_m log T + O(1),
or whether ties remain unresolved.

Do not claim recovery of a latent “true background period” unless you add extra assumptions and prove it.

TASK 6: Choose and formalize the model-selection framework
Pick the strongest mathematically coherent option and align the code and paper to it.

Option A: Exact orbitwise Bernoulli NML
- specify the probabilistic model on orbit classes
- derive the exact NML or an exact accepted alternative
- include correct complexity terms, constants, and non-identical orbit sizes
- verify whether omitted constants could change empirical winners

Option B: Exact two-part deterministic template + combinatorial defect code
- encode the template/background explicitly
- use the minimal Hamming residual weight and a combinatorial residual code such as log2 binom(N,w)
- use this if it aligns cleanly with the projection theorem and yields rigorous claims

Option C: Heuristic residual-compression selector
- keep RL/LZ4 as a heuristic screening score or geometric diagnostic only
- then remove theorem-level MDL/NML claims and relabel the method honestly

Prefer the strongest rigorous paper, not the smallest edit.
If exact NML is too heavy but exact two-part coding is clean, take the exact two-part route.
If neither can be made rigorous for the current selector, move RL/LZ4 to secondary analysis only.

TASK 7: Audit the current code against the mathematics
Read `coding.py` and `repair_nd.py` carefully.

You must answer:
- Is `template_bits_nml` correctly named?
- Is its docstring mathematically accurate?
- Is the paper’s theory optimizing the same objective as `mdl_total_bits`?
- Does Theorem 1 justify the selector currently used?
- Which comments and function names overclaim?

Then patch the code/comments accordingly.

At minimum, audit:
- `template_bits_nml`
- `mdl_total_bits`
- majority-vote projection logic
- tie handling
- any mention of “NML” or “parametric complexity”

Never silently keep misleading names.

TASK 8: Fix the run-length proposition
Verify the asymptotics for the actual gamma-coded run-length scheme used in the code.

Check whether the correct statement is:
- additive gap Θ(N)
- ratio Θ(N / log N)
- or something else

Give explicit constructions:
- same Hamming weight
- one highly clustered
- one highly fragmented
- compute RL codelengths exactly/asymptotically

Then rewrite the proposition and proof correctly.

TASK 9: Separate theorem-backed claims from heuristic / empirical claims
The paper currently risks mixing these levels.

You must make a strict separation:
- theorem-backed statements
- coding-framework statements
- heuristic residual-geometry statements
- empirical observations
- speculative interpretation

Do not allow the manuscript to imply:
- exact NML if it is not exact NML
- dynamical “defects” in the computational-mechanics sense if only projection residuals are observed
- coherent structures / particles without direct evidence

Prefer terminology like:
- projection residual
- residual mask
- persistent residual population
unless stronger evidence is added.

TASK 10: Reassess the empirical claims under the corrected theory
Using the provided data and, where feasible, reruns or small verification scripts:
- check whether the selected periods change under corrected penalties
- especially test cases with small reported margins
- compare current asymptotic penalty vs corrected exact/asymptotic alternatives
- compare combinatorial residual code vs RL
- test flattening-order sensitivity for RL
- report where the winner is stable and where it is not

Do not claim “confirmed convergence” from finite data.
You may say “empirical stabilization over the tested range” if that is what the data support.

Expected deliverables

Create these outputs:

1. `VERDICT.md`
A concise verdict on:
- current manuscript
- strongest corrected manuscript
- what still blocks acceptance

2. `CLAIM_LEDGER.md`
Every major claim with status and replacement.

3. `THEORY_NOTE.md`
Formal theorem statements, proofs, counterexamples, and assumptions.

4. `REVISION_PLAN.md`
A prioritized list of manuscript and code changes.

5. `MANUSCRIPT_PATCH.md`
Concrete replacement text for:
- title
- abstract
- introduction
- theory section
- discussion / limitations / conclusion
Only include wording you believe is mathematically honest.

6. `tests/test_theory.py`
Executable tests / checks for:
- partition projection theorem on small examples
- monotonicity under actual refinement
- counterexamples to false monotonicity forms
- counterexample to false period-convergence claim
- RL asymptotic examples if practical

7. `scripts/find_counterexamples.py`
Search small cases for false statements and produce explicit examples.

8. `scripts/compare_scores.py`
Compare:
- current score
- exact or corrected asymptotic Bernoulli-NML-like score if implemented
- exact two-part combinatorial score if implemented
- RL / LZ4 secondary diagnostics

Strong candidate theorem suite to aim for
Use this as a target, but only keep what you can prove.

A. Partition projection theorem
For any finite partition Π, majority vote gives an optimal Hamming projection onto the class of fields constant on Π, with exact minimum disagreement and uniqueness iff no ties.

B. Partition-refinement monotonicity
If Π_2 refines Π_1, the optimal Hamming disagreement under Π_2 is no larger than under Π_1.

C. Relative-periodic corollary
Only under a proved inclusion/refinement condition for the orbit partitions/model classes. State the exact condition you can prove, and no stronger one.

D. Nonidentifiability theorem
Without extra assumptions, no procedure based only on the observed spacetime can generally recover a unique “background period”.

E. Finite-candidate stabilization theorem
For a finite candidate set, eventual selection of the unique minimizer of asymptotic score density holds under explicit assumptions on the score decomposition.

F. Optional recoverability theorem under explicit noise assumptions
Only if you can actually prove it.
Possible form:
- exact relative-periodic background with minimal period
- i.i.d. or stationary ergodic aperiodic flip noise with rate < 1/2
- candidate set restricted appropriately
- exact code, not RL heuristic
Then the smallest correct background period may eventually win.
Do not claim this unless the proof is complete.

Behavior rules

- Do not stop after analysis. Make the edits and produce the files.
- Do not hand-wave proofs.
- When a proof attempt fails, switch to falsification mode and look for a counterexample.
- When exact NML is impractical, say so clearly and move to the strongest exact alternative.
- Never use “NML” as a marketing label.
- Never treat heuristic residual compression as theorem-backed unless you prove the exact selector you are optimizing.

Final response format
At the end of your work, give me:

1. A one-paragraph verdict on the current manuscript.
2. The strongest theorem suite you believe is actually true.
3. Which model-selection route you chose (exact NML, exact two-part, or heuristic secondary score).
4. A list of manuscript claims/sentences that must be deleted or rewritten.
5. A summary of code changes and test results.
6. Any remaining unresolved mathematical points.

Now inspect the repo/session materials and start the work.

