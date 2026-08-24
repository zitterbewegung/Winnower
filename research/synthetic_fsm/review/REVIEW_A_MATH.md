# Review A — Mathematical Correctness

Independent adversarial review, 2026-08-23. Read-only on the worktree; scratch
code outside the repository. Asked to audit the trajectory-prefix definition,
cycle canonicalization, the exact factorization of `C`, the codelength and its
tie rule, matching, family weighting, bootstrap and sign-flip formulas, Holm,
and the bounds assertions.

## VERDICT: **PASS WITH CONCERNS**

The dynamical core, the exact factorization of `C`, the MDL fit, the matching,
the family weighting and the Holm adjustment are all **mathematically correct
and exactly as specified**. No counterexample to the `s_f(u)` closed form was
found despite exhaustive search. Every reported number in `summary.json`
reproduces bit-for-bit from an independent path.

One **material** concern: the registered inference procedure (sign-flip +
percentile bootstrap) is measurably mis-calibrated for this estimand, in the
registered direction, because `delta_theta` is strongly right-skewed.

---

## 1. Trajectory prefix — VERIFIED

`synthetic_fsm.py:165-184`. The loop appends `x_t` while unseen and stops at the
first repeat, so `len(order) == tau_f(x)` and `order == [x_0..x_{tau-1}]`.
`V_f(x)` equals the forward-reachable set because a functional graph has
out-degree 1: the walk is a "rho" whose vertex set is closed under `f` and
contains `x`, hence equals the reachable closure.

Exhaustive over **all 1,382 maps for n = 2..5, every start state**, against
(a) a literal `tau` from the definition, (b) the visit-order list, and (c) an
independent transitive-closure reachable set:

```
exhaustive n=2..5: tau mismatches 0 | order mismatches 0 | V_f(x) != reachable-set 0
```

## 2. Cycle canonicalization — VERIFIED

`synthetic_fsm.py:200-210`, `:186-198`, `:227-244`.

- Lex-smallest rotation checked against explicitly enumerated rotations for all
  injective sequences of length 1..5 over 8 symbols — 0 failures;
  rotation-invariance 0 failures.
- Direction-sensitive: 0/210 length-3 cycles had
  `canonical(c) == canonical(reversed(c))`. Reversal is **not** identified.
- Labels are a deterministic function of `f` alone; verified over 300 random
  maps (n = 2..8) that labels and cycle list are identical for list vs ndarray
  input and that the cycle list is sorted — 0 failures.

## 3. The exact factorization of `C` — VERIFIED (exhaustively)

`synthetic_fsm.py:256-295`. The two case claims are individually correct:

- **Case A** (`y` reaches `u` under `f`, `y != f(u)`): the edited walk from `u`
  returns to `u`, so the edited terminal cycle *contains* `u` with successor
  `y`. If `u` was off its baseline cycle, the baseline cycle does not contain
  `u`; if `u` was on it, the successor there is `f(u) != y`. Either way the
  canonical tuples differ — and canonicalization preserves the successor
  relation (§2), which is what makes the argument sound.
- **Case B**: the edited walk never revisits `u`, so `f^{u->y}` agrees with `f`
  along the entire walk from `y`, giving `cycle_f(y)`.

Exclusion of `y = f(u)` is correct in both branches (`:283-288`).

Reproductions run — literal double average in exact `Fraction` arithmetic, never
calling the optimised routine:

```
exhaustive n=2,3,4: 1113 (map,state) pairs, disagreements=0
exhaustive n=5:     15625 pairs, cumulative disagreements=0
random n=6..8:      8400 pairs, cumulative disagreements=0
```

Targeted adversarial search for the requested counterexample — `y` reaches `u`,
`y != f(u)`, yet the edited canonical cycle from `u` equals `cycle_f(u)`:

```
ancestor cases examined: 33192
  of which y==u self-loops: 13326
  of which u on its own cycle: 20730
Claim A violations: 0     Claim B violations: 0
```

At `N = 64`, three randomly chosen holdout planted sources were checked against
the full literal double average over all 63 destinations × 64 start states in
exact rationals: `theta == s/63` and `C == vc*s/(64*63)` in all three.

**End-to-end independent recomputation**: `delta_theta` recomputed for all 240
holdout structured FSMs from the stored transition tables using only literal
definitions and `Fraction`, re-deriving pre-treatment strata from the skeleton:

```
max |independent delta_theta - stored| over 240 FSMs: 1.53e-16
independent exact Delta: 0.03111870802128677   reported: 0.031118708021286745
```

This is a stronger check than the shipped `verify_synthetic_fsm_estimator.py`,
which only re-aggregates the already-computed `diff_theta` column.

## 4. Codelength and model selection — VERIFIED, with three observations

- `codelength_affine(k)` bit-identical to an independently written formula for
  all `k = 0..64`; `L_full == 384.0` exactly.
- Row order is a-major/b-minor: `C[a*64+b] == affine_map(a,b)` for all 4096 rows.
- `np.argmin` first-minimum: guaranteed by NumPy's documented contract, and
  `bits` is a plain finite float64 1-D array. Verified over 109 random tables
  producing genuine minimum-`k` ties, plus a **constructed two-way tie at k=30**
  (`tab[x] = x` for even `x`, `3x mod 64` for odd): tied candidates `(3,0)` and
  `(35,32)`; `fit_mdl` selected `(3,0)`, the lex-smallest. Since `bits` depends
  only on the integer `k`, tied candidates get bit-identical floats, so "first
  minimum" is exactly "lex-smallest `(a,b)` among minimum-`k`".
- Brute-force selection agreement over the full 4096-candidate enumeration on 30
  maps, structured and random: **0 mismatches**.
- Full table wins exact ties: `if full_bits <= best_bits` (`:391`) is the
  registered `<=`.

**Observation 4a (minor).** At `n = 64` an exact tie is *impossible*:
`L(55) = 381.4536`, `L(56) = 384.7935`, and no `k` gives exactly 384. The tie
rule is unreachable, and `test_full_table_wins_ties` is tautological — it
re-implements the rule and would pass unchanged if `<=` were mutated to `<`. The
tie rule is therefore untested, though also unfalsifiable at the registered `n`.

**Observation 4b (minor).** `L(k)` is not monotone at the very top:
`L(64) = 400.5683 < L(63) = 400.5910`. Harmless: both exceed `L_full = 384`, so
the full table wins, and the observed data never reaches there (max implied
`k = 59`).

**Observation 4c (minor, worth stating in the write-up).** The frozen code
admits the affine model with up to **k = 55 exceptions** (86% of the table
wrong) as cheaper than the full table. Exactly one holdout random map exploited
this: `hol-random-000220292`, `best_affine_bits = 381.4536` (k = 55), fitted
`(a,b) = (53,7)`. That single map is the entire specificity shortfall. This is
faithful to the spec, but "selected the affine model" is not synonymous with
"found structure" at that end of the range.

## 5. Matching — VERIFIED

Controls are strictly skeleton-derived (pre-treatment) and exclude the planted
source. `delta_m = theta_f(u*) - mean_{v in M_m} theta_f(v)` with post-treatment
`theta`, exactly per PROTOCOL §7. An independent recomputation that rebuilt
strata from `skeleton_table_json` reproduced `matched_control_count` for all 240
holdout FSMs with zero mismatches.

## 6. Family weighting — VERIFIED

`equal_family_mean` is literally `0.5*mean(perm) + 0.5*mean(contract)`, no size
weighting. Recomputed: `0.031118708021286745`, identical to the reported `Delta`.

## 7. Bootstrap and sign-flip — implementation VERIFIED; the sign-flip null is MATERIALLY mis-calibrated

**Implementation (verified).** Stratified resampling at observed per-family
sizes, 2.5/97.5 percentiles, `p_left = (1 + #{stats <= observed})/(n_draws + 1)`
exactly as registered. The shared `PCG64(330001)` stream is consumed in the
registered order. The reviewer reproduced the entire stream and got every
reported p-value and CI to the last digit:

```
recomputed ci:     0.009616174329122745  0.053229401709838454   (reported: identical)
recomputed p_left  0.9972002799720028                            (reported: identical)
perm p_left 0.9982001799820018 / contr 0.7681231876812319        (reported: identical)
```

### FINDING 1 — MATERIAL: the registered confirmation rule is anti-conservative for FSM-H1

`synthetic_fsm.py:881-916` + PROTOCOL §9.2/§9.3.

The sign-flip null assumes each per-FSM effect is **symmetric about zero** under
H0. `delta_theta` is not remotely symmetric — it is one state's `theta` minus
the mean of up to 63 others, on a bounded, coarsely discrete grid (`s/63`):

```
permutation: mean=0.05260 median=0.00410 #zero=0  #neg=57 #pos=63 skew=1.03  range [-0.238, 0.492]
contracting: mean=0.00964 median=-0.00051 #zero=23 #neg=82 #pos=15 skew=3.34 range [-0.492, 0.905]
```

The reviewer built an exactly mean-zero null population by centring the observed
per-FSM effects within family (preserving shape and skew) and ran the registered
procedures over 2000–4000 replicates:

```
sign-flip type-I   left = 0.0720   right = 0.0365   two-sided = 0.0530
percentile-bootstrap 95% coverage of true 0 = 0.9455
   interval entirely below zero = 0.0385   entirely above = 0.0160
registered FSM-H1 rule (CI wholly < 0 AND p_left < 0.05): 0.0345   (nominal <= 0.025)
```

The inflation is **in the registered direction** — the left tail, which is
FSM-H1. The right tail is correspondingly conservative, so the *reported*
`p_right = 0.0029` is if anything understated by the same skew, not overstated.

> **Author replication.** This was independently re-run by the author over 1,500
> replicates (1,500 bootstrap resamples, 1,500 flips each), centring the observed
> holdout per-FSM effects within family:
>
> ```
> sign-flip p_left  < 0.05 : 0.0600     (nominal 0.050)
> sign-flip p_right < 0.05 : 0.0407     (nominal 0.050)
> bootstrap CI covers 0    : 0.9480     (nominal 0.950)
> CI entirely below 0      : 0.0313     (nominal 0.025)
> CI entirely above 0      : 0.0207     (nominal 0.025)
> registered FSM-H1 rule   : 0.0313     (nominal <= 0.025)
> ```
>
> The author's magnitudes are smaller than the reviewer's but agree in direction
> and sign: the registered rule is roughly **1.25×** anti-conservative for
> FSM-H1, and the right tail is conservative. Both estimates are reported;
> neither is adjusted away.

This is not a coding error; it is an inference-validity issue in the frozen
§9.2/§9.3. It cost nothing on this run — H1 was not confirmed and `Delta` came
out positive — but it must be disclosed. **It is not fixed on this revision:**
PROTOCOL §11 requires a documented protocol revision, new freeze and full
regeneration for any post-holdout change to the statistic. A skew-corrected
interval (BCa or studentized) plus a t-statistic-based flip would be the correct
remedy in a future revision.

The reviewer also ran a design-based re-randomisation: replanting the same kind
of edit at every other member of `u*`'s pre-treatment stratum, over all 240
holdout FSMs, reproduces `Delta ≈ +0.043 ± 0.009`, with the observed `+0.0311`
at design `p_left = 0.09`. The statistic's design variability (sd 0.0091) agrees
with the bootstrap sd (~0.011). This is a consistency check that passed, not a
defect; note that this reference distribution is *not* a no-effect null, since
replanting elsewhere reproduces the same residual-vs-regular contrast.

**Observation 7a (minor).** `cluster_bootstrap` is called with the identical
seed 330000 for all five outcome blocks and both splits
(`analyze_synthetic_fsm.py:433/441/449`), so blocks with the same family sizes
share the *same* resample index sets. Each marginal CI is still valid; the CIs
are just perfectly dependent across outcomes. **They must not be read as
independent corroboration.**

**Observation 7b (minor, latent).** `analyze_synthetic_fsm.py:235-241` returns
early when either family is empty **without consuming any draws from the shared
`flip_rng`**. Any future run where one block is unavailable would silently shift
every downstream block's sign-flip stream, breaking the §12 byte-for-byte
reproducibility claim relative to a run where it was available. All ten blocks
are `available: true` in this run, so it never fired.

## 8. Holm adjustment — VERIFIED

Standard step-down: sort ascending, `min(1, (m-rank)·p)`, running maximum for
monotonicity, written back to the original index. Randomized property check over
20,000 vectors (m = 1..5): **0 violations**. Reported values reproduce.

## 9. Bounds assertions — VERIFIED, with one dead-code note

Invoked unconditionally at the end of `entry_rows`, which is on the only
production path. Fault injection confirmed all six fire:

```
caught w==0: OK   caught w>1: OK   caught C>w: OK
caught C<0: OK    caught theta>1: OK   caught theta<0: OK
```

**Observation 9a (minor).** The `+ 1e-12` slack at `:650` is dead code.
`C = (vc*s)/4032` and `w = vc/64`; when `s = 63` the true quotient is exactly
`vc/64`, dyadic and exactly representable, so IEEE correctly-rounded division
returns it bit-exactly. Measured over 90 holdout maps × 64 states:
`max(C - w) = 0.0` exactly. The slack should be `0` so a real violation cannot
hide under it.

## Additional finding

### FINDING 2 — MINOR (latent): secondary entry weights are not renormalised

`synthetic_fsm.py:813` and `:826`. `entry_weight = 1.0 / n_res` is fixed at the
*full* residual count, but `emit` is skipped when a residual has no eligible
controls, and `per_fsm_secondary` sums over the surviving residuals only. An FSM
with `|D_hat| = 3` where one residual has no control would report `2/3` of its
true mean.

It cannot bite in this run: `fitted_residual_count == 1` for all 480 structured
FSMs, so `n_res = 1` and such an FSM simply drops out entirely. It would bite on
any future map with multiple fitted residuals. Descriptive analysis only; it
cannot touch the primary.

## What the reviewer did not find

No error in `trajectory_prefix`, `terminal_cycle`, `canonical_cycle`,
`cycle_labels`, `on_cycle_flags`, `reachability_matrix`, `visit_counts`. No
counterexample to the `s_f(u)` closed form over ~25,000 exhaustively enumerated
(map, state) pairs at n ≤ 5, 8,400 random pairs at n = 6..8, all 240 holdout
FSMs' full matched sets at n = 64 in exact rationals, and three full n = 64
double-average enumerations. No error in the codelength formula, candidate
ordering, tie-break or full-table rule. No post-treatment contamination in the
primary matching, no exclusion of controls beyond the planted source, no
implicit family reweighting. No error in the bootstrap scheme, the percentile
levels, the `p_left`/`p_right`/`p_two_sided` formulas, or Holm.
