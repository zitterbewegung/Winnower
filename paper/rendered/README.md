# Rendered 2-page PDF (typst)

`winnower_alife2026_lba.pdf` is a self-contained 2-page US-letter PDF of the
late-breaking abstract, laid out in a two-column conference format that closely
matches `alifeconf` (Figure 1 spans the top of page 1; Figure 2 spans the top
of page 2; all references fit on page 2).

It is produced with the typst compiler (a PyPI wheel — no TeX install needed):

    pip install typst pymupdf
    python paper/rendered/build_pdf_typst.py 0.80 0.92 10pt 8.5pt

Args are: fig1-width, fig2-width, body-font, reference-font.

The canonical LaTeX source remains `paper/alife2026_lba.tex` (compile on
Overleaf with the official alifeconf template); this rendered PDF is the
drop-in 2-page artifact for quick submission.
