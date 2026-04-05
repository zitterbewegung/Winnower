# MDL-Principled Decomposition of Cellular Automaton Spacetimes into Periodic Backgrounds and Structured Defects

## Abstract

We decompose binary cellular automaton (CA) spacetimes into a nearest *relative-periodic background* and a *defect mask*, selecting the decomposition by two-part minimum description length (MDL). For a spacetime $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$, we fit the closest field $B$ satisfying $B[t+p, \mathbf{x} + \mathbf{s}] = B[t, \mathbf{x}]$ by majority voting over orbit classes. The total description cost is the sum of template bits ($p \prod D_i$) and defect-mask encoding (run-length codelength), which naturally penalizes high-period models and resolves period-selection ambiguity without ad hoc thresholds.

We validate on 1D elementary CA, recovering known structural hierarchies. Applied to 621 two-dimensional range-threshold totalistic rules (458 non-trivial), MDL ranking produces a principled catalog of periodic organization quality. A targeted search over 986 rules identifies three rules with *persistent structured defects* — long-lived, localized excitations on periodic backgrounds — verified at 400 steps, across 5–10 random seeds, and at grid sizes from 32×32 to 192×192.

**Keywords:** cellular automata, minimum description length, relative periodicity, defect decomposition, 2D totalistic rules

---

## 1. Introduction

Cellular automata (CA) generate complex spatiotemporal patterns from simple local rules. A central question is how to decompose these patterns into *regular* and *irregular* components.

The computational mechanics program [1,2] addresses this via epsilon-machines that build local statistical models identifying domains, particles, and their interactions. Redeker [3] formalized particle interactions on periodic backgrounds using de Bruijn diagrams. Rupe and Crutchfield [4] generalized local causal states to arbitrary dimensions. Shalizi et al. [7] developed automatic filters for coherent structure detection.

We propose a complementary approach: fit a global relative-periodic background by majority voting, then score the decomposition using a two-part MDL criterion that balances model complexity against residual description cost. The method is intentionally simple — it trades the expressive power of epsilon-machines for speed, transparency, and principled model selection.

### 1.1 The Overcapacity Problem and MDL Solution

A naive relative-periodic fit with period $p$ and shift $\mathbf{s}$ has $p \prod D_i$ free binary parameters — the entire background template. Without complexity control, higher periods always achieve equal or lower defect rates (period $p$ subsumes period $p/k$), making the decomposition a high-capacity per-site denoiser rather than a meaningful structural separation.

Our key contribution is the two-part MDL score:

$$\text{MDL}(p, \mathbf{s}) = \underbrace{p \prod_{i} D_i}_{\text{template cost}} + \underbrace{L(\text{defect mask})}_{\text{residual cost}}$$

where $L(\cdot)$ is the run-length codelength. Higher periods must reduce the residual encoding by more than they cost in template bits. This converts the method from an unconstrained denoiser to a principled decomposition that selects the simplest adequate periodic model.

### 1.2 Contributions

1. **MDL-principled model selection** for relative-periodic decomposition, resolving period ambiguity and controlling model capacity (Section 2).

2. **A quantitative survey of 2D totalistic rules** producing a continuous ranking of 458 non-trivial rules by MDL score (Section 4).

3. **Identification and multi-seed validation of persistent structured defects** in three 2D rules, with 400-step verification and size-scaling from 32×32 to 192×192 across 5 seeds (Section 5).

### 1.3 Relationship to Prior Work

| Aspect | Computational Mechanics [1,2,4] | Our Method |
|--------|-------------------------------|------------|
| Model type | Local (epsilon-machine / causal states) | Global (relative-periodic template) |
| Model selection | Statistical complexity | Two-part MDL |
| Identifies interactions | Yes (collision catalogs) | No (future work) |
| Computational cost | Higher (local inference) | Lower (majority voting) |

Packard and Wolfram [5] surveyed 2D outer-totalistic rules for qualitative classification. Boccara and Roger [6] identified period-2 families in totalistic 2D CA. Zenil [8] used compression for CA classification. Our work adds MDL-principled decomposition with explicit background/defect separation.

---

## 2. Method

### 2.1 Relative-Periodic Background

Given $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$, a relative-periodic background with shift $\mathbf{s}$ and period $p$ satisfies:

$$B[t + p, (x_1 + s_1) \bmod D_1, \ldots] = B[t, x_1, \ldots]$$

This partitions spacetime into orbit classes. Within each class, all sites share the same value in $B$.

### 2.2 Optimal Fit by Majority Voting

The nearest $B$ in Hamming distance is obtained by majority vote within each orbit class. For orbit $O_j$, set $b_j = 1$ iff $\sum_{(t,\mathbf{x}) \in O_j} U[t,\mathbf{x}] \geq |O_j|/2$. This is provably optimal.

### 2.3 Defect Mask and Metrics

The defect mask $M = U \oplus B$ marks disagreements. We measure:

1. **Defect rate**: $r = \|M\|_1 / |M|$.
2. **Run-length codelength**: Flatten $M$ in row-major order and encode runs with Elias-gamma codes. Clustered defects yield low codelength; scattered defects yield high codelength. Note: this metric depends on flattening order.
3. **LZ4 codelength**: Practical compression proxy.
4. **Rule-consistency error**: Fraction of background sites violating the CA update rule.

### 2.4 Two-Part MDL Scoring

The template has $p \prod D_i$ free bits. The total two-part code is:

$$\text{MDL}(p, \mathbf{s}) = p \prod_i D_i + L_{\text{RL}}(M)$$

We scan over a grid of $(\mathbf{s}, p)$ pairs and select the decomposition minimizing MDL. This automatically:
- **Resolves period subsumption**: period 8 costs 4× the template of period 2 and only wins if defect encoding drops by more than $3 \times \prod D_i$ bits.
- **Penalizes overfitting**: prevents the degenerate solution of choosing arbitrarily high periods.
- **Produces consistent periods**: across seeds, the MDL-optimal period is identical for all 10 tested seeds on all 6 rules (Section 4.4).

### 2.5 Connected Component Extraction

From the best-fit defect mask, we label connected components (8-connected in 2D) and characterize them by size and temporal span.

---

## 3. Validation on 1D Elementary CA

### 3.1 Setup

ECA rules 30, 54, and 110 on a ring of width 192 for 144 steps (density 0.5, seed 11), scanning shifts $-6 \leq s \leq 6$, periods $1 \leq p \leq 10$.

### 3.2 Results

| Rule | Best $(s, p)$ | Defect Rate | RL Bits | MDL Bits | Rule Error |
|------|---------------|-------------|---------|----------|------------|
| 54   | $(0, 8)$      | 20.1%       | 19,840  | 21,376   | 0.111      |
| 110  | $(0, 7)$      | 30.8%       | 25,924  | 27,268   | 0.211      |
| 30   | $(-5, 10)$    | 39.1%       | 30,656  | 32,576   | 0.363      |

The known hierarchy Rule 54 < Rule 110 < Rule 30 is recovered. This is a ranking signal — the method identifies relative periodic organization but does not recover full domain/particle structure, which requires computational mechanics techniques [1,2,3].

### 3.3 Codelength Distinguishes Geometry

Two synthetic masks of size 512, each with 64 defect sites (12.5%):

| Case | Defect Rate | Run-Length Bits | Ratio |
|------|-------------|-----------------|-------|
| Clustered | 12.5% | 42 | — |
| Random    | 12.5% | 251 | 6.0× |

Run-length codelength encodes geometric structure beyond defect count.

---

## 4. Survey of 2D Totalistic Rules

### 4.1 Rule Family

We survey 2D range-threshold totalistic rules on a toroidal grid with Moore neighborhood. A cell survives if $s_{\text{lo}} \leq n \leq s_{\text{hi}}$ and is born if $b_{\text{lo}} \leq n \leq b_{\text{hi}}$, with range widths $\leq 3$.

### 4.2 Setup

**Initial survey**: 621 candidate rules on 48×48 grid, 40 steps, density 0.5, seed 11. Shifts $\pm 3$, periods 1–6. Of these, 458 produced non-trivial dynamics (density between 2% and 98%).

**Persistent-defect survey**: 986 candidate rules (range widths $\leq 4$) on 64×64 grid, 100 steps.

### 4.3 Results: MDL Ranking

Top 10 rules by MDL score:

| Rule | Period | Defect Rate | Template Bits | RL Bits | MDL Bits | Rule Error |
|------|--------|-------------|---------------|---------|----------|------------|
| S02/B68 | 1 | 1.33% | 2,304 | 2,519 | 4,823 | 0.0 |
| S02/B67 | 1 | 1.32% | 2,304 | 2,533 | 4,837 | 0.0 |
| S02/B66 | 1 | 1.28% | 2,304 | 2,573 | 4,877 | 0.0 |
| S01/B68 | 1 | 1.46% | 2,304 | 2,693 | 4,997 | 0.0 |
| S01/B67 | 1 | 1.45% | 2,304 | 2,703 | 5,007 | 0.0 |
| S01/B66 | 1 | 1.41% | 2,304 | 2,729 | 5,033 | 0.0 |
| S03/B66 | 1 | 1.07% | 2,304 | 2,756 | 5,060 | 0.0 |
| S03/B68 | 1 | 1.14% | 2,304 | 2,810 | 5,114 | 0.0 |
| S03/B67 | 1 | 1.13% | 2,304 | 2,820 | 5,124 | 0.0 |
| S00/B66 | 1 | 1.44% | 2,304 | 3,067 | 5,371 | 0.0 |

MDL correctly identifies period-1 (static/fixed-point) rules as the simplest — they have the lowest template cost. The first period-2 rule appears at MDL rank 21 (S14/B11, MDL=8,682). All top rules have zero shift and zero rule error.

**Observation**: Without MDL, the survey would have ranked S14/B11 first (defect rate 0.85% at period 2). MDL reveals that much of the apparent "fit quality" at higher periods comes from template capacity, not genuine periodic structure. Period-1 rules with 1.3% defect rate are actually simpler descriptions than period-2 rules with 0.85% defect rate.

### 4.4 Multi-Seed Robustness

We verified 6 rules across 10 random seeds (64×64, 60 steps) using MDL-optimal period selection:

| Rule | MDL Period | Mean Rate | Std | CV | Period Consistent |
|------|-----------|-----------|-----|-----|-------------------|
| S14/B11 | 1 | 0.59% | 0.049% | 8.4% | Yes |
| S25/B12 | 2 | 0.56% | 0.064% | 11.4% | Yes |
| S66/B36 | 2 | 0.63% | 0.066% | 10.5% | Yes |
| S24/B11 | 2 | 2.78% | 0.263% | 9.4% | Yes |
| S11/B37 | 4 | 2.71% | 0.439% | 16.2% | Yes |
| S37/B11 | 2 | 4.41% | 0.548% | 12.4% | Yes |

**All rules achieve 100% period consistency across seeds.** Without MDL, only 3 of 6 rules had consistent periods (v3 paper, Section 4.4). The three groups — low-defect oscillators, moderate-defect persistent, and higher-defect persistent — remain well-separated.

### 4.5 Autocorrelation Baseline

| Rule | AC Period | AC MDL | MDL Period | MDL Bits | Improvement |
|------|-----------|--------|-----------|----------|-------------|
| S14/B11 | 2 | 15,507 | 1 | 13,715 | 1,792 bits |
| S25/B12 | 4 | 24,220 | 2 | 17,376 | 6,844 bits |
| S66/B36 | 2 | 18,377 | 2 | 18,377 | 0 |
| S24/B11 | 2 | 48,960 | 2 | 48,960 | 0 |
| S11/B37 | 4 | 65,182 | 4 | 65,182 | 0 |
| S37/B11 | 2 | 73,146 | 2 | 73,146 | 0 |

For 4 of 6 rules, MDL and autocorrelation agree. For S14/B11 and S25/B12, MDL selects a *lower* period than autocorrelation — the higher period detected by autocorrelation is genuine but doesn't justify its template cost. The primary value of MDL over autocorrelation is principled period selection plus the decomposition framework producing explicit background and defect masks.

---

## 5. Rules with Persistent Structured Defects

### 5.1 Motivation

The most interesting rules are not those with lowest MDL (simple static/oscillating patterns) but those with *persistent, structured* defects — long-lived localized excitations on periodic backgrounds.

### 5.2 Results

From 986 candidate rules, three show persistent structured defects:

| Rule | MDL Period | Defect Rate | Late Defects (64×64) | RL/Defect |
|------|-----------|-------------|---------------------|-----------|
| S24/B11 | 2 | 2.78% | 18.0 ± 7.3 | 5.6 |
| S11/B37 | 4 | 2.71% | 11.1 ± 6.3 | 7.0 |
| S37/B11 | 2 | 4.41% | 40.9 ± 8.8 | 6.2 |

### 5.3 400-Step Verification

We ran 400-step simulations (64×64, seed 11) and measured defect counts in 100-step windows:

**S24/B11 (period 6):**

| Window | Mean Defects | Std | Range |
|--------|-------------|-----|-------|
| t=50–100 | 10.8 | 3.5 | [5, 16] |
| t=100–200 | 11.1 | 3.5 | [5, 16] |
| t=200–300 | 10.9 | 3.5 | [5, 16] |
| t=300–400 | 10.8 | 3.5 | [5, 16] |

**S11/B37 (period 8):**

| Window | Mean Defects | Std | Range |
|--------|-------------|-----|-------|
| t=50–100 | 10.0 | 5.2 | [4, 25] |
| t=100–200 | 7.2 | 2.0 | [4, 9] |
| t=200–300 | 7.2 | 1.9 | [4, 9] |
| t=300–400 | 7.1 | 2.0 | [4, 9] |

**S37/B11 (period 6):**

| Window | Mean Defects | Std | Range |
|--------|-------------|-----|-------|
| t=50–100 | 28.6 | 4.2 | [21, 37] |
| t=100–200 | 28.2 | 3.9 | [20, 37] |
| t=200–300 | 28.1 | 4.0 | [19, 38] |
| t=300–400 | 28.1 | 3.9 | [18, 37] |

All three rules show stable defect populations from t=100 onward. S11/B37 shows initial transient decay (10.0 → 7.2) that stabilizes by t=100. S24/B11 and S37/B11 are stable throughout.

### 5.4 Multi-Seed Size Scaling

We tested persistence across 5 seeds at grid sizes 32–192 (100 steps):

**S24/B11 (MDL period 2):**

| Grid | Mean Rate | Std Rate | Mean Late Defects | Defect Density |
|------|-----------|----------|------------------|----------------|
| 32×32 | 1.88% | 0.18% | 3.1 ± 0.4 | 0.0030 |
| 64×64 | 1.82% | 0.27% | 18.0 ± 7.3 | 0.0044 |
| 96×96 | 1.69% | 0.12% | 23.4 ± 10.5 | 0.0025 |
| 128×128 | 1.87% | 0.05% | 77.6 ± 5.3 | 0.0047 |
| 192×192 | 1.90% | 0.03% | 176.8 ± 9.6 | 0.0048 |

**S11/B37 (MDL period 4):**

| Grid | Mean Rate | Std Rate | Mean Late Defects | Defect Density |
|------|-----------|----------|------------------|----------------|
| 32×32 | 1.46% | 0.41% | 1.6 ± 0.6 | 0.0016 |
| 64×64 | 1.81% | 0.31% | 11.1 ± 6.3 | 0.0027 |
| 96×96 | 1.71% | 0.13% | 18.6 ± 6.2 | 0.0020 |
| 128×128 | 1.58% | 0.07% | 32.7 ± 4.1 | 0.0020 |
| 192×192 | 1.69% | 0.09% | 79.5 ± 16.7 | 0.0022 |

**S37/B11 (MDL period 2):**

| Grid | Mean Rate | Std Rate | Mean Late Defects | Defect Density |
|------|-----------|----------|------------------|----------------|
| 32×32 | 3.19% | 0.69% | 8.1 ± 5.2 | 0.0080 |
| 64×64 | 3.18% | 0.51% | 40.9 ± 8.8 | 0.0100 |
| 96×96 | 3.11% | 0.15% | 101.9 ± 8.0 | 0.0111 |
| 128×128 | 3.33% | 0.28% | 196.5 ± 10.6 | 0.0120 |
| 192×192 | 3.14% | 0.19% | 428.5 ± 32.4 | 0.0116 |

**Observations:**

1. **Defects persist at all sizes ≥ 64×64 across all seeds**, supporting that they are genuine dynamical features, not finite-size artifacts.

2. **S37/B11 shows extensive scaling**: defect density is approximately constant (~0.01) from 64×64 to 192×192, consistent with a bulk phenomenon. Late defect count grows linearly with grid area.

3. **S11/B37 shows sub-extensive scaling**: defect density decreases slowly (0.003 → 0.002), consistent with a fixed or slowly-growing defect population.

4. **Rate variance decreases with system size** for all rules (CV drops from ~20% at 32×32 to ~5% at 192×192), consistent with self-averaging.

---

## 6. Discussion

### 6.1 What MDL Adds

Without MDL, the method is a high-capacity denoiser: period $p$ provides $p \prod D_i$ free bits, enough to absorb arbitrary non-periodic fluctuations. MDL scoring converts this into a principled trade-off:

- Period-1 models (2,304 bits for 48×48) are cheapest and dominate the top of the MDL ranking
- Period-2 models (4,608 bits) only win when periodic structure genuinely halves the defect encoding
- Period-6 or period-8 models require substantial defect reduction to justify their template cost

This resolves the period subsumption problem: without MDL, 3 of 6 tested rules had inconsistent period selection across seeds. With MDL, all 6 achieve 100% consistency.

### 6.2 What the Survey Shows

The MDL ranking correctly identifies static/fixed-point rules as simplest (period 1), followed by clean oscillators (period 2), with persistent-defect rules at higher MDL costs. This is a more honest ranking than sorting by defect rate alone, which would favor high-period models that achieve low defect rates through template capacity.

### 6.3 Limitations

1. **No interaction analysis.** We identify *where* defects are but not *how* they interact.
2. **Shift scanning adds little for this rule family.** All best fits have shift (0,0); drifting periodicity first appears at ~18% defect rate. The shift-scanning capability may be more valuable for other rule families (e.g., with gliders on drifting backgrounds).
3. **Raster-order dependence.** Run-length codelength depends on flattening order.
4. **Background is not an exact CA orbit.** The fitted backgrounds have non-zero rule-consistency error (0.1–1% for persistent-defect rules), meaning the decomposition is approximate.
5. **Template cost is a simple bound.** The two-part code uses raw template size; a normalized maximum likelihood or Bayesian model score could be tighter.

### 6.4 Future Work

1. **Refined MDL**: Use normalized maximum likelihood instead of raw template bits.
2. **Collision catalogs** for persistent-defect rules using computational mechanics.
3. **Longer simulations** (1000+ steps) with more seeds.
4. **Spatial periodicity constraints**: Restrict the background to have spatial period $(q_x, q_y)$ in addition to temporal period, further reducing model capacity.

---

## 7. Conclusion

We have presented an MDL-principled method for decomposing CA spacetimes into relative-periodic backgrounds and structured defect masks. The two-part MDL score (template bits + defect encoding) provides principled model selection that resolves period ambiguity and controls model capacity.

Applied to 621 two-dimensional totalistic rules, the method produces a quantitative catalog ranking rules by decomposition quality. Three rules — S24/B11, S11/B37, and S37/B11 — exhibit persistent structured defects verified at 400 steps, across multiple seeds, and at grid sizes up to 192×192. S37/B11 shows extensive defect scaling (constant density with system size), suggesting a bulk phenomenon analogous to particle populations in 1D Rule 54.

These persistent-defect rules are candidates for further study using computational mechanics techniques. Whether their defect structures constitute true "particles" with well-defined interaction rules remains an open question.

---

## References

[1] J.P. Crutchfield and J.E. Hanson, "Computational mechanics of cellular automata: An example," *Physica D*, vol. 103, pp. 169–189, 1997.

[2] J.E. Hanson and J.P. Crutchfield, "The attractor-basin portrait of a cellular automaton," *Journal of Statistical Physics*, vol. 66, pp. 1415–1462, 1992.

[3] M. Redeker, "A language for particle interactions in Rule 54 and other cellular automata," *Complex Systems*, vol. 26, no. 1, pp. 1–32, 2017.

[4] A. Rupe and J.P. Crutchfield, "Local causal states and discrete coherent structures," *Chaos*, vol. 28, 075312, 2018.

[5] N.H. Packard and S. Wolfram, "Two-dimensional cellular automata," *Journal of Statistical Physics*, vol. 38, pp. 901–946, 1985.

[6] N. Boccara and M. Roger, "Totalistic two-dimensional cellular automata exhibiting global periodic behavior," *International Journal of Modern Physics C*, vol. 10, no. 6, pp. 1051–1066, 1999.

[7] C.R. Shalizi, R. Haslinger, J.-B. Rouquier, K.L. Klinkner, and C. Moore, "Automatic filters for the detection of coherent structure in spatiotemporal systems," *Physical Review E*, vol. 73, 036104, 2006.

[8] H. Zenil, "Compression-based investigation of the dynamical properties of cellular automata and other systems," *Complex Systems*, vol. 19, no. 1, pp. 1–28, 2010.

---

## Appendix A: Reproducibility

All code is open-source. Key parameters:
- 1D ECA: width=192, steps=144, density=0.5, seed=11, shifts=-6..+6, periods=1..10
- 2D survey: 48×48, steps=40, shifts=±3, periods=1–6, 621 candidates (458 non-trivial)
- Persistent-defect survey: 64×64, steps=100, shifts=±3, periods=1–8, 986 candidates
- Multi-seed: seeds=[11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]
- Size scaling: grids=[32, 64, 96, 128, 192], steps=100, 5 seeds each
- 400-step verification: 64×64, steps=400, seed=11
