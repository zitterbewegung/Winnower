# RESULTS — synthetic FSM residual/leverage

**Registered hypothesis FSM-H1 was falsified. The effect ran in the opposite
direction — but that positive effect is a computable constant of the frozen
design, not a finding about compression residuals.**

---

## 1. In plain language

We asked whether a transition that a compressor flags as "the one weird edge" —
a sparse deviation from an otherwise simple deterministic rule — is *less*
consequential than an ordinary transition, once you hold constant how often the
system's dynamics actually encounter that transition.

The registered answer is **no**: the flagged transition had *higher*, not lower,
conditional attractor-switch leverage than pre-treatment-exposure-matched
regular transitions. FSM-H1 fails.

But the more important answer, which four independent adversarial reviews forced
into the open, is that **the study cannot answer its own question, and the
positive number is an artefact of the design rather than a fact about
compression.** Three things establish this, and all three are proved rather than
argued:

1. On *every one* of the 4,096 affine skeletons, the matching stratum
   `(visit_count_0, on_cycle_0)` determines the outcome exactly. The
   pre-treatment placebo contrast is therefore **identically zero** — measured
   max `|delta|` = 2.776e-17 across all 240 held-out structured maps. There is
   nothing to compare before the edit; 100% of the effect is manufactured by the
   edit itself.
2. The sign is set by where the randomly drawn replacement destination happens
   to point. If it can reach the planted source — so the edit closes a new cycle
   — Δ = +0.4236; otherwise Δ = −0.0430. Averaging over the registered uniform
   destination law gives an **exact expected Δ of +0.042541**, computable in
   closed form with no data, no bootstrap and no p-value. The observed +0.031119
   is an ordinary draw from that. *The headline is a design constant.*
3. The effect reverses to −0.016646 the moment controls are matched on
   *post*-treatment exposure, and collapses to **exactly zero** (max per-FSM
   |effect| = 2.776e-17) when they are matched on post-treatment exposure *and*
   cycle membership.

Neither of the study's two "controls" had any power to fail. Perfect model
recovery is a **theorem** here, not a measurement: two distinct affine maps on
`Z_64` agree in at most 32 of 64 places, so a one-edge perturbation leaves the
true skeleton the unique minimiser. And a uniform random map beats the
full-table code only about 0.24–0.29% of the time, against a threshold that
allows 5%. "Both controls passed" is not evidence about this experiment.

What survives is a methodological result, not a scientific one: **whether you
match exposure before or after an intervention can flip the sign of a
residual–leverage estimate.** That warning transfers directly to the
cellular-automata and Boolean-network settings this study was abstracted from.

Read together with the sibling finite-state study in `PRIOR_ART.md` item 8,
which already reported exactly zero incremental effect for a
transition-exception codelength, this study **replicates that null in a
different estimand** and adds no evidence that MDL residual status per se
predicts attractor-switch leverage.

## 2. Scientific question

> Does a state transition identified as a sparse deviation from a compressed
> deterministic transition rule have lower conditional attractor-switch leverage
> than exposure-matched regular transitions?

The point was to remove spatial geometry, locality, neighbourhoods and parallel
state update from the residual/leverage question that arises in cellular
automata and Boolean-network work, and see whether anything survives.

## 3. Frozen design

Full detail in `PROTOCOL.md`; summary:

- Deterministic maps `f: S -> S`, `S = {0..63}`.
- Compressed candidate family: all 4096 affine maps `h(x) = (a x + b) mod 64`.
- Two structured families: **permutation** (`gcd(a,64)=1`) and **contracting**
  (`gcd(a,64)=2`); plus **random** maps (64 iid uniform destinations) as a
  negative control.
- Exactly one outgoing transition is replaced at a planted source `u*` drawn
  uniformly from states whose exact pre-treatment stratum
  `(visit_count_0, on_cycle_0)` has at least two members; the replacement
  destination is uniform on `S \ {h(u*)}`.
- Frozen MDL fit, exception codelength
  `L = log2(64^2) + log2(65) + log2(C(64,k)) + k log2(63)` against
  `L_full = 64 log2(64) = 384`; lexicographic `(a,b)` tie-break; full table wins
  exact ties. The fit sees only the static transition table.
- Exact intervention outcome, computed by full enumeration (no sampling):
  `C_f(u) = (1/63) Σ_{y≠f(u)} (1/64) Σ_x 1[cycle_{f^{u→y}}(x) ≠ cycle_f(x)]`,
  `θ_f(u) = C_f(u)/w_f(u)`, `w_f(u) = visitCount_f(u)/64`.
- Primary estimand: `δ_m = θ(u*) − mean θ over non-planted states in u*`'s exact
  **pre-treatment** stratum; `Δ = ½ mean(δ|permutation) + ½ mean(δ|contracting)`.
- 120 FSMs per family per split. Confirmatory split is holdout.
- **FSM-H1: `Δ < 0`**, confirmed only if the 95% cluster-bootstrap interval lies
  wholly below zero **and** the one-sided cluster sign-flip `p_left < 0.05`.

## 4. Commits

| Role | SHA |
|---|---|
| Base (`zitterbewegung/Winnower`, `main`) | `598a774abaef70236f62a5df8f312632e6cb7caa` |
| Freeze v1 | `100d4a1413c1fa901677aafd0b3b3906f240a835` |
| Freeze v2 (pre-holdout guard fix) | `b6db582b073094c1bf7754c0d78e6b26443e0431` |
| Freeze v3 (pre-holdout exact CSV float reads) | `37c0b8d132b26f13f9e85b28d305e3327afdbf31` |
| **Final pre-holdout freeze (used for the registered run)** | **`b61e402f6e501aa132d7310c400adfa7fa0024ab`** |
| Result commit | recorded in `RUN_LOG.md` section 14 and in the final report |

All three re-freezes happened **before any holdout outcome existed** and each is
documented in `RUN_LOG.md` sections 9, 10 and 11. Two were run-time guard
defects; one was an exact-float CSV read defect. None touched a generator,
codelength, estimand, matching rule, weighting, statistic or gate threshold.
Every intermediate development artifact was deleted rather than reused.

## 5. Development / holdout separation

Development seeds `110000–110359`; holdout seeds `220000–220359`; disjoint by
construction and verified in test. Development was run, validated and used only
for implementation diagnostics. The holdout split was generated **once**, with
the freeze SHA supplied on the command line and recorded in every artifact row.
The pre-frozen informative-cluster continuation rule was **not triggered** (both
structured families reached 120/120 informative, threshold 100), so no
continuation seed was used.

The two splits agree closely, which is worth stating because it was not
guaranteed:

| Split | Δ | 95% CI | permutation | contracting |
|---|---:|---|---:|---:|
| development | +0.036930 | [+0.015843, +0.059273] | +0.057926 | +0.015934 |
| holdout | +0.031119 | [+0.009616, +0.053229] | +0.052598 | +0.009639 |

### 5.1 Pre-freeze exposure — disclosed after adversarial review

Review D found, and the author confirms, that `RUN_LOG.md` §7.2 originally
recorded that a full-size pipeline validation had been run on a sentinel cohort
(`protocol_revision = 900`, all seeds shifted by 900,000,000) **before the first
freeze commit** — without stating its numbers. That was an inadequate
disclosure. The numbers seen were:

| pre-freeze sentinel (revision 900) | Δ | permutation | contracting |
|---|---:|---:|---:|
| development | +0.036159 | +0.074637 | −0.002319 |
| holdout | **+0.054684** | +0.077474 | +0.031895 |

together with `FSM_H1_confirmed: false`, both gates passing, and the same
"permutation carries it / contracting is null" split. So the direction and rough
magnitude of the registered result were known before `PROTOCOL.md` was
committed.

**No registered scientific choice could have been influenced, because none was
the author's to make.** Every scientific element — state set, both structured
families, the affine candidate family, the exact codelength and tie rule, the
planting rule, all six registered seed blocks, the continuation seeds and rule,
the estimand, the matching, the equal-family weighting, **the direction of
FSM-H1**, both gate thresholds, the bootstrap and sign-flip specifications, the
analysis RNG seeds and the interpretation gate — was specified verbatim in the
externally supplied task specification, which predates all work in this
repository. `PROTOCOL.md` is a transcription of it. The generator's RNG draw
order was fixed in code before the sentinel run.

**Consequence for wording.** The reversal is **not** presented anywhere in this
document as a falsified prediction or as a surprise. It is a confirmation, on
registered seeds, of a direction already observed on an exchangeable
non-registered cohort. See `PROTOCOL_ERRATA.md`, Erratum 8.

## 6. Recovery gate (positive control) — **PASS, but with no power to fail**

Holdout structured FSMs, n = 240 (120 permutation, 120 contracting):

| Quantity | Value | Threshold |
|---|---:|---:|
| affine-skeleton recovery rate | **1.000000** (240/240) | ≥ 0.99 |
| pooled planted-source precision | **1.000000** (TP 240, FP 0) | ≥ 0.99 |
| pooled planted-source recall | **1.000000** (TP 240, FN 0) | ≥ 0.99 |
| macro precision | 1.000000 | descriptive |
| macro recall | 1.000000 | descriptive |

Per family: permutation 1.0 / 1.0 / 1.0 (n = 120); contracting 1.0 / 1.0 / 1.0
(n = 120). Residual-set-size distribution: **`{1: 240}`** — every fitted residual
set was exactly the singleton planted source.

**This result is a theorem, not a measurement.** Two *distinct* affine maps on
`Z_64` agree in **at most 32 of 64 positions** (verified exhaustively over all
4096 × 4096 candidate pairs; the extremal pair is `(a,b) = (0,0)` vs `(32,0)`).
A structured map is at Hamming distance 1 from its own skeleton and at distance
≥ 32 from every other affine candidate, and the codelength is increasing in `k`
over that range. Exact recovery of the skeleton and of the singleton residual
set is therefore **forced**; it could not have come out otherwise for any seed.
The gate is an implementation self-check, not evidence about the phenomenon.

One consequence is analytic rather than empirical: because `D_hat = {u*}`
always, the secondary fitted-residual analysis is numerically *identical* to the
primary planted-label analysis. It is reported below as identical, not as
independent corroboration.

## 7. Specificity gate (negative control) — **PASS, but with ~0.3% failure probability**

| Quantity | Value | Threshold |
|---|---:|---:|
| holdout random maps selecting the full table | **119 / 120 = 0.991667** | ≥ 0.95 |

Development random maps: 120/120 = 1.000000.

**This gate also had almost no power to fail.** The affine model beats the full
table iff `k ≤ 55`, i.e. iff the observed map agrees with *some* affine candidate
in at least 9 of 64 positions. For a uniform random map and one fixed candidate
that probability is `7.038e-07`; the union bound over 4096 candidates is
**0.0029**, and direct simulation over 20,000 uniform random maps gives
**49/20,000 = 0.0024**. The registered threshold tolerates a 0.05 failure rate —
roughly 17× the expected rate. The observed 1/120 = 0.0083 is an ordinary draw.

The single holdout exception is worth naming rather than rounding away.
`hol-random-000220292` (seed 220292) selected the affine model `(a=53, b=7)` at
**381.4536 bits** against the full table's **384 bits** — a 2.55-bit margin —
with a fitted residual set of **55 of 64 entries**. That is a marginal
codelength tie, not a structure detection: nothing about a 55-entry exception
list is sparse. It is counted as a specificity failure anyway, as registered, and
it contributes zero rows to any estimand.

## 8. Informative-cluster gate — **PASS**

| Family | Informative FSMs (holdout) | Informative (development) | Threshold |
|---|---:|---:|---:|
| permutation | **120** | 120 | ≥ 100 |
| contracting | **120** | 120 | ≥ 100 |

The pre-frozen continuation rule was therefore **not triggered**. No
continuation seed was consumed; the registered revision-0 continuation bases,
unused, are `221000` (permutation) and `222000` (contracting), extended in
blocks of 40 up to a cap of 400 per family.

Matched-control counts per FSM (holdout): permutation min 1, median 63, max 63;
contracting min 1, median 15, max 31. No FSM was excluded; no skeleton required
resampling (0 resamples in either structured family, either split). Four holdout
structured FSMs have exactly one matched control and still carry full cluster
weight (their mean `delta_theta` is −0.30159); this matches the registered
estimand but the per-FSM effects are strongly heteroskedastic, `m` ranging 1–63.

## 9. Primary result — **FSM-H1 NOT CONFIRMED**

Holdout, 120 permutation + 120 contracting informative FSMs:

| Quantity | Value |
|---|---:|
| **Δ (equal-family-weighted)** | **+0.031118708021286745** |
| 95% cluster-bootstrap CI (10,000 resamples, seed 330000) | **[+0.009616174329122745, +0.053229401709838454]** |
| one-sided sign-flip `p_left` (registered, 10,000 draws, seed 330001) | **0.9972002799720028** |
| `p_right` | 0.0028997100289971 |
| two-sided p | 0.0057994200579942 |
| interval wholly below zero? | **No** |
| `p_left < 0.05`? | **No** |
| **FSM-H1 confirmed?** | **No** |

The registered verdict recorded in `summary.json` is:

> FSM-H1 not confirmed: no registered evidence for lower conditional
> attractor-switch leverage at compression residuals.

### 9.1 What is and is not licensed by the freeze

**Licensed.** `PROTOCOL.md` §9.2 pre-defines the two-sided p-value and §9.3
pre-commits to reporting the point estimate, interval, one-sided **and**
two-sided p regardless of outcome. Reporting `p = 0.0058` is therefore a
pre-registered quantity, not a post-hoc switch. Reporting that the interval
excludes zero is likewise licensed.

**Not licensed.** There is **no registered alternative, no registered alpha and
no registered power analysis in the positive direction.** The only frozen
decision rule is `Δ < 0` with the interval wholly below zero *and*
`p_left < 0.05`, and it returned `p_left = 0.9972`. Any sentence of the form
"the effect is significantly positive" would be an unregistered confirmatory
claim. The positive effect is **exploratory**, and it is uncorrected among the
**143** p-value fields this study reports; the only registered multiplicity
adjustment is Holm across the two family p-values within a block (§9.4).

In this case the exploratory status is moot, because §11.3 and §11.4 show the
positive effect is a computable constant of the design rather than an estimate
of anything.

### 9.2 The interpretation gate, applied honestly

Both identification gates passed, so the frozen rule labels the result
diagnostic of the registered compression-residual comparison. That rule is
satisfied — but §6 and §7 show neither gate had power to fail, and §11.3 shows
the estimand has no pre-treatment contrast to detect. **A passed gate with no
power does not license an interpretation.** The honest reading is that this
study identifies no effect of residual status per se.

### 9.3 Calibration of the registered test

Independently raised by Review A and replicated by the author: the sign-flip
null assumes each per-FSM effect is symmetric about zero, and the observed
effects are strongly right-skewed. Under an exactly mean-zero null built by
within-family centring of the observed effects (author, 1,500 replicates;
reviewer, 2,000–4,000):

| | author | reviewer | nominal |
|---|---:|---:|---:|
| `p_left < 0.05` | 0.0600 | 0.0720 | 0.050 |
| `p_right < 0.05` | 0.0407 | 0.0365 | 0.050 |
| CI covers 0 | 0.9480 | 0.9455 | 0.950 |
| **registered FSM-H1 rule** | **0.0313** | **0.0345** | **≤ 0.025** |

The registered rule is roughly 1.25–1.4× anti-conservative **in the H1
direction**, and the right tail is correspondingly conservative. Review D
reached the opposite conclusion using a different null (a sham source on the 120
holdout random maps, giving nominal-or-conservative rates); both are recorded in
`PROTOCOL_ERRATA.md`, Erratum 2, and they disagree. Either way this cannot have
manufactured the reported outcome, since H1 was not confirmed and the observed
sign is the opposite one. **It is not fixed on this revision:** PROTOCOL §11
requires a full protocol revision and regeneration for any post-holdout change
to the statistic.

## 10. Family-specific results and heterogeneity

| Family | n | mean δ | 95% CI | raw two-sided p | Holm two-sided p | raw `p_left` | Holm `p_left` |
|---|---:|---:|---|---:|---:|---:|---:|
| permutation | 120 | +0.052598399145492074 | [+0.017992478, +0.088313326] | 0.0037996200379962 | **0.0075992400759924** | 0.9982001799820018 | 1.0 |
| contracting | 120 | +0.009639016897081416 | [−0.013738074, +0.037342785] | 0.4639536046395361 | 0.4639536046395361 | 0.7681231876812319 | 1.0 |

The two family *means* agree in sign, so the automated `family_signs_differ`
flag returned `false`. **That flag is too weak to capture what is actually
happening**, and the heterogeneity is reported here regardless, as §9.5 of the
protocol intends:

| family | n | mean | median | sd | skew | kurtosis | >0 / =0 / <0 |
|---|---:|---:|---:|---:|---:|---:|---|
| permutation | 120 | +0.05260 | **+0.00410** | 0.196 | +1.03 | −0.09 | 63/0/57 |
| contracting | 120 | +0.00964 | **−0.00051** | 0.144 | **+3.34** | **+21.64** | 15/23/82 |

- Only the permutation family is individually distinguishable from zero; the
  contracting interval covers zero (Holm two-sided p = 0.464).
- **The median per-FSM effect is negative in the contracting family**, where 82
  of 120 FSMs are negative and 23 are exactly zero. Rank-based tests on the same
  data reject *toward the registered direction*: Wilcoxon p = 1.7e-11, sign test
  p = 2.4e-12. The positive contracting mean is produced by a right tail
  reaching +0.9048.
- In the permutation family the mean-based tests reject but the rank-based ones
  do not (Wilcoxon p = 0.306, sign test p = 0.648), and 57 of 120 FSMs point the
  other way.

The registered estimand is a mean, so the mean governs the verdict — but the
mean and the median disagree in sign, and that must be stated.

**Two structural confounds make the two families incomparable rather than two
samples of one phenomenon:**

1. *Family is perfectly collinear with pre-treatment cycle membership.* All 120
   permutation planted sources are on-cycle before the plant; all 120
   contracting planted sources are off-cycle. `diagnostics.by_pre_on_cycle` is
   therefore numerically identical to `diagnostics.by_family` and carries zero
   independent information.
2. *The families sample disjoint intervention regimes.* Permutation draws 51
   `pre_ancestor_of_source` / 4 `self_loop` / 65 `different_terminal_cycle` / 0
   `same_terminal_cycle`; contracting draws 4 / 1 / 0 / 115.

Stronger still: across **all 120 holdout permutation skeletons the only value of
`s_h(u)` observed is 63** — `theta_h(u) ≡ 1` for all 64 states of every
permutation skeleton. The pre-treatment matched contrast in that family is
identically zero by construction, so 100% of the signal in the family carrying
the significant p-value is created by the edit itself.

## 11. Secondary analyses, and the mechanism

All secondary; none can rescue or replace the primary test.

| Analysis | Δ (holdout) | 95% CI | `p_left` | two-sided p | n (perm, contr) |
|---|---:|---|---:|---:|---|
| `delta_C` | +0.029360 | [+0.004775, +0.054247] | 0.9898 | 0.0206 | (120, 120) |
| `delta_w` | +0.032583 | [+0.015699, +0.049898] | 0.9999 | 0.0004 | (120, 120) |
| fitted-residual, pre-treatment matched | +0.031119 | [+0.009616, +0.053229] | 0.9965 | 0.0072 | (120, 120) |
| **post-treatment exposure sensitivity** | **−0.016646** | **[−0.029047, −0.003213]** | **0.0084** | 0.0168 | (98, 118) |

The three secondary intervals in rows 1–3 are **not** independent corroboration
of the primary: `cluster_bootstrap` is invoked with the same registered seed
330000 for every block, so blocks with the same family sizes share identical
resample index sets (`PROTOCOL_ERRATA.md`, Erratum 3). The fitted-residual row
is additionally the *same number* as the primary, because recovery is forced
(§6); its p-values differ only because they consume later draws from the same
sign-flip stream.

### 11.1 The estimand is exactly affine in post-treatment exposure

`PROTOCOL.md` §6.1 asserted, before the freeze, that "`theta` is identically
free of `visitCount`". **That assertion is false and is retracted**
(`PROTOCOL_ERRATA.md`, Erratum 1). The exact identity is

```
s_f(u)     = visitCount_f(u) + 64 − B_f(u) − onCycle_f(u)
theta_f(u) = ( visitCount_f(u) + 64 − B_f(u) − onCycle_f(u) ) / 63
```

with `B_f(u)` the size of `u`'s terminal-cycle basin — **0 violations over all
46,080 committed entry rows**. `theta` is exactly affine in post-treatment visit
count with slope 1/63; `corr(theta, post_w) = 0.5787` on holdout structured rows.

Decomposing the headline through that identity (equal-family-weighted,
control-averaged, exact):

| term | Δ contribution | permutation | contracting |
|---|---:|---:|---:|
| `visitCount/63` | **+0.033100** | +0.079444 | −0.013245 |
| `−B/63` | −0.003169 | −0.029882 | +0.023545 |
| `−onCycle/63` | +0.001188 | +0.003036 | −0.000661 |
| **sum** | **+0.031119** | | |

**106% of the headline is the post-treatment visit-count gap.** The primary
outcome is, up to a factor of 64/63 and two small corrections, a restatement of
the registered *secondary* outcome `delta_w = +0.032583`.

Additionally, `theta = 1` for **every** on-cycle state (0 exceptions in 5,589
holdout structured on-cycle rows; off-cycle mean 0.1716, with 126 off-cycle rows
also at 1). `theta` is saturated on the terminal cycle, so `delta_theta` is
largely a difference of two *on-cycle rates*, not a graded leverage scale.

### 11.2 Why pre-treatment matching cannot work here

`visitCount_f(u*)` is **provably invariant** to editing `u*`'s own outgoing edge:
a first arrival at `u*` never traverses `f(u*)`. Measured: **0 of 480** planted
sources have `pre_visit_count != post_visit_count`. The pre-stratum controls have
no such protection — their mean post−pre visit-count drift is **−5.055**
(permutation) and **+0.778** (contracting).

Only 64.4% of the 8,526 primary control pairs share the entry's post-treatment
visit count and 63.0% share its post-treatment on-cycle flag, despite 100%
sharing both pre-treatment values.

Adding post-treatment covariates to the match:

| matching used (holdout, within pre-stratum) | Δ | perm | contr | n |
|---|---:|---:|---:|---|
| registered: `pre_vc` + `pre_on_cycle` | **+0.031119** | +0.052598 | +0.009639 | (120, 120) |
| + control matches entry's `post_visit_count` | **−0.014198** | −0.051668 | +0.023271 | (98, 118) |
| + matches `post_visit_count` **and** `post_on_cycle` | **−0.000000** | +0.000000 | −0.000000 | (55, 113) |

The last row is floating-point zero for **every single FSM** (max |per-FSM
effect| = 2.776e-17), which the §11.1 identity forces once `(vc, onCycle)` are
held fixed.

### 11.3 The pre-treatment placebo is identically zero, by construction

On **all 4,096 affine skeletons**, the matching stratum
`(visit_count, on_cycle)` determines `s` exactly — 0 violations. Consequently
the same estimand computed on the *un-edited* skeleton is identically zero:

```
pre-treatment placebo Delta = -2.949e-18     max |delta| = 2.776e-17   (n = 240)
```

There is no pre-treatment contrast for the design to detect. **100% of the
observed Δ is manufactured by the single planted edit**, and "being a residual"
and "being the edited edge" are the same event, with no residual variation to
separate them.

### 11.4 The sign is a free parameter of the destination law

Enumerating **all 63 replacement destinations at every realised holdout planted
source**, holding skeleton and source fixed:

| destination class | perm | contr | **Δ** | pairs |
|---|---:|---:|---:|---:|
| closes a new cycle through `u*` (destination reaches `u*` under `h`, or is `u*`) | +0.223835 | +0.623426 | **+0.423631** | 3,819 |
| every other destination | −0.073639 | −0.012312 | **−0.042976** | 11,301 |
| **exact expectation under the registered uniform destination law** | **+0.058375** | **+0.026707** | **+0.042541** | 15,120 |

Conditional on the realised skeletons and sources, the frozen design has an
**exact expected Δ of +0.042541**, obtainable in closed form with no holdout, no
bootstrap and no p-value. The observed +0.031119 is an unremarkable draw from
it. Replace the destination law with "uniform on non-ancestors of `u*`" and Δ
becomes ≈ −0.043 — and FSM-H1 would formally have been *confirmed*, with the
same code, the same gates and the same compression residual.

### 11.5 Fragility of the headline

| variant (holdout) | Δ |
|---|---:|
| as registered (equal-family mean) | **+0.031119** |
| pooled, no family weight | +0.031119 |
| equal-family **median** | +0.001792 |
| equal-family 10% trimmed mean | +0.012396 |
| equal-family **20% trimmed mean** | **+0.000568** |
| **drop the 32 single-64-cycle permutation skeletons** | **−0.019426** |

The 32 permutation FSMs whose skeleton is a single 64-cycle
(`pre_visit_count = 64`) average δ = +0.330593 and contribute **+0.044079 of a
+0.031119 total — 142% of the headline**. The other 88 permutation FSMs average
**−0.048491**. In those 32 maps every state is an ancestor of `u*`, so the edit
*always* closes a new cycle: the sign is forced by the algebra of affine
permutations on `Z_64`, not estimated.

### 11.6 The post-treatment reversal is not a selection artefact

The post-treatment sensitivity drops 24 structured holdout FSMs (22 permutation,
2 contracting) whose fitted residual has a post-treatment visit count shared by
no non-residual state. Those FSMs are **not** missing at random in the outcome:
their primary `delta_theta` means are −0.11486 (permutation) and −0.49206
(contracting), against +0.09019 and +0.01814 for the 216 retained. The retained
subsample is therefore *enriched for positive primary effect* — its primary Δ is
**+0.054167**, nearly double the headline — and post-treatment matching on that
same subsample still yields **−0.016646**. The sign reversal is caused by the
matching change, not by the exclusion. The dropping rule is not recorded in
`summary.json`, which reports only the surviving `n`; it is disclosed here.

### 11.7 Structural diagnostics (descriptive; not searched for a headline)

Per-FSM δ by planted destination type (holdout):

| Destination type | n | mean δ |
|---|---:|---:|
| `pre_ancestor_of_source` (edit closes a new cycle) | 55 | **+0.240305** |
| `self_loop` | 5 | **+0.210945** |
| `same_terminal_cycle` | 115 | −0.013820 |
| `different_terminal_cycle` | 65 | **−0.080211** |

`self_loop` and `pre_ancestor_of_source` are the **same mechanism**, split only
by the classifier's exclusive ordering (a self-loop in a permutation is always
also an ancestor); together they are the 60/240 FSMs of §11.4. The `self_loop`
mean is 4 permutation cases at +0.0375 plus one contracting outlier at +0.9048.

Per-FSM δ by pre-treatment visit-count stratum shows the same heterogeneity —
`visit_count_0 = 64` (n = 32) gives +0.330593, `visit_count_0 = 31` (n = 3) gives
−0.322751. Full breakdowns are in `results/summary.json` under
`holdout.diagnostics`.

## 12. Nulls, failures and counterexamples — nothing withheld

- **The registered hypothesis failed.** `p_left = 0.9972`.
- **The positive effect is a design constant**, expected value +0.042541 under
  the frozen destination law (§11.4), not an estimate of a residual property.
- **The pre-treatment placebo is identically zero** (§11.3) — the design has no
  pre-treatment contrast to work with, on any of the 4,096 affine skeletons.
- **Neither gate had power to fail** (§6, §7). "Both controls passed" is not
  evidence.
- **`PROTOCOL.md` §6.1 contains a false lemma**, now retracted
  (`PROTOCOL_ERRATA.md`, Erratum 1). It was the stated justification for the
  whole matching design.
- The **contracting family is a null on its own**, with a *negative* median and
  rank tests rejecting toward the registered direction (§10).
- The **specificity gate has one failure** (`hol-random-000220292`), described in
  full in §7.
- The **post-treatment sensitivity contradicts the primary in sign** (§11.2,
  §11.6), and the reversal survives on the subsample enriched *for* the primary
  effect.
- The **headline reverses** on dropping a mathematically identifiable 13%
  subgroup, and its 20% trimmed value is +0.000568 (§11.5).
- The **fitted-residual analysis adds no independent information** (§6, §11);
  nor do the `delta_C` / `delta_w` intervals, which share bootstrap resample
  indices with the primary (Erratum 3).
- The **registered confirmation rule is anti-conservative in the H1 direction**
  by ~1.25–1.4× (§9.3), and two reviewers' calibration analyses disagree.
- **Three implementation defects** were found and fixed before holdout, each
  with its own freeze commit (`RUN_LOG.md` §9–11). One of them — the CSV float
  read — was real but had a magnitude of **1.4e-16** on the primary estimate;
  RUN_LOG's original description of it overstated its scientific severity, and
  Review D was right to say so.
- **Two disclosed process exposures**: an early smoke test generated rows for 12
  registered holdout seeds into a discarded temp directory (`RUN_LOG.md` §7.1;
  excluding those 8 structured seeds gives Δ = +0.032277 vs +0.031119), and the
  full pipeline was run at full size on a sentinel cohort before the freeze, with
  its direction visible (§5.1).
- **Power**: the holdout CI half-width on Δ is 0.0218 in θ units. Effects smaller
  than roughly 0.02 would not have been detected. The contracting null is "no
  detected effect", not "no effect".

## 13. Prior-art-aware novelty and impact

`PRIOR_ART.md` records the audit performed before the hypothesis was frozen,
with two threats to novelty stated up front. Both were borne out.

1. **Zenil et al.'s algorithmic information dynamics** already asserts that a
   compression-relative ranking of a discrete dynamical system's components
   carries interventional meaning. The idea is not new here.
2. **A sibling internal study** (`aconsapart/ruler`,
   `research/three-outcome/finite_state_systems`, completed at `512ee425`)
   already reported *exactly zero* incremental predictive value for a
   transition-exception codelength on finite deterministic maps once exposure
   and a graph-cut condition are known — `Δ_R = 0`, `Δ_R:L = 0`, `Δ_joint = 0`,
   each with interval `[0, 0]`, on 864 identified systems, with a
   planted-interaction positive control passing.

**This study agrees with item 8.** The §11.3 result — the matching stratum
determines θ exactly on every affine skeleton, so the pre-treatment contrast is
identically zero — is that same statement in this study's coordinates. This is a
**replication of a known null in a different estimand**, and must be described
as such.

The pre-registered novelty sentence from `PRIOR_ART.md` still stands as a
statement about the *literature search*:

> The searched literature contains close work on functional-graph statistics,
> Boolean-network structural perturbations, basin and attractor effects, causal
> information, and algorithmic-information perturbation. The search did not
> identify the exact registered comparison between a static compression-residual
> flag and exposure-controlled generic transition-edit leverage in finite
> deterministic maps.

But the strongest claim the *evidence* supports is narrower:

> In a pre-registered, exactly enumerated study of 240 held-out 64-state
> deterministic maps, an MDL residual transition did not have lower conditional
> attractor-switch leverage than pre-treatment-exposure-matched regular
> transitions (Δ = +0.0311, 95% CI [+0.0096, +0.0532], registered one-sided
> p_left = 0.9972). Because the matching stratum determines θ exactly on every
> affine skeleton, the entire estimate is generated by the planted edit itself;
> its sign is set by whether the replacement destination happens to reach the
> planted source (Δ = +0.4236 when it does, −0.0430 when it does not, with exact
> expectation +0.0425 under the registered uniform destination law); and it
> reverses to −0.0166 under post-treatment exposure matching. The study
> therefore identifies no effect of residual status per se, and instead
> demonstrates that pre- versus post-treatment exposure matching can flip the
> sign of a residual–leverage estimate.

**Impact.** Three things, all modest, and only the first two are science:

1. A registered, exactly enumerated demonstration that the pre- versus
   post-treatment exposure-matching choice **flips the sign** of a
   residual–leverage estimate (+0.031119 → −0.016646, the latter on a subsample
   whose primary effect is *larger*). This transfers directly to the CA and
   Boolean-network settings this study abstracts from.
2. A closed-form account of why: the `theta = 1 ⟺ on-cycle` saturation, the
   `s = visitCount + 64 − B − onCycle` identity, and the destination-class
   decomposition showing the estimate's sign is a free parameter of the
   intervention's destination law.
3. A fully deterministic, byte-reproducible artifact set for a finite-map
   intervention study. That is craft, not science.

## 14. Limitations and non-claims

**The decisive limitation.** The registered design cannot separate "is a
compression residual" from "is the edited edge". Recovery is mathematically
forced, so `D_hat = {u*}` always; and the pre-treatment placebo is identically
zero, so there is no pre-treatment variation to condition on. Every number this
study reports about residuals is a number about the single planted intervention.
Any future version must decouple the two — see the falsification test below.

**Other limitations.**

- 64 states, one candidate family (affine mod 64), exactly one planted deviation
  per map. Nothing generalises to larger state spaces, richer model families, or
  multiple simultaneous residuals.
- θ is saturated: exactly 1 for every on-cycle state. `delta_theta` is largely a
  difference of on-cycle *rates*, not a graded leverage magnitude.
- θ is a **post-treatment** quantity while the primary match is pre-treatment,
  and `visitCount(u*)` is invariant to the edit while the controls' is not
  (§11.2). The registered match cannot equalise post-treatment position.
- The eligibility rule (`u*` drawn only from strata of size ≥ 2) over-samples
  states on long cycles in permutations, which is exactly what raises the
  probability that the destination reaches `u*`. The design's own inclusion rule
  biases toward the positive arm.
- `family` is perfectly collinear with `pre_on_cycle` and near-collinear with
  intervention type (§10); the study cannot attribute heterogeneity to one
  rather than another.
- The registered inference rule is anti-conservative in the H1 direction (§9.3),
  and two reviewers' calibration analyses disagree about the magnitude.
- Neither gate had power to fail (§6, §7).
- The direction of the result was visible pre-freeze on a sentinel cohort
  (§5.1).
- Codex review was unavailable (account usage limit until 2026-08-29); see
  `review/CODEX_AUDIT.md`. Four independent adversarial reviews were run instead.
- Generation wall-clock is recorded in `RUN_LOG.md` §12 rather than in
  `manifest.json`, because adding it would have required changing scientific
  code after the holdout.

**Non-claims.** This work does not claim a universal theorem, a new
computational-complexity class, a general law of emergence, biological
applicability, causal discovery in arbitrary systems, that residuals are
particles, or that affine FSMs represent all finite-state systems. It does not
claim that residuals have higher leverage. It does not claim the holdout
falsified a prediction or that the reversal was a surprise.

### 14.1 The cleanest falsification, and its predicted outcome

Re-run the identical frozen design at a new `protocol_revision`, changing
exactly one line: draw `y*` uniformly from `S \ ({h(u*)} ∪ Anc_h(u*))` —
forbid replacement destinations that reach the planted source under the
skeleton. Hold everything else fixed.

**Predicted result, from the exhaustive re-plant already run on the realised
holdout skeletons (§11.4): Δ ≈ −0.043 (permutation ≈ −0.074, contracting ≈
−0.012), interval wholly below zero, `p_left < 0.05` — FSM-H1 formally
"confirmed."** Same design, same code, same gates, same compression residual,
opposite registered verdict, obtained by changing a sampling distribution that
has nothing to do with compression. That would kill any claim that Δ measures a
property of residual transitions.

Two cheaper corroborating runs:

- **Decouple residual identity from the edit site.** Plant *two* deviations per
  map (`k = 2 ≪ 55`, so recovery stays exact) and compare δ at a residual
  against δ at a *non-residual* state matched on **post-treatment**
  `(visit_count, on_cycle)` in the same doubly-edited graph. Predicted: the
  residual-vs-non-residual contrast collapses to ≈ 0 while the
  edited-vs-unedited contrast persists.
- **Report the pre-treatment placebo as a standing diagnostic.** Predicted (and
  measured here): exactly 0.000000.

## 15. Independent-estimator result

`scripts/research/verify_synthetic_fsm_estimator.py` reimplements the primary
estimator from the protocol text using only the standard library and pandas,
importing neither `relative_symmetry_repair.synthetic_fsm` nor
`scripts/research/analyze_synthetic_fsm.py`. Against the committed
`matched_effects.csv.gz` bytes:

| Quantity | Production | Independent | \|difference\| |
|---|---:|---:|---:|
| combined Δ | 0.031118708021286745 | 0.031118708021286762 | **1.734723475976807e-17** |
| permutation mean | 0.052598399145492074 | 0.05259839914549211 | **3.469446951953614e-17** |
| contracting mean | 0.009639016897081416 | 0.009639016897081415 | **1.734723475976807e-18** |

Tolerance `1e-12`. **PASS** (`results/independent_check.json`).

**Honest caveat on the strength of this check.** As Review D observed, the
shipped verifier re-reads `matched_effects.csv.gz` and checks a weighted
`groupby.sum` against a weighted `groupby.sum`; agreement to 1e-17 is close to
vacuous. Three genuinely independent recomputations were run during adversarial
review and are the checks that matter:

| Independent path | Result |
|---|---|
| Review A: `delta_theta` for all 240 holdout structured FSMs from stored transition tables, literal definitions, exact `Fraction`, strata re-derived from the skeleton | max deviation **1.53e-16**; exact Δ = 0.03111870802128677 |
| Review C: all 720 FSMs reconstructed from the CSVs and every column recomputed from scratch (orbits, cycles, `s` by literal enumeration of all 63 edited maps, full 4096-candidate MDL fit, `delta_theta`) | max discrepancy **exactly 0.0** |
| Review D: clean-room recomputation from `entry_metrics.csv.gz` (planted state minus stratum-matched controls, no shared code path) | Δ = 0.031118708021286745 **exactly** |

Review C additionally verified the `theta = s/63` factorization in exact rational
arithmetic for 4,608 states across 72 FSMs — **0 mismatches** — and Review A
found no counterexample over ~25,000 exhaustively enumerated (map, state) pairs
at n ≤ 5.

## 16. Reproduction-hash result

A clean rerun into a fresh temporary directory, from the same freeze SHA,
reproduced every scientific artifact **byte-for-byte**, including the compressed
gzip bytes and the SVG:

| Artifact | SHA-256 | Clean rerun |
|---|---|---|
| `fsm_summary.csv.gz` | `333b8260fc4423e6fe884063d28ab050c2a5b68662bea6b89d5c98ce6d593169` | identical |
| `fsm_summary.csv.gz` (decompressed) | `894326e175cc07f4d61da4595aee2a958cf6a3db30497ff0b947ea7f6f7aeaae` | identical |
| `entry_metrics.csv.gz` | `089d1e59a1bf5eb25933f56a72508875e87e5f02e24ab3c6b6a825f676038d21` | identical |
| `entry_metrics.csv.gz` (decompressed) | `2473ab61eae36f79b63740ef0b572c210c6c6afafd644b2f42261b550e0a8041` | identical |
| `matched_effects.csv.gz` | `9de2e824addd9cab3dc1effe8775af51c4da5efe39b07989218f48b0187134cb` | identical |
| `matched_effects.csv.gz` (decompressed) | `56460d6f8269ec35de82c88ec7ab242c68ee85b3012c40229455e448df6c6b69` | identical |
| `summary.json` | `f8d86d658e43da05d18e0bf8155ce3745a602b70f86ca4389f868ceaae6c43ec` | identical |
| `effect_by_split_family.svg` | `d0256d4c1be0b9cb917565e53344957e588194140aa05b5a23d258c5e30ed042` | identical |

`manifest.json` is deliberately excluded from the scientific hash set: it
carries wall-clock runtimes and platform strings, which are volatile by design.

## 17. Adversarial review

Four independent adversarial reviews were run; full reports are in `review/`.

| Review | Scope | Verdict |
|---|---|---|
| `REVIEW_A_MATH.md` | mathematical correctness | **PASS WITH CONCERNS** |
| `REVIEW_B_LEAKAGE.md` | leakage and statistical validity | **DEFECTS FOUND** |
| `REVIEW_C_IMPLEMENTATION.md` | implementation and reproducibility | **PASS WITH CONCERNS** |
| `REVIEW_D_NOVELTY.md` | novelty and publishability (Codex substitute) | **NEEDS REVISION** |

The external Codex review specified by the repository's `CLAUDE.md` **could not
be run**: the account's Codex usage limit is exhausted until 2026-08-29. The
exact error and the full submitted prompt are preserved in
`review/CODEX_AUDIT.md`, and the identical prompt was put to an independent
reviewer instead (Review D).

Every finding that changed the write-up was **independently re-verified by the
author** before being incorporated; the verifications are quoted inline in each
review file. Two reviewer claims were corrected: Review C quoted a bootstrap
interval that does not match `summary.json` (the committed value is
authoritative), and Reviews A and D reach opposite conclusions about the
sign-flip calibration using different nulls — both are recorded rather than
reconciled.

Consequences, all of which alter wording and none of which alter a number
(PROTOCOL §11):

- `PROTOCOL.md` §6.1's central lemma is **retracted** in `PROTOCOL_ERRATA.md`.
- Eight errata are recorded against the frozen protocol. `PROTOCOL.md` itself is
  **not edited**, so its SHA-256 in `manifest.json` still verifies.
- §1, §5.1, §6, §7, §9, §10, §11, §12, §13 and §14 of this document were rewritten
  to state the mechanical account, the zero-power gates, the pre-freeze
  exposure and the fragility of the headline.

## 18. Exact reproduction commands

```bash
# from a clean checkout of the research branch
git checkout research/synthetic-fsm
uv venv --python 3.12 .venv
uv pip install --python ./.venv/bin/python \
    numpy==2.5.2 pandas==3.0.5 scipy==1.18.0 matplotlib==3.11.1 \
    numba==0.67.0 pytest==9.1.1 lz4 typer

# correctness
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_synthetic_fsm.py -q
PYTHONPATH=src ./.venv/bin/python -m pytest tests/ -q

# registered generation (both splits, protocol_revision 0)
PYTHONPATH=src ./.venv/bin/python scripts/research/run_synthetic_fsm.py \
    --split development --out-dir research/synthetic_fsm/results/raw \
    --freeze-sha b61e402f6e501aa132d7310c400adfa7fa0024ab --jobs 8
PYTHONPATH=src ./.venv/bin/python scripts/research/run_synthetic_fsm.py \
    --split holdout --out-dir research/synthetic_fsm/results/raw \
    --freeze-sha b61e402f6e501aa132d7310c400adfa7fa0024ab --jobs 8

# analysis and final artifacts
PYTHONPATH=src ./.venv/bin/python scripts/research/analyze_synthetic_fsm.py \
    --raw-dir research/synthetic_fsm/results/raw \
    --out-dir research/synthetic_fsm/results \
    --freeze-sha b61e402f6e501aa132d7310c400adfa7fa0024ab

# independent clean-room estimator
./.venv/bin/python scripts/research/verify_synthetic_fsm_estimator.py \
    --results-dir research/synthetic_fsm/results \
    --out research/synthetic_fsm/results/independent_check.json

# hash check
cd research/synthetic_fsm/results && shasum -a 256 -c <(grep -v decompressed hashes.sha256)
```

Wall-clock on the recorded platform (macOS 26.6.1, arm64, Python 3.12.13,
8 worker processes): development generation 1.6 s, holdout generation 1.6 s,
analysis 4.3 s, `tests/test_synthetic_fsm.py` ~15 s, full suite ~60–95 s.
