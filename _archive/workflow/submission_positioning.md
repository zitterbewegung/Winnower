# Submission Positioning

## Novelty Assessment

The paper makes three classes of contribution:

**Genuinely novel:**
- Bernoulli NML model selection for relative-periodic CA backgrounds, with a stabilization theorem (Theorem 3) proving eventual elimination of suboptimal candidates — no prior work proves this for periodic CA template selection
- Nonidentifiability result (Theorem 4) and its complement (Theorem 5): formal characterization of when background period recovery is and is not possible
- Systematic 2D surveys: 773 range-threshold rules + 106 LifeWiki named rules analyzed with the same NML framework, producing a quantitative catalog — broader than any prior periodic-structure survey of 2D Life-like rules
- Unified N-dimensional framework with shift vectors — same code and theory for 1D/2D/3D
- Baseline selector comparison showing NLL and residual minimization degenerate to overfitting without complexity penalty (NLL selects p=8 for all 105 nontrivial LifeWiki rules; NML selects p=1 for 97/105)
- Finite-horizon stabilization sweep across 9 rules in 1D/2D/3D showing ≤2 transitions before locking, with post-lock margins growing monotonically

**Framework/synthesis contribution (not fundamentally new primitive):**
- Relative-periodic background fitting via majority voting on orbit classes — conceptually related to Crutchfield's domain identification, but implemented as a global projection rather than local epsilon-machine construction
- Using compression-based diagnostics (RL, LZ4) for residual geometry — related to Zenil's compression-based CA classification, but applied to projection residuals rather than raw spacetimes

**Incremental over prior art:**
- 1D ECA results (Rule 54/110/30 hierarchy) are consistent with known computational-mechanics results, quantified differently
- Persistent-defect identification in 2D — conceptually analogous to Rule 54 particles, but discovered via automated survey rather than domain-specific analysis

## Experiment Package (v10)

The paper now includes two dedicated experiments beyond the core surveys:

1. **Baseline selector comparison** (Section 3.5): Three selectors (argmin defect_rate, argmin NLL, argmin NML) compared on 106 LifeWiki rules, 3 ECA rules, and 1 3D rule. Directly demonstrates that the complexity penalty is necessary, not just theoretically motivated.

2. **Finite-horizon stabilization sweep** (Section 3.6): 9 representative rules × 6 horizons (T=50–800 for 1D/2D, T=10–80 for 3D). Shows empirical stabilization with quantitative margin growth. All rules achieve stable_winner status. At most 2 period transitions observed.

These experiments strengthen the submission by providing direct empirical support for Theorems 2 and 3, moving beyond the survey-level evidence in earlier drafts.

## Reviewer Concerns to Anticipate

1. **Computational mechanics comparison**: Referees from the Crutchfield school will ask why this method doesn't directly compare against epsilon-machines or local causal states on shared benchmarks (especially Rule 54). The paper acknowledges this as future work.
2. **"Just majority voting"**: The projection theorem (Theorem 1) is elementary. The value is in the framework: connecting it to NML, proving stabilization, and applying it at scale.
3. **Single-seed surveys**: Most survey results use a single seed. Multi-seed validation is shown for selected rules only.
4. **Asymptotic NML**: The complexity term is asymptotic, not exact Shtarkov. Paper is honest about this.
5. **ECA-110 discrepancy**: Section 3.1 and Section 3.6 report different selected periods for ECA-110. This reflects different selection pipelines and is flagged with [AUTHOR VERIFY].

## Recommended Venues

### Best fit: ALIFE 2026
- **Deadline**: March 30, 2026
- **Format**: 8-page extended abstract
- **Why**: Strong CA community, method/framework papers welcome, empirical breadth valued, interdisciplinary audience. The expanded experiment package (baseline comparison + stabilization sweep) fits well within 8 pages as summary tables.
- **Risk**: Low — the cross-dimensional scope and survey scale fit well

### Strong fit: Complex Systems
- **Format**: Full journal paper, no strict page limit
- **Why**: Published Redeker's particle language paper, CA-focused, values systematic surveys and formal frameworks. Full experiment details can be included.
- **Risk**: Moderate — may want deeper connection to computational mechanics literature

### Strong fit: Journal of Cellular Automata
- **Format**: Full journal paper
- **Why**: Dedicated CA venue, values formal CA analysis, surveys, and classification results
- **Risk**: Low — but smaller readership than Complex Systems

### Ambitious: Chaos (AIP)
- **Format**: Regular article
- **Why**: Published Rupe & Crutchfield (2018) on local causal states; values information-theoretic approaches to spatiotemporal systems
- **Risk**: Higher — referees will expect direct comparison with computational mechanics and possibly experimental physics connections

### Ambitious: Physica D
- **Format**: Regular article
- **Why**: Published Crutchfield & Hanson (1997); foundational venue for CA theory
- **Risk**: Higher — strong theoretical expectations, may want deeper mathematical content or broader dynamical-systems framing

### Fallback: Entropy (MDPI)
- **Format**: Open access, information-theory focus
- **Why**: MDL/NML model selection fits the scope; CA applications welcome
- **Risk**: Low acceptance bar but lower prestige
