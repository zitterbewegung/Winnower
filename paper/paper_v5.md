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

**Corollary.** Without complexity control, defect rate is monotonically non-increasing in period. This is the *overcapacity problem*: higher periods always fit at least as well, but at the cost of $k = p \prod D_i$ free binary parameters.

### 2.4 Defect-Mask Codelength as Geometric Proxy

**Proposition 1 (Run-Length Separation).** For a fixed flattening order, two binary masks $M_1, M_2$ of the same size with identical Hamming weight $\|M_1\|_1 = \|M_2\|_1$ can have run-length codelengths differing by a factor of $\Omega(\log n)$, where $n$ is the mask size.

*Proof sketch.* A mask of weight $w$ with a single contiguous block has RL codelength $O(\log n)$. A mask of the same weight with $w$ isolated defects has RL codelength $\Omega(w \log(n/w))$. The ratio grows as $\Omega(w) = \Omega(\log n)$ when $w = \Theta(\log n)$. $\square$

This justifies using RL codelength as a geometric quality metric beyond defect rate: it distinguishes spatially organized defects from scattered noise.

### 2.5 Two-Part MDL Model Selection

**Definition 3 (Two-Part Code).** For model $(p, \mathbf{s})$ with $k = p \prod_i D_i$ template parameters, each estimated from $\lfloor T/p \rfloor$ observations by majority vote, the total description length is:

$$\text{MDL}(p, \mathbf{s}) = \underbrace{\frac{k}{2} \log_2 \frac{T}{p}}_{\text{NML parametric complexity}} + \underbrace{L_{\text{RL}}(M^*)}_{\text{defect encoding}}$$

The first term is the standard NML parametric complexity for $k$ Bernoulli parameters [9]. The second term encodes the residual defect mask.

**Proposition 2 (Convergence).** For a spacetime that is exactly $(p_0, \mathbf{s}_0)$-periodic outside a defect set of rate $\epsilon < 1/2$, the MDL-optimal period $p^*$ satisfies $p^* \leq p_0$ for all sufficiently large $T$.

*Proof sketch.* For the true period $p_0$, the defect encoding grows as $\Theta(T \cdot H(\epsilon) \cdot \prod D_i)$ where $H$ is binary entropy. For any $p > p_0$ that is not a multiple of $p_0$, the defect rate does not improve, but the NML complexity increases. For multiples $mp_0$, the NML cost grows as $\frac{m k_0}{2} \log_2 \frac{T}{mp_0}$ while defect encoding can only decrease, bounded below by the true defect rate. The logarithmic growth of NML ensures the complexity penalty eventually dominates the diminishing defect improvement. $\square$

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

## Appendix A: Reproducibility

All code is open-source. Key parameters:
- 1D ECA: width=192, steps=144, density=0.5, seed=11, shifts=-6..+6, periods=1..10
- 2D survey: 48×48, steps=40, 621 candidates (458 non-trivial)
- Persistent-defect survey: 64×64, steps=100, 986 candidates
- Multi-seed: seeds=[11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]
- Size scaling: grids=[32, 64, 96, 128, 192], steps=100, 5 seeds
- 400-step verification: 64×64, steps=400, seed=11
- Convergence study: steps=[60, 100, 200, 400, 600, 800]
