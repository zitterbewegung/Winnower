# Presentation Diagram Guide

This note exists for the less-flat presentation figure set. Use it when you want to show only the most interpretable rules at larger scale.

## Files

- `presentation_rules_1d.png`: larger 1D presentation panel.
- `presentation_rules_2d.png`: larger 2D presentation panel, cropped around the active region.
- `presentation_rules_3d.png`: larger 3D presentation panel using max projections rather than a single midplane slice.

## What the three panel types mean

- `Observed`: the raw cellular automaton state.
- `Background`: the selected relative-periodic scaffold found by the period-first Bernoulli-NML selector.
- `Defect`: the mismatch between the raw state and that scaffold.

## Why these should look less flat

- The 2D presentation panels are cropped to the active region instead of showing the full torus.
- The 3D presentation panels use max projections, so more volumetric structure survives the visualization.
- The rule list is smaller and biased toward visually stronger cases.

## 1D presentation rules

### ECA-54

- Selected winner: `(p, s) = (4, 0)`
- Winner margin: `1484.9` bits
- Defect rate: `0.179`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Alternating domains and clearer phase locking make the periodic scaffold easier to see.

### ECA-110

- Selected winner: `(p, s) = (7, 0)`
- Winner margin: `857.0` bits
- Defect rate: `0.314`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Drifting multi-phase lanes are visible; the best fit uses a nonzero shift to follow motion.

## 2D presentation rules

### Diamoeba

- Selected winner: `(p, s) = (2, (0, 0))`
- Winner margin: `369.3` bits
- Defect rate: `0.114`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Large breathing blobs dominate the frame and create a stronger long-horizon periodic signal.

### Maze with Mice

- Selected winner: `(p, s) = (2, (0, 0))`
- Winner margin: `10230.3` bits
- Defect rate: `0.007`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Maze-like corridors remain coherent while local fluctuations ride on top of them.

### S37/B11

- Selected winner: `(p, s) = (2, (0, 0))`
- Winner margin: `20464.8` bits
- Defect rate: `0.016`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Persistent residual structure remains after fitting, making the defect mask especially informative.

## 3D presentation rules

### 3d-life

- Selected winner: `(p, s) = (1, (0, 0, 0))`
- Winner margin: `6765.0` bits
- Defect rate: `0.111`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Dense midplane activity shows how a simple 3D rule can still look highly textured in projection.

### clouds

- Selected winner: `(p, s) = (1, (0, 0, 0))`
- Winner margin: `8366.1` bits
- Defect rate: `0.017`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: High-count thresholds create bulky, cloud-like regions instead of thin fronts.

### diamoeba3d

- Selected winner: `(p, s) = (1, (0, -2, 1))`
- Winner margin: `5507.5` bits
- Defect rate: `0.265`
- What the observed panel means: the raw CA state before any decomposition.
- What the background panel means: the periodic scaffold chosen by the selector.
- What the defect panel means: the cells where the scaffold is wrong, i.e. the residual structure.
- Why this rule is in the presentation set: Large volumetric domains survive for long periods, so the midplane slices show broad coherent masses.

