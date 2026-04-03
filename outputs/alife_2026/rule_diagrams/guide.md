# Rule Diagram Guide

These figures are discussion aids for the representative ALIFE rules. They are meant to be used alongside the theorem and method notes in `paper/paper_talking_points.md`.

## Files

- `representative_rules_1d.png`: observed 1D spacetimes, selected backgrounds, and residual masks.
- `representative_rules_2d.png`: early, middle, late, selected-background, and residual slices for the 2D panel.
- `representative_rules_3d.png`: midplane slices through the 3D panel with selected-background and residual views.
- `rule_mechanisms_1d.png`: lookup-table view of the studied elementary rules.
- `rule_mechanisms_2d.png`: Moore-neighborhood plus birth/survival count diagrams for the studied 2D rules.
- `rule_mechanisms_3d.png`: 3D Moore-neighborhood plus birth/survival count diagrams for the studied 3D rules.
- `presentation_rules_1d.png`: larger 1D presentation figure with fewer, more legible rules.
- `presentation_rules_2d.png`: larger 2D presentation figure cropped around active regions.
- `presentation_rules_3d.png`: larger 3D presentation figure using max projections instead of only a midplane.
- `presentation_guide.md`: plain-language explanation of what each presentation diagram means.
- `paper/figures/alife_representative_rules.png`: composite manuscript-ready version of the three overview panels.
- `paper/figures/alife_rule_mechanisms.png`: composite manuscript-ready version of the three mechanism panels.
- `paper/alife_figure_snippets.md`: ready-to-paste captions and labels.

## Recommended explanation order

1. Start with the mechanism figures. They explain what the local update rule is actually doing.
2. Move to the representative evolution panels. They show what those local rules look like at the scale of an entire spacetime.
3. Use the background and defect columns to explain the paper's decomposition idea: the selector finds a global scaffold, then studies what is left over.

## How to read the colors

- Light cells use `#fcdeb9` and mean value `0`.
- Dark cells use `#3b3b3b` and mean value `1`.
- Red cells use `#b00300` and mark disagreement with the selected relative-periodic background.
- In mechanism figures, `#b00300` marks birth counts and `#5f5f5f` marks survival counts.

## Representative 1D rules

- `ECA-30`: best `(p, s) = (1, -2)`, margin `153.4` bits, defect rate `0.471`. Chaotic texture with little large-scale repetition; the selector still prefers a simple background.
- `ECA-54`: best `(p, s) = (4, 0)`, margin `1484.9` bits, defect rate `0.179`. Alternating domains and clearer phase locking make the periodic scaffold easier to see.
- `ECA-110`: best `(p, s) = (7, 0)`, margin `857.0` bits, defect rate `0.314`. Drifting multi-phase lanes are visible; the best fit uses a nonzero shift to follow motion.

## Representative 2D rules

- `Diamoeba`: best `(p, s) = (2, (0, 0))`, margin `369.3` bits, defect rate `0.114`. Large breathing blobs dominate the frame and create a stronger long-horizon periodic signal.
- `Maze with Mice`: best `(p, s) = (2, (0, 0))`, margin `10230.3` bits, defect rate `0.007`. Maze-like corridors remain coherent while local fluctuations ride on top of them.
- `S24/B11`: best `(p, s) = (1, (0, 0))`, margin `1949.2` bits, defect rate `0.014`. Sparse patches form and dissolve, so the background captures only the broadest cadence.
- `S11/B37`: best `(p, s) = (2, (0, 0))`, margin `6111.3` bits, defect rate `0.014`. Explosive local birth competes with fast die-out, producing noisy but still structured slices.
- `S37/B11`: best `(p, s) = (2, (0, 0))`, margin `20464.8` bits, defect rate `0.016`. Persistent residual structure remains after fitting, making the defect mask especially informative.

## Representative 3D rules

- `3d-life`: best `(p, s) = (1, (0, 0, 0))`, margin `6765.0` bits, defect rate `0.111`. Dense midplane activity shows how a simple 3D rule can still look highly textured in projection.
- `clouds`: best `(p, s) = (1, (0, 0, 0))`, margin `8366.1` bits, defect rate `0.017`. High-count thresholds create bulky, cloud-like regions instead of thin fronts.
- `crystal`: best `(p, s) = (2, (0, 0, 0))`, margin `7435.7` bits, defect rate `0.209`. Low-count thresholds favor sparse growth and faceted, crystal-like fronts.
- `diamoeba3d`: best `(p, s) = (1, (0, -2, 1))`, margin `5507.5` bits, defect rate `0.265`. Large volumetric domains survive for long periods, so the midplane slices show broad coherent masses.

## Suggested talking points

- The mechanism figures explain the rule itself. The overview figures explain the global behavior that the selector is trying to summarize.
- In 1D, the shift parameter is easiest to explain because diagonal motion is visually obvious.
- In 2D and 3D, the defect masks are often more informative than the raw slices because they separate the fitted scaffold from the persistent irregular structures.
- Use high-margin cases to explain stabilization. Use noisy or low-structure cases to explain why period 1 often wins.

