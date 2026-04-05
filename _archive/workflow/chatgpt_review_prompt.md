# Instructions for Reviewer

I'm submitting the following paper to Chaos or Physica D. You are a referee who is an expert in both computational mechanics (Crutchfield/Hanson school — epsilon-machines, domain filters, local causal states) and MDL theory (Grünwald's framework — two-part codes, NML, parametric complexity).

Please:
1. Write a detailed referee report as if this were a real submission.
2. Rate: novelty, rigor, significance, presentation (1-10 each).
3. Identify every claim that is overstated, underproven, or misleading.
4. Tell me exactly what changes would move this from "reject" to "accept."
5. Are the theorems correctly stated? Are the proofs sufficient or do they need strengthening?
6. Is the NML convergence argument sound? What would make it rigorous?
7. What is the strongest version of this paper that could exist?

After your report, we will iterate — I'll fix what you flag and paste revisions back.

## Known issues from prior review (please help fix, not just re-discover)

A previous automated review (Codex/GPT-5.4, 154k tokens) found three specific problems:

1. **Proposition 2 (convergence) is FALSE as stated.** Counterexample: a period-1 spacetime (all zeros) with defects at every 3rd step (rate 1/3 < 1/2). Period p=3 fits perfectly and wins MDL for all large T, because the defects themselves are periodic. The claim "p* ≤ p0 for large T" fails when defect structure has its own periodicity. Please help me find the correct statement — what convergence guarantee CAN we make?

2. **"NML parametric complexity" is overstated.** The score (k/2) log(T/p) with a run-length residual code is not strict NML in the Grünwald sense. It should be called "MDL-inspired" or "asymptotic parametric penalty." What is the correct MDL-theoretic framing for this criterion?

3. **Monotonicity corollary is too strong.** Theorem 2 is correct for divisibility chains (p1 | p2), but the corollary claiming "defect rate is monotonically non-increasing in period" doesn't hold for arbitrary periods (e.g., p=5 vs p=6). Please help me state this correctly.

---

# PAPER

# Symmetry-Projection Decomposition of Cellular Automaton Spacetimes: Theory, MDL Model Selection, and Persistent Defects in 2D Rules

## Abstract

We develop a rule-agnostic theory for decomposing binary cellular automaton (CA) spacetimes into a nearest relative-periodic background and a structured defect mask. The theory rests on three components: (1) an *orbitwise L1 projection theorem* showing that majority voting over orbit classes yields the unique optimal Hamming approximation in the relative-periodic model class; (2) a *partition-refinement monotonicity result* that formalizes why higher periods always achieve lower defect rates, motivating explicit complexity control; and (3) a *two-part MDL criterion* using NML parametric complexity that selects the simplest adequate periodic model, with period convergence as observation length grows.

Applied to 621 two-dimensional totalistic rules (458 non-trivial), the method produces a quantitative catalog of periodic organization quality. A targeted search identifies three rules with persistent structured defects — verified at 400 steps, across multiple seeds, and at grid sizes up to 192×192 — including one (S37/B11) exhibiting extensive defect scaling.

**Keywords:** cellular automata, minimum description length, symmetry projection, defect decomposition, parametric complexity

---

## 1. Introduction

Cellular automata (CA) generate complex spatiotemporal patterns from simple local rules. Decomposing these patterns into regular and irregular components is a central problem in CA theory.

The computational mechanics program [1,2] builds local epsilon-machine models that identify domains, particles, and their interactions. Redeker [3] formalized particle catalogs via de Bruijn diagrams. Rupe and Crutchfield [4] generalized local causal states to arbitrary dimensions. Shalizi et al. [7] developed automatic coherent-structure filters. These methods build rich local models at significant computational cost.

We develop a complementary *global* approach: project a spacetime onto its nearest relative-periodic field, select the periodicity class by description length, and characterize the residual. The method is intentionally simple — it trades local expressiveness for speed, transparency, and information-theoretic model selection.

### 1.1 Contributions

1. **Formal theorems** characterizing the L1 projection and its properties (Section 2).
2. **NML-based model selection** with proven period convergence properties (Section 2.5).
3. **Quantitative 2D rule survey** and **identification of persistent structured defects** with multi-seed, multi-scale validation (Sections 4–5).

### 1.2 Relationship to Prior Work

| Aspect | Computational Mechanics [1,2,4] | This Work |
|--------|-------------------------------|-----------|
| Model | Local (epsilon-machine) | Global (relative-periodic projection) |
| Selection | Statistical complexity | Two-part MDL (NML) |
| Interactions | Yes (collision catalogs) | No (future work) |
| Cost | Higher | O(n) per model |

Packard and Wolfram [5] surveyed 2D rules qualitatively. Boccara and Roger [6] identified period-2 families. Zenil [8] used compression for CA classification. Our work adds a formal projection theory with MDL model selection.

---

## 2. Theory

### 2.1 Relative-Periodic Model Class

**Definition 1.** Given a binary spacetime $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$, shift vector $\mathbf{s} = (s_1, \ldots, s_n) \in \mathbb{Z}^n$, and period $p \geq 1$, the *relative-periodic model class* $\mathcal{B}(p, \mathbf{s})$ consists of all fields $B$ satisfying:

$$B[t + p, (x_1 + s_1) \bmod D_1, \ldots, (x_n + s_n) \bmod D_n] = B[t, x_1, \ldots, x_n]$$

for all valid indices. This constraint partitions spacetime into *orbit classes* $\{O_j\}_{j=1}^{k}$ where $k = p \prod_i D_i$. Within each class, $B$ is constant.

### 2.2 Orbitwise L1 Projection

**Theorem 1 (Optimal Hamming Projection).** Let $n_j^{(1)} = |\{(t,\mathbf{x}) \in O_j : U[t,\mathbf{x}] = 1\}|$ and $n_j^{(0)} = |O_j| - n_j^{(1)}$. The Hamming distance $d(U, B) = |\{(t,\mathbf{x}) : U[t,\mathbf{x}] \neq B[t,\mathbf{x}]\}|$ is minimized over $\mathcal{B}(p, \mathbf{s})$ by setting:

$$b_j = \begin{cases} 1 & \text{if } n_j^{(1)} > n_j^{(0)} \\ 0 & \text{if } n_j^{(0)} > n_j^{(1)} \\ \text{either} & \text{if } n_j^{(0)} = n_j^{(1)} \end{cases}$$

The minimum defect count is $\sum_j \min(n_j^{(0)}, n_j^{(1)})$. The minimizer is unique iff no orbit class has $n_j^{(0)} = n_j^{(1)}$.

*Proof.* The Hamming distance decomposes additively over orbit classes: $d(U,B) = \sum_j d_j$ where $d_j$ counts disagreements within $O_j$. Since $B$ is constant on each $O_j$, choosing $b_j$ independently minimizes each $d_j = \min(n_j^{(0)}, n_j^{(1)})$. $\square$

**Definition 2.** The *defect mask* is $M = U \oplus B^*$ where $B^*$ is the optimal projection. The *defect rate* is $r = \|M\|_1 / |U|$.

### 2.3 Partition-Refinement Monotonicity

**Theorem 2 (Monotonicity).** If period $p_2$ is a multiple of $p_1$ (i.e., $p_2 = m \cdot p_1$ for integer $m \geq 1$) with the same shift $\mathbf{s}$, then the orbit partition under $p_2$ refines the partition under $p_1$, and:

$$d^*(p_2, \mathbf{s}) \leq d^*(p_1, \mathbf{s})$$

where $d^*$ denotes the optimal Hamming distance.

*Proof.* Each orbit class under $p_1$ splits into $m$ or fewer classes under $p_2$. Independent majority voting on finer classes can only reduce or maintain total disagreements. $\square$

**Corollary.** Along any divisibility chain $p, 2p, 3p, \ldots$, defect rate is monotonically non-increasing. More generally, for a fixed candidate set, the minimum achievable defect rate over all periods $\leq P$ is non-increasing in $P$. This is the *overcapacity problem*: higher periods can always fit at least as well as their divisors, but at the cost of $k = p \prod D_i$ free binary parameters.

### 2.4 Defect-Mask Codelength as Geometric Proxy

**Proposition 1 (Run-Length Separation).** For a fixed flattening order, two binary masks $M_1, M_2$ of the same size with identical Hamming weight $\|M_1\|_1 = \|M_2\|_1$ can have run-length codelengths differing by a factor of $\Omega(\log n)$, where $n$ is the mask size.

*Proof sketch.* A mask of weight $w$ with a single contiguous block has RL codelength $O(\log n)$. A mask of the same weight with $w$ isolated defects has RL codelength $\Omega(w \log(n/w))$. The ratio grows as $\Omega(w) = \Omega(\log n)$ when $w = \Theta(\log n)$. $\square$

This justifies using RL codelength as a geometric quality metric beyond defect rate: it distinguishes spatially organized defects from scattered noise.

### 2.5 Two-Part MDL Model Selection

**Definition 3 (Two-Part Code).** For model $(p, \mathbf{s})$ with $k = p \prod_i D_i$ template parameters, each estimated from $\lfloor T/p \rfloor$ observations by majority vote, the total description length is:

$$\text{MDL}(p, \mathbf{s}) = \underbrace{\frac{k}{2} \log_2 \frac{T}{p}}_{\text{parametric penalty}} + \underbrace{L_{\text{RL}}(M^*)}_{\text{defect encoding}}$$

The first term is the asymptotic parametric complexity for $k$ Bernoulli parameters, each estimated from $\lfloor T/p \rfloor$ observations [9, Ch. 3]. It approximates the NML stochastic complexity but is not exact NML, since the residual code (run-length encoding) is a fixed-order heuristic rather than a normalized maximum likelihood code. We call this an *MDL-motivated* criterion: it inherits the key MDL property that model complexity competes against data fit, without claiming full NML optimality.

**Remark (No general convergence guarantee).** One might hope that $p^*$ converges to the "true" background period $p_0$ as $T \to \infty$. This does *not* hold in general: if the defects themselves have periodic structure (e.g., defects at every $k$-th step), then period $p_0 \cdot k$ absorbs the defects into the template and achieves a lower MDL score for all large $T$. The MDL criterion correctly identifies the period that best describes the *entire* spacetime, not just the "background" — the distinction between background periodicity and defect periodicity is not intrinsic to the data.

**Proposition 2 (Finite-Candidate Stabilization).** Within a fixed candidate set $\{1, \ldots, P_{\max}\}$, the MDL-selected period $p^*$ stabilizes for sufficiently large $T$: there exists $T_0$ such that $p^*(T) = p^*(T_0)$ for all $T > T_0$, provided the empirical per-orbit defect rates converge.

*Proof sketch.* Each new observation length $T$ yields a fresh spacetime and MDL scores, so the scores are not literally continuous functions of $T$. However, under the assumption that empirical per-orbit defect rates converge as $T \to \infty$, the MDL score for each candidate period converges to a well-defined limit (logarithmic penalty growing as $O(\log T)$ plus defect encoding growing as $\Theta(T)$). Since the per-site defect-encoding rates generically differ between candidates, the linear terms eventually dominate, and the ranking stabilizes. $\square$

This is confirmed empirically: for all three persistent-defect rules, the MDL-optimal period stabilizes by $T = 600$ with margins increasing monotonically thereafter (Section 5.3).

**Selection rule.** We scan a grid of $(p, \mathbf{s})$ pairs and select the model minimizing MDL. The model index cost $\log_2(|\text{candidates}|)$ is constant across all models and does not affect selection.

---

## 3. Validation on 1D Elementary CA

ECA rules 30, 54, and 110 on a ring of width 192 for 144 steps, scanning shifts $\pm 6$, periods 1–10.

| Rule | Best $(s, p)$ | Defect Rate | RL Bits | Rule Error |
|------|---------------|-------------|---------|------------|
| 54   | $(0, 8)$      | 20.1%       | 19,840  | 0.111      |
| 110  | $(0, 7)$      | 30.8%       | 25,924  | 0.211      |
| 30   | $(-5, 10)$    | 39.1%       | 30,656  | 0.363      |

The known hierarchy Rule 54 < Rule 110 < Rule 30 [1,2,3] is recovered. The method provides a positive control for the MDL ranking without claiming to recover full domain/particle structure.

**Codelength distinguishes geometry.** Two synthetic masks of size 512, each with 64 defects: clustered (42 RL bits) vs scattered (251 RL bits), a 6× ratio at identical Hamming weight, illustrating Proposition 1.

---

## 4. Survey of 2D Totalistic Rules

### 4.1 Setup

We survey 621 range-threshold totalistic rules on a 48×48 torus (Moore neighborhood, 40 steps, density 0.5, seed 11). A cell survives if $s_{\text{lo}} \leq n \leq s_{\text{hi}}$ and is born if $b_{\text{lo}} \leq n \leq b_{\text{hi}}$, with range widths $\leq 3$. Of 621 candidates, 458 produce non-trivial dynamics.

### 4.2 MDL Ranking

Top rules by MDL score are period-1 (static/fixed-point) patterns — MDL correctly identifies these as the simplest descriptions. Period-2 oscillators (e.g., S14/B11) appear at MDL rank ~20. All top rules have zero shift and zero rule-consistency error.

**Observation.** Nonzero-shift (drifting) periodicity first appears at ~19% defect rate. For this rule family, the shift parameter does not improve decomposition quality — an empirical finding, not a limitation of the theory.

### 4.3 Multi-Seed Robustness

We verified 6 rules across 10 seeds (64×64, 60 steps) with NML period selection:

| Rule | NML Period | Mean Rate | CV | Period Consistent |
|------|-----------|-----------|-----|-------------------|
| S14/B11 | 1 | 0.59% | 8.4% | 10/10 |
| S25/B12 | 2 | 0.56% | 11.4% | 10/10 |
| S66/B36 | 2 | 0.63% | 10.5% | 10/10 |
| S24/B11 | 2 | 2.78% | 9.4% | 10/10 |
| S11/B37 | 4 | 2.71% | 16.2% | 10/10 |
| S37/B11 | 2 | 4.41% | 12.4% | 10/10 |

At 60 steps, NML selects conservative (lower) periods with 100% seed consistency. At longer horizons (T ≥ 400), the NML-optimal period increases for persistent-defect rules as the data justifies more complex models — converging with increasing margins (Section 5.3). This is the expected behavior of principled model selection.

---

## 5. Persistent Structured Defects in 2D Rules

### 5.1 Motivation

The most interesting rules are those with persistent, structured defects — long-lived, spatially localized excitations on periodic backgrounds.

### 5.2 400-Step Verification

We ran 400-step simulations (64×64, seed 11) and measured defect counts in 100-step windows:

| Rule | Window | Mean Defects | Std | Range |
|------|--------|-------------|-----|-------|
| S24/B11 | t=50–100 | 10.8 | 3.5 | [5, 16] |
| S24/B11 | t=300–400 | 10.8 | 3.5 | [5, 16] |
| S11/B37 | t=50–100 | 10.0 | 5.2 | [4, 25] |
| S11/B37 | t=300–400 | 7.1 | 2.0 | [4, 9] |
| S37/B11 | t=50–100 | 28.6 | 4.2 | [21, 37] |
| S37/B11 | t=300–400 | 28.1 | 3.9 | [18, 37] |

All three rules show stable defect populations from t=100 onward. S11/B37 shows initial transient decay that stabilizes. S24/B11 and S37/B11 are stable throughout.

### 5.3 Period Convergence with Observation Length

NML period selection converges as the observation window grows:

| Rule | T=60 | T=100 | T=200 | T=400 | T=600 | T=800 |
|------|------|-------|-------|-------|-------|-------|
| S24/B11 | 2 | 2 | 2 | 4 | 6 | 6 |
| S11/B37 | 4 | 4 | 4 | 4 | 8 | 8 |
| S37/B11 | 2 | 2 | 2 | 6 | 6 | 6 |

Margins between best and runner-up *increase* with T (e.g., S37/B11: 4.6k bits at T=60 → 60k bits at T=800), confirming convergence to a stable period rather than unbounded drift. The converged periods (6, 8, 6) are consistent with the known period subsumption structure: period 6 subsumes periods 1, 2, 3; period 8 subsumes 1, 2, 4.

**Seed consistency at T=600:** S24/B11: 9/10 period 6; S11/B37: 7/10 period 4, 3/10 period 8 (harmonics); S37/B11: 9/10 period 6.

### 5.4 Multi-Seed Size Scaling

5 seeds, grid sizes 32–192, 100 steps:

**S37/B11 — Extensive scaling:**

| Grid | Mean Rate | Late Defects | Defect Density |
|------|-----------|-------------|----------------|
| 32×32 | 3.19% | 8.1 ± 5.2 | 0.008 |
| 64×64 | 3.18% | 40.9 ± 8.8 | 0.010 |
| 96×96 | 3.11% | 101.9 ± 8.0 | 0.011 |
| 128×128 | 3.33% | 196.5 ± 10.6 | 0.012 |
| 192×192 | 3.14% | 428.5 ± 32.4 | 0.012 |

Defect density is approximately constant (~0.01) from 64×64 to 192×192 across 5 seeds, consistent with a bulk (extensive) phenomenon. Late defect count scales linearly with grid area.

**S11/B37 — Sub-extensive scaling:**

| Grid | Mean Rate | Late Defects | Defect Density |
|------|-----------|-------------|----------------|
| 64×64 | 1.81% | 11.1 ± 6.3 | 0.003 |
| 128×128 | 1.58% | 32.7 ± 4.1 | 0.002 |
| 192×192 | 1.69% | 79.5 ± 16.7 | 0.002 |

Defect density slowly decreases, consistent with a fixed or slowly-growing population.

---

## 6. Discussion

### 6.1 What the Theory Provides

The symmetry-projection framework gives:
1. **An optimal decomposition** (Theorem 1) for any binary spacetime and any periodic model class.
2. **A formal explanation** of why naive defect-rate ranking is misleading (Theorem 2), motivating MDL.
3. **A geometric quality metric** (Proposition 1) that distinguishes structured from scattered defects beyond Hamming distance.
4. **Principled model selection** (Definition 3) with convergence properties (Proposition 2).

### 6.2 What It Does Not Provide

The method identifies *where* defects are but not *how* they interact. It does not claim to recover domain/particle structure in the computational mechanics sense [1,2]. The fitted backgrounds are nearest periodic fields, not exact CA orbits — rule-consistency error measures how close the approximation is. Component-level lifetime and interaction analysis is deferred to future work.

### 6.3 Limitations

1. **Run-length codelength is order-dependent** (Section 2.4). It is a geometric proxy under a fixed traversal, not an intrinsic geometric measure.
2. **Shift scanning adds little for this rule family.** All best fits have shift (0,0).
3. **NML period selection is window-dependent** at short horizons (Section 5.3), converging for sufficiently long observations.
4. **Component-level evidence is preliminary.** We show persistent defect mass; component lifetimes and trajectories are future work.

### 6.4 Future Work

1. **Component tracking**: lifetimes, velocities, collision catalogs.
2. **Direct comparison** with local causal states [4] on Rule 54 and 2D rules.
3. **Refined MDL**: normalized maximum likelihood or Bayesian model selection.
4. **Spatial periodicity constraints** to further reduce template capacity.

---

## 7. Conclusion

We have developed a symmetry-projection theory for decomposing CA spacetimes into relative-periodic backgrounds and structured defect masks. The orbitwise L1 projection is provably optimal, partition-refinement monotonicity motivates complexity control, and NML-based two-part coding provides convergent model selection. Applied to 2D totalistic rules, the method identifies three rules with persistent structured defects, including S37/B11 with extensive defect scaling — a candidate for further computational-mechanics analysis.

---

## References

[1] J.P. Crutchfield and J.E. Hanson, "Computational mechanics of cellular automata: An example," *Physica D*, vol. 103, pp. 169–189, 1997.

[2] J.E. Hanson and J.P. Crutchfield, "The attractor-basin portrait of a cellular automaton," *J. Statistical Physics*, vol. 66, pp. 1415–1462, 1992.

[3] M. Redeker, "A language for particle interactions in Rule 54 and other cellular automata," *Complex Systems*, vol. 26, no. 1, pp. 1–32, 2017.

[4] A. Rupe and J.P. Crutchfield, "Local causal states and discrete coherent structures," *Chaos*, vol. 28, 075312, 2018.

[5] N.H. Packard and S. Wolfram, "Two-dimensional cellular automata," *J. Statistical Physics*, vol. 38, pp. 901–946, 1985.

[6] N. Boccara and M. Roger, "Totalistic two-dimensional cellular automata exhibiting global periodic behavior," *Int. J. Modern Physics C*, vol. 10, no. 6, pp. 1051–1066, 1999.

[7] C.R. Shalizi, R. Haslinger, J.-B. Rouquier, K.L. Klinkner, and C. Moore, "Automatic filters for the detection of coherent structure in spatiotemporal systems," *Physical Review E*, vol. 73, 036104, 2006.

[8] H. Zenil, "Compression-based investigation of the dynamical properties of cellular automata and other systems," *Complex Systems*, vol. 19, no. 1, pp. 1–28, 2010.

[9] P. Grünwald, *The Minimum Description Length Principle*, MIT Press, 2007.

---

# SOURCE CODE

## coding.py — MDL scoring with NML parametric complexity

```python
from __future__ import annotations

import math
from typing import Iterable

import lz4.frame
import numpy as np
from scipy.special import gammaln


def log2_binomial(n: int, k: int) -> float:
    """Stable base-2 log of n choose k."""
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 <= k <= n")
    if k == 0 or k == n:
        return 0.0
    return float((gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)) / math.log(2.0))


def combinatorial_repair_bits(total_sites: int, defect_sites: int, alphabet_size: int = 2) -> float:
    """Idealized repair codelength assuming an incompressible defect mask."""
    bits = log2_binomial(int(total_sites), int(defect_sites))
    if alphabet_size > 2:
        bits += defect_sites * math.log2(alphabet_size - 1)
    return float(bits)


def gamma_bits(n: int) -> int:
    """Bit length of Elias-gamma coding, simplified for positive integers."""
    if n <= 1:
        return 1
    return 2 * int(math.floor(math.log2(int(n)))) + 1


def run_length_bits(mask: np.ndarray) -> int:
    """Simple structured-mask proxy based on run-length coding."""
    flat = np.ravel(mask).astype(np.uint8)
    if flat.size == 0:
        return 0
    changes = np.flatnonzero(flat[1:] != flat[:-1]) + 1
    boundaries = np.concatenate(([0], changes, [flat.size]))
    runs = np.diff(boundaries)
    return int(1 + sum(gamma_bits(int(run)) for run in runs))


def lz4_mask_bits(mask: np.ndarray, compression_level: int = 12) -> int:
    """Practical compressor proxy for the defect mask."""
    packed = np.packbits(np.ravel(mask).astype(np.uint8))
    payload = packed.tobytes()
    compressed = lz4.frame.compress(payload, compression_level=compression_level)
    return int(8 * len(compressed))


def template_bits_raw(period: int, spatial_shape: tuple[int, ...]) -> int:
    """Raw template size: period * prod(spatial_shape) free binary values."""
    n = period
    for d in spatial_shape:
        n *= d
    return n


def template_bits_nml(period: int, spatial_shape: tuple[int, ...], steps: int) -> float:
    """Parametric complexity (NML-style) for the background template.

    Each of the k = period * prod(spatial_shape) binary template bits is
    estimated from steps / period observations by majority vote. The
    standard parametric complexity for k Bernoulli parameters, each with
    n_obs samples, is (k / 2) * log2(n_obs). This grows logarithmically
    with observation length T, so model selection stabilizes as T -> inf.
    """
    k = period
    for d in spatial_shape:
        k *= d
    n_obs = max(steps / period, 1)
    return k / 2.0 * math.log2(n_obs)


template_bits = template_bits_raw  # backwards compat alias


def mdl_total_bits(
    period: int,
    spatial_shape: tuple[int, ...],
    steps: int,
    defect_mask: np.ndarray,
    defect_encoding: str = "run_length",
) -> tuple[float, int, float]:
    """Two-part MDL score: NML template complexity + defect encoding cost.

    Returns (template_cost, defect_cost, total).
    """
    t_bits = template_bits_nml(period, spatial_shape, steps)
    if defect_encoding == "run_length":
        d_bits = run_length_bits(defect_mask)
    elif defect_encoding == "lz4":
        d_bits = lz4_mask_bits(defect_mask)
    else:
        raise ValueError(f"Unknown encoding: {defect_encoding}")
    return t_bits, d_bits, t_bits + d_bits
```

## repair_nd.py — Core orbitwise projection algorithm

```python
"""N-dimensional relative-periodic repair for 2D and 3D cellular automata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import ndimage

from .coding import combinatorial_repair_bits, lz4_mask_bits, run_length_bits, template_bits_raw, template_bits_nml


@dataclass(slots=True)
class RelativePeriodicFitND:
    """Relative-periodic fit for an N-dimensional CA spacetime."""
    shift: tuple[int, ...]       # spatial shift vector (one per spatial dim)
    period: int                  # temporal period
    background: np.ndarray
    defect_mask: np.ndarray
    defect_sites: int
    total_sites: int
    defect_rate: float
    combinatorial_bits: float
    run_length_bits: int
    lz4_bits: int
    template_bits: int = 0
    mdl_bits: float = 0           # NML template complexity + run_length_bits
    rule_error: float | None = None

    def to_record(self) -> dict[str, float | int | None]:
        rec: dict[str, float | int | None] = {
            "period": self.period,
        }
        for i, s in enumerate(self.shift):
            rec[f"shift_{i}"] = s
        rec.update({
            "defect_sites": self.defect_sites,
            "total_sites": self.total_sites,
            "defect_rate": self.defect_rate,
            "combinatorial_bits": self.combinatorial_bits,
            "run_length_bits": self.run_length_bits,
            "lz4_bits": self.lz4_bits,
            "template_bits": self.template_bits,
            "mdl_bits": self.mdl_bits,
            "rule_error": self.rule_error,
        })
        return rec


def component_labels_nd(
    shape: tuple[int, ...],
    shift: tuple[int, ...],
    period: int,
) -> np.ndarray:
    """Label each spacetime site by its relative-periodic orbit class.

    shape : (steps, *spatial_dims)
    shift : spatial shift vector (length = number of spatial dims)
    period : temporal period

    The constraint is:
        B[t + p, (x0 + s0) mod D0, (x1 + s1) mod D1, ...] = B[t, x0, x1, ...]
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    steps = shape[0]
    spatial_dims = shape[1:]
    n_spatial = len(spatial_dims)
    if len(shift) != n_spatial:
        raise ValueError(f"shift has {len(shift)} components but spacetime has {n_spatial} spatial dims")

    t = np.arange(steps, dtype=np.int64)
    residue = t % period
    orbit_step = t // period

    coords = np.meshgrid(
        np.arange(steps, dtype=np.int64),
        *[np.arange(d, dtype=np.int64) for d in spatial_dims],
        indexing="ij",
    )
    t_grid = coords[0]
    res_grid = t_grid % period
    ostep_grid = t_grid // period

    label = res_grid.copy()
    multiplier = period
    for i, (dim_size, s) in enumerate(zip(spatial_dims, shift)):
        start = (coords[i + 1] - ostep_grid * s) % dim_size
        label = label + start * multiplier
        multiplier *= dim_size

    return label.astype(np.int32)


def _majority_binary_by_labels_nd(
    spacetime: np.ndarray,
    labels: np.ndarray,
    n_labels: int,
) -> np.ndarray:
    flat_labels = labels.ravel()
    flat_values = spacetime.ravel().astype(np.int64)
    totals = np.bincount(flat_labels, minlength=n_labels)
    ones = np.bincount(flat_labels, weights=flat_values, minlength=n_labels)
    majority_values = (2 * ones >= totals).astype(np.uint8)
    return majority_values[labels]


def fit_relative_periodic_background_nd(
    spacetime: np.ndarray,
    shift: tuple[int, ...],
    period: int,
    *,
    rule_error_fn=None,
) -> RelativePeriodicFitND:
    """Project an N-dimensional binary spacetime onto the nearest relative-periodic background."""
    if spacetime.ndim < 2:
        raise ValueError("spacetime must be at least 2D (time + spatial)")
    if np.any((spacetime != 0) & (spacetime != 1)):
        raise ValueError("spacetime must be binary")

    spatial_dims = spacetime.shape[1:]
    if len(shift) != len(spatial_dims):
        raise ValueError(f"shift has {len(shift)} components but spacetime has {len(spatial_dims)} spatial dims")

    labels = component_labels_nd(spacetime.shape, shift=shift, period=period)
    n_labels = period
    for d in spatial_dims:
        n_labels *= d

    background = _majority_binary_by_labels_nd(spacetime.astype(np.uint8), labels, n_labels)
    defect_mask = spacetime.astype(np.uint8) != background
    defect_sites = int(defect_mask.sum())
    total_sites = int(defect_mask.size)
    rule_error = None if rule_error_fn is None else rule_error_fn(background)

    rl_bits = run_length_bits(defect_mask)
    steps = spacetime.shape[0]
    t_bits_raw = template_bits_raw(period, spatial_dims)
    t_bits_nml = template_bits_nml(period, spatial_dims, steps)
    mdl = t_bits_nml + rl_bits

    return RelativePeriodicFitND(
        shift=tuple(int(s) for s in shift),
        period=int(period),
        background=background.astype(np.uint8),
        defect_mask=defect_mask,
        defect_sites=defect_sites,
        total_sites=total_sites,
        defect_rate=defect_sites / total_sites if total_sites > 0 else 0.0,
        combinatorial_bits=combinatorial_repair_bits(total_sites, defect_sites, alphabet_size=2),
        run_length_bits=rl_bits,
        lz4_bits=lz4_mask_bits(defect_mask),
        template_bits=t_bits_raw,
        mdl_bits=mdl,
        rule_error=rule_error,
    )
```

---

# KEY EXPERIMENTAL DATA

## Period convergence (NML, seed 11, 64×64):
```
S24/B11: T=60→p=2, T=100→p=2, T=200→p=2, T=400→p=4, T=600→p=6(margin 6.9k), T=800→p=6(margin 13.9k)
S11/B37: T=60→p=4, T=100→p=4, T=200→p=4, T=400→p=4, T=600→p=8(margin 2.2k), T=800→p=8(margin 14.3k)
S37/B11: T=60→p=2, T=100→p=2, T=200→p=2, T=400→p=6(margin 14.9k), T=600→p=6(margin 40.8k), T=800→p=6(margin 60.4k)
```

## Seed consistency at T=600 (10 seeds):
```
S24/B11: [6,6,6,2,6,6,6,6,6,6] (9/10 period 6)
S11/B37: [8,4,4,8,4,4,4,4,4,4] (7/10 period 4, 3/10 period 8 — harmonics)
S37/B11: [6,6,6,6,6,6,4,6,6,6] (9/10 period 6)
```

## 400-step verification (seed 11, 64×64):
```
S24/B11: t=50-100: 10.8±3.5, t=300-400: 10.8±3.5 (stable)
S11/B37: t=50-100: 10.0±5.2, t=300-400: 7.1±2.0 (transient → stable)
S37/B11: t=50-100: 28.6±4.2, t=300-400: 28.1±3.9 (stable)
```

## Multi-seed size scaling (5 seeds, 100 steps):
```
S37/B11 defect density: 32→0.008, 64→0.010, 96→0.011, 128→0.012, 192→0.012 (extensive)
S11/B37 defect density: 64→0.003, 128→0.002, 192→0.002 (sub-extensive)
```
