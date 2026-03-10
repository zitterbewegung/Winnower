# Relative Symmetry-Repair for Cellular Automata: Conclusions

## Method

We fit **relative-periodic backgrounds** B[t+p, (x+s) mod W] = B[t, x] to cellular automaton spacetimes across a grid of (shift, period) pairs. The residual (defect mask) is then analyzed via:
- Defect rate (fraction of disagreeing sites)
- Run-length bits (codelength of defect mask — measures geometric structure)
- LZ4 bits (practical compression proxy)
- Rule consistency error (whether the fitted background obeys the CA rule)
- Connected component extraction (defect "particles")

## Key Results

### 1D Elementary Cellular Automata
- **Rule 54**: Best fit at shift=0, period=8, ~20% defect rate. Defects collapse into clean world-tubes and domain walls — the canonical case of localized excitations on a periodic background.
- **Rule 110**: Intermediate case at shift=0, period=7, ~31% defect rate. Real coherent organization but more complicated residual dynamics.
- **Rule 30**: Weak relative periodicity at shift=-5, period=10, ~39% defect rate. Defects remain diffuse — no sharp spectral valley.

### Defect Geometry vs. Defect Count
Two masks with **identical** defect counts (64/512 = 12.5%) have vastly different run-length costs: **42 bits** (clustered) vs. **251 bits** (random). This demonstrates that Hamming distance alone misses structural content — the codelength of the repair encodes geometric information that raw defect count does not.

### 2D Totalistic Rules Survey (~700 rules scanned)
- **S14/B11**: 0.85% defect rate, period 2 — best overall
- **S25/B12**: 0.91% defect rate, period 4
- **S66/B36**: 0.98% defect rate, period 2
- All top results have **zero rule error** (fitted backgrounds are dynamically consistent)
- Nonzero-shift (drifting) periodicity is rare in 2D; best shifted rules have ~18-20% defect rates

### Persistent Structured Defects in 2D (Analogue of Rule 54 Particles)
A second survey specifically targeting rules with persistent, non-vanishing defects found:
- **S24/B11**: 1.7% defect rate, defects decline from ~130 to ~11 per frame but persist
- **S11/B37**, **S37/B11**: ~2-3% defect rates with stable late-time defect populations (~23-29 per frame)
- These exhibit long-lived localized defect structures — the 2D analogue of Rule 54's particle-like excitations

### N-dimensional Generalization
The same pipeline (scan → fit → decompose → extract components) works for 1D, 2D, and 3D cellular automata with arbitrary shift vectors and periods.

## Prior Art Context

The closest prior work is **Crutchfield's computational mechanics** (epsilon-machines, domain filters for ECA Rule 54) and **Redeker's particle language formalism** for Rule 54. Key differences from our approach:

1. **Computational mechanics** builds epsilon-machines from local statistics — a bottom-up, information-theoretic approach. Our method is top-down: we directly optimize a global relative-periodic background and measure what's left.
2. **Redeker's particle formalism** extracts regular expressions from de Bruijn diagrams for specific rules. Our method is rule-agnostic — it works on any spacetime array without knowing the update rule.
3. **No prior work** (that we found) uses **codelength of the defect mask** as a metric for structural quality of the decomposition. The run-length bits vs. combinatorial bits comparison is novel.
4. **No prior work** systematically surveys 2D totalistic rules for relative-periodic structure or identifies the best-fitting 2D rules with persistent structured defects.
5. **The N-dimensional generalization** with shift vectors is new.

## Assessment of Novelty

**What is clearly novel:**
- The codelength-based quality metric for background fits (run-length bits of defect mask)
- The systematic 2D survey identifying rules like S14/B11 as having near-perfect periodic backgrounds
- The persistent-defect survey finding 2D analogues of Rule 54 particles
- The unified N-dimensional framework with shift vectors

**What is incremental over prior art:**
- The relative-periodic background fitting itself — conceptually similar to Crutchfield's domain identification, but implemented differently (global optimization vs. local epsilon-machines)
- The 1D ECA results (Rule 54/110/30 hierarchy) — consistent with known results but quantified differently

**What would strengthen publishability:**
- Theoretical analysis: why do certain 2D rules have such low defect rates?
- Connection to computational mechanics: prove equivalence or complementarity with epsilon-machine approach
- Larger-scale experiments: bigger grids, more time steps, multiple seeds
- Application: use the decomposition for something (prediction, compression, classification)
