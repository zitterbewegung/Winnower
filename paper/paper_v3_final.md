# Approximate Symmetry-Repair Decomposition for Cellular Automata: Method and a Survey of 2D Rules with Persistent Structured Defects

## Abstract

We introduce a method for decomposing cellular automaton (CA) spacetimes into a nearest *relative-periodic background* and a structured *defect mask*. For a binary spacetime field $U[t, \mathbf{x}]$, we fit the closest field $B$ satisfying $B[t+p, \mathbf{x} + \mathbf{s}] = B[t, \mathbf{x}]$ (modulo spatial periodicity) by majority voting over orbit classes, then measure the residual using three complementary metrics: defect rate, run-length codelength, and LZ4 compression. The run-length codelength of the defect mask distinguishes geometrically structured defects from scattered ones even when the Hamming distance is identical.

We validate on 1D elementary cellular automata (Rules 30, 54, 110), recovering known structural hierarchies. We then survey 700+ two-dimensional totalistic rules, identifying rules with sub-1% defect rates and zero rule-consistency error. A targeted search finds rules with *persistent structured defects* — long-lived, localized excitations on periodic backgrounds. Robustness experiments across 10 random seeds (coefficient of variation 8–16%) and size-scaling from 64×64 to 192×192 support the persistence of these defect structures.

**Keywords:** cellular automata, relative periodicity, defect decomposition, codelength, 2D totalistic rules, structured defects

---

## 1. Introduction

Cellular automata (CA) generate complex spatiotemporal patterns from simple local rules. A central question in CA theory is how to decompose these patterns into *regular* (predictable) and *irregular* (informative) components.

The computational mechanics program of Crutchfield and collaborators [1,2] addresses this via epsilon-machines and domain filters, building local statistical models that identify domains, particles, and their interactions. Redeker [3] formalized particle interactions on periodic backgrounds for all 1D CA using de Bruijn diagrams. Rupe and Crutchfield [4] generalized local causal states to arbitrary dimensions. Shalizi et al. [7] developed automatic filters for coherent structure detection.

We propose a complementary approach: fit a global relative-periodic background by majority voting over orbit classes, then characterize the residual using description-length metrics. The method is intentionally simple — it trades the expressive power of epsilon-machines for speed, transparency, and ease of application to new rule families.

Our contributions are:

1. **A codelength-based quality metric** for decomposition: the run-length coding cost of the defect mask, which captures geometric structure that defect rate alone misses (Section 3.3).

2. **A quantitative survey of 2D totalistic rules** using relative-periodic decomposition, producing a continuous ranking of ~460 non-trivial rules by defect rate and codelength (Section 4).

3. **Identification and initial validation of 2D rules with persistent structured defects** — long-lived, localized defect structures on periodic backgrounds — supported by multi-seed and size-scaling experiments (Section 5).

### 1.1 Relationship to Prior Work

Our method should be understood as complementary to, not a replacement for, computational mechanics. Key distinctions:

| Aspect | Computational Mechanics [1,2,4] | Our Method |
|--------|-------------------------------|------------|
| Model type | Local (epsilon-machine / causal states) | Global (relative-periodic template) |
| Quality metric | Statistical complexity | Defect-mask codelength |
| Identifies interactions | Yes (collision catalogs) | No (future work) |
| Computational cost | Higher (local inference) | Lower (majority voting) |

Packard and Wolfram [5] surveyed 2D outer-totalistic rules for qualitative behavioral classification. Boccara and Roger [6] identified period-2 families. Our survey uses quantitative decomposition metrics, producing a continuous ranking rather than discrete classification. We note that our highest-ranked rules (sub-1% defect rate) are primarily Class 2 oscillators — not deep discoveries in themselves — while the more interesting contribution is the persistent-defect family (Section 5).

---

## 2. Method

### 2.1 Relative-Periodic Background

Given a binary spacetime array $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$, a *relative-periodic background* with shift vector $\mathbf{s} = (s_1, \ldots, s_n)$ and temporal period $p$ satisfies:

$$B[t + p, (x_1 + s_1) \bmod D_1, \ldots, (x_n + s_n) \bmod D_n] = B[t, x_1, \ldots, x_n]$$

This constraint partitions all spacetime sites into *orbit classes*. Within each class, all sites in $B$ share the same value.

### 2.2 Fitting by Majority Voting

The nearest relative-periodic background (in Hamming distance) is obtained by majority voting within each orbit class. This is provably optimal: it minimizes the number of disagreeing sites.

### 2.3 Defect Mask and Metrics

The *defect mask* $M = U \oplus B$ marks disagreements. We quantify it using:

1. **Defect rate**: $r = \|M\|_1 / |M|$. Measures closeness of fit.
2. **Run-length codelength**: Flatten $M$ in raster order and encode runs with Elias-gamma codes. Measures *geometric complexity* — clustered defects yield low codelength; scattered defects yield high codelength. *Note*: this metric depends on the raster ordering; we use row-major (C-order) flattening throughout. For spacetimes with strong anisotropy, alternative orderings (e.g., column-major or Hilbert-curve) could yield different values.
3. **LZ4 codelength**: Practical compression proxy.
4. **Rule-consistency error** (when rule is known): fraction of sites where $B$ violates the CA update rule.

### 2.4 Scanning and Selection

We scan over a grid of $(\mathbf{s}, p)$ pairs. The best decomposition is selected by sorting on defect rate (primary) then run-length bits (secondary).

**Period subsumption**: A fit with period $p$ is always at least as good as one with period $p/k$ for integer $k$, since period $p$ subsumes period $p/k$ (e.g., period 8 subsumes periods 1, 2, and 4). When reporting "best period," we report the value achieving the lowest defect rate, which may be a higher harmonic of the fundamental period.

### 2.5 Connected Component Extraction

From the best-fit defect mask, we label connected components with full-connectivity neighborhoods (8-connected in 2D) and characterize them by size, temporal span, and spatial extent.

---

## 3. Validation on 1D Elementary Cellular Automata

### 3.1 Setup

We simulate ECA rules 30, 54, and 110 on a ring of width 192 for 144 steps (density 0.5, seed 11), scanning shifts $-6 \leq s \leq 6$ and periods $1 \leq p \leq 10$.

### 3.2 Results

| Rule | Best $(s, p)$ | Defect Rate | Run-Length Bits | Rule Error |
|------|---------------|-------------|-----------------|------------|
| 54   | $(0, 8)$      | 20.1%       | 19,840          | 0.111      |
| 110  | $(0, 7)$      | 30.8%       | 25,924          | 0.211      |
| 30   | $(-5, 10)$    | 39.1%       | 30,656          | 0.363      |

This confirms the known hierarchy: Rule 54 has clean periodic domains with localized defects; Rule 110 is intermediate; Rule 30 resists periodic decomposition [1,2,3].

### 3.3 Codelength Distinguishes Geometry

Two synthetic defect masks of size 512, each with exactly 64 defect sites (12.5%):

| Case | Defect Rate | Combinatorial Bits | Run-Length Bits | Ratio |
|------|-------------|-------------------|-----------------|-------|
| Clustered | 12.5% | 274.1 | 42 | — |
| Random    | 12.5% | 274.1 | 251 | 6.0× |

The combinatorial bits (count-dependent only) are identical. Run-length bits differ by 6×, demonstrating that codelength encodes geometric information beyond defect count.

---

## 4. Survey of 2D Totalistic Rules

### 4.1 Rule Family

We survey 2D *range-threshold* totalistic rules on a toroidal grid with Moore neighborhood. A cell survives if its neighbor count $n$ satisfies $s_{\text{lo}} \leq n \leq s_{\text{hi}}$, and is born if $b_{\text{lo}} \leq n \leq b_{\text{hi}}$, with range widths $\leq 3$.

### 4.2 Setup

**Initial survey**: 48×48 grid, 40 steps, density 0.5, seed 11. Shifts $\pm 3$, periods 1–6.

**Re-analysis**: Top candidates on 96×96 grid, 80 steps, shifts $\pm 4$, periods 1–8.

### 4.3 Results

Of ~700 rules, 459 produced non-trivial dynamics. Top 10 by defect rate:

| Rule | Shift | Period | Defect Rate | RL Bits | Rule Error |
|------|-------|--------|-------------|---------|------------|
| S14/B11 | (0,0) | 2 | 0.85% | 4,074 | 0.0 |
| S25/B12 | (0,0) | 4 | 0.91% | 4,572 | 0.0 |
| S66/B36 | (0,0) | 2 | 0.98% | 5,518 | 0.0 |
| S67/B36 | (0,0) | 2 | 1.01% | 5,652 | 0.0 |
| S25/B22 | (0,0) | 4 | 1.05% | 5,304 | 0.0 |
| S68/B36 | (0,0) | 6 | 1.06% | 5,848 | 0.0 |
| S03/B66 | (0,0) | 1 | 1.07% | 2,756 | 0.0 |
| S03/B67 | (0,0) | 1 | 1.13% | 2,820 | 0.0 |
| S14/B66 | (0,0) | 6 | 1.13% | 4,382 | 0.0 |
| S25/B11 | (0,0) | 6 | 1.14% | 6,768 | 0.001 |

All top rules have zero shift and zero rule error. These are primarily Class 2 oscillators — the decomposition correctly identifies them as near-perfect periodic systems. Drifting periodicity (nonzero shift) first appears at ~18% defect rate.

### 4.4 Multi-Seed Robustness

We verified the top 6 rules across 10 random seeds (width=64, height=64, 60 steps):

| Rule | Mean Rate | Std | CV |
|------|-----------|-----|-----|
| S14/B11 | 0.54% | 0.046% | 8.4% |
| S25/B12 | 0.54% | 0.064% | 12.0% |
| S66/B36 | 0.63% | 0.066% | 10.5% |
| S24/B11 | 2.57% | 0.231% | 9.0% |
| S11/B37 | 2.66% | 0.436% | 16.4% |
| S37/B11 | 4.15% | 0.547% | 13.2% |

All rules produce non-trivial dynamics for every seed. The three groups — low-defect oscillators (S14/B11, S25/B12, S66/B36), moderate-defect persistent (S24/B11, S11/B37), and higher-defect persistent (S37/B11) — remain well-separated across seeds, though orderings *within* each group can swap. For example, S14/B11 and S25/B12 trade first and second place depending on the seed. Coefficients of variation are under 17% for all rules.

The best-fit period can vary across seeds due to period subsumption (Section 2.4): e.g., S25/B12 sometimes selects period 2 instead of 4 when a higher harmonic achieves slightly lower defect rate.

---

## 5. Rules with Persistent Structured Defects

### 5.1 Motivation

The most interesting rules are not those with lowest defect rates (simple oscillators) but those with *persistent, structured* defects. We target rules where:
- Defect rate is 0.5–30%
- Late-time defect count >10 per frame
- Low run-length bits per defect site (spatially organized)

### 5.2 Results

From 202 rules with persistent defects, the top candidates:

| Rule | Defect Rate | Best Period | Late Defects | RL/Defect |
|------|-------------|--------|--------------------|-----------|
| S24/B11 | 1.72% | 6 | 10.8 ± 3.5 | 5.6 |
| S47/B66 | 2.82% | 6 | 25.4 ± 9.7 | 3.6 |
| S11/B37 | 2.12% | 4* | 23.1 ± 3.7 | 7.0 |
| S37/B11 | 2.80% | 6 | 28.8 ± 4.7 | 6.2 |

*S11/B37 achieves its best fit at period 4 in the initial 64×64 survey but at period 8 in larger-grid and multi-seed experiments, consistent with period subsumption (Section 2.4). We treat both as valid representations of the same underlying periodicity.

### 5.3 Size Scaling

We tested whether persistent defects remain present at larger grid sizes (32–192, 100 steps, seed 11). This is a single-seed experiment and should be interpreted as suggestive rather than definitive.

**S24/B11:**

| Grid | Defect Rate | Late Defects | Defect Density |
|------|-------------|-------------|----------------|
| 32×32 | 1.95% | 2.8 ± 1.2 | 0.0028 |
| 64×64 | 1.72% | 10.8 ± 3.5 | 0.0026 |
| 96×96 | 1.63% | 14.2 ± 2.7 | 0.0015 |
| 128×128 | 1.66% | 31.6 ± 8.1 | 0.0019 |
| 192×192 | 1.68% | 76.4 ± 11.0 | 0.0021 |

**S11/B37:**

| Grid | Defect Rate | Late Defects | Defect Density |
|------|-------------|-------------|----------------|
| 32×32 | 2.03% | 0.7 ± 0.5 | 0.0006 |
| 64×64 | 2.01% | 17.1 ± 3.2 | 0.0042 |
| 96×96 | 1.71% | 20.2 ± 3.4 | 0.0022 |
| 128×128 | 1.60% | 22.0 ± 3.9 | 0.0013 |
| 192×192 | 1.47% | 37.2 ± 5.1 | 0.0010 |

**S37/B11:**

| Grid | Defect Rate | Late Defects | Defect Density |
|------|-------------|-------------|----------------|
| 32×32 | 2.62% | 2.8 ± 1.5 | 0.0027 |
| 64×64 | 2.80% | 28.8 ± 4.7 | 0.0070 |
| 96×96 | 2.51% | 60.1 ± 8.9 | 0.0065 |
| 128×128 | 2.62% | 127.6 ± 12.5 | 0.0078 |
| 192×192 | 2.56% | 265.6 ± 26.6 | 0.0072 |

**Observations:**

1. **Defects persist at all sizes ≥ 64×64**, consistent with them being a genuine feature of the dynamics rather than a finite-size artifact. At 32×32, defect counts fall below our detection threshold, suggesting a minimum system size is needed.

2. **Defect density varies across rules.** For S37/B11, late-time defect density is approximately constant (~0.007) across grid sizes from 64 to 192, consistent with an extensive (bulk) phenomenon. For S11/B37, defect density decreases with system size (0.004 → 0.001), which could indicate a fixed or slowly-growing defect population. However, drawing firm conclusions about asymptotic scaling behavior requires multi-seed experiments at each size and longer simulation times, which we leave to future work.

3. **Independent verification at 400 steps** (not shown in detail) confirms that late-time defect counts remain stable rather than continuing to decay, supporting the claim that these are genuinely persistent rather than slowly-transient defects.

### 5.4 Autocorrelation Baseline

We compared our period-scanning method against simple temporal autocorrelation:

| Rule | AC Period | AC Rate | Our Period | Our Rate | Improvement |
|------|-----------|---------|-----------|----------|-------------|
| S14/B11 | 2 | 0.58% | 2 | 0.58% | 0% |
| S25/B12 | 4 | 0.56% | 4 | 0.56% | 0% |
| S66/B36 | 2 | 0.65% | 2 | 0.65% | 0% |
| S24/B11 | 2 | 2.96% | 6 | 2.70% | 8.7% |
| S11/B37 | 4 | 3.09% | 8 | 2.99% | 3.2% |
| S37/B11 | 2 | 4.38% | 6 | 4.12% | 5.9% |

For simple oscillators (top 3), autocorrelation finds the same period — our method adds nothing beyond what a standard spectral analysis would reveal. For persistent-defect rules (bottom 3), period scanning finds *higher harmonics* that yield 3–9% better fits. The shift scanning does not help for these particular rules (all best shifts are (0,0)), though it may be relevant for other rule families not explored here.

**Interpretation**: The primary value of our approach over autocorrelation is not in period detection *per se* but in the *decomposition framework*: producing an explicit background and defect mask, with the codelength metric providing a geometric quality measure.

---

## 6. Discussion

### 6.1 What This Method Is

The relative-periodic fitting method is a lightweight computational heuristic, not a theoretical advance over computational mechanics. Its strengths are:
- **Speed**: majority voting is O(n) per (shift, period) pair
- **Transparency**: the decomposition is immediately interpretable
- **Generality**: works on any binary spacetime without rule knowledge

Its main limitation is that it provides no mechanism for understanding defect *interactions* — a key strength of the computational mechanics framework [1,2].

### 6.2 What the 2D Survey Shows

The top-ranked rules by defect rate are Class 2 oscillators — this is expected, not surprising. The genuine finding is the persistent-defect family (Section 5), where:
- Defects are a stable, non-transient feature (verified at 400 steps)
- They persist across multiple grid sizes (64–192)
- Different rules show qualitatively different defect density scaling

We are careful not to call these "particles" in the Crutchfield/Redeker sense, which implies a full interaction theory. What we have shown is that certain 2D rules produce *candidate particle-like defect structures* — long-lived, spatially localized, and geometrically organized — which merit further investigation using computational mechanics techniques.

### 6.3 Limitations

1. **No interaction analysis.** We identify *where* defects are but not *how* they interact.
2. **Single seed for scaling.** Multi-seed size-scaling would strengthen the evidence.
3. **Raster-order dependence.** The run-length metric depends on flattening order (Section 2.3).
4. **Period subsumption.** The "best period" is not always unique; higher harmonics can achieve marginally better fits.

### 6.4 Future Work

1. **Collision catalogs** for persistent-defect rules
2. **Direct comparison** with local causal states [4] on Rule 54 and the 2D rules
3. **Multi-seed size scaling** with longer simulations (1000+ steps)
4. **Theoretical analysis** of why certain rules support persistent defects

---

## 7. Conclusion

We have presented a simple method for decomposing CA spacetimes into relative-periodic backgrounds and structured defect masks, with defect-mask codelength as a quality metric. The method recovers known 1D ECA structure and, applied to ~700 2D totalistic rules, produces a quantitative catalog of periodic organization quality.

The main empirical contribution is the identification and initial validation of 2D rules with persistent structured defects — most notably S24/B11, S11/B37, and S37/B11 — which exhibit long-lived, localized defect structures on periodic backgrounds. Size-scaling experiments are consistent with these being genuine features of the dynamics rather than finite-size artifacts, and independent 400-step runs confirm that defect populations stabilize rather than decay.

These persistent-defect rules are candidates for further study using computational mechanics techniques to characterize defect interactions and dynamics. Whether these structures constitute true "particles" in the Crutchfield/Redeker sense — with well-defined interaction rules and conservation laws — remains an open question.

---

## References

[1] J.P. Crutchfield and J.E. Hanson, "Computational mechanics of cellular automata: An example," *Physica D*, vol. 103, pp. 169–189, 1997.

[2] J.E. Hanson and J.P. Crutchfield, "The attractor-basin portrait of a cellular automaton," *Journal of Statistical Physics*, vol. 66, pp. 1415–1462, 1992.

[3] M. Redeker, "A language for particle interactions in Rule 54 and other cellular automata," *Complex Systems*, vol. 26, no. 1, pp. 1–32, 2017.

[4] A. Rupe and J.P. Crutchfield, "Local causal states and discrete coherent structures," *Chaos*, vol. 28, 075312, 2018.

[5] N.H. Packard and S. Wolfram, "Two-dimensional cellular automata," *Journal of Statistical Physics*, vol. 38, pp. 901–946, 1985.

[6] N. Boccara and M. Roger, "Some properties of local and nonlocal site exchange deterministic cellular automata," *International Journal of Modern Physics C*, vol. 10, pp. 1439–1470, 1999.

[7] C.R. Shalizi, R. Haslinger, J.-B. Rouquier, K.L. Klinkner, and C. Moore, "Automatic filters for the detection of coherent structure in spatiotemporal systems," *Physical Review E*, vol. 73, 036104, 2006.

---

## Appendix A: Reproducibility

All experiments use the open-source code at [repository URL]. Key parameters:
- 1D ECA: width=192, steps=144, density=0.5, seed=11, shifts=-6..+6, periods=1..10
- 2D survey: 48×48, steps=40, shifts=±3, periods=1–6
- Persistent defects: 64×64 (survey), 128×128 (detailed), 100–120 steps
- Multi-seed: seeds=[11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]
- Size scaling: grids=[32, 64, 96, 128, 192], steps=100, seed=11

## Appendix B: Full 2D Survey Data

The complete survey of 459 non-trivial rules with all metrics is available as supplementary CSV data.
