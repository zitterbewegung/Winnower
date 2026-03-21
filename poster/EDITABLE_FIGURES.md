# Editable Figure Notes

This repo now has a practical split between figures that can be regenerated natively as vector graphics and figures that are best handled by converting an existing vector PDF.

## Best cases: regenerate directly as vector

These are script-generated with Matplotlib and can now be exported directly as `pdf` and `svg`:

- `scripts/alife_algorithm_figure.py`
- `scripts/alife_rule_diagrams.py`
- `scripts/alife_stabilization_summary.py`

Recommended commands:

```bash
./venv/bin/python scripts/alife_algorithm_figure.py --export-formats png,pdf,svg
./venv/bin/python scripts/alife_rule_diagrams.py --export-formats png,pdf
./venv/bin/python scripts/alife_stabilization_summary.py --export-formats png,pdf,svg
```

This is the preferred route for:

- `outputs/alife_2026/rule_diagrams/presentation_rules_*.pdf`
- `outputs/alife_2026/rule_diagrams/rule_mechanisms_*.pdf`
- `outputs/alife_2026/editable_figures/stabilization_summary.{pdf,svg}`

For the large array-based rule panels, `pdf` is the more practical editable format. Bulk `svg` export is technically possible but slow and often produces unwieldy files.

`algorithm_detailed.{png,pdf,svg}` now comes from the native regeneration script, so it no longer depends on PDF conversion.

## What not to do unless necessary

- Do not treat the manuscript composite PNGs as editable sources.
- Do not force the pixel-array decomposition panels into TikZ by hand. The files become huge and unpleasant to edit.
- Do not assume every `svg` is equally editable: some exports still contain embedded raster image regions or outlined fonts.

## TikZ / PGF guidance

TikZ or PGF is reasonable for:

- simple line charts
- algorithm schematics
- annotations added on top of a figure

TikZ or PGF is a poor fit for:

- large binary-array image panels
- multi-panel decomposition figures with thousands of cell rectangles
- any figure whose main content is already naturally represented as an image grid

For this project, the practical editable hierarchy is:

1. Native Matplotlib PDF
2. Native Matplotlib SVG
3. Inkscape/Illustrator editing of PDF or SVG
4. TikZ redraw only for small schematic figures
