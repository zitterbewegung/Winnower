# Manuscript Patch

Concrete replacement text for paper_v7.md. Only sections requiring changes are shown.
All wording below is mathematically honest.

---

## Title

**Current:** Consistent Period Selection for Cellular Automaton Spacetimes via Orbit-Class MDL

**Replacement:** Model Selection Stabilization for Relative-Periodic Decomposition of Cellular Automaton Spacetimes

**Rationale:** "Consistent" has a specific meaning in statistics (convergence to the true parameter). The theorem proves *stabilization* of a finite selector, not statistical consistency in the classical sense. "MDL" in the title is acceptable but the body should clarify the exact score.

---

## Abstract

**Replacement:**

We prove that model selection over relative-periodic backgrounds of cellular automaton (CA) spacetimes stabilizes to a unique period as the observation window grows. The argument rests on a dimension-agnostic *orbit-class reduction*: fitting a relative-periodic background to a binary spacetime decomposes into independent majority voting on orbit classes (Theorem 1), partition refinement along constant-velocity chains makes higher periods monotonically more expressive (Theorem 2), and a Bernoulli NML criterion with $O(\log T)$ complexity penalty against $\Theta(T)$ data-fit cost yields eventual stabilization of the selected model (Theorem 3). We also prove that background period recovery is impossible in general without additional assumptions (Theorem 4). The theory applies identically to 1D, 2D, and 3D automata.

Cross-dimensional experiments validate the stabilization: selected periods lock for 1D elementary CA (rules 30, 54, 110), 2D totalistic rules (458 non-trivial from 621 candidates), and 3D totalistic rules — with margins growing after stabilization. As an application, the framework identifies three 2D rules with persistent structured projection residuals, including one (S37/B11) exhibiting extensive residual scaling verified at 400 steps, across multiple seeds, and at grid sizes up to 192x192.

**Changes:** "converges" → "stabilizes"; "MDL consistency" → "eventual stabilization"; "defects" → "projection residuals" (in formal context); added Theorem 4 (nonidentifiability); removed claim of "consistent model selection" which overstates.

---

## Section 2.3: Monotonicity and Overcapacity

**Replacement:**

**Theorem 2 (Monotonicity under Velocity-Matched Refinement).** Let $(p_1, \mathbf{s}_1)$ and $(p_2, \mathbf{s}_2)$ be two relative-periodic models. If there exists an integer $m \geq 1$ such that $p_2 = m \cdot p_1$ and $s_2^{(i)} \equiv m \cdot s_1^{(i)} \pmod{D_i}$ for each spatial dimension $i$, then the orbit partition under $(p_2, \mathbf{s}_2)$ refines the partition under $(p_1, \mathbf{s}_1)$, and:

$$d^*(p_2, \mathbf{s}_2) \leq d^*(p_1, \mathbf{s}_1)$$

The condition $s_2 = m \cdot s_1 \pmod{D}$ means the two models share the same *characteristic velocity* $\mathbf{s}/p$. In particular, for shift $\mathbf{s} = \mathbf{0}$, monotonicity holds along all divisibility chains $p, 2p, 3p, \ldots$

*Proof.* Under the stated condition, the periodicity map $\tau_2: (t, \mathbf{x}) \mapsto (t + p_2, \mathbf{x} + \mathbf{s}_2 \bmod \mathbf{D})$ equals $\tau_1^m$, the $m$-fold composition of the $(p_1, \mathbf{s}_1)$ map. Therefore, the $\tau_2$-orbit of any point is a subset of its $\tau_1$-orbit, so the $\tau_2$-partition refines the $\tau_1$-partition. By Theorem 1, optimizing over a finer partition can only reduce total disagreement. $\square$

**Remark.** The velocity-matching condition is necessary in general. For example, on a ring of width 4, the models $(p=1, s=1)$ and $(p=2, s=1)$ share the same shift but *not* the same velocity ($1/1 \neq 1/2$). The checkerboard spacetime $U[t,x] = (t+x) \bmod 2$ has $d^*(1,1) = 0$ but $d^*(2,1) = 4$, violating monotonicity. (See `tests/test_theory.py::TestMonotonicityCounterexample`.)

**Corollary (Overcapacity).** Along any constant-velocity divisibility chain, the residual count is monotonically non-increasing. This creates an *overcapacity problem*: naive residual-count minimization always prefers the highest available period. This motivates the complexity-penalized criterion below.

---

## Section 2.4: Model Selection Criterion

**Replacement:**

**Definition 3 (Bernoulli NML Score).** For model $(p, \mathbf{s})$ with orbit classes $\{O_j\}_{j=1}^{k}$ where $k = p \prod_i D_i$, each orbit class $O_j$ has $n_j = \lfloor T/p \rfloor$ or $\lceil T/p \rceil$ observations. The Bernoulli NML score is:

$$\text{NML}(p, \mathbf{s}) = \underbrace{\sum_{j=1}^{k} n_j \, H_b(\hat\theta_j)}_{\text{negative log-likelihood}} + \underbrace{\sum_{j=1}^{k} \frac{1}{2} \log_2 n_j}_{\text{asymptotic parametric complexity}}$$

where $\hat\theta_j = n_j^{(1)} / n_j$ is the empirical frequency of 1s in orbit class $j$, and $H_b(\theta) = -\theta \log_2 \theta - (1-\theta) \log_2(1-\theta)$ is binary entropy.

The first term is the exact Bernoulli maximum likelihood data-fit cost. The second is the asymptotic NML parametric complexity for $k$ independent Bernoulli parameters [9, Ch. 3], accurate to $O(k)$ additive bits. The combined score is an asymptotic approximation to the normalized maximum likelihood code for the orbit-class Bernoulli model. It is not exact NML (the exact normalizing constants involve sums of binomial coefficients), but the $O(k)$ error does not affect asymptotic model selection since the NLL term is $\Theta(T)$.

**Remark.** The negative log-likelihood is related to but distinct from the Hamming defect count: $\text{NLL} = \sum_j n_j H_b(\hat\theta_j)$ while the defect count is $\sum_j n_j \min(\hat\theta_j, 1 - \hat\theta_j)$. Both are zero for perfectly periodic backgrounds and positive for imperfect fits, but they weight errors differently.

---

## Section 2.5: Stabilization Theorem

**Replacement (including new Theorem 4):**

**Theorem 4 (Nonidentifiability of Background Period).** For any period $p_0$, shift $\mathbf{s}$, and MDL-type criterion with $O(\log T)$ penalty and $\Theta(T)$ data-fit cost, there exist spacetimes for which the criterion does not select $p_0$ for any $T$ beyond some threshold. Specifically, if the projection residual under $(p_0, \mathbf{s})$ has its own periodic structure with period $k > 1$, then the candidate $(k \cdot p_0, k \cdot \mathbf{s} \bmod \mathbf{D})$ absorbs the residual into its template and eventually achieves a lower total score.

The observed spacetime does not intrinsically separate into "background" plus "residual" without additional assumptions. The selected period is the one that best compresses the *entire* spacetime, not necessarily the one matching an external notion of "true background."

**Theorem 3 (Stabilization of Bernoulli NML Selection).** Let $\mathcal{C} = \{c_1, \ldots, c_m\}$ be a fixed finite candidate set. For each candidate $c$ with $k_c$ orbit classes, let $\text{NML}(c, T)$ be the Bernoulli NML score from Definition 3.

**Assumption:** For each candidate $c$, the per-site entropy rate $h_c = \lim_{T \to \infty} \text{NLL}_c(T) / N(T)$ exists, where $N(T) = T \cdot \prod_i D_i$ is the total number of spacetime sites.

**Conclusion:** There exists $T_0$ such that the NML-selected candidate $c^*(T) = \arg\min_{c \in \mathcal{C}} \text{NML}(c, T)$ is constant for all $T > T_0$. The stabilized selection minimizes $h_c$, with ties broken by $k_c$ (fewer parameters preferred).

*Proof.* The NML score decomposes as:

$$\text{NML}(c, T) = h_c \cdot N(T) + \frac{k_c}{2} \log_2 T + O(k_c)$$

For any two candidates $c_1, c_2$:

$$\text{NML}(c_1, T) - \text{NML}(c_2, T) = (h_{c_1} - h_{c_2}) \cdot N(T) + \frac{k_{c_1} - k_{c_2}}{2} \log_2 T + O(1)$$

**Case 1:** $h_{c_1} \neq h_{c_2}$. The $\Theta(T)$ term dominates, so the candidate with smaller $h$ wins permanently for all sufficiently large $T$.

**Case 2:** $h_{c_1} = h_{c_2}$. The $O(\log T)$ term dominates, and the candidate with smaller $k_c$ wins permanently.

Since $|\mathcal{C}|$ is finite, all pairwise comparisons stabilize, giving a unique winner for $T > T_0$. $\square$

**Corollary (Dimension-agnostic).** Theorem 3 makes no reference to spatial dimension. It applies identically to 1D rings, 2D tori, 3D tori, or any periodic lattice.

**Remark on run-length encoding.** An alternative MDL criterion using $\frac{k}{2} \log_2(T/p) + L_{\text{RL}}(M^*)$ (BIC-type penalty plus run-length defect encoding) satisfies an analogous stabilization theorem under the additional assumption that the per-site RL rate $\ell_c = \lim L_{\text{RL}} / N(T)$ converges. This assumption is plausible but stronger than the NLL convergence assumed above, since RL codelength depends on the spatial geometry of residuals, not just their frequency. We use the NML score as the primary selection criterion and report RL codelength as a secondary geometric diagnostic (Proposition 1).

---

## Section 3 header

**Current:** "Cross-Dimensional Validation"

**Replacement:** "Cross-Dimensional Experiments"

**Rationale:** "Validation" implies the experiments prove the theorem. They are consistent with the theorem but do not validate it (they are finite).

---

## Section 3.4 Summary

**Current:** "In all cases, the MDL-selected period makes finitely many transitions then stabilizes, exactly as Theorem 3 predicts."

**Replacement:** "In all tested cases, the NML-selected period makes finitely many transitions then stabilizes over the observed range, consistent with Theorem 3. The margins grow after stabilization in all cases, providing empirical evidence that the asymptotic regime has been reached, though finite data cannot prove this."

---

## Section 5.1

**Current:** "A consistency theorem (Theorem 3) proving MDL period selection converges"

**Replacement:** "A stabilization theorem (Theorem 3) proving that NML model selection over the finite candidate set eventually locks to a unique winner"

---

## Section 5.3 Limitations

**Add as Limitation 0 (before current list):**

0. **Monotonicity requires velocity matching.** Theorem 2 holds along constant-velocity chains ($s_2 = m \cdot s_1 \bmod D$), not arbitrary period multiples with the same shift. For shift-zero scanning (the empirically dominant case), all divisibility chains satisfy the condition. For nonzero shifts, this restriction matters.

---

## Section 6 Conclusion

**Current first sentence:** "We have proved that MDL model selection over relative-periodic CA backgrounds is consistent: the selected period converges to a unique limit as the observation window grows (Theorem 3)."

**Replacement:** "We have proved that Bernoulli NML model selection over relative-periodic CA backgrounds stabilizes: the selected period eventually locks to a unique winner as the observation window grows (Theorem 3), though the selected period need not correspond to any external notion of 'true background period' (Theorem 4)."

---

## Terminology replacements (global)

| Current | Replacement | Scope |
|---------|-------------|-------|
| "MDL consistency" | "model selection stabilization" | throughout |
| "converges to" (re: period) | "stabilizes to" or "locks to" | throughout |
| "defects" (formal context) | "projection residuals" | theorems, definitions |
| "defects" (informal) | acceptable with disclaimer | discussion, applications |
| "exact NML" | "asymptotic NML" or "Bernoulli NML" | throughout |
| "NML parametric complexity" | "asymptotic parametric complexity" | Definition 3 |
| "convergence confirmed" | "empirical stabilization observed" | Section 3 |
