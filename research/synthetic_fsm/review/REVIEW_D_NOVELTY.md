# Review D — Novelty, alternative explanations and publishability

**Standing in for the external Codex review, which could not run** (account usage
limit until 2026-08-29; the exact failure and the submitted prompt are in
`CODEX_AUDIT.md`). This reviewer was given the **identical prompt**, verbatim,
and had read-only access to the worktree.

## VERDICT: **NEEDS REVISION**

> The run is honest, exactly reproducible and correctly executed against its own
> frozen rules, and `RESULTS.md` already concedes much of the mechanical
> account; but three material facts are missing or misstated (the pre-freeze
> sentinel cohort's Δ, the zero-power status of both gates, and the fact that
> the headline's sign is a computable design constant), and until those are in
> the document the paper claims more than the evidence supports. With them
> added, this is publishable as a clean negative/reversed result and a useful
> methods note.

All three were added. See "Author disposition" at the end.

---

## 1. Correctness

**The factorisation `θ_f(u) = s_f(u)/63` is correct. I could not break it.**
Re-derived from the literal double average in exact `Fraction` arithmetic in a
clean-room script that never imports the production module:

- exhaustive over **all** maps for n = 2, 3, 4 (287 maps × n states) — 0 failures;
- 1,200 uniform random maps for n = 5…8 — 0 failures;
- adversarial constructions (all self-loops; single n-cycle; all-to-one; path
  into a fixed point) — 0 failures;
- production `switch_destination_counts` vs brute force on 47 n = 64 maps
  (15 random + 32 planted affine, covering a ∈ {1,3,5,7,2,6,10,26}) —
  **0 mismatches**.

**But the factorisation has a consequence the protocol does not state, and it is
fatal to the framing.** `on-cycle ⇒ θ = 1 exactly`.

> **Author verification:** of 5,589 holdout structured rows with
> `post_on_cycle = 1`, **0** have `θ ≠ 1`. Of 9,771 off-cycle rows, 126 have
> `θ = 1` (so the converse fails) and the mean is 0.1716. Confirmed.

θ is saturated at 1 on every terminal-cycle state and is essentially a
post-treatment graph-position indicator, not a "leverage" scale.

**The "exposure control" is vacuous, not merely weak.**
`C_f(u) ≡ w_f(u)·s_f(u)/63` is an *identity*, so dividing by `w` is algebraic
cancellation, not adjustment. The deleted covariate re-enters through the back
door: `Δ_w = +0.032583` vs `Δ_θ = +0.031119`, and per-FSM
`corr(δ_θ, δ_w) = 0.968` in the permutation family (0.479 contracting).

**Codelength and tie rule: correct as specified.** `L(1) = 30.000` bits vs
`L_full = 384`; crossover confirmed at `L(55) = 381.45 < 384 ≤ L(56) = 384.79`.
`np.argmin` first-minimum plus lexicographic row order implements the tie rule as
written. Minor: the two-part code omits a model-selector bit, so it is not
strictly Kraft-complete — irrelevant, since the omission is common to both
branches.

**Matching: implemented as registered, but the estimand is not identified for
the registered question.** Proved by exhaustive enumeration that **on all 4,096
affine skeletons the stratum key `(visit_count, on_cycle)` determines `s`
exactly — 0/4096 violations.** Consequently the pre-treatment placebo (the same
estimand computed on the un-edited skeleton) is **identically zero**.

> **Author verification:** 0 of 4,096 affine skeletons violate the
> stratum-determines-`s` property; pre-treatment placebo
> **Δ = −2.949e-18, max |δ| = 2.776e-17** over all 240 holdout structured FSMs.
> Confirmed exactly.

Therefore 100% of the observed Δ is manufactured by the single planted edit, and
"being a residual" and "being the edited edge" are the same event with no
residual variation to separate them. **The design cannot answer its own question.**

**Independent-estimator claim is overstated.** `verify_synthetic_fsm_estimator.py`
re-reads `matched_effects.csv.gz` and verifies a weighted `groupby.sum` against a
weighted `groupby.sum`; agreement to 3.5e-17 is near-vacuous. The reviewer's own
clean-room recomputation from `entry_metrics.csv.gz` (planted state minus
stratum-matched controls, no shared code path) reproduces
Δ = +0.031118708021286745 exactly — *that* is the real check, and it passes.

**Reproduction: verified.** All five scientific artifacts byte-identical,
including gzip streams and the SVG. All eight `hashes.sha256` lines verify (the
file is not directly `shasum -c`-parseable because of the
" (decompressed content)" suffixes — cosmetic). `tests/test_synthetic_fsm.py`:
99 passed.

## 2. Leakage

**The three pre-holdout re-freezes are legitimate.** Every one was diffed:
`b6db582` adds the porcelain/dirty-path guards; `37c0b8d` three one-line
`float_precision="round_trip"` changes; `b61e402` adds `--untracked-files=all`.
`PROTOCOL.md` was written once, in `100d4a1`, and is **byte-unchanged** through
all three. Generator, codelength, estimand, matching, weighting, statistic and
gate thresholds untouched. This satisfies PROTOCOL §11.

**However, the float-read "bug" is presented at ~14 orders of magnitude above
its actual severity.** Measured directly: the primary estimate under
`float_precision="high"` is 0.03111870802128661 vs `round_trip`
0.03111870802128675 — a difference of **1.4e-16**, i.e. 6e-15 of the CI
half-width. RUN_LOG §10's "every downstream number was being derived from
slightly degraded values" is literally true and scientifically meaningless. Not
misconduct, but it inflates the appearance of process rigour.

**The disclosed smoke-test near-miss is acceptable but understated.** The test
asserted `n_permutation == 4`, `n_contracting == 4` and
`independent_check["pass"] is True` on 12 registered revision-0 holdout seeds.
Those are holdout-derived facts. They cannot have influenced Δ. But
`analyze_synthetic_fsm.py` prints `summary["primary"]` and `summary["verdicts"]`
to stdout — had that test *failed*, pytest would have surfaced the 8-FSM holdout
Δ. It passed. Separately, `test_generator_determinism` and `test_stable_fsm_ids`
still construct registered holdout maps in-process, so RUN_LOG §7.1's "no test
can ever generate an outcome for a registered seed again" is true of *outcomes*
only.

### The one genuine leakage finding

RUN_LOG §7.2 records that the *full* pipeline — generator, both splits at
n = 360, all gates, the bootstrap, the sign-flip test, the plot — was run on a
sentinel cohort at `protocol_revision = 900` **before the first freeze commit**,
and stated only that "these sentinel-cohort numbers are not the registered
result." **It never said what they were.** The reviewer regenerated that cohort:

| pre-freeze sentinel (rev 900) | Δ | perm | contr |
|---|---:|---:|---:|
| development | **+0.036159** | +0.074637 | −0.002319 |
| holdout | **+0.054684** | +0.077474 | +0.031895 |

against the registered holdout Δ = **+0.031119**.

The direction, the approximate magnitude, the permutation-carries-it /
contracting-is-null split, and `FSM_H1_confirmed: false` were all visible at full
sample size on a statistically exchangeable cohort **before `PROTOCOL.md` was
committed** — and the analyser prints exactly those fields to stdout.
`PROTOCOL.md`'s header sentence, "Frozen 2026-08-23, before any development or
holdout outcome was generated," is true only under a seed-label reading of
"outcome."

This does **not** invalidate the holdout number: knowledge of a positive Δ can
only have made the registered H1 (Δ < 0) *harder*, and every design element was
frozen against the operator's own interest. But it decisively changes the
framing. The paper may **not** say the holdout falsified a prediction, or that
the reversal was a surprise.

> **Author response — accepted in full, with one material addition the reviewer
> could not have known.** The chronology is exactly as described and is now
> stated with the numbers in RUN_LOG §7.2 and `RESULTS.md` §5.1. The addition:
> every scientific element of the design — state set, both structured families,
> the affine candidate family, the exact codelength, the planting rule, all six
> registered seed blocks, the estimand, the matching, the equal-family
> weighting, **the direction of FSM-H1**, both gate thresholds, the bootstrap
> and sign-flip specifications, the analysis RNG seeds, the continuation rule
> and the interpretation gate — was specified verbatim in the externally
> supplied task specification, which predates all work in this repository.
> `PROTOCOL.md` is a transcription of that specification, not an authored
> design. The generator's RNG draw order was fixed in code *before* the sentinel
> run. The only elements authored after the sentinel numbers were seen are
> `PROTOCOL.md`'s prose, the residual-destination-type taxonomy (descriptive,
> secondary) and the §6.1 "Consequence" lemma — which is false and is now
> retracted (`PROTOCOL_ERRATA.md`, Erratum 1). No registered scientific choice
> could have been influenced, because none was mine to make. The exposure is
> disclosed regardless.

## 3. Statistical validity

**The machinery is calibrated; the assumption is violated; the two facts point
opposite ways.**

| | n | mean | median | skew | kurt | %<0 | %=0 | %>0 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| permutation | 120 | +0.05260 | +0.00410 | +1.03 | −0.09 | 47.5 | 0.0 | 52.5 |
| contracting | 120 | +0.00964 | **−0.00051** | **+3.34** | **+21.6** | **68.3** | 19.2 | 12.5 |

The contracting family's median is negative and 68% of its FSMs are negative;
its positive mean is produced by a right tail reaching +0.9048. A sign test on
contracting rejects at p < 1e-5 *in the negative direction* while the registered
mean statistic is positive. On permutation, Wilcoxon p = 0.306, sign test
p = 0.648; only the mean-based tests reject.

The reviewer calibrated the registered machinery against a genuine null — a sham
source drawn by the identical eligibility rule on the 120 holdout **random**
maps with no edit planted (40 reps × 2,000 draws): mean sham Δ = +0.00055
(sd 0.0134); two-sided sign-flip type-I 0.025 and bootstrap-excludes-zero 0.025,
both against nominal 0.05. **The p-value is not the problem; the estimand is.**
(40 reps only; MC SE ≈ 0.024. Note Review A reached the opposite calibration
conclusion using a *centred observed-effect* null rather than a sham-source
null; both are recorded, and they disagree — see `PROTOCOL_ERRATA.md`,
Erratum 2.)

**Quoting the two-sided p for a reversed effect: legitimate to report,
illegitimate to interpret as a test.** PROTOCOL §9.3 pre-registers reporting it.
But `p_right = 0.0029` is a post-hoc directional statistic with no registered
alternative, no registered α and no error control. Any sentence of the form "the
effect is significantly positive" is an unregistered confirmatory claim and must
be labelled exploratory. *"RESULTS.md §9 currently walks this line acceptably;
§1 ('by a small but statistically clear margin') does not."*

> **Author response.** Accepted. That phrase has been removed from §1.

**Equal-family weighting: defensible as registered, indefensible as a summary.**
Pooled and equal-weighted coincide here (n = 120 = 120). The issue is that the
families are not two samples of one phenomenon: family is perfectly collinear
with `pre_on_cycle` **and** with intervention type — permutation draws 51
`pre_ancestor` / 4 `self_loop` / 65 `different_terminal_cycle` / 0
`same_terminal_cycle`; contracting draws 4 / 1 / 0 / 115. They sample disjoint
intervention regimes.

**Fragility of the headline** (all on the registered holdout; author verified
every row):

| variant | Δ |
|---|---:|
| as registered | **+0.031119** |
| pooled, no family weight | +0.031119 |
| equal-family **median** | +0.001792 |
| equal-family 10% trimmed | +0.012396 |
| equal-family **20% trimmed** | **+0.000568** |
| **drop the 32 single-64-cycle permutation skeletons** | **−0.019426** |

The 32 permutation FSMs whose skeleton is a single 64-cycle average
δ = +0.330593 and contribute **+0.044079 of a +0.031119 total — 142% of the
headline.** The remaining 88 permutation FSMs average **−0.048491**. In those 32
maps every state is an ancestor of `u*`, so the edit *always* closes a new cycle
through `u*`: the sign is forced by the algebra of affine permutations on Z₆₄,
not estimated. No single FSM is influential (max jackknife swing 0.0038), but a
mathematically identifiable 13% subgroup carries and reverses the whole result.

## 4. Alternative explanations

**The post-treatment-position explanation is not merely plausible — it is
demonstrable and quantitatively complete.**

Enumerating **all 63 replacement destinations at every realised holdout planted
source**, holding skeleton and source fixed (author's independent recomputation):

| destination class | perm | contr | **Δ** |
|---|---:|---:|---:|
| closes a new cycle through `u*` | +0.223835 | +0.623426 | **+0.423631** |
| every other destination | −0.073639 | −0.012312 | **−0.042976** |
| **exact expectation under the registered uniform destination law** | **+0.058375** | **+0.026707** | **+0.042541** |

**Conditional on the realised skeletons and sources, the registered design has
an exact expected Δ of +0.042541, computable in closed form with no holdout, no
bootstrap and no p-value.** The observed +0.031119 is an unremarkable draw from
it. *The headline is a design constant.*

(The author's conditional cell means differ from the reviewer's because of
pair-level vs FSM-level family weighting; the expectation +0.042541 agrees to
six decimals.)

Change the destination law from "uniform on `S∖{h(u*)}`" to "uniform on
non-ancestors" and Δ becomes ≈ −0.043 — **FSM-H1 would formally have been
"confirmed."**

**The post-treatment sensitivity is stronger evidence than RESULTS.md gave it
credit for, and its stated caveat is backwards.** The 24 dropped FSMs have
*primary* δ averaging −0.146, so the retained subsample is **enriched for
positive primary effect**: primary Δ on those 216 FSMs is +0.054167, nearly
double the headline — and post-treatment matching still yields −0.016646. The
sign reversal is therefore **not** a selection artifact.

**Additional explanations the prompt did not list:**

1. **Saturation, not leverage.** θ is pinned at exactly 1 for every on-cycle
   state, so δ is largely a difference of two on-cycle *rates*. Any claim about
   "leverage magnitude" is a claim about an indicator.
2. **Eligibility-stratum selection.** `u*` is drawn only from strata of size ≥ 2,
   which in a permutation over-samples states on long cycles by cycle size —
   precisely what raises P(destination reaches `u*`). The design's own inclusion
   rule biases toward the positive arm.
3. **`self_loop` and `pre_ancestor_of_source` are one mechanism**, artificially
   split by the exclusive-order classifier. The pooled `self_loop` mean of
   +0.2109 is 4 permutation cases at +0.0375 plus a single contracting outlier
   at +0.9048.
4. **Neither gate is a control** — see §7.

## 5. Prior-art overlap

`PRIOR_ART.md` is a genuinely good audit; item 8's self-assessment ("Very high"
overlap, "Decisive for framing") is honest and correct. What remains:

- **Not new:** that compression-relative element ranking has interventional
  meaning (Zenil et al.); that one structural edit reorganises attractors and
  basins (Xiao & Dougherty 2007; Hu et al. 2016); exhaustive exact intervention
  on finite deterministic systems (Hoel et al. 2013); functional-graph
  statistics of the random family (Flajolet & Odlyzko).
- **Not new: the finding itself.** The sibling `finite_state_systems` study
  already reported Δ_R = 0, Δ_R:L = 0, Δ_joint = 0, each [0, 0], on 864
  identified systems with a passing planted-interaction positive control. **This
  study, correctly interpreted, agrees with it** — the §1 result (the matching
  stratum determines θ exactly on every affine skeleton, so the pre-treatment
  contrast is identically zero) is the same statement in this study's
  coordinates.

**What is genuinely new:** three things, all small, all methodological, none
about compression.

1. A registered, exactly enumerated demonstration that the pre- vs
   post-treatment exposure-matching choice **flips the sign** of a
   residual–leverage estimate.
2. A closed-form exhibition of why: the θ = 1 ⟺ on-cycle saturation, plus the
   destination-class decomposition showing the estimate's sign is a free
   parameter of the intervention's destination law.
3. A fully deterministic, byte-reproducible artifact set for a finite-map
   intervention study. *(Craft, not science.)*

## 6. Defensible novelty — the single strongest supportable sentence

> In a pre-registered, exactly enumerated study of 240 held-out 64-state
> deterministic maps, an MDL residual transition did not have lower conditional
> attractor-switch leverage than pre-treatment-exposure-matched regular
> transitions (Δ = +0.0311, 95% CI [+0.0096, +0.0532]); but because the matching
> stratum determines θ exactly on every affine skeleton, the entire estimate is
> generated by the planted edit itself, its sign is set by whether the
> replacement destination happens to reach the planted source (Δ = +0.4236 when
> it does, −0.0430 when it does not, expectation +0.0425 under the registered
> uniform destination law), and it reverses to −0.0166 under post-treatment
> exposure matching — so the study identifies no effect of residual status per
> se and instead demonstrates that pre- versus post-treatment exposure matching
> can flip the sign of a residual–leverage estimate.

## 7. Strongest claim the authors may make

**May claim:** (1) the registered hypothesis was not confirmed
(Δ = +0.031118708021286745, CI [+0.009616174, +0.053229402], registered
`p_left = 0.9972`); (2) the result is exactly reproducible; (3) pre- vs
post-treatment exposure matching flips the sign; (4) this replicates, in a
different estimand, the sibling study's null.

**May NOT claim:** that residuals have *higher* leverage (the positive Δ is a
design constant with expectation +0.0425, flips to −0.019 on removing a
mathematically identifiable 13% subgroup, has a 20%-trimmed value of +0.0006,
and 47.5% of permutation FSMs point the other way); that the holdout falsified a
prediction or that the reversal was a surprise; that "both controls behaved
perfectly" implies anything; that θ "controls exposure."

**Neither gate is a control with power to fail.**

> **Author verification.** Two distinct affine maps on Z₆₄ agree in **at most 32
> of 64** positions (verified over all 4096×4096 pairs), so a k = 1 perturbation
> leaves the true skeleton the unique minimiser — any rival has k ≥ 32. Skeleton
> recovery of 240/240 and a singleton residual set are **mathematically forced**,
> not measured. For specificity, affine beats the full table iff k ≤ 55, i.e.
> agreement ≥ 9 of 64; P(one fixed candidate) = 7.04e-07, union bound over 4096
> candidates = 0.0029, and empirically **49/20,000 = 0.0024** of uniform random
> maps select affine — against a registered threshold of 0.05. Both figures
> confirmed. The reviewer is right: neither gate could plausibly have failed.

## 8. Strongest falsification

**Re-run the identical frozen design at a new `protocol_revision`, changing
exactly one line: draw `y*` uniformly from `S ∖ ({h(u*)} ∪ Anc_h(u*))` —
forbid replacement destinations that reach the planted source under the
skeleton.** Everything else held fixed.

**Prediction, from the exhaustive re-plant already run on the realised holdout
skeletons: Δ ≈ −0.043 (permutation ≈ −0.074, contracting ≈ −0.012), interval
wholly below zero, `p_left < 0.05` — FSM-H1 would be formally "confirmed."** The
same design, same code, same gates, same compression residual, opposite
registered verdict, obtained by changing a sampling distribution that has
nothing to do with compression. That kills any claim that Δ measures a property
of residual transitions.

Two cheap corroborating runs:

- **Decouple residual identity from the edit site.** Plant *two* deviations per
  map and compare δ at a residual against δ at a *non-residual* state matched on
  **post-treatment** `(visit_count, on_cycle)` in the same doubly-edited graph.
  Prediction: the residual-vs-non-residual contrast collapses to ≈ 0 while the
  edited-vs-unedited contrast persists.
- **Report the pre-treatment placebo explicitly.** Prediction: **exactly
  0.000000** (measured max |δ_pre| = 2.8e-17 over all 240 holdout FSMs).

---

## Author disposition

All three "missing or misstated" facts were added:

1. **Pre-freeze sentinel cohort Δ** — now stated with numbers in RUN_LOG §7.2
   and `RESULTS.md` §5.1, together with the fact that no registered scientific
   choice was the author's to make.
2. **Zero-power status of both gates** — now `RESULTS.md` §6 and §7, with the
   32/64 affine-agreement bound and the 0.0029/0.0024 specificity figures.
3. **The headline's sign is a computable design constant** — now `RESULTS.md`
   §11 and §12, with the +0.042541 expectation and the full fragility table.

The three mandated sentences appear in `RESULTS.md` §1, §5.1, §11 and §12.
The claim "by a small but statistically clear margin" was removed from §1.
Nothing was softened, and no number changed.
