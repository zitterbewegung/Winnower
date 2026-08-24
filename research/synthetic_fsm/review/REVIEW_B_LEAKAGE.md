# Review B — Leakage and Statistical Validity

Independent adversarial review, 2026-08-23. Read-only on the worktree; scratch
code outside the repository. Asked to hunt for holdout-dependent tuning,
post-treatment information in the primary match, hidden exclusions, seed reuse,
unequal cluster weighting, pseudoreplication, inappropriate one-sided testing,
concealed family heterogeneity, and mechanical explanations of the effect.

## VERDICT: **DEFECTS FOUND**

The *process* is clean — no holdout-dependent tuning, seed reuse, hidden
exclusions in the primary, unequal cluster weighting, or non-reproducibility.
The **defects are mathematical and interpretive**: the frozen protocol contains
a false load-bearing lemma, and the positive headline is an exact mechanical
consequence of post-treatment graph position, not a property of compression
residuals. *As computed, every number is right; as interpreted, the headline is
an artefact.*

Every number below was recomputed by the reviewer from the row-level artifacts.
The author independently re-verified each headline claim; where the author's
recomputation differs slightly, both are shown.

---

## Finding 1 — [BLOCKING] The protocol's central mathematical claim is FALSE

PROTOCOL §6.1 states, as a "**Consequence, stated before freeze**":

> `theta` is identically free of `visitCount`. The primary estimand therefore
> compares a purely structural per-edge quantity, and pre-treatment exposure
> matching controls the covariate that drives the sibling study's `O = E*C`
> boundary.

This is wrong. The exact identity is

```
s_f(u)     = visitCount_f(u) + 64 - B_f(u) - onCycle_f(u)
theta_f(u) = ( visitCount_f(u) + 64 - B_f(u) - onCycle_f(u) ) / 63
```

where `B_f(u)` is the size of `u`'s terminal-cycle basin.

> **Author verification: violations over all 46,080 entry rows = 0.** Confirmed.

Proof: every ancestor of `u` flows into `cycle_f(u)`, so
`#{non-ancestors sharing u's cycle} = B - visitCount`, and `f(u)` always shares
`u`'s cycle. Substituting into
`s = 63 - #{non-ancestors, != f(u), sharing u's cycle}` gives the identity.

`theta` is therefore **exactly affine in post-treatment visit count with slope
1/63**. `corr(theta, post_w) = 0.579` on holdout structured rows (author:
0.5787). The stated justification for the whole design — that `theta` is
exposure-free and pre-matching therefore suffices — collapses.

Exact additive decomposition of the headline (author's recomputation; each term
is the equal-family-weighted, control-averaged difference):

| term | Δ contribution | permutation | contracting |
|---|---:|---:|---:|
| `visitCount/63` | **+0.033100** | +0.079444 | −0.013245 |
| `−B/63` | −0.003169 | −0.029882 | +0.023545 |
| `−onCycle/63` | +0.001188 | +0.003036 | −0.000661 |
| **sum** | **+0.031119** | | |

reproducing the reported `Delta = +0.031118708021286745` exactly.
**106% of the headline is the post-treatment visit-count gap** — i.e. the
headline is, up to a factor of 64/63 and two small corrections, a restatement of
the registered *secondary* outcome `delta_w = +0.032583`.

## Finding 2 — [BLOCKING] The effect is mechanical, and the mechanism is provable

`visitCount_f(u*)` is **mathematically invariant** to editing `u*`'s own
outgoing edge — a first arrival at `u*` never traverses `f(u*)`.

> **Author verification: 0 of 480 planted sources have
> `pre_visit_count != post_visit_count`.** Confirmed.

The controls have no such protection. Mean post−pre visit-count drift of
pre-stratum controls (author's per-FSM recomputation): **−5.055 (permutation)**,
**+0.778 (contracting)**. (Reviewer, aggregating per pair: −5.005 / +0.834.)

So pre-stratum matching matches the entry to controls *at a covariate value the
entry keeps by construction and the controls lose*. Downstream (author's
recomputation, holdout, all within pre-stratum):

| matching used | Δ | perm | contr | n |
|---|---:|---:|---:|---|
| registered: `pre_vc` + `pre_on_cycle` | **+0.031119** | +0.052598 | +0.009639 | (120, 120) |
| + control matches entry's `post_visit_count` | **−0.014198** | −0.051668 | +0.023271 | (98, 118) |
| + matches `post_visit_count` **and** `post_on_cycle` | **−0.000000** | +0.000000 | −0.000000 | (55, 113) |

The last row is not approximately zero. **Max |per-FSM effect| = 2.78e-17** —
floating-point zero, for every single FSM. This is forced by the Finding-1
identity once `(vc, onCycle)` are held fixed.

Only **64.4%** of the 8,526 primary control pairs share the entry's post visit
count and **63.0%** share its post on-cycle flag, despite 100% sharing both
pre-treatment values.

## Finding 3 — [MATERIAL] The whole effect lives in 60/240 FSMs where the random destination happened to close a new cycle

`planted_destination_type` is a property of the uniform draw of `y*`, not of
residual-ness (author's recomputation):

| stratum (holdout structured) | n | perm mean | contr mean | equal-family |
|---|---:|---:|---:|---:|
| cycle-closing (`pre_ancestor_of_source` ∪ `self_loop`) | 60 | +0.20955 (55) | +0.54921 (5) | **+0.37938** |
| all others | 180 | −0.08021 (65) | −0.01382 (115) | **−0.04702** |

25% of FSMs carry the entire effect and **removing them reverses the sign**.
When `y*` reaches `u*` under `h`, the edit necessarily creates a new cycle
through `u*`, which by the Finding-1 identity maximises `theta(u*)`. This is
arithmetic, not biology.

## Finding 4 — [MATERIAL] `family` is perfectly collinear with `pre_on_cycle`; the permutation family has zero pre-treatment outcome variance

Crosstab of planted sources, **both splits**: permutation 120/120
`pre_on_cycle = 1`, contracting 120/120 `pre_on_cycle = 0`.

Stronger: across **all 120 holdout permutation skeletons the only value of
`s_h(u)` observed is 63** — i.e. `theta_h(u) ≡ 1` for all 64 states of every
permutation skeleton.

> **Author verification: holdout permutation skeleton `s` values = `[63]`
> exactly. Contracting skeletons range 1–63 with 6 distinct values.** Confirmed.

The pre-treatment matched contrast in the permutation family is therefore
**identically zero by construction**; 100% of the permutation signal — the
family carrying the significant p-value — is created by the edit itself.

Consequence for reporting: `summary.json`'s `diagnostics.by_pre_on_cycle` is
numerically *identical* to `diagnostics.by_family`. It is presented as a
separate structural breakdown but carries zero independent information.

## Finding 5 — [MATERIAL] Family heterogeneity is real and the automated flag misses it

`family_signs_differ` is `np.sign(perm_mean) != np.sign(contr_mean)` — it
returns `false` here. But:

- permutation +0.052598, CI [+0.0180, +0.0883], Holm two-sided **0.0076**
- contracting +0.009639, CI [**−0.0137**, +0.0373], Holm two-sided **0.464** —
  interval covers zero
- the means differ 5.5×, and the contracting *median* is **−0.00051** with
  **82/120 negative, 23/120 exactly zero, 15/120 positive**

> **Author verification: contracting 15 positive / 23 zero / 82 negative,
> median −0.00051.** Confirmed.

PROTOCOL §9.5 requires heterogeneity to be reported "if family signs differ
materially". The coded test is too weak to fire on this pattern. The combined
equal-weight mean averages two structurally incomparable regimes (Finding 4) in
which only one shows anything.

## Finding 6 — [MATERIAL] The per-FSM distribution is a skewed mixture; the *median* runs in the registered direction in both families

Author's recomputation:

| family | n | mean | median | sd | skew | kurtosis | >0 / =0 / <0 |
|---|---:|---:|---:|---:|---:|---:|---|
| permutation | 120 | +0.05260 | **+0.00410** | 0.196 | +1.03 | −0.09 | 63/0/57 |
| contracting | 120 | +0.00964 | **−0.00051** | 0.144 | **+3.34** | **+21.64** | 15/23/82 |

Rank-based tests on the same data point the other way: contracting Wilcoxon
signed-rank **p = 1.7e-11** and sign test **p = 2.4e-12**, both toward
**negative**; permutation Wilcoxon p = 0.306, sign test p = 0.648.

The registered estimand is a mean, so the mean is what governs. But the
sign-flip null is *symmetry of each per-FSM effect about zero*, not *zero mean*,
and with skew +3.34 and 19% exact ties that null is false for reasons of shape.
The analytic normal check agrees closely with the bootstrap (SE 0.011116,
z = 2.800, p = 0.0051; 1.96·SE = 0.021787 vs bootstrap half-width 0.021806), so
the interval itself is sound. See Review A Finding 1 for the calibration
consequence.

## Finding 7 — [MATERIAL] The post-treatment sensitivity silently drops 24 FSMs, and they are the most negative ones

`n = (98, 118)` in `secondary_fitted_post`. Cause: for 24 structured holdout
FSMs the single fitted residual has a `post_visit_count` shared by **no**
non-residual state (values 8, 16, 31, 32 — the exactly-half and full-basin
cases), so `matched_effect_rows` emits no rows and `per_fsm_secondary`'s
`groupby` drops the cluster without recording it.

> **Author verification: 24 dropped — 22 permutation, 2 contracting. Their
> `delta_theta` means are −0.11486 (perm) and −0.49206 (contr), versus +0.09019
> and +0.01814 for the retained 216.** Confirmed.

The reversal is **not** a selection artefact: on the common 216 FSMs the
pre-matched Δ is **+0.054167** versus post-matched −0.016646. The sign flip is
caused by the matching change, not the exclusion. But the differential drop must
be disclosed; `summary.json` reports only the surviving `n`, never the rule.

## Finding 8 — [MINOR] `secondary_fitted_pre` is bit-identical to the primary

Recovery is perfect: `is_planted_source == is_fitted_residual` in
**30,720/30,720** structured entry rows (author: confirmed);
`fitted_residual_count == 1` for all 480 structured FSMs. Consequently
`secondary_fitted_pre` and `primary_planted_pre` have the same entries, the same
control sets, and `max |diff_theta difference| = 0.0`. It is the same number
computed twice, not a replication.

## Finding 9 — [MINOR, but must be stated precisely] What the frozen rule does and does not license

**Licensed by the freeze:**

- PROTOCOL §9.2 pre-defines `p_two_sided`, and §9.3 pre-commits to reporting the
  point estimate, interval, one-sided **and** two-sided p-value regardless of
  outcome. Reporting `p = 0.0058` is therefore *not* a post-hoc switch.
- Reporting that the pre-registered interval `[+0.009616, +0.053229]` excludes
  zero.
- The verdict actually emitted: `FSM_H1_confirmed = false`.

**NOT licensed by the freeze:**

- Any *confirmatory* claim in the positive direction. §9.3's only decision rule
  is `H1: Delta < 0`. There is no registered positive alternative, no registered
  alpha for it, and no registered power analysis for it. "Significantly in the
  opposite direction" is an **exploratory** finding.
- Any multiplicity claim: `summary.json` contains **143** p-value fields (author's
  count; reviewer said 142) across 5 estimand blocks × 2 splits × {combined,
  permutation, contracting}. The only registered adjustment is Holm across the
  two *family* p-values within a block (§9.4). The headline two-sided p is not
  corrected for anything.

---

## What the reviewer could NOT break

1. **No holdout-dependent tuning.** `git diff 100d4a1 b61e402 -- src scripts` is
   95 added lines, all of them `_porcelain_lines()` / `dirty_paths()` guard
   helpers, the `--untracked-files=all` flag, the `--allow-dirty` guard call in
   the analyser, and four `float_precision="round_trip"` additions. **No
   generator, codelength, estimand, matching, weighting, statistic or gate
   threshold moved.** The whole diff was read; the RUN_LOG's claim is accurate.
2. **No code changed after the holdout outcome.** On-disk SHA-256 of all five
   scientific files matches `manifest.json`'s `code_hashes` and freeze commit
   `b61e402` exactly.
3. **Seeds.** Exactly the registered blocks, `dev ∩ holdout = ∅`, 720 unique
   `fsm_id`, `protocol_revision = 0` in all three CSVs, `continuation_blocks = 0`
   (correctly not triggered).
4. **Full reproduction.** Byte-for-byte for all five scientific artifacts.
5. **`pre_*` really is the skeleton.** All 8,526 primary pairs share
   `pre_visit_count` and `pre_on_cycle`; 3,910/15,360 structured holdout entry
   rows have `pre_vc != post_vc` and 2,239 have `pre_on_cycle != post_on_cycle`,
   so the columns are genuinely distinct; random maps have `pre ≡ post`.
6. **No unequal weighting or pseudoreplication.** `fsm_weight ≡ 1`,
   `entry_weight ≡ 1` in the primary, `family_weight ∈ {0.5}`, `control_weight`
   sums to exactly 1 per FSM per analysis, exactly one entry state per FSM in
   the primary, and **0** random-family rows enter any estimand.
7. **No hidden missingness in the primary.** 720 FSMs present, `informative == 1`
   for all 240 structured holdout FSMs, 0 NaN `delta_theta`, 64 entry rows per
   FSM.
8. **The disclosed near-miss is non-influential.** Excluding the 8 exposed
   structured seeds gives Δ = **+0.032277** vs +0.031119 (author: confirmed,
   n = (116, 116)). The tests that still touch registered holdout seeds assert
   only table equality and an ID string — no outcome value.
9. **Specificity outlier is inert.** The one random holdout map selecting affine
   contributes **0** rows to any estimand.

Minor note not rising to a finding: 4 holdout structured FSMs have
`matched_control_count == 1` (mean `delta_theta` −0.302) yet receive full
cluster weight. This matches the registered estimand, but the FSM-level effects
are heteroskedastic by a large factor (`m` ranges 1–63). Author: confirmed, 4
FSMs, mean −0.30159.

---

## Author disposition

All thirteen "must contain" sentences the reviewer supplied have been
incorporated into `RESULTS.md` — §1, §9, §10, §11, §12 and §14 — and the false
lemma is retracted in `PROTOCOL_ERRATA.md`. Nothing was softened. No number
changed: PROTOCOL §11 permits wording correction and claim narrowing after
holdout, and forbids anything else without a full protocol revision.
