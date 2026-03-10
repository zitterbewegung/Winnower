# Consistent Period Selection for Cellular Automaton Spacetimes via Orbit-Class NML

## Abstract

We prove that model selection over relative-periodic backgrounds of cellular automaton (CA) spacetimes converges to a unique period as the observation window grows. The argument rests on a dimension-agnostic *orbit-class reduction*: fitting a relative-periodic background to a binary spacetime decomposes into independent Bernoulli estimation on orbit classes (Theorem 1), partition refinement makes higher periods monotonically more expressive (Theorem 2), and an exact Bernoulli NML (normalized maximum likelihood) criterion with parametric complexity $O(\log T)$ against data-fit cost $\Theta(T)$ yields consistent model selection (Theorem 3). Under an aperiodic-defect condition, the selected period recovers the true background period (Theorem 4). The theory applies identically to 1D, 2D, and 3D automata.

Cross-dimensional experiments validate the convergence: NML-selected periods stabilize for 1D elementary CA (rules 30, 54, 110), 2D totalistic rules (773 non-trivial from 1,050 candidates), and 3D totalistic rules — with margins growing monotonically after stabilization. As an application, the framework identifies 2D rules with persistent structured defects, including one (S37/B11) exhibiting extensive defect scaling verified across multiple grid sizes and seeds.

**Keywords:** cellular automata, normalized maximum likelihood, model selection consistency, symmetry projection, defect decomposition

---

## 1. Introduction

Cellular automata (CA) generate complex spatiotemporal patterns from simple local rules. Decomposing these patterns into regular and irregular components is a central problem in CA theory, with applications to understanding emergent computation, classifying rule complexity, and identifying coherent structures.

The computational mechanics program [1,2] builds local epsilon-machine models that identify domains, particles, and their interactions. Redeker [3] formalized particle catalogs via de Bruijn diagrams. Rupe and Crutchfield [4] generalized local causal states to arbitrary dimensions. Shalizi et al. [7] developed automatic coherent-structure filters. These methods build rich local models at significant computational cost.

We take a different approach: rather than building local models, we ask a global model-selection question. *Given a finite family of relative-periodic templates, which template best describes the data?* We show that this question has a clean answer — the NML-optimal period converges — and that the convergence proof is dimension-agnostic, applying uniformly to 1D, 2D, and 3D automata.

### 1.1 Contributions

1. **Orbit-class reduction** (Theorem 1): fitting a relative-periodic background reduces to independent majority voting on orbit classes, yielding the unique Hamming-optimal projection in $O(n)$ time.
2. **Monotonicity and overcapacity** (Theorem 2): higher periods always achieve lower defect rates along divisibility chains, necessitating complexity control.
3. **NML consistency** (Theorem 3): under ergodic defect rates, the NML-selected period stabilizes with growing margins — proved for any spatial dimension, with no assumption on defect geometry.
4. **Identifiability** (Theorem 4): when defects are aperiodic relative to the background, NML recovers the true background period.
5. **Cross-dimensional validation**: convergence confirmed empirically for 1D (ECA 30/54/110), 2D (773 totalistic rules), and 3D (totalistic rules on a 3-torus).
6. **Application**: identification of persistent structured defects in 2D rules, with extensive scaling in S37/B11.

### 1.2 Relationship to Prior Work

| Aspect | Computational Mechanics [1,2,4] | This Work |
|--------|-------------------------------|-----------|
| Model class | Local (epsilon-machine) | Global (relative-periodic) |
| Selection criterion | Statistical complexity | Exact Bernoulli NML |
| Consistency proof | — | Theorem 3 |
| Identifiability | — | Theorem 4 |
| Dimensionality | Case-by-case | Dimension-agnostic |
| Cost | Higher | $O(n)$ per model |

Packard and Wolfram [5] surveyed 2D rules qualitatively. Boccara and Roger [6] identified period-2 families. Zenil [8] used compression for CA classification. Our contribution is a *consistency theorem* for period selection that applies across dimensions, with the surveys as validation.

---

## 2. Theory

### 2.1 Relative-Periodic Model Class

**Definition 1.** Given a binary spacetime $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$, shift vector $\mathbf{s} = (s_1, \ldots, s_n) \in \mathbb{Z}^n$, and period $p \geq 1$, the *relative-periodic model class* $\mathcal{B}(p, \mathbf{s})$ consists of all fields $B$ satisfying:

$$B[t + p, (x_1 + s_1) \bmod D_1, \ldots, (x_n + s_n) \bmod D_n] = B[t, x_1, \ldots, x_n]$$

for all valid indices. This constraint partitions spacetime into *orbit classes* $\{O_j\}_{j=1}^{k}$ where $k = p \prod_i D_i$. Within each class, $B$ is constant. The definition is identical for $n = 1, 2, 3$, or any dimension.

### 2.2 Orbit-Class Reduction

**Theorem 1 (Optimal Hamming Projection).** Let $n_j^{(1)} = |\{(t,\mathbf{x}) \in O_j : U[t,\mathbf{x}] = 1\}|$ and $n_j^{(0)} = |O_j| - n_j^{(1)}$. The Hamming distance $d(U, B) = |\{(t,\mathbf{x}) : U[t,\mathbf{x}] \neq B[t,\mathbf{x}]\}|$ is minimized over $\mathcal{B}(p, \mathbf{s})$ by setting:

$$b_j = \begin{cases} 1 & \text{if } n_j^{(1)} > n_j^{(0)} \\ 0 & \text{if } n_j^{(0)} > n_j^{(1)} \\ \text{either} & \text{if } n_j^{(0)} = n_j^{(1)} \end{cases}$$

The minimum defect count is $\sum_j \min(n_j^{(0)}, n_j^{(1)})$. The minimizer is unique iff no orbit class has $n_j^{(0)} = n_j^{(1)}$.

*Proof.* The Hamming distance decomposes additively over orbit classes: $d(U,B) = \sum_j d_j$ where $d_j$ counts disagreements within $O_j$. Since $B$ is constant on each $O_j$, choosing $b_j$ independently minimizes each $d_j = \min(n_j^{(0)}, n_j^{(1)})$. $\square$

This is the *orbit-class reduction*: the spatiotemporal fitting problem decomposes into $k$ independent binary estimation problems. The reduction is exact and holds in any dimension. The optimal projection is computable in $O(|U|)$ time via a single pass over the data.

**Definition 2.** The *defect mask* is $M = U \oplus B^*$ where $B^*$ is the optimal projection. The *defect rate* is $r = \|M\|_1 / |U|$.

### 2.3 Monotonicity and Overcapacity

**Theorem 2 (Monotonicity).** If period $p_2$ is a multiple of $p_1$ (i.e., $p_2 = m \cdot p_1$ for integer $m \geq 1$) with the same shift $\mathbf{s}$, then the orbit partition under $p_2$ refines the partition under $p_1$, and:

$$d^*(p_2, \mathbf{s}) \leq d^*(p_1, \mathbf{s})$$

where $d^*$ denotes the optimal Hamming distance.

*Proof.* Each orbit class $O_j$ under $p_1$ is the union of $m$ orbit classes under $p_2$. Independent majority voting on finer classes can only reduce or maintain total disagreements, since optimizing over a finer partition is a relaxation. $\square$

**Corollary (Overcapacity).** Along any divisibility chain $p, 2p, 3p, \ldots$, defect rate is monotonically non-increasing. This creates an *overcapacity problem*: higher periods always fit at least as well as their divisors, but use $k = p \prod D_i$ free parameters. Naive defect-rate minimization always prefers the highest available period. This motivates the NML criterion below.

### 2.4 Exact Bernoulli NML Criterion

The orbit-class reduction (Theorem 1) shows that each model $(p, \mathbf{s})$ decomposes the data into $k = p \prod_i D_i$ independent Bernoulli estimation problems. This motivates a *Bernoulli NML* criterion where the statistical model family is exactly the one implied by the orbit-class structure.

**Definition 3 (Orbit-class Bernoulli model).** For model $(p, \mathbf{s})$ with $k$ orbit classes, each orbit class $O_j$ has $n_j = |O_j|$ observations and empirical frequency $\hat{\theta}_j = n_j^{(1)} / n_j$. The Bernoulli maximum-likelihood estimate for the $j$-th class is $\hat{\theta}_j$, with negative log-likelihood:

$$\text{NLL}(p, \mathbf{s}) = \sum_{j=1}^{k} n_j \, H_b(\hat{\theta}_j)$$

where $H_b(\theta) = -\theta \log_2 \theta - (1-\theta) \log_2(1-\theta)$ is binary entropy (with $0 \log 0 = 0$).

**Definition 4 (Bernoulli NML score).** The normalized maximum likelihood score for $k$ independent Bernoulli classes is:

$$\text{NML}(p, \mathbf{s}) = \underbrace{\text{NLL}(p, \mathbf{s})}_{\text{data fit}} + \underbrace{\sum_{j=1}^{k} \frac{1}{2} \log_2 n_j}_{\text{parametric complexity}}$$

The complexity term $\frac{1}{2} \log_2 n_j$ is the asymptotic Bernoulli NML normalizing constant for class $j$ with $n_j$ observations [9, §11.3]. For a single Bernoulli parameter with $n$ observations, this approximation is tight: the exact normalizer is $\frac{1}{2}\log_2(n/2) + O(1/n)$.

**Remark (Relationship to Hamming projection).** Majority vote (Theorem 1) minimizes Hamming distance; the Bernoulli MLE $\hat{\theta}_j$ minimizes negative log-likelihood. These serve different purposes: majority vote produces the optimal background decomposition, while NML selects among competing decompositions. The two coincide when $\hat{\theta}_j \in \{0, 1\}$ (pure orbit classes) and diverge most when $\hat{\theta}_j \approx 1/2$ (maximally noisy classes).

**Remark (No geometry dependence).** Unlike run-length or LZ4 codelengths, the NML score depends only on the orbit-class statistics $(n_j, n_j^{(1)})$ — it is independent of the spatial arrangement of defects and of the traversal order. This makes the criterion intrinsic to the orbit-class structure.

### 2.5 NML Consistency Theorem

This is the main theoretical result.

**Theorem 3 (NML Consistency).** Let $\mathcal{C} = \{(p_1, \mathbf{s}_1), \ldots, (p_m, \mathbf{s}_m)\}$ be a fixed finite candidate set. For each candidate $c \in \mathcal{C}$, let $k_c = p_c \prod_i D_i$ be the number of orbit classes and let $n_j(T)$ denote the size of the $j$-th orbit class at observation length $T$. Assume:

(A1) *Ergodic orbit-class frequencies*: for each candidate $c$ and each orbit class $j$, the empirical frequency $\hat{\theta}_j(T) \to \theta_j^*$ as $T \to \infty$.

Then:

(i) The per-site NLL rate converges: $\text{NLL}(c, T) / T \to \lambda_c$ where $\lambda_c = \lim_{T\to\infty} \frac{1}{T}\sum_j n_j(T) H_b(\theta_j^*)$.

(ii) The parametric complexity is $O(\log T)$: specifically, $\sum_j \frac{1}{2}\log_2 n_j(T) = \frac{k_c}{2} \log_2 \frac{T}{p_c} + O(1)$ since each orbit class has $n_j = \lfloor T/p_c \rfloor$ or $\lceil T/p_c \rceil$ observations.

(iii) The NML-selected candidate $c^*(T) = \arg\min_{c \in \mathcal{C}} \text{NML}(c, T)$ stabilizes: there exists $T_0$ such that $c^*(T) = c^*(T_0)$ for all $T > T_0$.

(iv) The stabilized selection minimizes the asymptotic per-site NLL rate $\lambda_c$, breaking ties by parametric complexity (fewer parameters preferred).

*Proof.* Under (A1), the NML score for candidate $c$ decomposes as:

$$\text{NML}(c, T) = \text{NLL}(c, T) + \sum_j \frac{1}{2}\log_2 n_j(T) = \lambda_c \cdot T + \frac{k_c}{2}\log_2 T + O(1)$$

For any two candidates $c_1, c_2$:

$$\text{NML}(c_1, T) - \text{NML}(c_2, T) = (\lambda_{c_1} - \lambda_{c_2}) \cdot T + \frac{k_{c_1} - k_{c_2}}{2} \log_2 T + O(1)$$

**Case 1:** $\lambda_{c_1} \neq \lambda_{c_2}$. The linear term dominates for large $T$, so the candidate with smaller $\lambda$ wins permanently.

**Case 2:** $\lambda_{c_1} = \lambda_{c_2}$. The logarithmic term dominates, and the simpler model (fewer parameters) wins permanently.

Since $|\mathcal{C}|$ is finite, all pairwise comparisons stabilize, giving a unique winner for $T > T_0$. $\square$

**Corollary (Dimension-agnostic).** Theorem 3 makes no reference to spatial dimension $n$. It applies identically to 1D rings, 2D tori, 3D tori, or any periodic lattice.

**Remark (Comparison with v6 proof).** The previous MDL formulation (paper v6) used run-length codelength $L_{\text{RL}}$ as the data-fit term, requiring an additional assumption (A2: $\Omega(T)$ runs) to ensure $L_{\text{RL}} = \Theta(T)$. The NML formulation removes this assumption entirely: the data-fit term is the Bernoulli NLL, which is always $\Theta(T)$ under (A1) whenever any orbit class has $\theta_j^* \in (0,1)$. This makes the proof strictly cleaner.

### 2.6 Identifiability

**Definition 5.** The *true background period* $p_0$ of a CA spacetime is the smallest period such that the defect mask $M^*_{p_0}$ has vanishing structure: all orbit classes under $p_0$ have asymptotic frequency $\theta_j^* \in \{0, 1\}$ (i.e., the background is an exact relative-periodic orbit, modulo finite transients).

**Theorem 4 (Identifiability under Aperiodic Defects).** Let $p_0$ be the true background period and suppose defects are aperiodic in the following sense: for all orbit classes $j$ under model $p_0$, the empirical frequency $\theta_j^* \in \{0, 1\}$, but for any strict multiple $p = m \cdot p_0$ ($m > 1$), the refinement of some orbit class produces sub-classes with the same frequency $\theta_j^* \in \{0, 1\}$. Then:

(i) $\text{NLL}(p, T) = \text{NLL}(p_0, T) + o(T)$ for any multiple $p = m \cdot p_0$, because splitting a pure orbit class ($\theta^* \in \{0,1\}$) into sub-classes does not reduce NLL.

(ii) The parametric complexity for $p$ exceeds that of $p_0$: $\frac{k_p}{2}\log_2 T > \frac{k_{p_0}}{2}\log_2 T$ since $k_p = m \cdot k_{p_0}$.

(iii) Therefore NML selects $p_0$ over all its strict multiples for large $T$.

*Proof.* When $\theta_j^* \in \{0,1\}$, we have $H_b(\theta_j^*) = 0$, so the NLL contribution from class $j$ is zero. Splitting $O_j$ into $m$ sub-classes $O_{j_1}, \ldots, O_{j_m}$ with the same frequency preserves $H_b = 0$ for each sub-class, so NLL is unchanged. But the complexity increases by $\frac{m-1}{2}\log_2(T/p)$ per split class. Since $k_p > k_{p_0}$, the complexity difference $\frac{k_p - k_{p_0}}{2}\log_2 T \to +\infty$, and NML penalizes the larger model. $\square$

**Remark (Impossibility with periodic defects).** If defects themselves have period $q$, then period $p_0 \cdot q$ absorbs defects into the template, achieving pure orbit classes ($H_b = 0$) and thus NLL = 0. In this case NML may prefer $p_0 \cdot q$ over $p_0$, because the NLL reduction (from $\Theta(T)$ to 0) outweighs the complexity increase ($O(\log T)$). This is *principled* behavior: the data genuinely admits a simpler (zero-defect) description at the higher period. The distinction between "background periodicity" and "defect periodicity" is not intrinsic to the observation.

### 2.7 Geometric Diagnostics: Run-Length and LZ4

The NML criterion (Definition 4) is the primary model selector. For geometric analysis of defect masks *after* model selection, we use two compression-based diagnostics:

**Run-length codelength** $L_{\text{RL}}(M)$: Elias-gamma code over run lengths of the flattened defect mask. This measures spatial clustering: a contiguous defect block costs $O(\log n)$ bits, while $w$ scattered defects cost $\Omega(w \log(n/w))$ bits.

**LZ4 codelength** $L_{\text{LZ4}}(M)$: LZ4 compression of the packed defect mask. A practical compressor proxy.

**Proposition 1 (Run-Length Separation).** Two binary masks of the same size and Hamming weight can have run-length codelengths differing by a factor of $\Omega(\log n)$.

*Proof sketch.* A mask of weight $w$ with a single contiguous block has RL codelength $O(\log n)$. A mask of the same weight with $w$ isolated defects has RL codelength $\Omega(w \log(n/w))$. $\square$

These diagnostics are *not* used for model selection — they depend on traversal order and do not correspond to the NML data-fit term. They are useful for characterizing defect geometry after the NML-selected model is fixed.

---

## 3. Cross-Dimensional Validation

We validate Theorem 3 by sweeping the observation length $T$ and tracking the NML-selected period across 1D, 2D, and 3D cellular automata.

### 3.1 1D Elementary CA

ECA rules 30, 54, and 110 on a ring of width 192, scanning shifts $\pm 6$, periods 1–10.

**NML-optimal decomposition (T = 144, shift = 0):**

| Rule | Best $(s, p)$ | Defect Rate | NLL Bits | Complexity | NML Bits |
|------|---------------|-------------|----------|------------|----------|
| 54   | $(0, 4)$      | 20.1%       | 17,477   | 1,985      | 19,462   |
| 110  | $(0, 7)$      | 30.8%       | 22,842   | 2,931      | 25,774   |
| 30   | $(5, 1)$      | 46.3%       | 27,489   | 688        | 28,177   |

The known complexity hierarchy Rule 54 < Rule 110 < Rule 30 [1,2,3] is recovered under NML ranking.

**Period convergence (1D):**

| Rule | T=50 | T=100 | T=200 | T=400 | T=600 | T=800 | Margin at T=800 |
|------|------|-------|-------|-------|-------|-------|-----------------|
| ECA-54  | 4 | 4 | 4 | 4 | 4 | 4 | 1,993 |
| ECA-110 | 7 | 7 | 7 | 7 | 7 | 7 | 18,378 |
| ECA-30  | 1 | 1 | 1 | 1 | 1 | 1 | 598 |

All three 1D rules show *immediate* stabilization — the NML-selected period is constant from T=50 onward, with positive margins at every point. Margins grow monotonically, exactly as Theorem 3 predicts. Rule 110 shows the strongest separation (margin 18,378 bits at T=800), consistent with its pronounced period-7 Ether background.

### 3.2 2D Totalistic Rules

#### 3.2.1 Survey

We survey 1,050 range-threshold totalistic rules on a 48×48 torus (Moore neighborhood, 40 steps, density 0.5, seed 11). A cell survives if $s_{\text{lo}} \leq n \leq s_{\text{hi}}$ and is born if $b_{\text{lo}} \leq n \leq b_{\text{hi}}$, with range widths $\leq 4$. Of 1,050 candidates, 773 produce non-trivial dynamics (end density between 2% and 98%). Of these, 172 have nonzero best-fit shift (drifting periodic structure).

Top rules by NML score are near-fixed-point patterns with $<1\%$ defect rates — NML correctly identifies these as the simplest descriptions. Period-2 oscillators (159 rules) appear at NML rank ~20, with no period $\geq 3$ selected at this short horizon (40 steps). Period distribution: 614 period-1, 159 period-2.

#### 3.2.2 Multi-Seed Robustness

We verified 6 rules across 10 seeds (64×64, 60 steps):

| Rule | Modal Period | Mean Rate | CV | Period Consistent |
|------|-------------|-----------|-----|-------------------|
| S14/B11 | 1 | 0.59% | 8.4% | 10/10 |
| S25/B12 | 2 | 0.58% | 15.6% | 8/10 |
| S66/B36 | 2 | 0.63% | 10.5% | 10/10 |
| S24/B11 | 2 | 2.78% | 9.4% | 10/10 |
| S11/B37 | 4 | 2.75% | 18.7% | 7/10 |
| S37/B11 | 2 | 4.41% | 12.4% | 10/10 |

Rules with near-zero NML margins (S25/B12, S11/B37) show seed-dependent period selection at short horizons — consistent with Theorem 3, which requires the linear NLL terms to dominate.

#### 3.2.3 Period Convergence (2D)

| Rule | T=60 | T=100 | T=200 | T=400 | T=600 | T=800 | Margin at T=800 |
|------|------|-------|-------|-------|-------|-------|-----------------|
| S24/B11 | 1 | 1 | 1 | 2 | 2 | 2 | 13,115 |
| S11/B37 | 2 | 2 | 2 | 4 | 4 | 4 | 22,352 |
| S37/B11 | 1 | 1 | 2 | 2 | 2 | 2 | 16,006 |

The 2D persistent-defect rules show *progressive* stabilization: the NML-selected period increases in discrete jumps (1→2 for S24/B11, 2→4 for S11/B37, 1→2 for S37/B11), then locks with growing margins. This is the regime described by Theorem 3's impossibility remark: periodic defect structure is absorbed into higher-period templates, and NML correctly identifies the period that best compresses the entire spacetime.

Notably, NML selects *lower* periods than the previous MDL formulation (which used RL codelength as data fit). For example, S24/B11 converges to period 2 under NML vs period 6 under MDL — the RL artifact inflated the data-fit term for higher periods, making them appear artificially competitive.

### 3.3 3D Totalistic Rules

Diamoeba3d rule (survive 5–8, birth 5–8) on a 16×16×16 3-torus, shift (0,0,0):

| T | Period | NML Bits | Margin |
|---|--------|----------|--------|
| 10 | 6 | 26,406 | 5,560 |
| 20 | 6 | 75,703 | 3,055 |
| 40 | 1 | 158,154 | 3,505 |
| 60 | 1 | 232,856 | 4,872 |
| 80 | 1 | 303,209 | 5,840 |

The initial T=10–20 selection of period 6 is a small-sample artifact (10–20 time steps with a period-6 model means only 1–3 full cycles per orbit class, where overfitting is expected). By T=40, NML stabilizes to period 1 with margins growing monotonically — confirming Theorem 3 in 3D. The 3D-life rule (survive 4–5, birth 5) dies out, providing a null result.

### 3.4 Summary of Convergence Evidence

| Dimension | Rules Tested | Stabilization Onset | Behavior |
|-----------|-------------|--------------------|-----------|
| 1D | ECA 30, 54, 110 | Immediate (T=50) | Period locked from first measurement |
| 2D | 3 persistent-defect rules | T=200–400 | Progressive jumps, then locked |
| 3D | diamoeba3d | T=40 | Initial transient, then locked |

In all cases, the NML-selected period makes finitely many transitions then stabilizes, exactly as Theorem 3 predicts. The convergence rate depends on how quickly the asymptotic NLL rates $\lambda_c$ separate: 1D rules separate immediately, 3D rules after one correction, and 2D persistent-defect rules (where defects have their own periodic structure) take longest.

---

## 4. Application: Persistent Structured Defects in 2D

### 4.1 400-Step Verification

We ran 400-step simulations (64×64, seed 11) and measured defect counts in 100-step windows:

| Rule | Period | Window | Mean Defects | Std | Range |
|------|--------|--------|-------------|-----|-------|
| S24/B11 | 2 | t=50–100 | 14.8 | 1.3 | [13, 17] |
| S24/B11 | 2 | t=300–400 | 14.8 | 1.3 | [13, 17] |
| S11/B37 | 4 | t=50–100 | 15.5 | 5.2 | [10, 31] |
| S11/B37 | 4 | t=300–400 | 12.6 | 2.0 | [10, 15] |
| S37/B11 | 2 | t=50–100 | 28.6 | 4.2 | [21, 37] |
| S37/B11 | 2 | t=300–400 | 28.1 | 3.9 | [18, 37] |

All three rules show stable defect populations from t=100 onward.

### 4.2 Size Scaling

5 seeds, grid sizes 32–192, 100 steps:

**S37/B11 — Extensive scaling:**

| Grid | Mean Rate | Late Defects | Defect Density |
|------|-----------|-------------|----------------|
| 32×32 | 3.47% | 11.4 ± 5.3 | 0.011 |
| 64×64 | 3.26% | 45.7 ± 6.6 | 0.011 |
| 96×96 | 3.11% | 101.9 ± 8.0 | 0.011 |
| 128×128 | 3.33% | 196.5 ± 10.6 | 0.012 |
| 192×192 | 3.14% | 428.5 ± 32.4 | 0.012 |

Defect density is approximately constant (~0.011) across 5 seeds and 5 grid sizes, consistent with a bulk (extensive) phenomenon.

**S11/B37 — Sub-extensive scaling:**

| Grid | Mean Rate | Late Defects | Defect Density |
|------|-----------|-------------|----------------|
| 32×32 | 1.46% | 1.6 ± 0.6 | 0.0016 |
| 64×64 | 1.81% | 11.1 ± 6.3 | 0.0027 |
| 96×96 | 1.71% | 18.6 ± 6.2 | 0.0020 |
| 128×128 | 1.58% | 32.7 ± 4.1 | 0.0020 |
| 192×192 | 1.69% | 79.5 ± 16.7 | 0.0022 |

Defect density drops from 64×64 to 96×96 then stabilizes around 0.002, consistent with a sub-extensive population.

---

## 5. Discussion

### 5.1 What the Theory Provides

The orbit-class reduction (Theorem 1) transforms a seemingly complex spatiotemporal fitting problem into standard Bernoulli estimation. This enables:

1. **Exact optimal decomposition** in $O(n)$ time for any dimension.
2. **A formal explanation** of overcapacity (Theorem 2), showing why naive defect-rate ranking is inadequate.
3. **A consistency theorem** (Theorem 3) proving NML period selection converges, with a single assumption (ergodic orbit-class frequencies) and no dependence on defect geometry.
4. **An identifiability result** (Theorem 4) showing NML recovers the true period when defects are aperiodic, with a clean impossibility characterization when they are not.

The key insight is that the *same* theoretical framework — orbit classes → Bernoulli estimation → NML consistency — applies without modification across spatial dimensions.

### 5.2 NML vs Legacy MDL

The previous formulation (paper v6) used a two-part MDL criterion: approximate parametric penalty $\frac{k}{2}\log_2(T/p)$ plus run-length codelength $L_{\text{RL}}$ of the defect mask. This had three weaknesses:

1. **Model mismatch**: the RL codelength is not the data-fit term of the Bernoulli model implied by the orbit-class structure. NLL is.
2. **Geometry dependence**: RL codelength depends on the spatial arrangement of defects and the flattening order, making it non-intrinsic.
3. **Extra assumption**: the convergence proof required an $\Omega(T)$ runs condition to ensure $L_{\text{RL}} = \Theta(T)$, which NML does not need.

In practice, NML and MDL agree on period selection for most rules (e.g., both select period 4 for Rule 54). They diverge for 2D rules with periodic defects, where NML selects lower, more parsimonious periods.

We retain RL and LZ4 codelengths as geometric diagnostics (Section 2.7) for characterizing defect spatial structure after model selection.

### 5.3 What the Framework Does Not Provide

The method identifies *where* defects are but not *how* they interact. It does not recover domain/particle structure in the computational mechanics sense [1,2]. The fitted backgrounds are nearest periodic fields, not exact CA orbits. Component-level lifetime and interaction analysis is future work.

### 5.4 Limitations

1. **Shift scanning adds little for this rule family.** All 2D best fits have shift (0,0). The theoretical framework supports nonzero shifts, but the empirical gain is rule-dependent.
2. **NML selects the best-compressing period, not necessarily the "true" period.** When defects have their own periodicity, NML absorbs them into higher-period templates (Theorem 4 impossibility remark). This is principled but may not match a physicist's intuition.
3. **Asymptotic NML complexity.** The $\frac{1}{2}\log_2 n_j$ complexity term is an asymptotic approximation to the exact Bernoulli NML normalizer. For very small orbit classes ($n_j < 10$), the approximation is less tight — relevant only at the smallest $T$ values.
4. **Bernoulli i.i.d. assumption.** Within each orbit class, the NML criterion treats observations as i.i.d. Bernoulli. In reality, successive observations within an orbit class are separated by $p$ time steps and may have temporal correlations. Under ergodicity (A1), these correlations do not affect the asymptotic rate, but they may affect finite-sample behavior.

### 5.5 Future Work

1. **Component tracking**: lifetimes, velocities, collision catalogs.
2. **Direct comparison** with local causal states [4] on Rule 54 and 2D rules.
3. **Larger surveys**: extend to 1000+ 2D rules and broader 3D rule families.
4. **Finite-sample corrections**: exact (non-asymptotic) Bernoulli NML normalizer, or plug-in corrections for small orbit classes.
5. **Shift optimization**: joint NML optimization over both shift and period.

---

## 6. Conclusion

We have proved that NML model selection over relative-periodic CA backgrounds is consistent: the selected period converges to a unique limit as the observation window grows (Theorem 3). The proof requires only ergodic orbit-class frequencies — no assumption on defect geometry — and is dimension-agnostic, resting on the orbit-class reduction that decomposes spatiotemporal fitting into independent Bernoulli estimation. When defects are aperiodic, NML recovers the true background period (Theorem 4); when defects are periodic, NML correctly absorbs them into the template.

Cross-dimensional experiments on 1D elementary CA, 2D totalistic rules, and 3D totalistic rules confirm the convergence prediction, with NML-selected periods stabilizing and margins growing monotonically. As an application, the framework identifies 2D rules with persistent structured defects exhibiting extensive scaling — candidates for further computational-mechanics analysis.

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

[10] Y. Shtarkov, "Universal sequential coding of single messages," *Problems of Information Transmission*, vol. 23, pp. 3–17, 1987.

---

## Appendix A: Reproducibility

All code is open-source. Key parameters:
- 1D ECA: width=192, steps=144, density=0.5, seed=11, shifts=−6..+6, periods=1..10
- 1D convergence: T=[50, 100, 200, 400, 600, 800], periods=1..10
- 2D survey: 48×48, steps=40, 1,050 candidates (773 non-trivial), range width ≤ 4
- 2D convergence: 64×64, T=[60, 100, 200, 400, 600, 800], periods=1..8
- 3D convergence: 16×16×16, T=[10, 20, 40, 60, 80], periods=1..6
- Multi-seed: seeds=[11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]
- Size scaling: grids=[32, 64, 96, 128, 192], steps=100, 5 seeds
- 400-step verification: 64×64, steps=400, seed=11
- Model selector: exact Bernoulli NML (orbit-class NLL + asymptotic parametric complexity)

## Appendix B: Geometric Diagnostics

Run-length and LZ4 codelengths are used as geometric diagnostics, not for model selection. Example: two synthetic masks of size 512, each with 64 defects — clustered (42 RL bits) vs scattered (251 RL bits), a 6× ratio at identical Hamming weight. This illustrates Proposition 1 and motivates RL/LZ4 as post-selection defect geometry characterizers.

## Appendix C: NML vs Legacy MDL Period Selection

| Rule | MDL Period | NML Period | Agreement |
|------|-----------|-----------|-----------|
| ECA-54 (1D) | 4 | 4 | Yes |
| ECA-110 (1D) | 7 | 7 | Yes |
| ECA-30 (1D) | 1 | 1 | Yes |
| S24/B11 (2D, T=800) | 6 | 2 | No — NML more parsimonious |
| S11/B37 (2D, T=800) | 8 | 4 | No — NML more parsimonious |
| S37/B11 (2D, T=800) | 6 | 2 | No — NML more parsimonious |
| diamoeba3d (3D) | 1 | 1 | Yes |

NML and MDL agree for 1D and 3D rules but diverge for 2D rules with periodic defects, where the RL data-fit artifact in MDL inflates scores for higher periods.
