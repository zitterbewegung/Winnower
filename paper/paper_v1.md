# Approximate Symmetry-Repair Decomposition for Cellular Automata: Method and a Survey of 2D Rules with Persistent Structured Defects

## Abstract

We introduce a method for decomposing cellular automaton (CA) spacetimes into a nearest *relative-periodic background* and a structured *defect mask*. For a binary spacetime field $U[t, \mathbf{x}]$, we fit the closest field $B$ satisfying $B[t+p, \mathbf{x} + \mathbf{s}] = B[t, \mathbf{x}]$ (modulo spatial periodicity) by majority voting over orbit classes, then measure the residual using three complementary metrics: defect rate, run-length codelength, and LZ4 compression. The run-length codelength of the defect mask distinguishes geometrically structured defects from scattered ones even when the Hamming distance is identical — a property that neither defect rate nor standard compressors capture as cleanly.

We validate on 1D elementary cellular automata (Rules 30, 54, 110), recovering known structural hierarchies. We then conduct a systematic survey of 700+ two-dimensional totalistic (range-threshold) rules, scanning over shift vectors and temporal periods. We identify rules with sub-1% defect rates and zero rule-consistency error, as well as a family of rules exhibiting *persistent structured defects* — long-lived, localized excitations on a near-perfect periodic background, constituting 2D analogues of Rule 54's well-known particle-like dynamics.

**Keywords:** cellular automata, relative periodicity, defect decomposition, codelength, 2D totalistic rules, structured defects

---

## 1. Introduction

Cellular automata (CA) generate complex spatiotemporal patterns from simple local rules. A central question in CA theory is how to decompose these patterns into *regular* (predictable) and *irregular* (informative) components. The computational mechanics program of Crutchfield and collaborators [1,2] addresses this via epsilon-machines and domain filters, building local statistical models that identify domains, particles, and their interactions. Redeker [3] formalized particle interactions on periodic backgrounds for all 1D CA using de Bruijn diagrams.

These approaches are powerful but methodologically specialized: epsilon-machines require inferring local causal states from spacetime statistics, and de Bruijn methods require explicit knowledge of the update rule. We propose a complementary approach that is simpler and more direct: fit a global relative-periodic background by majority voting, then analyze the residual.

Our contributions are:

1. **A description-length metric for decomposition quality.** We show that the run-length codelength of the defect mask captures geometric structure that defect rate alone misses. Two decompositions with identical defect counts can have 6x different codelengths depending on whether defects are clustered or scattered (Section 3.3).

2. **A systematic survey of 2D totalistic rules.** We scan ~700 rules defined by survival and birth count thresholds, fitting relative-periodic backgrounds with 2D shift vectors. We catalog rules by defect rate, identifying sub-1% cases and characterizing their periodic structure (Section 4).

3. **Identification of 2D rules with persistent structured defects.** We find rules where defect populations stabilize at nonzero levels with spatially localized, long-lived structures — 2D analogues of the particle-like excitations known from Rule 54 (Section 5).

### 1.1 Relationship to Prior Work

Our method should be understood as complementary to, not a replacement for, computational mechanics. Table 1 summarizes the key differences.

| Aspect | Computational Mechanics [1,2] | Our Method |
|--------|-------------------------------|------------|
| Model type | Local (epsilon-machine) | Global (relative-periodic) |
| Requires rule knowledge | No (behavior-driven) | No (behavior-driven) |
| Output | Causal states, domains, particles | Background + defect mask |
| Quality metric | Statistical complexity | Defect-mask codelength |
| Dimensionality | Generalized to d-D [4] | Generalized to d-D |
| Identifies interactions | Yes (collision catalogs) | No (future work) |

Rupe and Crutchfield [4] generalized local causal states to arbitrary dimensions. Our N-dimensional generalization is thus not novel in concept but differs in mechanism: we fit a single global periodic template rather than inferring local statistical models.

Packard and Wolfram [5] surveyed 2D outer-totalistic rules for qualitative behavioral classification. Boccara and Roger [6] identified period-2 families. Our survey differs in using quantitative relative-periodic decomposition with codelength metrics, producing a continuous ranking rather than a discrete classification.

---

## 2. Method

### 2.1 Relative-Periodic Background

Given a binary spacetime array $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$ (time $\times$ spatial dimensions), a *relative-periodic background* with shift vector $\mathbf{s} = (s_1, \ldots, s_n)$ and temporal period $p$ satisfies:

$$B[t + p, (x_1 + s_1) \bmod D_1, \ldots, (x_n + s_n) \bmod D_n] = B[t, x_1, \ldots, x_n]$$

for all valid $t$. This constraint partitions all spacetime sites into *orbit classes*: sites related by repeated application of the shift-and-advance operation. Within each orbit class, all sites in $B$ must share the same value.

### 2.2 Fitting by Majority Voting

The nearest relative-periodic background (in Hamming distance) is obtained by majority voting within each orbit class:

$$B[\text{site}] = \begin{cases} 1 & \text{if } \sum_{\text{orbit}} U[\text{site}'] \geq |\text{orbit}|/2 \\ 0 & \text{otherwise} \end{cases}$$

This is optimal: it minimizes the number of sites where $U \neq B$.

### 2.3 Defect Mask and Metrics

The *defect mask* $M = U \oplus B$ marks all sites where the source disagrees with the fitted background. We quantify the decomposition using three metrics:

1. **Defect rate**: $r = |M|_1 / |M|$, the fraction of defect sites. Measures closeness of fit.

2. **Run-length codelength**: We flatten $M$ and encode it as a sequence of runs using Elias-gamma codes for run lengths. This measures the *geometric complexity* of the defect pattern — clustered defects produce long runs and low codelength; scattered defects produce short runs and high codelength.

3. **LZ4 codelength**: Practical compression of the bit-packed defect mask. Serves as a cross-check on run-length coding.

Additionally, when the CA rule is known, we compute a **rule-consistency error**: the fraction of sites where the fitted background $B$ violates the local update rule. A background with zero rule error is dynamically consistent — it could be a true CA orbit.

### 2.4 Scanning

We scan over a grid of $(\mathbf{s}, p)$ pairs and report the full *symmetry-defect spectrum*: a table of all metrics for each parameter combination. The best decomposition is selected by sorting on defect rate (primary) then run-length bits (secondary).

### 2.5 Connected Component Extraction

From the best-fit defect mask, we extract connected components using full-connectivity neighborhood labeling (8-connected in 2D, 26-connected in 3D). Components are characterized by their size, temporal span, and spatial extent.

---

## 3. Validation on 1D Elementary Cellular Automata

### 3.1 Setup

We simulate three well-studied ECA rules (30, 54, 110) on a ring of width 192 for 144 steps from random initial conditions (density 0.5, seed 11). We scan shifts $-6 \leq s \leq 6$ and periods $1 \leq p \leq 10$.

### 3.2 Results

| Rule | Best $(s, p)$ | Defect Rate | Run-Length Bits | Rule Error |
|------|---------------|-------------|-----------------|------------|
| 54   | $(0, 8)$      | 20.1%       | 19,840          | 0.111      |
| 110  | $(0, 7)$      | 30.8%       | 25,924          | 0.211      |
| 30   | $(-5, 10)$    | 39.1%       | 30,656          | 0.363      |

These results confirm the known structural hierarchy: Rule 54 has the cleanest periodic organization with well-localized particle-like defects; Rule 110 shows intermediate organization; Rule 30 resists periodic decomposition. The defect-rate spectrum for Rule 54 shows a sharp minimum, while Rule 30's spectrum is relatively flat — consistent with the computational mechanics characterization of Rule 54 as having well-defined domains and Rule 30 as lacking them [1,2].

### 3.3 Codelength Distinguishes Geometry

To demonstrate that defect rate alone is insufficient, we construct two synthetic defect masks of size 512 with exactly 64 defect sites (12.5% defect rate):
- **Clustered**: defects concentrated in a single contiguous block
- **Random**: defects scattered uniformly at random

| Case | Defect Sites | Defect Rate | Combinatorial Bits | Run-Length Bits |
|------|-------------|-------------|-------------------|-----------------|
| Clustered | 64 | 12.5% | 274.1 | 42 |
| Random    | 64 | 12.5% | 274.1 | 251 |

The combinatorial bits (which depend only on count) are identical. The run-length bits differ by a factor of 6x. This illustrates why codelength is a more informative metric than defect rate for evaluating decomposition quality.

---

## 4. Survey of 2D Totalistic Rules

### 4.1 Rule Family

We survey 2D *range-threshold* totalistic rules on a toroidal grid with Moore neighborhood (8 neighbors). A cell survives if its neighbor count $n$ satisfies $s_{\text{lo}} \leq n \leq s_{\text{hi}}$, and a dead cell is born if $b_{\text{lo}} \leq n \leq b_{\text{hi}}$. This yields a 4-parameter family $(s_{\text{lo}}, s_{\text{hi}}, b_{\text{lo}}, b_{\text{hi}})$ with $0 \leq s_{\text{lo}} \leq s_{\text{hi}} \leq 8$ and $1 \leq b_{\text{lo}} \leq b_{\text{hi}} \leq 8$.

We restrict to cases where the range width $\leq 3$ (i.e., $s_{\text{hi}} - s_{\text{lo}} \leq 3$ and $b_{\text{hi}} - b_{\text{lo}} \leq 3$), yielding ~700 candidate rules.

### 4.2 Experimental Setup

**Initial survey** (Section 4.3): 48×48 grid, 40 steps, density 0.5, seed 11. Shifts $\pm 3$, periods 1–6. Rules producing trivial end states (density <2% or >98%) are excluded.

**Detailed analysis** (Section 4.4): Top candidates re-analyzed on 96×96 grid, 80 steps, with shifts $\pm 4$ and periods 1–8.

### 4.3 Survey Results

Of ~700 rules scanned, 459 produced non-trivial dynamics. The top 10 by defect rate:

| Rule | Best Shift | Period | Defect Rate | Run-Length Bits | Rule Error |
|------|-----------|--------|-------------|-----------------|------------|
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

**Key findings:**

1. **All top rules have zero or near-zero rule error**, meaning the fitted backgrounds are dynamically consistent — they could be actual CA orbits.

2. **All top rules have zero shift**, indicating static (non-drifting) periodic structure. Drifting periodicity (nonzero shift) first appears at much higher defect rates (~18%).

3. **Periods are small** (1, 2, 4, or 6), suggesting these rules settle into simple oscillatory regimes.

4. The best rule, **S14/B11** (survive with 1–4 neighbors, born with exactly 1 neighbor), achieves a remarkable 0.85% defect rate with period 2.

### 4.4 Characterization of Top Rules

The low defect rates of top rules arise because these rules rapidly settle into near-perfect periodic patterns with only sparse, localized violations. The period-1 rules (e.g., S03/B66) reach a fixed point; period-2 rules (e.g., S14/B11) produce a global oscillation. These are primarily Wolfram Class 2 behaviors — orderly but not complex.

---

## 5. Rules with Persistent Structured Defects

### 5.1 Motivation

The most scientifically interesting rules are not those with the *lowest* defect rates (which tend to be simple oscillators) but those with *persistent, structured* defects — analogous to Rule 54's particles. We conducted a targeted survey for rules where:

- Defect rate is between 0.5% and 30% (not trivially low or high)
- Late-time defect count remains above 10 per frame (defects persist, not just transient)
- Defect run-length bits per defect site is low (defects are spatially organized, not scattered)

### 5.2 Setup

We simulated on 64×64 grids for 100 steps, then re-analyzed top candidates on 128×128 grids for 120 steps with shifts $\pm 4$ and periods 1–8.

### 5.3 Results

We found 202 rules with persistent defects. The top candidates ranked by a combined score (defect rate × run-length bits per defect site):

| Rule | Defect Rate | Period | Late Defects/Frame | Late Std | RL/Defect |
|------|-------------|--------|--------------------|----------|-----------|
| S24/B11 | 1.72% | 6 | 10.8 ± 3.5 | 3.5 | 5.6 |
| S47/B66 | 2.82% | 6 | 25.4 ± 9.7 | 9.7 | 3.6 |
| S11/B37 | 2.12% | 4 | 23.1 ± 3.7 | 3.7 | 7.0 |
| S01/B37 | 2.19% | 4 | 22.0 ± 3.7 | 3.7 | 6.8 |
| S37/B11 | 2.80% | 6 | 28.8 ± 4.7 | 4.7 | 6.2 |

**Key observations:**

1. **Defects persist stably.** For S24/B11, the defect count drops from ~130 (early transient) to ~11 (late steady state) but does not decay to zero. The late-time standard deviation is small (~3.5), indicating a stable population.

2. **Defects are spatially localized.** The low run-length-per-defect ratios indicate clustered, organized defect structures rather than uniform noise.

3. **Long-lived components exist.** Connected component analysis on the 128×128 runs reveals defect components spanning more than 1/3 of the total simulation time.

4. **These are 2D analogues of Rule 54 particles.** Like Rule 54's gliders and domain walls, these defect structures represent localized excitations propagating on an otherwise periodic background.

### 5.4 Detailed Analysis: S24/B11

S24/B11 (survive with 2–4 neighbors, born with exactly 1 neighbor) is the most interesting candidate. On a 128×128 grid for 120 steps:

- Best fit: shift=(0,0), period=6
- Defect rate: 1.72% (1,410 defect sites out of ~82,000 total)
- Rule error: 0.0 (background is dynamically consistent)
- Early defects: ~130 per frame (transient)
- Late defects: ~11 per frame (steady state), std ~3.5
- Long-lived defect components spanning >40 time steps

The defect mask evolution shows defects coalescing from an initial diffuse distribution into a small number of persistent, compact structures that maintain their integrity over many time steps.

---

## 6. Discussion

### 6.1 When Is This Method Appropriate?

The relative-periodic fitting method works best for CA that exhibit clear periodic domains — Wolfram Class 2 and the "edge of chaos" regime (Class 4, like Rule 110 and Rule 54). For strongly chaotic rules (Class 3, like Rule 30), the method still produces valid decompositions but the defect masks are diffuse and uninformative, consistent with the absence of clean periodic domains.

### 6.2 Limitations

1. **No interaction analysis.** Unlike computational mechanics [1,2] or Redeker's formalism [3], we do not catalog particle interactions or collisions. The defect mask identifies *where* defects are, but not *what* they do when they meet.

2. **Majority voting is approximate.** Our fitted background is the nearest field satisfying the periodic constraint, but it may not be the *unique* or *best* periodic background in a dynamical sense. Computational mechanics' epsilon-machines identify domains based on local predictive equivalence, which can be more principled.

3. **Single seed.** Our surveys use a single random seed. While the qualitative findings (which rules produce low defect rates) are robust, quantitative defect rates can vary across seeds and system sizes. A production study should average over multiple seeds.

4. **Grid size effects.** Small grids (48×48 in the initial survey) may introduce finite-size artifacts. The top candidates were re-analyzed at 128×128, but a systematic size-scaling study would strengthen the results.

### 6.3 Future Work

1. **Benchmark against computational mechanics.** A direct comparison of our decomposition with Hanson-Crutchfield domain filters on Rule 54 would clarify whether the methods identify the same structures.

2. **Collision catalogs for 2D particles.** For rules like S24/B11, systematically catalog defect interactions: do they scatter, annihilate, or produce new defects?

3. **Spectral/autocorrelation baselines.** Compare our shift-period scanning against Fourier-based period detection to establish that the relative-periodic fit captures structure beyond simple autocorrelation.

4. **Larger-scale 2D experiments.** Run the persistent-defect survey at 256×256 and 512×512 to verify that defect structures survive finite-size scaling.

---

## 7. Conclusion

We have presented a simple, rule-agnostic method for decomposing cellular automaton spacetimes into relative-periodic backgrounds and structured defect masks, with the run-length codelength of the defect mask as a key quality metric. Applied to 1D ECA, the method recovers known structural hierarchies. Applied to a survey of ~700 2D totalistic rules, it identifies a spectrum of behaviors from near-perfect oscillators (sub-1% defect rate) to rules with persistent, spatially organized defects analogous to Rule 54's particles.

The method is intentionally simple — majority voting over orbit classes — making it fast, easy to implement, and applicable to any dimension. It complements rather than replaces the more sophisticated machinery of computational mechanics, offering a quick first-pass decomposition that can identify interesting rules for deeper analysis.

---

## References

[1] J.P. Crutchfield and J.E. Hanson, "Computational mechanics of cellular automata: An example," *Physica D*, vol. 103, pp. 169–189, 1997.

[2] J.E. Hanson and J.P. Crutchfield, "The attractor-basin portrait of a cellular automaton," *Journal of Statistical Physics*, vol. 66, pp. 1415–1462, 1992.

[3] M. Redeker, "A language for particle interactions in Rule 54 and other cellular automata," *Complex Systems*, vol. 26, no. 1, pp. 1–32, 2017.

[4] A. Rupe and J.P. Crutchfield, "Local causal states and discrete coherent structures," *Chaos*, vol. 28, 075312, 2018.

[5] N.H. Packard and S. Wolfram, "Two-dimensional cellular automata," *Journal of Statistical Physics*, vol. 38, pp. 901–946, 1985.

[6] N. Boccara and M. Roger, "Some properties of local and nonlocal site exchange deterministic cellular automata," *International Journal of Modern Physics C*, vol. 10, pp. 1439–1470, 1999.

[7] C.R. Shalizi, R. Haslinger, J.-B. Rouquier, K.L. Klinkner, and C. Moore, "Automatic filters for the detection of coherent structure in spatiotemporal systems," *Physical Review E*, vol. 73, 036104, 2006.
