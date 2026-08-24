# PROTOCOL ERRATA

`PROTOCOL.md` is **frozen**. Its SHA-256
(`060d385bb1ed0d6c671f1019d7cac636cc30311166a4d4b68c7a57248945d1b6`) is recorded
in `results/manifest.json` and was verified by the holdout runner before the
registered run. It is therefore **not edited**, even where it is wrong. Errors
in the registered document are recorded here instead, so that the frozen file
stays a faithful record of what was actually registered.

PROTOCOL §11 permits wording corrections and claim narrowing after holdout,
provided they alter no number and are documented. Everything below alters no
number.

---

## Erratum 1 — §6.1's "Consequence, stated before freeze" is mathematically false. **RETRACTED.**

Raised as a blocking finding by Review B (`review/REVIEW_B_LEAKAGE.md`,
Finding 1) and independently verified by the author.

### What the protocol says

> **Consequence, stated before freeze:** `theta` is identically free of
> `visitCount`. The primary estimand therefore compares a purely structural
> per-edge quantity, and pre-treatment exposure matching controls the covariate
> that drives the sibling study's `O = E*C` boundary (see `PRIOR_ART.md`,
> item 8). If FSM-H1 is null, the honest reading is that it replicates item 8's
> null in a different estimand; if FSM-H1 confirms, the effect must come from
> the residual edge's *graph position*, not from its exposure.

### Why it is false

The first sentence conflates two different statements:

1. `theta_f(u) = C_f(u) / w_f(u)` divides out the exposure *factor* `w` that
   appears multiplicatively in `C`. **True**, and this is what §6.1's
   factorization proves.
2. The resulting quantity `s_f(u)/63` contains no information about
   `visitCount`. **False.**

The exact identity, with `B_f(u)` the number of states whose terminal cycle is
`cycle_f(u)` (the basin of `u`'s terminal cycle), is

```
s_f(u)     = visitCount_f(u) + 64 − B_f(u) − onCycle_f(u)
theta_f(u) = ( visitCount_f(u) + 64 − B_f(u) − onCycle_f(u) ) / 63
```

**Proof.** From the closed form used in `switch_destination_counts`,

```
s = |anc(u) \ {f(u)}| + |{y ∉ anc(u) : y ≠ f(u), cycle(y) ≠ cycle(u)}|
```

Every ancestor of `u` reaches `cycle_f(u)`, so among the `64 − visitCount(u)`
non-ancestors exactly `B − visitCount(u)` share `u`'s terminal cycle, leaving
`64 − B` that do not. And `f(u)` always shares `u`'s terminal cycle, so it never
appears in that second set and needs no exclusion there; in the first term it is
excluded exactly when it is an ancestor, i.e. exactly when `u` is on its own
cycle. Hence `s = (visitCount − onCycle) + (64 − B)`. ∎

**Verification:** 0 violations over all 46,080 committed entry rows (both
splits, all 720 FSMs). `corr(theta, post_w) = 0.5787` on holdout structured
rows.

### What follows

- `theta` is **exactly affine in post-treatment visit count with slope 1/63**.
- The registered primary estimand therefore does **not** compare "a purely
  structural per-edge quantity". It compares a quantity that is one part
  post-treatment exposure, one part terminal-basin size, one part cycle
  membership.
- Matching on *pre*-treatment exposure consequently does **not** control the
  exposure component of the outcome, because the plant changes exposure
  asymmetrically: `visitCount_f(u*)` is provably invariant to editing `u*`'s own
  outgoing edge (0 of 480 planted sources changed), while the pre-stratum
  controls drift by −5.055 (permutation) and +0.778 (contracting) on average.
- The final sentence of the retracted paragraph — "if FSM-H1 confirms, the
  effect must come from the residual edge's *graph position*, not from its
  exposure" — is also void, for the same reason.

### What does **not** change

- The factorization `theta_f(u) = s_f(u)/63`,
  `C_f(u) = visitCount_f(u)·s_f(u)/(64·63)` is **correct** and was verified
  exhaustively in exact rational arithmetic (Review A §3, Review C §3, and
  `tests/test_synthetic_fsm.py`).
- Every committed number is unchanged. This erratum corrects an interpretive
  lemma, not a computation.
- The registered estimand, matching, seeds, gates and decision rule are
  unchanged. FSM-H1 remains falsified with `p_left = 0.9972`.

### Effect on the conclusions

Material, and reported in `RESULTS.md` §11–§12: the positive Δ is fully
accounted for by the post-treatment visit-count term (+0.033100 of the +0.031119
total, i.e. 106%), and vanishes to exactly zero when controls are additionally
matched on post-treatment visit count and cycle membership.

---

## Erratum 2 — §9.2/§9.3's confirmation rule is anti-conservative for FSM-H1

Raised by Review A (`review/REVIEW_A_MATH.md`, Finding 1) and independently
replicated by the author.

The cluster sign-flip test assumes each per-FSM effect is symmetric about zero
under the null. The observed per-FSM effects are strongly right-skewed
(permutation skew +1.03; contracting skew +3.34 with excess kurtosis +21.64 and
23/120 exact zeros). Under an exactly mean-zero null built by within-family
centring of the observed effects:

| | author, 1,500 reps | reviewer, 2,000–4,000 reps | nominal |
|---|---:|---:|---:|
| sign-flip `p_left < 0.05` | 0.0600 | 0.0720 | 0.050 |
| sign-flip `p_right < 0.05` | 0.0407 | 0.0365 | 0.050 |
| bootstrap CI covers 0 | 0.9480 | 0.9455 | 0.950 |
| CI entirely below 0 | 0.0313 | 0.0385 | 0.025 |
| CI entirely above 0 | 0.0207 | 0.0160 | 0.025 |
| **registered FSM-H1 rule** | **0.0313** | **0.0345** | **≤ 0.025** |

The inflation is in the registered direction (the left tail, which is FSM-H1);
the right tail is correspondingly conservative, so the reported
`p_right = 0.0029` is if anything understated by the same skew.

**Not fixed on this revision.** PROTOCOL §11 requires a documented protocol
revision, a new freeze commit, a deterministic seed offset and complete
regeneration for any post-holdout change to the statistic. Changing the test now
would be exactly the tuning the freeze exists to prevent. A skew-corrected
interval (BCa or studentized bootstrap) plus a t-statistic-based sign-flip
would be the correct remedy in a future revision.

The practical consequence for *this* run is nil: FSM-H1 was not confirmed, and
the observed effect has the opposite sign, so an anti-conservative left tail
cannot have manufactured the reported outcome.

---

## Erratum 3 — §9.1's family intervals are perfectly dependent across outcome blocks

Raised by Review A (Observation 7a).

`cluster_bootstrap` is invoked with the same registered seed 330000 for every
outcome block. Blocks whose family sample sizes coincide (primary `theta`,
`delta_C`, `delta_w`, `secondary_fitted_pre` — all 120/120) therefore share
*identical* resample index sets. Each marginal interval is valid; the intervals
are simply not independent across outcomes and **must not be read as independent
corroboration of one another**. This is inherent in the frozen "use seed 330000"
instruction and is not a coding error.

---

## Erratum 4 — §5's tie rule is unreachable at `n = 64`

Raised by Review A (Observation 4a).

The frozen rule "if `L_full <= L(h*, E*)`, select the full table" is correct as
implemented (`<=`), but at `n = 64` no `k` produces exactly 384 bits:
`L(55) = 381.4536` and `L(56) = 384.7935`. The tie branch can never be taken,
and `tests/test_synthetic_fsm.py::test_full_table_wins_ties` is consequently
tautological — it would pass unchanged if `<=` were mutated to `<`. The rule is
untested but also unfalsifiable at the registered state size.

Relatedly (Observation 4b), `L(k)` is not monotone at the extreme:
`L(64) = 400.5683 < L(63) = 400.5910`. Both exceed `L_full = 384`, so the full
table always wins there and no observed map approaches it (max implied
`k = 59`).

---

## Erratum 5 — §10.2/§10.3 entry weights are not renormalised

Raised by Review A (Finding 2).

`entry_weight = 1/|D_hat|` is fixed at the full residual count, but a residual
with no eligible control emits no rows, and the per-FSM sum runs over surviving
residuals only. An FSM with three fitted residuals, one of which has no control,
would contribute `2/3` of its true mean.

**Inert in this run:** `fitted_residual_count == 1` for all 480 structured FSMs,
so such an FSM drops out entirely rather than being under-weighted. This is the
mechanism behind the 24 dropped FSMs in `secondary_fitted_post`, which is
disclosed in `RESULTS.md` §11. It would bite on any future run with multiple
fitted residuals per map. Descriptive analyses only; the primary cannot be
affected.

---

## Erratum 6 — §12's byte-for-byte guarantee has a latent dependency

Raised by Review A (Observation 7b).

`analyze_synthetic_fsm.estimate_block` returns early when either family is empty
**without consuming any draws from the shared sign-flip stream**. In any future
run where one block is unavailable, every downstream block's stream would shift,
so artifacts would not be byte-comparable against a run where it was available.
All ten blocks are `available: true` in this run, so the branch never fired and
the §12 guarantee held (verified: byte-identical clean rerun).

---

## Erratum 7 — §8's two "gates" have essentially no power to fail

Raised by Review D (`review/REVIEW_D_NOVELTY.md`, §7) and verified by the author.

Both gates pass, and both were essentially guaranteed to pass. They should be
read as **implementation self-checks**, not as controls that could have
discriminated anything.

**Recovery gate is mathematically forced.** Two *distinct* affine maps on `Z_64`
agree in **at most 32 of 64 positions** (verified exhaustively over all
4096 × 4096 candidate pairs; the extreme pair is `(a,b) = (0,0)` vs `(32,0)`).
A map that is an affine skeleton `h` with exactly one transition replaced is
therefore at Hamming distance 1 from `h` and at distance ≥ 32 from every other
affine candidate. Since the codelength is increasing in `k` over this range,
`h` is the unique minimiser and `D_hat = {u*}` **as a theorem**. Skeleton
recovery of 240/240 with pooled precision and recall 1.000 could not have come
out otherwise.

**Specificity gate has ~0.3% failure probability against a 5% threshold.** The
affine model beats the full table iff `k <= 55`, i.e. iff the observed map
agrees with some affine candidate in at least 9 of 64 positions. For a uniform
random map and one fixed candidate that probability is `7.038e-07`; the union
bound over 4096 candidates is **0.0029**, and direct simulation over 20,000
uniform random maps gives **49/20000 = 0.0024**. The registered threshold allows
a 0.05 failure rate — roughly 17× the expected rate. The observed 1/120 = 0.0083
is an ordinary draw.

**Consequence for wording.** "Both controls behaved perfectly" is not evidence
about the experiment. `RESULTS.md` §6 and §7 now state the power of each gate
alongside its value.

---

## Erratum 8 — §0's freeze header is true only under a seed-label reading of "outcome"

Raised by Review D (§2, "the one genuine leakage finding").

`PROTOCOL.md`'s header states it was "Frozen 2026-08-23, before any development
or holdout outcome was generated." No *registered-seed* outcome had been
generated. But the full pipeline had already been run end-to-end at full sample
size on a sentinel cohort (`protocol_revision = 900`, seeds shifted by
900,000,000), and its results were seen by the operator:

| pre-freeze sentinel (rev 900) | Δ | permutation | contracting |
|---|---:|---:|---:|
| development | +0.036159 | +0.074637 | −0.002319 |
| holdout | +0.054684 | +0.077474 | +0.031895 |

The direction, the approximate magnitude, the "permutation carries it /
contracting is null" split and `FSM_H1_confirmed: false` were therefore all known
before the freeze commit.

**Why this could not have influenced the registered design.** Every scientific
element of this protocol — the state set, both structured families, the affine
candidate family, the exact codelength and tie rule, the planting rule, all six
registered seed blocks, the continuation seeds and rule, the estimand, the
matching, the equal-family weighting, **the direction of FSM-H1**, both gate
thresholds, the bootstrap and sign-flip specifications, the analysis RNG seeds
and the interpretation gate — was specified verbatim in the externally supplied
task specification, which predates all work in this repository. `PROTOCOL.md` is
a transcription of that specification, not an authored design. The generator's
RNG draw order was fixed in code *before* the sentinel run.

The only elements authored after the sentinel numbers were seen are
`PROTOCOL.md`'s prose, the residual-destination-type taxonomy (descriptive,
secondary) and the §6.1 "Consequence" lemma — which is false and is retracted in
Erratum 1 above.

**What this does change.** The reversal must not be described as a falsified
prediction or as a surprise. It is a confirmation, on registered seeds, of a
direction already observed on an exchangeable non-registered cohort. This is
stated in `RESULTS.md` §5.1 and `RUN_LOG.md` §7.2.
