# Model Selection Stabilization for Relative-Periodic Decomposition of Cellular Automaton Spacetimes

## Abstract

We prove that Bernoulli NML model selection over relative-periodic backgrounds of cellular automaton (CA) spacetimes stabilizes as the observation window grows: every candidate whose asymptotic per-site NLL rate exceeds the minimum is eventually excluded (Theorem 3). When the rate-minimizing candidate is unique — which holds in all cases we test — the selected model locks to a single winner. The argument rests on a dimension-agnostic *orbit-class reduction*: fitting a relative-periodic background to a binary spacetime decomposes into independent majority voting on orbit classes (Theorem 1), partition refinement along constant-velocity chains makes higher periods monotonically more expressive (Theorem 2), and the Bernoulli NML criterion's $O(\log T)$ complexity penalty is eventually dominated by $\Theta(T)$ data-fit gaps between candidates with distinct rates. We also show by explicit construction that background period recovery is impossible in general without additional assumptions (Theorem 4). The theory applies identically to 1D, 2D, and 3D automata.

Cross-dimensional experiments are consistent with the stabilization prediction: selected periods lock for 1D elementary CA (rules 30, 54, 110), 2D totalistic rules (from a survey of 773 range-threshold candidates and all 106 named Life-like rules from the LifeWiki), and a 3D totalistic rule — with margins growing after the selected period locks. The LifeWiki survey demonstrates the stabilization theorem in action: Diamoeba transitions from period 1 to period 2 between T=100 and T=400 as the NLL gap crosses the complexity threshold, while Fredkin (B1357/S02468) is the only rule achieving period 8. As an application, the framework identifies 2D rules with persistent structured projection residuals, including one (S37/B11) exhibiting extensive residual scaling verified at 400 steps, across multiple seeds, and at grid sizes up to 192×192.

**Keywords:** cellular automata, normalized maximum likelihood, model selection stabilization, symmetry projection, projection residual decomposition

---

## 1. Introduction

Cellular automata (CA) generate complex spatiotemporal patterns from simple local rules. Decomposing these patterns into regular and irregular components is a central problem in CA theory, with applications to understanding emergent computation, classifying rule complexity, and identifying coherent structures.

The computational mechanics program [1,2] builds local epsilon-machine models that identify domains, particles, and their interactions. Redeker [3] formalized particle catalogs via de Bruijn diagrams. Rupe and Crutchfield [4] generalized local causal states to arbitrary dimensions. Shalizi et al. [7] developed automatic coherent-structure filters. These methods build rich local models at significant computational cost.

We take a different approach: rather than building local models, we ask a global model-selection question. *Given a finite family of relative-periodic templates, which template best describes the data?* We show that this question has a clean asymptotic answer: every candidate whose per-site NLL rate is suboptimal is eventually excluded, and if the rate-minimizer is unique then the NML-optimal candidate stabilizes. The proof is dimension-agnostic, applying uniformly to 1D, 2D, and 3D automata.

### 1.1 Contributions

1. **Orbit-class reduction** (Theorem 1): fitting a relative-periodic background reduces to independent majority voting on orbit classes, yielding a Hamming-optimal projection (unique when no orbit class has an exact tie) in $O(|U|)$ time per candidate model.
2. **Monotonicity under velocity matching** (Theorem 2): higher periods achieve lower residual counts along constant-velocity divisibility chains, necessitating complexity control.
3. **Model selection stabilization** (Theorem 3): under convergent orbit-class frequencies, every suboptimal candidate is eventually excluded; when the rate-minimizer is unique, selection locks to a single winner. Proved for any spatial dimension, with no assumption on residual geometry.
4. **Nonidentifiability** (Theorem 4): background period recovery is impossible in general; periodic residual structure can be absorbed by higher-period templates. Demonstrated by explicit construction.
5. **Cross-dimensional experiments**: empirical stabilization observed for 1D (ECA 30/54/110), three selected 2D totalistic rules (from a survey of 773), and one 3D rule on a 3-torus.
6. **Application**: identification of persistent structured projection residuals in 2D rules, with extensive scaling in S37/B11.

### 1.2 Relationship to Prior Work

| Aspect | Computational Mechanics [1,2,4] | This Work |
|--------|-------------------------------|-----------|
| Model class | Local (epsilon-machine) | Global (relative-periodic) |
| Selection criterion | Statistical complexity | Bernoulli NML |
| Stabilization proof | — | Theorem 3 |
| Nonidentifiability | — | Theorem 4 |
| Dimensionality | Case-by-case | Dimension-agnostic |
| Cost | Higher | $O(|U|)$ per candidate |

Packard and Wolfram [5] surveyed 2D rules qualitatively. Boccara and Roger [6] identified period-2 families. Zenil [8] used compression for CA classification. Our contribution is a *rate-based elimination and stabilization theorem* for selection over relative-periodic candidates that applies across dimensions, with the surveys as empirical evidence.

---

## 2. Theory

### 2.1 Relative-Periodic Model Class

**Definition 1.** Given a binary spacetime $U \in \{0,1\}^{T \times D_1 \times \cdots \times D_n}$, shift vector $\mathbf{s} = (s_1, \ldots, s_n) \in \mathbb{Z}^n$, and period $p \geq 1$, the *relative-periodic model class* $\mathcal{B}(p, \mathbf{s})$ consists of all fields $B$ satisfying:

$$B[t + p, (x_1 + s_1) \bmod D_1, \ldots, (x_n + s_n) \bmod D_n] = B[t, x_1, \ldots, x_n]$$

for all valid indices. This constraint partitions spacetime into *orbit classes* $\{O_j\}_{j=1}^{k}$ where $k = p \prod_i D_i$. Within each class, $B$ is constant. The definition is identical for $n = 1, 2, 3$, or any dimension.

We write $N(T) = T \prod_i D_i$ for the total number of spacetime sites.

### 2.2 Orbit-Class Reduction

**Theorem 1 (Optimal Hamming Projection).** Let $n_j^{(1)} = |\{(t,\mathbf{x}) \in O_j : U[t,\mathbf{x}] = 1\}|$ and $n_j^{(0)} = |O_j| - n_j^{(1)}$. The Hamming distance $d(U, B) = |\{(t,\mathbf{x}) : U[t,\mathbf{x}] \neq B[t,\mathbf{x}]\}|$ is minimized over $\mathcal{B}(p, \mathbf{s})$ by setting:

$$b_j = \begin{cases} 1 & \text{if } n_j^{(1)} > n_j^{(0)} \\ 0 & \text{if } n_j^{(0)} > n_j^{(1)} \\ \text{either} & \text{if } n_j^{(0)} = n_j^{(1)} \end{cases}$$

The minimum residual count is $\sum_j \min(n_j^{(0)}, n_j^{(1)})$. The minimizer is unique if and only if no orbit class has $n_j^{(0)} = n_j^{(1)}$.

*Proof.* The Hamming distance decomposes additively over orbit classes: $d(U,B) = \sum_j d_j$ where $d_j$ counts disagreements within $O_j$. Since $B$ is constant on each $O_j$, choosing $b_j$ independently minimizes each $d_j = \min(n_j^{(0)}, n_j^{(1)})$. $\square$

This is the *orbit-class reduction*: the spatiotemporal fitting problem decomposes into $k$ independent binary estimation problems. The reduction is exact and holds in any dimension. A Hamming-optimal projection is computable in $O(|U|)$ time per candidate model via a single pass over the data. (When some orbit class has $n_j^{(0)} = n_j^{(1)}$, the minimum Hamming distance is unique but may be achieved by more than one projection; in the implementation, ties are broken toward 1.)

**Definition 2.** The *projection residual mask* (or *defect mask*) is $M = U \oplus B^*$ where $B^*$ is the Hamming-optimal projection (with ties broken deterministically). The *defect rate* is $r = \|M\|_1 / N(T)$.

### 2.3 Monotonicity and Overcapacity

**Theorem 2 (Monotonicity under Velocity-Matched Refinement).** Let $(p_1, \mathbf{s}_1)$ and $(p_2, \mathbf{s}_2)$ be two relative-periodic models. If there exists an integer $m \geq 1$ such that $p_2 = m \cdot p_1$ and $s_2^{(i)} \equiv m \cdot s_1^{(i)} \pmod{D_i}$ for each spatial dimension $i$, then the orbit partition under $(p_2, \mathbf{s}_2)$ refines the partition under $(p_1, \mathbf{s}_1)$, and:

$$d^*(p_2, \mathbf{s}_2) \leq d^*(p_1, \mathbf{s}_1)$$

The condition $s_2 = m \cdot s_1 \pmod{D}$ means the two models share the same *characteristic velocity* $\mathbf{s}/p$. In particular, for shift $\mathbf{s} = \mathbf{0}$, monotonicity holds along all divisibility chains $p, 2p, 3p, \ldots$

*Proof.* Under the stated condition, the periodicity map $\tau_2: (t, \mathbf{x}) \mapsto (t + p_2, \mathbf{x} + \mathbf{s}_2 \bmod \mathbf{D})$ equals $\tau_1^m$, the $m$-fold composition of the $(p_1, \mathbf{s}_1)$ map. Therefore, the $\tau_2$-orbit of any point is a subset of its $\tau_1$-orbit, so the $\tau_2$-partition refines the $\tau_1$-partition. By Theorem 1, optimizing over a finer partition can only reduce total disagreement. $\square$

**Remark.** The velocity-matching condition is necessary in general. For example, on a ring of width 4, the models $(p=1, s=1)$ and $(p=2, s=1)$ share the same shift but *not* the same velocity ($1/1 \neq 1/2$). The checkerboard spacetime $U[t,x] = (t+x) \bmod 2$ has $d^*(1,1) = 0$ but $d^*(2,1) = 4$, violating monotonicity.

**Corollary (Overcapacity).** Along any constant-velocity divisibility chain, the residual count is monotonically non-increasing. This creates an *overcapacity problem*: naive residual-count minimization always prefers the highest available period. This motivates the complexity-penalized criterion below.

### 2.4 Bernoulli NML Criterion

The orbit-class reduction (Theorem 1) shows that each model $(p, \mathbf{s})$ decomposes the data into $k = p \prod_i D_i$ independent Bernoulli estimation problems. This motivates a *Bernoulli NML* criterion where the statistical model family is exactly the one implied by the orbit-class structure.

**Definition 3 (Orbit-class Bernoulli model).** For model $(p, \mathbf{s})$ with $k$ orbit classes, each orbit class $O_j$ has $n_j = |O_j|$ observations and empirical frequency $\hat{\theta}_j = n_j^{(1)} / n_j$. The Bernoulli maximum-likelihood estimate for the $j$-th class is $\hat{\theta}_j$, with negative log-likelihood:

$$\text{NLL}(p, \mathbf{s}) = \sum_{j=1}^{k} n_j \, H_b(\hat{\theta}_j)$$

where $H_b(\theta) = -\theta \log_2 \theta - (1-\theta) \log_2(1-\theta)$ is binary entropy (with $0 \log 0 = 0$).

**Definition 4 (Bernoulli NML score).** The normalized maximum likelihood score for $k$ independent Bernoulli classes is:

$$\text{NML}(p, \mathbf{s}) = \underbrace{\text{NLL}(p, \mathbf{s})}_{\text{data fit}} + \underbrace{\sum_{j=1}^{k} \frac{1}{2} \log_2 n_j}_{\text{asymptotic parametric complexity}}$$

The complexity term $\frac{1}{2} \log_2 n_j$ is the asymptotic NML parametric complexity for class $j$ with $n_j$ observations [9, §11.3], originating from the Shtarkov normalizing constant for Bernoulli families [10]. The combined score is an asymptotic approximation to the normalized maximum likelihood code for the orbit-class Bernoulli model. It is not exact NML (the exact normalizing constants involve sums of binomial coefficients), but the $O(k)$ additive error does not affect asymptotic model selection since the NLL term is $\Theta(N(T))$.

**Remark (Relationship to Hamming projection).** Majority vote (Theorem 1) minimizes Hamming distance; the Bernoulli MLE $\hat{\theta}_j$ minimizes negative log-likelihood. These serve different purposes: majority vote produces the optimal background decomposition, while NML selects among competing decompositions. The two coincide when $\hat{\theta}_j \in \{0, 1\}$ (pure orbit classes) and diverge most when $\hat{\theta}_j \approx 1/2$ (maximally noisy classes).

**Remark (No geometry dependence).** Unlike run-length or LZ4 codelengths, the NML score depends only on the orbit-class statistics $(n_j, n_j^{(1)})$ — it is independent of the spatial arrangement of residuals and of the traversal order. This makes the criterion intrinsic to the orbit-class structure.

### 2.5 Stabilization Theorem

This is the main theoretical result.

**Theorem 3 (Rate-Based Elimination and Stabilization of Bernoulli NML Selection).** Let $\mathcal{C} = \{(p_1, \mathbf{s}_1), \ldots, (p_m, \mathbf{s}_m)\}$ be a fixed finite candidate set. For each candidate $c \in \mathcal{C}$, let $k_c = p_c \prod_i D_i$ be the number of orbit classes and let $n_j(T)$ denote the size of the $j$-th orbit class at observation length $T$. Assume:

(A1) *Convergent orbit-class frequencies*: for each candidate $c$ and each orbit class $j$, the empirical frequency $\hat{\theta}_j(T) \to \theta_j^*$ as $T \to \infty$.

Define the *per-site NLL rate* $\lambda_c = \frac{1}{k_c} \sum_{j=1}^{k_c} H_b(\theta_j^*)$, and let $\lambda^* = \min_{c \in \mathcal{C}} \lambda_c$. Then:

(i) The per-site NLL converges:

$$\frac{\text{NLL}(c, T)}{N(T)} \to \lambda_c.$$

Moreover,

$$\text{NML}(c, T) = \lambda_c \cdot N(T) + \frac{k_c}{2}\log_2 T + o(N(T)).$$

(ii) *(Pairwise comparison.)* If $\lambda_{c_1} < \lambda_{c_2}$, then:

$$\text{NML}(c_1, T) < \text{NML}(c_2, T)$$

for all sufficiently large $T$.

(iii) *(Elimination.)* Every candidate $c$ with $\lambda_c > \lambda^*$ is eventually excluded: there exists $T_c$ such that $c \notin \arg\min_{c' \in \mathcal{C}} \text{NML}(c', T)$ for all $T > T_c$.

(iv) *(Stabilization under unique rate-minimizer.)* If $\lambda^*$ is achieved by a unique candidate $c^*$, then NML selection stabilizes: there exists $T_0$ such that $\arg\min \text{NML}(\cdot, T) = \{c^*\}$ for all $T > T_0$.

*Proof.* Under (A1), each $\hat{\theta}_j(T) \to \theta_j^*$. Since $H_b$ is continuous on $[0,1]$, we have $H_b(\hat{\theta}_j(T)) = H_b(\theta_j^*) + o(1)$. Each orbit class has $n_j(T) = T/p_c + O(1)$ observations, so:

$$n_j(T) \cdot H_b(\hat{\theta}_j(T)) = \frac{T}{p_c} \cdot H_b(\theta_j^*) + o(T).$$

Summing over $j = 1, \ldots, k_c$ gives:

$$\text{NLL}(c, T) = \frac{T}{p_c} \sum_j H_b(\theta_j^*) + o(T) = \lambda_c \cdot N(T) + o(N(T)),$$

since $N(T)/k_c = T/p_c$. Dividing by $N(T)$ proves the first claim in (i).

For the complexity: $\sum_j \frac{1}{2} \log_2 n_j(T) = \frac{k_c}{2} \log_2(T/p_c) + O(1) = \frac{k_c}{2} \log_2 T + O(1)$. Combining gives (i).

For (ii), subtract the two expansions:

$$\text{NML}(c_2, T) - \text{NML}(c_1, T) = (\lambda_{c_2} - \lambda_{c_1}) \cdot N(T) + o(N(T)).$$

Since $\lambda_{c_2} - \lambda_{c_1} > 0$ and $N(T) \to \infty$, the right-hand side tends to $+\infty$, so $\text{NML}(c_1, T) < \text{NML}(c_2, T)$ for all sufficiently large $T$.

For (iii), if $\lambda_c > \lambda^*$, choose any $c' \in \mathcal{C}$ with $\lambda_{c'} = \lambda^*$. By (ii), $\text{NML}(c', T) < \text{NML}(c, T)$ for all sufficiently large $T$, so $c$ is eventually excluded.

For (iv), if $c^*$ is the unique minimizer of $\lambda_c$, then for every other $c$, we have $\lambda_{c^*} < \lambda_c$, so by (ii), $\text{NML}(c^*, T) < \text{NML}(c, T)$ for all sufficiently large $T$. Taking the maximum over the finitely many competitors gives a single $T_0$ after which $\arg\min \text{NML}(\cdot, T) = \{c^*\}$. $\square$

**Remark (What Theorem 3 does and does not prove).** Theorem 3 proves pairwise eventual ordering between candidates with distinct rates, hence elimination of all non-rate-minimizers, and full stabilization only when the rate-minimizer is unique. It does *not* resolve ties among candidates with the same minimal rate $\lambda^*$.

**Remark (Tie-breaking at the logarithmic level).** Resolving ties among rate-minimizers at the $O(\log T)$ level requires a stronger assumption — for instance, that $\text{NLL}_c(T) = \lambda_c \cdot N(T) + o(\log T)$ — under which the complexity penalty $\frac{k_c}{2} \log_2 T$ breaks ties in favor of fewer parameters (lower $k_c$). Since $k_c = p_c \prod_i D_i$, candidates with the same period have the same $k_c$, so same-period ties (differing only in shift) cannot be resolved even under this strengthened assumption; a deterministic tie-break (e.g., lexicographic on shift) may be imposed. For finite deterministic CA, orbit-class frequencies converge at rate $O(1/T)$, but the resulting NLL correction is $O(\log T)$ (from orbit classes that are asymptotically pure but have $O(1)$ transient defects), which is the same order as the complexity term; whether ties are resolved depends on the specific transient structure.

**Remark (Empirical rate gaps).** In all experiments reported in Section 3, the margins between the NML-selected candidate and the runner-up grow linearly in $T$, indicating distinct $\lambda_c$ values. Conclusion (iv) therefore matches the observed regime.

**Corollary (Dimension-agnostic).** Theorem 3 makes no reference to spatial dimension $n$. It applies identically to 1D rings, 2D tori, 3D tori, or any periodic lattice.

**Remark on run-length encoding.** An alternative MDL criterion using $\frac{k}{2} \log_2(T/p) + L_{\text{RL}}(M^*)$ (BIC-type penalty plus run-length residual encoding) satisfies an analogous stabilization theorem under analogous assumptions on the per-site RL rate. For finite deterministic CA, this convergence can be proved under a "no exact frequency ties" condition (see Appendix D). We use the NML score as the primary selection criterion because assumption (A1) is automatically satisfied for finite deterministic CA (by eventual periodicity of the state sequence), and report RL codelength as a secondary geometric diagnostic (Proposition 1).

### 2.6 Nonidentifiability

**Theorem 4 (Nonidentifiability of Background Period for Bernoulli NML).** For any period $p_0$ and shift $\mathbf{s}$, there exist an integer $q > 1$ and a binary spacetime $U$ such that, for the candidates

$$c_0 = (p_0, \mathbf{s}), \qquad c_1 = (q \cdot p_0, q \cdot \mathbf{s} \bmod \mathbf{D}),$$

the following hold:

(i) $\lambda_{c_0} > 0$,

(ii) $\lambda_{c_1} = 0$,

(iii) $\text{NML}(c_1, T) < \text{NML}(c_0, T)$ for all sufficiently large $T$.

*Proof sketch.* Construct a spacetime $U$ as follows. Let $B$ be an exactly $(p_0, \mathbf{s})$-periodic binary field. Choose an integer $q > 1$ and a second $(p_0, \mathbf{s})$-periodic field $B' \neq B$. Define $U[t, \mathbf{x}] = B[t, \mathbf{x}]$ when $\lfloor t / p_0 \rfloor \not\equiv 0 \pmod{q}$, and $U[t, \mathbf{x}] = B'[t, \mathbf{x}]$ otherwise.

Under candidate $c_0 = (p_0, \mathbf{s})$: the template must choose one value per orbit class, but the orbit classes that include both $B$-steps and $B'$-steps have mixed values. Since $B' \neq B$, at least one $(p_0,\mathbf{s})$-orbit class mixes two symbols with asymptotic frequencies $1/q$ and $(q-1)/q$, so $\lambda_{c_0} > 0$.

Under candidate $c_1 = (q \cdot p_0, q \cdot \mathbf{s} \bmod \mathbf{D})$: the template has $q$ independent layers (one per residue class of $\lfloor t/p_0 \rfloor \bmod q$). Each layer sees a constant pattern, so all orbit classes are pure: $\lambda_{c_1} = 0$.

By Theorem 3(ii), $c_1$ eventually beats $c_0$, proving (iii). $\square$

The observed spacetime does not intrinsically separate into "background" plus "residual" without additional assumptions. The selected period is the one that best compresses the *entire* spacetime, not necessarily the one matching an external notion of "true background period."

### 2.7 Identifiability for Eventually Exactly Periodic Backgrounds

**Definition 5.** The *true background period* $p_0$ of a CA spacetime is the smallest period for which there exist a shift $\mathbf{s}$ and a transient time $T_0$ such that

$$U[t + p_0, \mathbf{x} + \mathbf{s} \bmod \mathbf{D}] = U[t, \mathbf{x}]$$

for all $t \geq T_0$ and all spatial indices $\mathbf{x}$. That is, after a finite transient the spacetime is exactly relative-periodic with period $p_0$.

**Theorem 5 (Identifiability for Eventually Exactly Periodic Backgrounds).** Let $p_0$ be the true background period (Definition 5) for some shift $\mathbf{s}$, witnessed by a transient time $T_0$. Then for any velocity-matched strict multiple $p = m \cdot p_0$ ($m > 1$) with shift $m \cdot \mathbf{s} \bmod \mathbf{D}$:

(i) The per-site NLL rates are equal: $\lambda_p = \lambda_{p_0} = 0$.

(ii) The NLL difference satisfies:

$$\text{NLL}(p, T) - \text{NLL}(p_0, T) = O(1).$$

(iii) The NML score difference satisfies:

$$\text{NML}(p, T) - \text{NML}(p_0, T) = \frac{(m-1) k_{p_0}}{2} \log_2 T + O(1) \to +\infty.$$

(iv) Therefore NML selects $p_0$ over $p$ for all sufficiently large $T$.

*Proof.* After time $T_0$, the spacetime is exactly $(p_0,\mathbf{s})$-periodic, so every $(p_0,\mathbf{s})$-orbit class is pure outside the finite prefix $t < T_0$. Hence $\lambda_{p_0} = 0$. The same exact periodicity implies exact $(p, m\mathbf{s})$-periodicity for every multiple $p = m \cdot p_0$, so $\lambda_p = 0$ as well. This proves (i).

Only orbit classes intersecting the finite transient prefix $t < T_0$ contribute nonzero NLL. There are finitely many such classes. For each such class, passing from $p_0$ to $p = m \cdot p_0$ splits one class into $m$ sub-classes, but the total number of transient disagreements in that class stays fixed. The change in Bernoulli MLE codelength from such a split is bounded by a constant depending only on the transient counts and on $m$, not on $T$. Summing over the finitely many transient classes gives (ii).

Meanwhile, the complexity difference is:

$$\text{COMP}(p,T) - \text{COMP}(p_0,T) = \frac{m \cdot k_{p_0}}{2} \log_2 \frac{T}{m \cdot p_0} - \frac{k_{p_0}}{2} \log_2 \frac{T}{p_0} + O(1) = \frac{(m-1) k_{p_0}}{2} \log_2 T + O(1).$$

Combining this with (ii) gives (iii). Since the score difference tends to $+\infty$, the higher-period model is eventually worse, proving (iv). $\square$

**Remark.** Theorems 4 and 5 are complementary: when the background is eventually exactly periodic after a finite transient, NML recovers the true period (Theorem 5); when residuals have their own periodic structure, NML absorbs them into higher-period templates (Theorem 4). The distinction between "background periodicity" and "residual periodicity" is not intrinsic to the observation.

### 2.8 Geometric Diagnostics: Run-Length and LZ4

The NML criterion (Definition 4) is the primary model selector. For geometric analysis of projection residual masks *after* model selection, we use two compression-based diagnostics:

**Run-length codelength** $L_{\text{RL}}(M)$: Elias-gamma code over run lengths of the flattened residual mask. This measures spatial clustering: a contiguous residual block costs $O(\log n)$ bits, while $w$ scattered residuals cost $\Omega(w \log(n/w))$ bits.

**LZ4 codelength** $L_{\text{LZ4}}(M)$: LZ4 compression of the packed residual mask. A practical compressor proxy.

**Proposition 1 (Run-Length Separation).** Two binary masks of the same size and Hamming weight can have run-length codelengths differing by a factor of $\Omega(\log n)$.

*Proof sketch.* A mask of weight $w$ with a single contiguous block has RL codelength $O(\log n)$. A mask of the same weight with $w$ isolated defects has RL codelength $\Omega(w \log(n/w))$. $\square$

These diagnostics are *not* used for model selection — they depend on traversal order and do not correspond to the NML data-fit term. They are useful for characterizing residual geometry after the NML-selected model is fixed.

---

## 3. Cross-Dimensional Experiments

We test Theorem 3 by sweeping the observation length $T$ and tracking the NML-selected period across 1D, 2D, and 3D cellular automata.

### 3.1 1D Elementary CA

ECA rules 30, 54, and 110 on a ring of width 192, scanning shifts $\pm 6$, periods 1–10.

**NML-optimal decomposition (T = 144, best across all scanned shifts):**

| Rule | Best $(s, p)$ | Defect Rate | NLL Bits | Complexity | NML Bits |
|------|---------------|-------------|----------|------------|----------|
| 54   | $(0, 4)$      | 20.1%       | 17,477   | 1,985      | 19,462   |
| 110  | $(0, 7)$      | 30.8%       | 22,842   | 2,931      | 25,774   |
| 30   | $(5, 1)$      | 46.3%       | 27,489   | 688        | 28,177   |

The known complexity hierarchy Rule 54 < Rule 110 < Rule 30 [1,2,3] is recovered under NML ranking. Note that Rule 30's NML-optimal shift is 5 (not 0), reflecting the diagonal structure of its spacetime.

**Period stabilization (1D):**

| Rule | T=50 | T=100 | T=200 | T=400 | T=600 | T=800 | Margin at T=800 |
|------|------|-------|-------|-------|-------|-------|-----------------|
| ECA-54  | 4 | 4 | 4 | 4 | 4 | 4 | 1,993 |
| ECA-110 | 7 | 7 | 7 | 7 | 7 | 7 | 18,378 |
| ECA-30  | 1 | 1 | 1 | 1 | 1 | 1 | 598 |

All three 1D rules show *immediate* stabilization — the NML-selected period is constant from T=50 onward, with positive margins at every point. Margins grow linearly in $T$, indicating distinct per-site NLL rates ($\lambda_c$ values) and confirming that Theorem 3(iv) applies. Rule 110 shows the strongest separation (margin 18,378 bits at T=800), consistent with its pronounced period-7 Ether background.

### 3.2 2D Totalistic Rules

#### 3.2.1 Survey

We survey 1,050 range-threshold totalistic rules on a 48×48 torus (Moore neighborhood, 40 steps, density 0.5, seed 11). A cell survives if $s_{\text{lo}} \leq n \leq s_{\text{hi}}$ and is born if $b_{\text{lo}} \leq n \leq b_{\text{hi}}$, with range widths $\leq 4$. Of 1,050 candidates, 773 produce non-trivial dynamics (end density between 2% and 98%). Of these, 172 have nonzero best-fit shift (drifting periodic structure).

Top rules by NML score are near-fixed-point patterns with $<1\%$ defect rates — NML correctly identifies these as the simplest descriptions. Period-2 oscillators (159 rules) appear at NML rank ~20, with no period $\geq 3$ selected at this short horizon (40 steps). Period distribution: 614 period-1, 159 period-2.

This survey characterizes the NML-selected period distribution at a single short horizon. It does not by itself demonstrate stabilization, which requires tracking period selection as $T$ grows (Section 3.2.3).

#### 3.2.1b LifeWiki Named Rules Survey

We also survey all 106 named Life-like rules from the LifeWiki [13] using the general (non-contiguous) B/S notation. Unlike the range-threshold survey above, this includes rules with non-contiguous birth/survival sets (e.g., B36/S23 = HighLife, B3678/S34678 = Day & Night).

**Setup.** 64×64 torus, density 0.5, seed 42, periods 1–8, shifts $-2$ to $+2$ in each spatial dimension. The general-purpose Life-like simulator supports arbitrary B/S rulestrings via lookup tables.

**Results at T=100** (105 nontrivial rules):

| Period | Count | Notable Rules |
|--------|-------|---------------|
| p=1 | 97 | Life, HighLife, Day & Night, Coral, Diamoeba, ... |
| p=2 | 7 | B01245/S01245, Oils, B026/S1, Long Life, Majority, ... |
| p=8 | 1 | Fredkin (B1357/S02468) |

All selections are `stable_winner` (margin > 2 bits). Six rules select nonzero shift (drifting backgrounds): Seeds (1,0), Live Free or Die (0,-1), Gnarl (0,2), B25/S4 (1,0), Dance (0,-1), Feux (2,0).

**Results at T=400** (103 nontrivial rules):

| Period | Count | Notable Rules |
|--------|-------|---------------|
| p=1 | 94 | Life, HighLife, Day & Night, Coral, ... |
| p=2 | 7 | +Diamoeba, +Maze with Mice; −Serviettes |
| p=4 | 1 | B017/S01 (was p=2 at T=100) |
| p=8 | 1 | Fredkin |

Three rules changed period between T=100 and T=400:

| Rule | T=100 | T=400 | Interpretation |
|------|-------|-------|----------------|
| Diamoeba (B35678/S5678) | p=1 | **p=2** | Period-2 oscillation: NLL gap grows from 7,749 to 17,085, crossing the complexity threshold at T≈400 |
| Maze with Mice (B37/S12345) | p=1 | **p=2** | Period-2 "mice" oscillators visible at longer horizon |
| B017/S01 | p=2 | **p=4** | Deeper periodic structure revealed |
| Serviettes (B234/S) | p=2 | **p=1** | Transient period-2 signal; at T=400 complexity cost dominates |

This demonstrates Theorem 3 in action: the NLL improvement for genuine periodic structure grows as $\Theta(T)$ while complexity grows as $O(\log T)$, so real periodic signals eventually overcome the penalty. Conversely, spurious signals (Serviettes) are correctly eliminated as the horizon grows. Among the 106 named rules, **Fredkin's period-8 selection stands out** — its parity-rule replication cycle produces the only period $>4$ in the entire catalog.

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

Rules with near-zero NML margins (S25/B12, S11/B37) show seed-dependent period selection at short horizons — consistent with Theorem 3, which requires the linear NLL gap to dominate at large $T$.

#### 3.2.3 Period Stabilization (2D)

| Rule | T=60 | T=100 | T=200 | T=400 | T=600 | T=800 | Margin at T=800 |
|------|------|-------|-------|-------|-------|-------|-----------------|
| S24/B11 | 1 | 1 | 1 | 2 | 2 | 2 | 13,115 |
| S11/B37 | 2 | 2 | 2 | 4 | 4 | 4 | 22,352 |
| S37/B11 | 1 | 1 | 2 | 2 | 2 | 2 | 16,006 |

The 2D persistent-residual rules show *progressive* stabilization: the NML-selected period increases in discrete jumps (1→2 for S24/B11, 2→4 for S11/B37, 1→2 for S37/B11), then locks with growing margins. This is the regime described by Theorem 4 (nonidentifiability): periodic residual structure is absorbed into higher-period templates, and NML correctly identifies the period that best compresses the entire spacetime.

Notably, NML selects *lower* periods than a previous formulation that used RL codelength as the data-fit term. For example, S24/B11 stabilizes to period 2 under NML vs period 6 under that RL-based MDL criterion — the RL artifact inflated the data-fit term for higher periods, making them appear artificially competitive.

### 3.3 3D Totalistic Rules

Diamoeba3d rule (survive 5–8, birth 5–8) on a 16×16×16 3-torus, shift (0,0,0):

| T | Period | NML Bits | Margin |
|---|--------|----------|--------|
| 10 | 6 | 26,406 | 5,560 |
| 20 | 6 | 75,703 | 3,055 |
| 40 | 1 | 158,154 | 3,505 |
| 60 | 1 | 232,856 | 4,872 |
| 80 | 1 | 303,209 | 5,840 |

The initial T=10–20 selection of period 6 is a small-sample artifact (10–20 time steps with a period-6 model means only 1–3 full cycles per orbit class, where overfitting is expected). By T=40, NML stabilizes to period 1, with margins growing monotonically thereafter — consistent with Theorem 3 in 3D. Note that the margin *drops* from T=10 to T=20 (5,560 → 3,055) before the period switches; this is expected during the pre-stabilization transient. The 3D-life rule (survive 4–5, birth 5) dies out, providing a null result.

### 3.4 Summary of Stabilization Evidence

| Dimension | Rules Tested | Stabilization Onset | Behavior |
|-----------|-------------|--------------------|-----------|
| 1D | ECA 30, 54, 110 | Immediate (T=50) | Period locked from first measurement |
| 2D | 3 persistent-residual rules | T=200–400 | Progressive jumps, then locked |
| 2D | 106 LifeWiki named rules | T=100–400 | 3 rules change period; 103 stable |
| 3D | diamoeba3d | T=40 | Initial transient, then locked |

In all tested cases, the NML-selected period makes finitely many transitions then stabilizes over the observed range, consistent with Theorem 3. The margins grow after the selected period locks, providing empirical evidence that the asymptotic regime has been reached, though finite data cannot prove this. The stabilization rate depends on how quickly the per-site NLL rates $\lambda_c$ separate: 1D rules separate immediately, 3D rules after one correction, and 2D persistent-residual rules (where residuals have their own periodic structure) take longest.

These results cover a small number of detailed case studies (3 rules per dimension). The broader 2D survey (Section 3.2.1) characterizes period *distribution* at a single short horizon, not stabilization.

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

5 seeds, grid sizes 32–192, 100 steps. In the tables below, *Mean Rate* is the defect rate $r = \|M\|_1 / N(T)$ averaged over seeds (computed over the late half of the simulation, $t > T/2$). *Late Defects* is the mean number of defect sites per time step in the late half. *Defect Density* is Late Defects divided by the spatial grid area $D^2$, measuring defects per spatial site per time step.

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

1. **Hamming-optimal decomposition** in $O(|U|)$ time per candidate model, for any dimension.
2. **A formal explanation** of overcapacity (Theorem 2), showing why naive defect-rate ranking is inadequate.
3. **A stabilization theorem** (Theorem 3) proving that every suboptimal candidate is eventually excluded, and that when the rate-minimizer is unique, NML selection locks to a single winner. The proof requires only convergent orbit-class frequencies and no assumption on residual geometry.
4. **A nonidentifiability result** (Theorem 4) showing by explicit construction that background period recovery is impossible in general, with recovery guaranteed when the background is eventually exactly periodic after a finite transient (Theorem 5).

The key insight is that the *same* theoretical framework — orbit classes → Bernoulli estimation → NML stabilization — applies without modification across spatial dimensions.

### 5.2 NML vs Legacy MDL

A previous formulation used a two-part MDL criterion: approximate parametric penalty $\frac{k}{2}\log_2(T/p)$ plus run-length codelength $L_{\text{RL}}$ of the residual mask. This had three weaknesses:

1. **Model mismatch**: the RL codelength is not the data-fit term of the Bernoulli model implied by the orbit-class structure. NLL is.
2. **Geometry dependence**: RL codelength depends on the spatial arrangement of residuals and the flattening order, making it non-intrinsic.
3. **Extra assumption**: the convergence proof required an $\Omega(T)$ runs condition to ensure $L_{\text{RL}} = \Theta(T)$, which NML does not need.

In practice, NML and MDL agree on period selection for most rules (e.g., both select period 4 for Rule 54). They diverge for 2D rules with periodic residuals, where NML selects lower, more parsimonious periods.

We retain RL and LZ4 codelengths as geometric diagnostics (Section 2.8) for characterizing residual spatial structure after model selection.

### 5.3 What the Framework Does Not Provide

The method identifies *where* residuals are but not *how* they interact. It does not recover domain/particle structure in the computational mechanics sense [1,2]. The fitted backgrounds are nearest periodic fields, not exact CA orbits. Component-level lifetime and interaction analysis is future work.

### 5.4 Limitations

0. **Monotonicity requires velocity matching.** Theorem 2 holds along constant-velocity chains ($s_2 = m \cdot s_1 \bmod D$), not arbitrary period multiples with the same shift. For shift-zero scanning (the empirically dominant case), all divisibility chains satisfy the condition. For nonzero shifts, this restriction matters.
1. **Shift scanning matters for some rules but not the case studies.** The three rules examined in detail (S24/B11, S11/B37, S37/B11) all have best-fit shift $(0,0)$. In the broader 2D survey, however, 172 of 773 non-trivial rules have nonzero best-fit shift. The theoretical framework supports arbitrary shifts, but the detailed convergence analysis in Section 3.2.3 covers only shift-zero cases.
2. **NML selects the best-compressing period, not necessarily the "true" period.** When residuals have their own periodicity, NML absorbs them into higher-period templates (Theorem 4). This is principled but may not match a physicist's intuition.
3. **Asymptotic NML complexity.** The $\frac{1}{2}\log_2 n_j$ complexity term is an asymptotic approximation to the Bernoulli NML normalizer. For very small orbit classes ($n_j < 10$), the approximation is less tight — relevant only at the smallest $T$ values.
4. **Bernoulli i.i.d. assumption.** Within each orbit class, the NML criterion treats observations as i.i.d. Bernoulli. In reality, successive observations within an orbit class are separated by $p$ time steps and may have temporal correlations. Under (A1), these correlations do not affect the asymptotic rate, but they may affect finite-sample behavior.
5. **Stabilization requires unique rate-minimizer.** Theorem 3 proves full stabilization only when a unique candidate achieves the minimum per-site NLL rate. When multiple candidates share the minimal rate, only elimination of non-rate-minimizers is guaranteed. In practice, rate ties have not been observed in our experiments.

### 5.5 Future Work

1. **Component tracking**: lifetimes, velocities, collision catalogs.
2. **Direct comparison** with local causal states [4] on Rule 54 and 2D rules.
3. **Larger surveys**: extend to 1000+ 2D rules and broader 3D rule families.
4. **Finite-sample corrections**: exact (non-asymptotic) Bernoulli NML normalizer, or plug-in corrections for small orbit classes.
5. **Shift optimization**: joint NML optimization over both shift and period.
6. **Period-level selection**: defining the score of a period as $\min_{\mathbf{s}} \text{NML}(p, \mathbf{s})$ would make the selected *period* the primary output; the associated shift becomes a secondary attribute. This may simplify the stabilization analysis since same-period candidates always share the same $k_c$.

---

## 6. Conclusion

We have proved that Bernoulli NML model selection over relative-periodic CA backgrounds stabilizes: every candidate whose per-site NLL rate exceeds the minimum is eventually excluded (Theorem 3). When the rate-minimizing candidate is unique — as it is in all cases we test — the selected model locks to a single winner, though the selected period need not correspond to any external notion of "true background period" (Theorem 4). The proof requires only convergent orbit-class frequencies — no assumption on residual geometry — and is dimension-agnostic, resting on the orbit-class reduction that decomposes spatiotemporal fitting into independent Bernoulli estimation. When the background is eventually exactly periodic after a finite transient, NML recovers the true period (Theorem 5); when residuals are periodic, NML correctly absorbs them into the template.

Cross-dimensional experiments on 1D elementary CA, selected 2D totalistic rules, and a 3D totalistic rule are consistent with the stabilization prediction, with NML-selected periods locking and margins growing after stabilization. As an application, the framework identifies 2D rules with persistent structured projection residuals exhibiting extensive scaling — candidates for further computational-mechanics analysis.

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

All code is open-source: [AUTHOR INSERT REPO URL], commit [AUTHOR INSERT COMMIT HASH].

Key parameters:
- 1D ECA: width=192, steps=144, density=0.5, seed=11, shifts=−6..+6, periods=1..10
- 1D convergence: T=[50, 100, 200, 400, 600, 800], periods=1..10
- 2D survey: 48×48, steps=40, 1,050 candidates (773 non-trivial), range width ≤ 4, shifts=±3
- 2D convergence: 64×64, T=[60, 100, 200, 400, 600, 800], periods=1..8
- 3D convergence: 16×16×16, T=[10, 20, 40, 60, 80], periods=1..6
- Multi-seed: seeds=[11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]
- Size scaling: grids=[32, 64, 96, 128, 192], steps=100, 5 seeds
- 400-step verification: 64×64, steps=400, seed=11
- Model selector: Bernoulli NML (orbit-class NLL + asymptotic parametric complexity)

## Appendix B: Geometric Diagnostics

Run-length and LZ4 codelengths are used as geometric diagnostics, not for model selection. Example: two synthetic masks of size 512, each with 64 defects — clustered (42 RL bits) vs scattered (251 RL bits), a 6× ratio at identical Hamming weight. This illustrates Proposition 1 and motivates RL/LZ4 as post-selection residual geometry characterizers.

## Appendix C: NML vs Legacy MDL Period Selection

The table below compares NML-selected and MDL-selected periods. For 1D rules, the comparison is at $T = 800$ [AUTHOR VERIFY HORIZON]. For 2D rules, $T = 800$. For diamoeba3d, $T = 80$ [AUTHOR VERIFY HORIZON].

| Rule | MDL Period | NML Period | Agreement |
|------|-----------|-----------|-----------|
| ECA-54 (1D) | 4 | 4 | Yes |
| ECA-110 (1D) | 7 | 7 | Yes |
| ECA-30 (1D) | 1 | 1 | Yes |
| S24/B11 (2D, T=800) | 6 | 2 | No — NML more parsimonious |
| S11/B37 (2D, T=800) | 8 | 4 | No — NML more parsimonious |
| S37/B11 (2D, T=800) | 6 | 2 | No — NML more parsimonious |
| diamoeba3d (3D) | 1 | 1 | Yes |

NML and MDL agree for 1D and 3D rules but diverge for 2D rules with periodic residuals, where the RL data-fit artifact in MDL inflates scores for higher periods.

## Appendix D: RL Rate Convergence for Finite Deterministic CA

This appendix establishes that the per-site run-length rate converges for finite deterministic CA, closing the gap noted in the run-length encoding remark of Section 2.5.

**Lemma D.1 (RL convergence for eventually periodic sequences).** Let $b_1, b_2, \ldots$ be a binary sequence that is eventually periodic with pre-period $T_0$ and period $Q$. Then $\lim_{N \to \infty} L_{\text{RL}}(b_1 \cdots b_N) / N = C / Q$, where $C$ is the per-period RL cost.

*Proof.* Write $N = T_0 + MQ + R'$ with $0 \leq R' < Q$. The RL codelength is $L_{\text{RL}} = L_{\text{transient}} + M \cdot C + O(\log Q)$, so $L_{\text{RL}} / N \to C/Q$ as $M \to \infty$. $\square$

**Theorem D.2 (RL Rate Convergence for Finite CA).** Let $U$ be the spacetime of a deterministic CA on finite spatial domain $\{0,1\}^D$, and let $(p, s)$ be a candidate model. Assume no exact frequency ties: for each orbit class $j$, $\theta_j^* \neq 1/2$. Then $\lim_{T \to \infty} L_{\text{RL}}(M^*_c(T)) / (T \cdot D)$ exists.

*Proof sketch.* (1) The CA state sequence is eventually periodic (pigeonhole on $\{0,1\}^D$). (2) Orbit-class frequencies converge at rate $O(1/T)$; by the no-ties assumption, the majority vote stabilizes. (3) After stabilization, the residual mask rows are periodic, so the flattened mask is eventually periodic. (4) By Lemma D.1, $L_{\text{RL}}/N$ converges. $\square$

**Corollary D.3 (Unconditional NML convergence).** For a deterministic CA on a finite spatial domain, the per-site NLL converges *unconditionally* (no ties assumption needed): $\lim_{T \to \infty} \text{NLL}_c(T) / N(T) = \lambda_c$ exists.

*Proof.* The per-orbit-class frequency $\hat{\theta}_j(T) \to \theta_j^*$ by eventual periodicity, without requiring the no-ties condition. Since $H_b$ is continuous, $n_j \cdot H_b(\hat{\theta}_j) / N(T) \to (1/k_c) \cdot H_b(\theta_j^*)$. Summing gives $\lambda_c$. When $\theta_j^* = 1/2$, the NLL contribution is $n_j$ bits regardless of tie-breaking, so NLL does not depend on the no-ties condition. Combined with the $O(\log T)$ complexity, Theorem 3 applies. $\square$

**Remark.** When $\theta_j^* = 1/2$ exactly, the majority vote may oscillate with $T$, potentially changing $L_{\text{RL}}$ by $\Theta(T)$ per flip. This is non-generic but possible (e.g., Rule 30 on width 8 has all classes with $\theta^* = 0.5$). NML is preferable to RL as a selector because NML converges unconditionally.
