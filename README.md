# Relative symmetry-repair analysis for cellular automata

This project implements a practical version of the **relative symmetry-repair** idea discussed in our paper drafts.

The code uses:
- `numpy` for array programming
- `numba` for fast ECA simulation
- `pandas` for tabular spectrum summaries
- `scipy` for component extraction and stable combinatorial codelengths
- `matplotlib` for plots
- `lz4` for a practical compression proxy
- `typer` for a small modern CLI
- `jupyter` for the companion notebook

## What the program does

For a binary spacetime field `U[t, x]`, and for each shift-period pair `(s, p)`, the program constructs the nearest background satisfying

`B[t + p, (x + s) mod W] = B[t, x]`.

It then reports:
- defect count and defect rate
- idealized combinatorial repair bits
- run-length repair bits
- an `lz4`-compressed repair-mask proxy
- optional local-rule inconsistency of the fitted background

This lets you:
- build a **symmetry-defect spectrum**
- compare rules such as 30, 54, and 110
- extract connected defect world-tubes from the best fit
- demonstrate that equal Hamming-distance defects can have different repair codelengths

The primary background model scanned by the code is a relative-periodic spacetime pattern:

`B[t + p, (x + s) mod W] = B[t, x]`

where:
- `p` is the temporal period
- `s` is the spatial shift applied after each period
- `W` is the ring width

The CLI scans a grid of `(shift, period)` pairs and keeps the best-fitting background for each pair.

## Quick start

From the project root:

```bash
python -m pip install -e .
python -m relative_symmetry_repair.cli analyze --rule 110 --output-dir outputs/rule_110
```

Open the notebook:

```bash
jupyter notebook notebooks/relative_symmetry_repair_demo.ipynb
```

## Output guide

Each rule directory under `outputs/` contains four PNG files plus CSV summaries.

| File pattern | What it shows | How to read it | What to look for |
| --- | --- | --- | --- |
| `rule_<n>_spacetime.png` | The raw simulated CA spacetime. | Horizontal axis is cell index. Vertical axis is time, increasing from top to bottom. White means state `0`; black means state `1`. | Repeated diagonal motifs, stable domains, and long-lived boundaries or lanes. |
| `rule_<n>_defect_rate.png` | Heatmap of defect rate over scanned `(shift, period)` pairs. | X-axis is shift, Y-axis is period. Darker cells are lower defect rate, so lower is better. The outlined square marks the minimum scanned value. | Dark basins or isolated minima. A broad dark valley suggests a robust relative-periodic fit. |
| `rule_<n>_run_length_bits.png` | Heatmap of run-length repair cost for the defect mask. | Same axes as the defect-rate heatmap. Darker cells mean fewer run-length bits, so the defect mask is more structured and easier to compress. | Whether low-defect regions are also low-codelength regions. If not, the defects are numerous enough to fit well but still geometrically messy. |
| `rule_<n>_decomposition.png` | Best-fit decomposition into source, fitted background, and defect mask. | Left: raw source spacetime. Middle: nearest relative-periodic background. Right: defect mask, where red cells disagree with the fitted background. | Compact defect world-tubes, coherent slanted boundaries, and whether the fitted background captures the large-scale domain structure. |

The CSV files provide the same information numerically:
- `rule_<n>_spectrum.csv`: one row per scanned `(shift, period)` pair, including `defect_rate`, `run_length_bits`, `lz4_bits`, and `rule_error`
- `rule_<n>_components.csv`: connected components extracted from the best-fit defect mask
- `best_relative_periodic_fits.csv`: best default fit per rule for the notebook runs
- `reflection_repair_comparison.csv`: comparison showing that equal defect counts can still have very different repair codelengths

## Common legend

The generated PNGs now use a consistent visual language:
- White in source and background plots means binary state `0`
- Black in source and background plots means binary state `1`
- Red in defect masks means the source disagrees with the fitted background at that site
- Heatmap colorbars are quantitative legends; lower values are better
- The outlined square on each heatmap marks the minimum scanned value in that chart

## How to interpret the metrics

- `defect_rate`: fraction of spacetime sites where the source differs from the fitted relative-periodic background. Lower means a closer fit.
- `run_length_bits`: bit cost of a simple run-length code applied to the defect mask. Lower means defects are more spatially and temporally organized.
- `combinatorial_bits`: idealized codelength that depends only on how many defects there are, not on where they sit.
- `lz4_bits`: practical compressor proxy for the defect mask.
- `rule_error`: local-rule inconsistency rate of the fitted background under the original ECA rule. Lower means the fitted background behaves more like a true CA orbit instead of only matching the spacetime statistically.

The CLI chooses the displayed best-fit decomposition by sorting on:
1. lowest `defect_rate`
2. then lowest `rule_error`
3. then lowest `run_length_bits`

This ordering matters. Two fits can have similar defect counts but very different defect geometry, and the run-length plot makes that visible.

## What To Look For In The Checked-In PNGs

The checked-in `outputs/` directory was produced with the CLI defaults (`width=192`, `steps=144`, `density=0.5`, `seed=11`, shifts `-6..6`, periods `1..10`).

| Rule | Best `(shift, period)` | Reading of the PNGs |
| --- | --- | --- |
| `30` | `(-5, 10)` | The spacetime stays visually noisy, the defect-rate heatmap improves gradually rather than forming a sharp valley, and the decomposition mask remains diffuse. Interpret this as weak relative periodicity: the fit can lower the mismatch rate, but the remaining defects are not cleanly localized. |
| `54` | `(0, 8)` | The heatmaps show a pronounced low-value basin and the decomposition mask collapses into clean world-tubes and domain walls. Interpret this as strong evidence for a relative-periodic domain background with localized excitations riding on top of it. |
| `110` | `(0, 7)` | The heatmaps contain clear low-value pockets, but not as cleanly isolated as Rule 54. The decomposition shows a structured background plus persistent slanted defect structures. Interpret this as an intermediate case: real coherent organization, but with more complicated residual dynamics. |

In practice:
- If `defect_rate` is low and `run_length_bits` is also low, the fitted background is both close and structurally meaningful.
- If `defect_rate` is low but `run_length_bits` stays high, the fit is close only in a pointwise sense; the defects are still scattered.
- If the decomposition mask shows a few coherent tubes, the system has localized defects against a regular background.
- If the decomposition mask looks like pepper noise everywhere, the chosen relative-periodic ansatz is probably not capturing the right organization.

## Notes

The notebook fits **relative-periodic backgrounds in spacetime**. It does *not* solve the harder inverse problem of finding a nearest state `y` such that `Phi^p(y) = g y` exactly under the CA dynamics. To keep that limitation visible, the code also computes a local-rule inconsistency score for each fitted background.
