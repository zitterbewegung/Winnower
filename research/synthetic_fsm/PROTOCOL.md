# PROTOCOL — synthetic FSM residual/leverage (protocol_revision = 0)

Frozen **2026-08-23**, before any development or holdout outcome was generated.
Base commit: `598a774abaef70236f62a5df8f312632e6cb7caa`
(`zitterbewegung/Winnower`, `main`, subject "Create uv.lock").
Research branch: `research/synthetic-fsm`.

Prior art was audited before this file was written; see `PRIOR_ART.md`.

---

## 0. Question

> Does a state transition identified as a sparse deviation from a compressed
> deterministic transition rule have lower conditional attractor-switch
> leverage than exposure-matched regular transitions?

This is a deliberately restricted test of whether the residual/leverage
relationship reported for cellular automata and Boolean networks survives
after spatial geometry, locality, neighbourhoods and parallel state update are
removed. A positive result would be evidence for a geometry-independent
phenomenon **within this registered model family only**. It would not
establish a universal law. A null, positive, heterogeneous or gate-failing
result is a valid completed outcome.

## 1. Formal system

Deterministic maps `f: S -> S` with `S = {0, ..., 63}`, `N = 64`.

For an initial state `x`: `x_0 = x`, `x_{t+1} = f(x_t)`.

```
tau_f(x) = min{ t >= 1 : x_t in {x_0, ..., x_{t-1}} }
V_f(x)   = { x_0, ..., x_{tau_f(x)-1} }              (distinct pre-repeat prefix)
visitCount_f(u) = |{ x in S : u in V_f(x) }|
w_f(u)   = visitCount_f(u) / 64
```

A state is `on_cycle` exactly when it lies on the directed terminal cycle of
its functional-graph component.

A directed cycle is represented canonically by the lexicographically smallest
rotation of its directed state sequence. Reversal is **not** an equivalence:
edge direction matters.

## 2. Compressed candidate family

```
h_{a,b}(x) = (a*x + b) mod 64,    a, b in {0, ..., 63}      (4096 candidates)
```

Two structured skeleton families:

- **permutation**: `a` uniform on the 32 residues with `gcd(a, 64) = 1`
  (equivalently the odd residues); `b` uniform on `0..63`.
- **contracting**: `a` uniform on the 16 residues with `gcd(a, 64) = 2`;
  `b` uniform on `0..63`.

RNG: `numpy.random.Generator(numpy.random.PCG64(seed))`. A single FSM seed
completely determines skeleton selection, any skeleton resampling, source
selection and destination selection.

## 3. Planting exactly one structural deviation

For each structured skeleton `h`:

1. compute `visit_count_0` and `on_cycle_0` from the **unmodified** skeleton;
2. form exact pre-treatment strata `(visit_count_0, on_cycle_0)`;
3. eligible sources = states whose stratum contains at least two states;
4. draw the planted source `u*` uniformly from the eligible set;
5. draw the replacement destination `y*` uniformly from `S \ {h(u*)}`
   (63 options; self-loops are allowed when `u* != h(u*)`);
6. replace only that transition.

If a sampled skeleton has no eligible source, resample the skeleton from the
same seeded stream. **Resampling is driven only by source eligibility.** It is
never driven by MDL recovery, leverage, attractor behaviour, effect direction
or any other post-plant property.

Draw order in the seeded stream is fixed as: `a`, `b`, (repeat `a`, `b` while
ineligible), `u*`, `y*`.

```
f(u) = y*      if u == u*
f(u) = h(u)    otherwise
```

**random family**: each of the 64 destinations is drawn independently and
uniformly from `0..63`. Random maps are never conditioned, resampled or
excluded on the basis of their fitted model. For a random map the
pre-treatment map is the map itself (nothing is planted), so pre- and
post-treatment columns coincide by construction.

## 4. Registered sample and seeds

Per split: 120 permutation, 120 contracting, 120 random.

```
development permutation: 110000..110119
development contracting: 110120..110239
development random:      110240..110359

holdout permutation:     220000..220119
holdout contracting:     220120..220239
holdout random:          220240..220359
```

`protocol_revision = 0`.

### 4.1 Exposed-holdout seed rule

If registered holdout outcomes have already been exposed, or if a genuine
implementation bug is found **after** any holdout outcome has been generated,
increment `protocol_revision` and add `1_000_000 * protocol_revision` to every
development and holdout seed (and to every continuation seed). New seeds are
never chosen by hand after seeing an effect.

### 4.2 Pre-frozen informative-cluster continuation rule

An FSM is **informative** for the primary planted-label estimand when it has at
least one non-planted control in its registered pre-treatment stratum and all
exact metrics are defined.

- If either structured holdout family has fewer than 100 informative FSMs,
  extend that family in deterministic blocks of 40.
- Revision-0 continuation seeds begin at `221000` (permutation) and `222000`
  (contracting); block `k` uses `base + 40*k .. base + 40*k + 39`.
- Later revisions apply the same `1_000_000 * revision` offset.
- Continuation is determined by eligibility and data validity only — never by
  effect size or sign.
- Stop as soon as each family has at least 100 informative FSMs.
- Cap continuation at 400 additional FSMs per family. If the cap is reached,
  finish with an explicit identifiability-gate failure.

No attempted seed is silently dropped; every attempted seed and its status is
recorded in `results/fsm_summary.csv.gz`.

## 5. Frozen static MDL fit

For each observed map `f` evaluate all 4096 affine candidates. With
`k(h, f) = |{u : f(u) != h(u)}|`:

```
L(h, E)  = log2(64^2) + log2(65) + log2(C(64, k)) + k * log2(63)
L_full   = 64 * log2(64) = 384
```

1. Select the candidate of minimum codelength.
2. Ties in codelength break lexicographically on `(a, b)`.
3. If `L_full <= L(h*, E*)`, select the full-table model and mark the map
   `unstructured`.
4. Otherwise select the affine model and set `D_hat = {u : f(u) != h*(u)}`.

The fit may use only the complete static transition table. It must not use
trajectories, visit counts, occupancy, cycle membership, attractors, basin
size, `C`, `theta`, planted labels, or family labels beyond candidate
generation.

## 6. Exact intervention outcome

For `y != f(u)`, `f^{u->y}` is `f` with only the outgoing transition of `u`
changed to `y`. Let `cycle_g(x)` be the canonical directed terminal cycle
reached from `x` under `g`.

```
C_f(u)     = (1/63) * sum_{y != f(u)} (1/64) * sum_{x in S}
             1[ cycle_{f^{u->y}}(x) != cycle_f(x) ]
theta_f(u) = C_f(u) / w_f(u)
```

`w_f(u) > 0` always, because the trajectory from `x = u` visits `u`.

### 6.1 Exact factorization (permitted, and independently tested)

If the baseline trajectory from `x` never visits `u`, editing the outgoing edge
of `u` cannot affect it. If it does visit `u`, its baseline terminal cycle
equals the terminal cycle reached from `u`, and its edited terminal cycle
equals the edited terminal cycle reached from `u`. Therefore with

```
s_f(u) = |{ y != f(u) : cycle_{f^{u->y}}(u) != cycle_f(u) }|
```

we have exactly

```
theta_f(u) = s_f(u) / 63
C_f(u)     = visitCount_f(u) * s_f(u) / (64 * 63)
```

Canonical stored quantities are integers:
`visit_count`, `switch_destination_count`, `C_numerator = visit_count *
switch_destination_count`, `C_denominator = 64*63`,
`theta_numerator = switch_destination_count`, `theta_denominator = 63`.
Floating-point columns are derived from these integers.

For every state the implementation asserts
`0 < w(u) <= 1`, `0 <= C(u) <= w(u) <= 1`, `0 <= theta(u) <= 1`.

`tests/test_synthetic_fsm.py` checks the factorization against a literal,
independent enumeration of the double average, in exact rational arithmetic,
for many maps with `N <= 8` and for spot-checked `N = 64` maps.

**Consequence, stated before freeze:** `theta` is identically free of
`visitCount`. The primary estimand therefore compares a purely structural
per-edge quantity, and pre-treatment exposure matching controls the covariate
that drives the sibling study's `O = E*C` boundary (see `PRIOR_ART.md`, item 8).

## 7. Primary matched effect

For each structured FSM with planted source `u*`, the control set `M_m` is
every non-planted state `v` with

```
visit_count_0(v) == visit_count_0(u*)    and    on_cycle_0(v) == on_cycle_0(u*)
```

(both **pre-treatment**, i.e. computed on the skeleton `h`).

```
delta_m = theta_f(u*) - (1/|M_m|) * sum_{v in M_m} theta_f(v)
```

The confirmatory holdout estimand is the equal-family-weighted mean

```
Delta = 0.5 * mean(delta_m | permutation) + 0.5 * mean(delta_m | contracting)
```

Unequal family sample counts never implicitly reweight the families.

Analogous effects for `C` and `w` are reported. Neither may replace the
registered `theta` estimand.

## 8. Frozen hypotheses and decision rules

1. **Recovery gate (positive control):** on holdout structured FSMs,
   affine-skeleton identification and planted-source precision and recall are
   each at least 0.99.
2. **Specificity gate (negative control):** at least 95% of holdout random maps
   select the full-table model.
3. **FSM-H1 (only confirmatory scientific hypothesis):** `Delta < 0`; sparse
   compression deviations have lower conditional attractor-switch leverage than
   pre-exposure-matched regular transitions.

Pooled recovery counts over holdout structured FSMs:

```
TP = number of planted sources included in D_hat
FP = number of non-planted entries included in D_hat
FN = number of planted sources omitted from D_hat
precision = TP / (TP + FP)        recall = TP / (TP + FN)
```

If no residual entries are predicted, precision is zero for gate purposes.
Macro precision and recall (per-FSM averages) are descriptive only. Holdout
random-map specificity is `(# selecting full-table) / (# random maps)`.

## 9. Frozen statistical procedure

Analysis RNG seeds, `numpy.random.Generator(PCG64(seed))`:

```
cluster bootstrap: 330000
cluster sign flip: 330001
```

### 9.1 Cluster bootstrap

10,000 stratified resamples. Each resample: resample informative permutation
FSMs with replacement at the observed permutation sample size; resample
informative contracting FSMs with replacement at the observed contracting
sample size; take the mean within each family; average the two family means
with equal weight. Report the percentile interval at the 2.5th and 97.5th
percentiles. Family-specific intervals are the 2.5/97.5 percentiles of the
corresponding family means from the same 10,000 resamples.

### 9.2 Cluster sign-flip test

10,000 Monte Carlo sign-flip draws over per-FSM effects. Each FSM effect is
flipped independently and the same equal-family-weighted statistic recomputed.

```
p_left      = (1 + #{permuted statistics <= observed Delta}) / 10001
p_right     = (1 + #{permuted statistics >= observed Delta}) / 10001
p_two_sided = min(1, 2 * min(p_left, p_right))
```

`p_left` is the registered one-sided p-value for the negative alternative.

Sign-flip draws are consumed from one `PCG64(330001)` stream in this fixed
order per split: primary `theta`, then `delta_C`, then `delta_w`, then
`secondary_fitted_pre`, then `secondary_fitted_post`; within each block the
combined test is drawn first, then permutation, then contracting. Splits are
processed in the order `development`, `holdout`.

### 9.3 Confirmation rule

FSM-H1 is confirmed only when **both** hold:

1. the 95% bootstrap interval lies wholly below zero;
2. the one-sided sign-flip p-value is below 0.05.

The point estimate, interval, one-sided p-value and two-sided p-value are
reported regardless of outcome.

### 9.4 Family-specific multiplicity

Family-specific tests are descriptive. Holm adjustment is applied across the
two family p-values. Raw and adjusted values are both reported.

### 9.5 Interpretation gate

The H1 statistic is always reported, but it is interpreted as evidence about
**compression residuals** only if both the recovery and specificity gates pass.

If H1 passes but a model-identification gate fails, the verdict is:

```
directional effect observed, but not diagnostic of the registered
compression-residual interpretation
```

If family signs differ materially, the heterogeneity is reported even when the
equal-weight combined statistic meets the formal H1 rule.

## 10. Secondary analyses

Secondary analyses cannot rescue or replace the primary test.

- **10.1 Family-specific effects.** Permutation and contracting effects with
  bootstrap intervals and Holm-adjusted descriptive p-values.
- **10.2 Fitted-residual analysis.** Repeat the comparison using `D_hat`
  instead of the planted label. Within one FSM each fitted residual `r` gets
  `delta_r = theta(r) - mean over non-residual states in r`'s exact
  pre-treatment stratum; the FSM-level value is the **unweighted mean over that
  FSM's residuals** (entry weight `1/|D_hat|`), so an FSM never receives weight
  proportional to its residual count. FSMs remain the clusters.
- **10.3 Post-treatment exposure sensitivity.** The same fitted-residual
  comparison, but controls are non-residual states matched on exact
  **post-treatment integer visit count**. Explicitly labelled post-treatment
  and observational.
- **10.4 Structural diagnostics.** Effects broken out by pre-treatment cycle
  membership, pre-treatment visit-count stratum, cycle length, residual
  destination type and family. Descriptive only; these are not searched for a
  replacement headline.

Residual destination type is classified against the skeleton `h`, in this
exclusive order: `self_loop`; `pre_ancestor_of_source` (the destination reaches
the source under `h`, so the edit closes a new cycle); `same_terminal_cycle`;
`different_terminal_cycle`.

## 11. Anti-leakage and bug-fix rules

Development data is for implementation diagnostics only. It may not be used to
change direction, estimand, matching, family weights, candidate model,
codelength, exclusions, sample size based on effect, continuation based on
effect, bootstrap, p-value definition or gate thresholds.

**Before holdout**, a genuine implementation bug may be fixed, provided the bug
is documented, correctness tests are rerun, a new freeze commit is created, and
the final pre-holdout freeze SHA is identified.

**After any holdout outcome is generated or inspected**, a code or analysis bug
requires: preservation of the invalidated run and its hashes in a clearly
marked quarantine or audit record; a documented protocol revision; a new freeze
commit; deterministic seed offset by `1_000_000 * revision`; complete
regeneration of development and holdout artifacts; and no reuse of the exposed
holdout as confirmatory evidence.

Wording corrections and claim narrowing that do not alter numbers are allowed
after holdout and must be documented.

### 11.1 Prohibited tuning

Hand-picking maps, seeds, source states, destinations, exclusions or examples;
changing the frozen design after viewing holdout results; replacing exact
intervention enumeration with Monte Carlo; hiding nulls, failed gates,
heterogeneity, low power or implementation deviations; optimising the
experiment to produce the expected sign.

## 12. Determinism

Rows are sorted by explicit stable keys (`split, family, seed[, state |
analysis, entry_state, control_state]`) with a stable mergesort; column order
is fixed by construction order; floats are written with `%.17g` (exact float64
round-trip); UTF-8 with `\n` newlines; gzip written with `mtime=0` and no
embedded filename; JSON written with sorted keys and two-space indent; SVG
written with a fixed `svg.hashsalt` and `Date` metadata removed. Volatile
runtime timestamps live only in `manifest.json` and are excluded from the
scientific hash set.

A clean rerun must reproduce `summary.json` byte-for-byte and all registered
CSV contents exactly.

## 13. Independent estimator

`scripts/research/verify_synthetic_fsm_estimator.py` reimplements the primary
estimator using only the standard library and pandas. It imports neither
`relative_symmetry_repair.synthetic_fsm` nor
`scripts.research.analyze_synthetic_fsm`. It must agree with the production
combined estimate and both family means within `1e-12`.
