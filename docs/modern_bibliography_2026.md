# Modern bibliography research (July 2026)

The existing references (`paper/novelty_prior_art_refs.bib` and the
`thebibliography` block in `paper/paper_alife2026.tex`) top out at
Mordvintsev et al. (2020) and Grünwald & Roos (2019). This note collects
verified 2020–2025 literature that updates each strand of the paper.
BibTeX entries live in `paper/modern_refs.bib`.

## Old → new mapping

| Existing reference | Modern update | Why it matters here |
|---|---|---|
| Rupe & Crutchfield 2018 (local causal states); Rupe et al. 2019 (DisCo) | **Rupe & Crutchfield 2024**, *On Principles of Emergent Organization*, Physics Reports 1071:1–47 (arXiv:2311.13749) | The current authoritative survey of the local-causal-state / intrinsic-computation program. Any comparison of the codelength approach against computational mechanics should cite this rather than stopping at 2018–2019. |
| Rupe et al. 2019 (DisCo) | **Rupe, Kashinath, Kumar & Crutchfield 2025**, Chaos 35(8):083110 (arXiv:2304.12586) | Journal-strength successor to DisCo: lightcone/local-causal-state segmentation applied to real spatiotemporal fields (extreme weather). Closest modern competitor to the defect-mask pipeline. |
| — | **Rupe & Crutchfield 2020**, *Spacetime Autoencoders Using Local Causal States* (arXiv:2010.05451) | Frames domain/defect decomposition as encode/decode of spacetime fields — directly comparable to the paper's background-fit + residual-mask coding view. |
| Zenil 2010; Zenil et al. 2018 (compression classification) | **Vispoel, Daly & Baetens 2022**, Physica D 432:133074; **Rollier et al. 2024**, *A Comprehensive Taxonomy of Cellular Automata* (arXiv:2401.08408, CNSNS) | Standard modern citations for "where classification of CA stands"; position the codelength metric within the current landscape. |
| Li & Packard–style rule-space work | **Hudcová & Mikolov 2021**, Artificial Life 27(3–4):220–245; **Alfaro & Sanjuán 2024**, Chaos 34(8):083129 | Two recent quantitative classification schemes (transient growth; Hamming/damage spreading) that a new metric should be contrasted with. |
| Zenil compression program | **Cisneros 2023**, *Unsupervised Learning in Complex Systems* (arXiv:2307.10993) | PhD thesis with compression-based structure/complexity-growth metrics for CA; overlaps with the codelength-of-defect-mask idea. |
| Lizier et al. 2008; Shalizi et al. 2006 (filters/structure detection) | **Seck-Tuoh-Mora et al. 2023**, Mathematics 11(20):4319 | Recent non-information-theoretic glider-detection method (perturbed mean-field), useful as an alternative baseline in related work. |
| Grünwald 2007; Shtarkov 1987 | **Yamanishi 2023**, *Learning with the MDL Principle*, Springer | Current book-length MDL treatment (NML variants, change/anomaly detection). Modern anchor for the NML/Shtarkov codelength machinery. |
| Chan 2019 (Lenia); Mordvintsev et al. 2020 (NCA) | **Hamon et al. 2024**, Science Advances 10:eadp0834; **Plantec et al. 2025**, Flow-Lenia, Artificial Life (arXiv:2506.08569); **Niklasson et al. 2021**, Distill | Current state of the Lenia/NCA line for the ALife framing and future-work section. |

## Relevance to issue #1 (novelty-claim verification)

Issue #1 asks to verify the claim of the "first stabilization theorem for
periodic template selection" against the computational-mechanics
literature. The closest modern material found:

- Rupe & Crutchfield 2024 (Physics Reports) — surveys the whole
  computational-mechanics program through 2024; it contains synchronization
  and domain-detection results but **no finite-time stabilization theorem
  for selection among periodic templates**.
- Travers & Crutchfield 2011 (already cited) remains the closest prior art
  (exact/asymptotic synchronization for finite-state sources); it concerns
  synchronizing to a *given* process, not selecting a template by
  codelength.
- Hudcová & Mikolov 2021 prove properties of transient classification but
  nothing about template selection.

Within the searched literature the novelty claim survives, provided it is
phrased as "stabilization of *codelength-based selection* among periodic
templates" (selection consistency), distinguishing it from the
synchronization theorems above.

## Verification status

All bibliographic data (authors, venue, volume/pages where given) were
checked against arXiv listings or publisher pages in July 2026. DOIs are
included only where confirmed; entries without DOIs carry arXiv eprint IDs
instead. Candidates found but *not* included for lack of verifiable
metadata: CNN-based automated CA classification (arXiv:2409.02740),
"The Glider Equation for Asymptotic Lenia" (arXiv:2508.04167).
