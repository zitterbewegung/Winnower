# Codex audit — NOT AVAILABLE

The repository's `CLAUDE.md` asks that novelty and publishability conclusions be
piped to `codex exec` for independent review, with the full transcript returned.
That was attempted and **failed for an external reason**. This file records the
attempt verbatim so the absence is auditable rather than silent.

## What was run

```console
$ codex --version
codex-cli 0.149.0

$ codex exec --sandbox read-only --skip-git-repo-check \
    -C /Users/r2q2/Projects/ishtar/fsm-winnower - < codex_prompt.md
```

The full audit prompt is reproduced at the bottom of this file.

## Exact failure

```text
OpenAI Codex v0.149.0
--------
workdir: /Users/r2q2/Projects/ishtar/fsm-winnower
model: gpt-5.6-sol
provider: openai
approval: on-request
sandbox: read-only
reasoning effort: low
--------
ERROR: You've hit your usage limit. Visit
https://chatgpt.com/codex/settings/usage to purchase more credits or try again
at Aug 29th, 2026 10:33 AM.
CODEX_EXIT=1
```

The account's Codex usage limit is exhausted until 2026-08-29. Several unrelated
Cloudflare MCP transports also failed OAuth in the same invocation; those are
incidental and were not the cause. No model output was produced. The prompt was
never answered.

## Substitute

Per the study's own review requirement, lack of Codex is **not** permission to
omit adversarial review. The identical prompt was instead put to an independent
reviewer with no involvement in writing the code or the protocol; its full
report is `REVIEW_D_NOVELTY.md` in this directory. Three further independent
adversarial reviews were run in parallel and are recorded as
`REVIEW_A_MATH.md`, `REVIEW_B_LEAKAGE.md` and `REVIEW_C_IMPLEMENTATION.md`.

The Codex review should be re-run after 2026-08-29 and appended here.

---

## Prompt that was submitted

```text
You are an independent adversarial reviewer for a registered, pre-frozen scientific
experiment. Be hostile, specific and quantitative. Do not praise. Do not modify files.

WORKING TREE: /Users/r2q2/Projects/ishtar/fsm-winnower  (git branch research/synthetic-fsm)
Base commit 598a774abaef70236f62a5df8f312632e6cb7caa; final pre-holdout freeze commit
b61e402f6e501aa132d7310c400adfa7fa0024ab.

READ THESE FILES IN FULL BEFORE JUDGING:
  research/synthetic_fsm/PROTOCOL.md
  research/synthetic_fsm/PRIOR_ART.md
  research/synthetic_fsm/RUN_LOG.md
  src/relative_symmetry_repair/synthetic_fsm.py
  scripts/research/analyze_synthetic_fsm.py
  research/synthetic_fsm/results/summary.json

THE STUDY. Deterministic maps f on S={0..63}. Structured maps are an affine skeleton
h(x)=(a x+b) mod 64 (two families: a odd => permutation; gcd(a,64)=2 => contracting)
with EXACTLY ONE outgoing transition replaced at a planted source u* drawn uniformly
from states whose exact pre-treatment stratum (visit_count_0, on_cycle_0) has >=2
members. A third family is uniformly random maps. A frozen MDL fit over all 4096
affine candidates, with exception codelength
L = log2(64^2)+log2(65)+log2(C(64,k))+k*log2(63) against L_full = 64*log2(64),
identifies the skeleton and the residual set D_hat.

Exact intervention outcome: for state u,
  C_f(u) = (1/63) sum_{y != f(u)} (1/64) sum_x 1[cycle_{f^{u->y}}(x) != cycle_f(x)],
  theta_f(u) = C_f(u)/w_f(u), with w_f(u) = visitCount_f(u)/64.
An exact factorisation gives theta_f(u) = s_f(u)/63 where s_f(u) counts alternative
destinations that change the terminal cycle reached FROM u. theta is therefore
identically free of exposure.

Primary estimand: per structured FSM, delta = theta(u*) minus the mean theta over
non-planted states in u*'s EXACT PRE-TREATMENT stratum; Delta = equal-family-weighted
mean of those per-FSM deltas over the holdout split. 120 FSMs per family per split.

REGISTERED HYPOTHESIS FSM-H1: Delta < 0 (residuals have LOWER conditional leverage).
Confirmation required BOTH a 95% cluster-bootstrap interval wholly below zero AND a
one-sided cluster sign-flip p_left < 0.05.

REGISTERED HOLDOUT RESULT (protocol_revision 0, one run, no continuation needed):
  Recovery gate: skeleton recovery 240/240 = 1.0; pooled precision 1.0; pooled recall 1.0
    (TP 240, FP 0, FN 0); every structured FSM has exactly one fitted residual. PASS.
  Specificity gate: 119/120 = 0.99167 of holdout random maps select the full table. PASS.
  Informative-cluster gate: 120 and 120 (threshold 100). PASS.
  PRIMARY: Delta = +0.031118708021286745, 95% CI [+0.009616174, +0.053229402],
    p_left = 0.9972, p_right = 0.0029, two-sided p = 0.0058.  FSM-H1 NOT CONFIRMED;
    the effect is significantly in the OPPOSITE direction.
  Families: permutation +0.052598 [+0.017992, +0.088313], two-sided Holm p = 0.0076;
            contracting +0.009639 [-0.013738, +0.037343], two-sided Holm p = 0.464.
  Development split agreed: Delta = +0.036930 [+0.015843, +0.059273].
  Secondary delta_C = +0.029360 [+0.004775, +0.054247]; delta_w = +0.032583.
  Fitted-residual (pre-treatment matched) analysis is numerically IDENTICAL to the
    primary because recovery was perfect (D_hat = {u*} for all 240 FSMs).
  POST-TREATMENT exposure sensitivity REVERSES the sign:
    Delta = -0.016646 [-0.029047, -0.003213], p_left = 0.0084, on n = (98, 118).
  Diagnostics (holdout, per-FSM delta by planted destination type):
    pre_ancestor_of_source +0.2403 (n=55); self_loop +0.2109 (n=5);
    same_terminal_cycle -0.0138 (n=115); different_terminal_cycle -0.0802 (n=65).
  Family is perfectly collinear with pre_on_cycle: all 120 permutation planted sources
    are on-cycle pre-treatment, all 120 contracting planted sources are off-cycle.
  Independent clean-room estimator agrees to 3.5e-17. A clean rerun reproduces every
  artifact byte-for-byte including gzip bytes and the SVG.

DISCLOSED PROCESS FACTS (in RUN_LOG.md): three pre-holdout bug fixes each produced a
new freeze commit (two run-time guard fixes, one exact-CSV-float-read fix); and an early
smoke test generated rows for 12 registered holdout seeds into a discarded pytest
tmp_path without any statistic being observed.

ANSWER THESE, EACH WITH A HEADING AND A CONCRETE JUDGEMENT:
 1. CORRECTNESS. Is the theta = s/63 factorisation right? Is the codelength and its
    tie rule right? Is the matching right? Try to break the factorisation.
 2. LEAKAGE. Is there any route by which the holdout influenced a frozen choice?
    Are the three pre-holdout re-freezes legitimate under the stated rule?
 3. STATISTICAL VALIDITY. Is the cluster sign-flip null appropriate? Is quoting the
    two-sided p for a reversed effect legitimate, given a one-sided registered test?
    Is the equal-family weighting defensible given the 5x family gap and the
    family/pre_on_cycle collinearity?
 4. ALTERNATIVE EXPLANATIONS. The strongest one I can see: theta is a POST-treatment
    quantity, the planted edit reshapes the post-treatment graph, and the planted
    source sits at the epicentre; pre-treatment matching cannot equalise post-treatment
    graph position. Is the positive Delta therefore mechanical rather than informative
    about compression? Are there other explanations I have missed?
 5. PRIOR-ART OVERLAP. Given PRIOR_ART.md — especially Zenil et al.'s algorithmic
    information dynamics and the sibling finite-state study that already reported
    exactly zero incremental effect for a transition-exception codelength — what, if
    anything, is left that is genuinely new here?
 6. DEFENSIBLE NOVELTY. Write the single strongest sentence that this evidence
    actually supports, and nothing stronger.
 7. STRONGEST CLAIM. What is the strongest claim the authors may make?
 8. STRONGEST FALSIFICATION. What single further experiment would most cleanly kill
    the claim, and what would you predict it shows?

End with a VERDICT line: PUBLISHABLE AS A NEGATIVE/REVERSED RESULT / NEEDS REVISION /
NOT PUBLISHABLE, plus the three sentences the final RESULTS.md must contain.
```
