# Code Verification and Correctness Analysis

## Agent Swarm Audit Summary (2026-03-11)

Four parallel agents audited the empirical pipeline. Results below.

---

## 1. Survey Script (`scripts/survey_lifewiki_rules.py`)

**Verdict: CORRECT.** No bugs that would cause rules to be silently dropped or duplicated.

| Check | Result |
|-------|--------|
| All 106 rules processed | ✓ CSV always has 106 rows |
| Trivial rules recorded (not dropped) | ✓ Hardcoded record with `status="trivial"`, `selected_period=1` |
| Error handling records failures | ✓ `status=f"error: {e}"` appended |
| No rule duplication | ✓ Single loop, one record per iteration |
| Shift ranges correct | ✓ `range(-2, 3)` = [-2, -1, 0, 1, 2] |
| `steps` semantics | ✓ `steps=100` → 100 frames (initial + 99 transitions), matches docstring |

**Minor issues:**
- `is_trivial()` has latent IndexError for `steps=1` (never triggered at default `steps=100`)
- Error handler reads `has_b0` from raw JSON instead of parsing rulestring (fragile but correct)

## 2. Data File (`data/lifewiki_rules.json`)

**Verdict: CORRECT.**

| Check | Result |
|-------|--------|
| Exactly 106 rules | ✓ |
| No duplicate rulestrings | ✓ |
| No duplicate names | ✓ |
| All rulestrings parse correctly | ✓ |
| B0 rules identified | 9 rules with B0 (strobing) |
| Empty-survive rules | 2 rules: Seeds (B2/S), Serviettes (B234/S) |

## 3. Selection Logic (`selection.py`)

**Verdict: CORRECT.**

| Check | Result |
|-------|--------|
| Period-first: min NML over shifts per period | ✓ `group.loc[group["nml_bits"].idxmin()]` |
| Sorting: (nml_bits, period) ascending | ✓ Lower NML wins, lower period breaks ties |
| Margin: runner_up - selected | ✓ Always ≥ 0 by construction |
| Status classification | ✓ margin > 2 → stable_winner, 0–2 → near_tie, ≤ 0 → unresolved |
| Edge case: single candidate | ✓ margin = inf → stable_winner |
| Dict key matching (1D and ND) | ✓ (shift, period) keys consistent between repair and selection |

**Minor issues:**
- `_group_by_period()` accepts unused `fits` parameter (dead code)
- `selected_shift` stored as raw tuple in ND case (could affect JSON serialization)

## 4. NML Computation (`coding.py`)

**Verdict: CORRECT.**

| Check | Result |
|-------|--------|
| Shtarkov normalizer formula | ✓ Matches `C(n) = Σ binom(n,k)(k/n)^k((n-k)/n)^(n-k)` |
| Boundary terms (k=0, k=n) | ✓ Uses 0^0 = 1 convention via separate handling |
| Numerical stability | ✓ Log-sum-exp trick in base 2 |
| n ≤ 1 returns 0 | ✓ |
| Exact vs asymptotic cutoff at n=200 | ✓ ~0.3-bit discontinuity, documented and acceptable |
| NLL for pure orbit classes (θ=0 or 1) | ✓ Returns 0 bits |
| NML = NLL + complexity | ✓ |

**Minor issues:**
- `gamma_bits(0)` would raise OverflowError (unreachable in practice)
- LRU cache size 4096 is sufficient (max unique n ≤ 200)

---

## 5. Arithmetic Reconciliation

The period distribution counts do NOT sum to 106 at either horizon because **trivial rules are excluded from the distribution**. This is correct behavior — trivial rules (dead/all_ones/static) have degenerate spacetimes that are not meaningful to analyze for periodic structure.

### T=100 (105 nontrivial + 1 trivial = 106)
| Category | Count | Rules |
|----------|-------|-------|
| Nontrivial | 105 | (97 p=1, 7 p=2, 1 p=8) |
| Dead | 1 | Replicator (B1357/S1357) |

### T=400 (103 nontrivial + 3 trivial = 106)
| Category | Count | Rules |
|----------|-------|-------|
| Nontrivial | 103 | (94 p=1, 7 p=2, 1 p=4, 1 p=8) |
| Dead | 2 | Replicator, Lifeguard 2 (B3/S4567) |
| All-ones | 1 | Iceballs (B25678/S5678) |

### Period changes (4 rules, not 3)
| Rule | T=100 | T=400 |
|------|-------|-------|
| Diamoeba (B35678/S5678) | p=1 | p=2 |
| Maze with Mice (B37/S12345) | p=1 | p=2 |
| B017/S01 | p=2 | p=4 |
| Serviettes (B234/S) | p=2 | p=1 |

### Rules that became trivial between T=100 and T=400
| Rule | T=100 | T=400 |
|------|-------|-------|
| Iceballs (B25678/S5678) | nontrivial (density 0.477) | all_ones (density 1.0) |
| Lifeguard 2 (B3/S4567) | nontrivial (density 0.014) | dead (density 0.0) |

---

## 6. Conclusion

**No correctness bugs were found in the empirical pipeline.** The code correctly:
- Simulates all 106 rules with the general Life-like lookup-table simulator
- Classifies trivial rules and records them (does not drop them)
- Runs period-first NML selection for nontrivial rules
- Records all results in the CSV

The apparent arithmetic discrepancy (period counts not summing to 106) is explained by trivial rule exclusion, which is correct behavior that was inadequately documented in the paper text. This has now been fixed with explicit trivial/nontrivial accounting in both paper_v8.md and paper_alife2026.tex.
