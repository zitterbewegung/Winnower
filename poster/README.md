# ALIFE 2026 Poster

This directory holds both published artifacts: the accepted late-breaking
abstract and the poster board assembled from it. Accepted LBAs are presented
as posters and are not included in the proceedings.

## Files

- `alife2026_poster.tex` / `.pdf` — the accepted ALIFE 2026 late-breaking abstract (US-letter, 2 pages of main text). This is the canonical copy; the review site and `deploy-review-site.yml` both read it from here.
- `alife_2026_poster.tex` — standalone landscape poster source (48x36 in board)
- `alife_2026_poster.pdf` — compiled poster output after a successful local build
- `alifeconf.sty` — symlink to `../paper/alifeconf.sty`, the official conference style shared with the companion paper
- `EDITABLE_FIGURES.md` — notes on which figure families are best edited as PDF, SVG, or by direct redraw

## Build

From this directory:

```bash
pdflatex -interaction=nonstopmode alife2026_poster.tex   # late-breaking abstract
pdflatex -interaction=nonstopmode alife_2026_poster.tex  # poster board
```

The board uses checked-in image assets from:

- `../_archive/alternate_layouts/alife_lba_bundle/figures/`
- `../outputs/alife_2026/rule_diagrams/`
- `../paper/figures/`

## Data choices for this draft

This poster intentionally favors the newer ALIFE-facing artifacts over older summary notes that still contain stale periods.

Primary sources used here:

- `../_archive/alternate_layouts/alife_lba_bundle/alife_lba_2026_knuth.tex`
- `../outputs/alife_2026/rule_diagrams/presentation_guide.md`
- `../results/baseline_selector_summary.csv`
- `../outputs/alife_2026/null_controls/null_controls_summary.csv`
- `../outputs/strengthening_v2/multi_seed_mdl.csv`
- `../outputs/strengthening_v2/multiseed_scaling.csv`

## Next edits worth making

1. Replace the placeholder affiliation line.
2. Decide whether the poster should foreground 2D only or keep the current cross-dimensional story.
3. If this will go to print, regenerate or upsample any figure that needs to occupy a very large fraction of the board.
4. Clean stale contradictory period claims in older repo summaries before reusing them elsewhere.
