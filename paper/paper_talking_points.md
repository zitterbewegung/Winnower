# Paper Talking Points

This note is for discussing the paper in plain language. It summarizes the core method, what the theorems do, what is and is not "machine learning," and a few compact examples.

## One-sentence pitch

The paper treats a cellular automaton spacetime as data, fits competing relative-periodic background templates, scores them with a Bernoulli NML criterion, and proves when the selected template stabilizes and when "true background period" is or is not recoverable.

## Short versions

### 30-second version

The paper is not about neural networks. It is a model-selection framework for CA spacetime analysis. For each candidate period and shift, it groups cells into orbit classes, estimates a Bernoulli parameter for each class, and scores the candidate by fit plus complexity. The key theorem says that in a finite candidate set, any candidate with worse asymptotic per-site NLL is eventually eliminated, so the selected model stabilizes when there is a unique best rate.

### 2-minute version

The main move is an orbit-class reduction. A candidate relative-periodic background defines equivalence classes in spacetime, and the best background for that candidate is obtained independently on each class. Under Hamming loss that is just majority vote. Under the Bernoulli likelihood view, each class becomes a tiny Bernoulli estimation problem. That gives a Bernoulli NML score for each candidate.

The theorem chain is:

1. Theorem 1: the best background for a fixed candidate is orbitwise majority vote.
2. Theorem 2: universal monotonicity of fit happens exactly along velocity-matched divisibility chains, which explains overcapacity.
3. Theorem 3: NML scores look like a linear fit term plus a logarithmic complexity term, so candidates with worse asymptotic fit are eventually excluded.
4. Theorem 4: without extra assumptions, the "true background period" is not identifiable.
5. Theorem 5: if the spacetime becomes exactly periodic after a finite transient, the smallest true period is eventually selected.

## What the method is doing

A candidate is a pair `(p, s)`:

- `p` = temporal period
- `s` = spatial shift per period

That candidate induces orbit classes:

- points connected by repeatedly applying `(t, x) -> (t + p, x + s)`

A candidate background is any binary field that is constant on each orbit class.

For each orbit class `j`:

- count the number of ones and zeros
- estimate `theta_j` = fraction of ones
- compute the Bernoulli negative log-likelihood contribution

The candidate score is:

```text
NML = NLL + complexity
```

where:

- `NLL` rewards orbit classes that are close to pure
- `complexity` penalizes candidates with more orbit classes

## Is this machine learning?

Short answer: only in the broad classical-statistics sense.

What it does use:

- maximum-likelihood estimation of Bernoulli parameters
- MDL/NML-style model selection

What it does not use:

- neural networks
- gradient descent
- labeled training data
- learned features or embeddings

Good short phrasing:

> It is closer to classical model selection than to modern machine learning.

## Core definitions in plain language

### Bernoulli parameter

If a variable is binary, the Bernoulli parameter is just the probability of a `1`.

In this paper, each orbit class gets its own Bernoulli parameter:

```text
theta_j = fraction of ones in orbit class j
```

### NLL

Negative log-likelihood measures how badly a candidate explains the data.

- pure orbit classes have low NLL
- mixed orbit classes have high NLL

### NML

Normalized maximum likelihood is a complexity-penalized score:

```text
NML = NLL + complexity penalty
```

Lower is better.

## The theorem chain

### Theorem 1: Optimal Hamming Projection

Statement in plain English:

- once a candidate `(p, s)` is fixed, the best binary background is obtained by majority vote on each orbit class

Why it matters:

- it turns a global fitting problem into many independent local decisions
- it makes the projection computable in one pass over the data

Useful way to say it:

> For a fixed candidate background, fitting is trivial: each orbit class votes for 0 or 1.

### Theorem 2: Exact Characterization of Universal Refinement and Monotonicity

Statement in plain English:

- a more complex candidate is universally at least as good as a simpler one if and only if it is a true refinement along the same velocity-matched divisibility chain

What that means:

- "higher period always fits at least as well" is not true in general
- it is true exactly when the finer candidate literally splits the coarser orbit classes

Why it matters:

- it explains overcapacity
- it shows why naive defect minimization and naive likelihood minimization overfit along refinement chains

Useful way to say it:

> Theorem 2 says overfitting is structural, but only on very specific chains of matched period-and-shift refinements.

### Theorem 3: Rate-Based Elimination and Stabilization

Statement in plain English:

- each candidate has a long-run per-site fit rate `lambda_c`
- the NML score is asymptotically `lambda_c * N(T) + O(log T)`
- so any candidate with a worse rate is eventually eliminated

Why it matters:

- it gives a theorem-level reason the selected period stabilizes
- it separates short-horizon ambiguity from long-horizon behavior

Important caveat:

- full unique-winner stabilization requires a unique best rate
- the theorem does not resolve all tie cases

Useful way to say it:

> The linear fit gap eventually dominates the logarithmic complexity correction.

### Theorem 4: Nonidentifiability

Statement in plain English:

- in general, the observed spacetime does not uniquely determine a "true background period"

Construction idea:

- mix two different lower-period backgrounds in a higher-period schedule
- the lower-period model sees mixed orbit classes
- the higher-period model separates the phases and wins

Why it matters:

- the selected period is the best-compressing description of the whole spacetime
- that is not always the same as a physically preferred notion of background

Useful way to say it:

> The selector identifies the best global explanation of the spacetime, not an intrinsic background-residual decomposition.

### Theorem 5: Identifiability for Eventually Exactly Periodic Backgrounds

Statement in plain English:

- if the spacetime becomes exactly relative-periodic after a finite transient, then NML eventually prefers the smallest true period over larger matched multiples

Why:

- all matched multiples get asymptotic NLL rate 0
- only the finite transient contributes nonzero NLL difference
- the larger models still pay a bigger complexity penalty

Why it matters:

- it gives the clean recovery regime that complements Theorem 4

Useful way to say it:

> Theorem 5 says recovery works when the post-transient spacetime is genuinely exactly periodic.

## Small examples worth remembering

### Example A: pure drift versus static

Use ECA 240 and ECA 204 on the same initial state:

- ECA 240 shifts the pattern right each step, so `(p=1, s=1)` fits well
- ECA 204 is the identity rule, so `(p=1, s=0)` fits well

This is a good way to explain what the shift parameter means.

### Example B: ECA 110 small run

For the small run discussed in the repo, the winner was:

```text
(period = 4, shift = -2)
```

with:

```text
NLL        = 13.7744 bits
complexity = 45.6391 bits
NML        = 59.4135 bits
margin     = 14.8314 bits over the runner-up
```

Good interpretation:

> The spacetime is almost a perfect drifting 4-phase template, with a small amount of residual disorder concentrated in one phase.

### Example C: nonidentifiability toy construction

Take two period-1 static backgrounds:

- `B = 1000`
- `B' = 1100`

Alternate them in time:

```text
t0: 1000
t1: 1100
t2: 1000
t3: 1100
```

Then:

- `(1, 0)` sees a mixed column and has positive asymptotic NLL rate
- `(2, 0)` separates even and odd rows into pure classes and has rate 0

This is the simplest concrete way to explain Theorem 4.

## Honest limitations

Good things to say clearly:

- The framework is global, not local. It does not recover particles or interaction grammars the way computational mechanics aims to.
- Theorem 3 is about eventual ordering of candidates with distinct asymptotic rates. It is not a blanket theorem for every tie case.
- The selected period is not always a "true background period" in a physical sense; Theorem 4 explicitly warns against that reading.
- RL and LZ4 are residual-geometry diagnostics, not the primary theorem-backed selector.

## Good answers to likely questions

### "Why not just minimize defect rate?"

Because defect rate and raw likelihood are monotone along refinement chains. Without complexity control, larger-period candidates are weakly favored by construction.

### "Why NML?"

Because it matches the orbit-class Bernoulli model family and gives a principled fit-plus-complexity tradeoff with asymptotic stabilization.

### "What is the main theorem-level contribution?"

The cleanest answer is:

- the orbit-class Bernoulli framing
- the exact refinement/monotonicity characterization in Theorem 2
- the stabilization theorem in Theorem 3
- the sharp nonidentifiability versus identifiability boundary in Theorems 4 and 5

### "What is the strongest novelty claim?"

The safest answer is:

- Theorem 2's necessity direction
- the explicit Theorem 4 / Theorem 5 identifiability boundary
- the application of the MDL/NML model-selection framework to cross-dimensional CA background analysis

## Suggested closing summary

The paper's message is not "we found the true background period of every CA." The message is:

1. Relative-periodic background fitting has a clean orbit-class formulation.
2. Bernoulli NML gives a principled selector over that model family.
3. The selector stabilizes under broad conditions.
4. What it stabilizes to is the best global explanation of the observed spacetime, which is sometimes but not always a physically privileged background.
