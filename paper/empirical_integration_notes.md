# Empirical Integration Notes

## Sections Changed

### Abstract (paper_v8.md)
- Already updated in prior session to mention LifeWiki survey, Diamoeba transition, Fredkin period-8
- Language uses "consistent with" rather than "confirms" or "verifies"

### Section 3.2.1b — LifeWiki Named Rules Survey (NEW in v8)
- Added complete subsection with T=100 and T=400 tables
- Period distribution, transition analysis, Fredkin highlight
- Fixed: text now says "four rules changed" (was "three") — Serviettes was being counted but text said three

### Section 3.4 — Summary Table
- Added row for "106 LifeWiki" with "3 change; 103 stable" (at T=100→T=400)

### Reproducibility (Appendix A)
- Already includes LifeWiki survey parameters

## Claims Strengthened
- Empirical coverage broadened from "3 rules per dimension" case studies to include 106 named LifeWiki rules
- Stabilization theorem demonstration now includes Diamoeba p=1→p=2 transition as concrete example of NLL gap crossing complexity threshold

## Claims Softened
- Paper already uses conservative language: "consistent with", "provides evidence", "empirical stabilization observed"
- Finite-horizon results explicitly disclaimed: "finite data cannot prove this"

## Numerical Consistency Verification
- T=100: 106 total, 105 nontrivial (1 trivial = B/S with all dead). Period sum: 97+7+1 = 105. ✓
- T=400: 106 total, 103 nontrivial (3 trivial = original dead + Iceballs→all_ones + Lifeguard 2→dead). Period sum: 94+7+1+1 = 103. ✓
- 4 rules changed period between T=100 and T=400 (all nontrivial at both horizons): Diamoeba, Maze with Mice, B017/S01, Serviettes. ✓
- 2 rules became trivial between T=100 and T=400: Iceballs (B25678/S5678→all_ones), Lifeguard 2 (B3/S4567→dead). ✓
- All 106 rules at T=100 had status `stable_winner`. ✓
- All 103 nontrivial rules at T=400 had status `stable_winner`. ✓

## Unresolved Issues
- See `author_action_items.md`
