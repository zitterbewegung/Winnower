import sys, typst, fitz, pathlib
D = pathlib.Path(__file__).parent

TEMPLATE = r'''
#set page(paper: "us-letter", margin: (left: 0.75in, right: 0.75in, top: 0.9in, bottom: 1.1in), columns: 2)
#set columns(gutter: 0.375in)
#set text(font: "Liberation Serif", size: BODYPT)
#set par(justify: true, leading: LEADEM, spacing: SPACEEM, first-line-indent: 0em)
#show heading.where(level: 1): it => block(above: 0.8em, below: 0.4em, text(size: 11pt, weight: "bold", it.body))

#place(top + center, scope: "parent", float: true, clearance: 0.5em)[
  #align(center)[
    #text(size: 15pt, weight: "bold")[Winnower: Inferring Periodic Domains in Cellular Automata]
    #v(0.35em)
    #text(size: 11pt)[Joshua Herman#super[1]]\
    #text(size: 10pt)[#super[1]Independent Researcher --- zitterbewegung\@gmail.com]
  ]
]

#place(top + center, scope: "parent", float: true, clearance: 0.5em)[
  #align(center)[#image("algorithm_nml.png", width: FIG1W)]
  #text(size: 8.6pt)[*Figure 1.* Winnower's domain-inference pipeline. A candidate spatiotemporal translation (p, s) partitions the observed CA space--time sites into translation orbits. Orbit-majority states define the candidate domain template, mismatches define the defect mask, and the Bernoulli NML criterion balances fit and model complexity.]
]

#text(size: ABSPT)[*Abstract.* Cellular automata (CAs) often generate extended periodic domains together with localized structures and interfaces between domains. We present _Winnower_, a model-selection method for inferring a periodic spatiotemporal domain from a finite CA space--time observation. A candidate temporal period and spatial displacement induce translation orbits over the observed sites. Assigning each orbit its majority state gives the domain template with minimum Hamming disagreement for that candidate. Winnower ranks candidates using the Bernoulli normalized maximum likelihood (NML) criterion and returns the selected template and a defect mask. In preliminary one-, two-, and three-dimensional experiments, the selected symmetry stabilized after short transients. The NML complexity term also prevented systematic period inflation: for 105 nontrivial Life-like rules, unpenalized likelihood selected the largest scanned period in every case, whereas NML selected period 1 for 97 rules. Several defect masks retained persistent localized structure. These results suggest that Winnower can provide a global preprocessing step for CA rule-space surveys before local particle or coherent-structure analysis. Data and code: `github.com/zitterbewegung/Winnower`.]
#v(0.35em)

= Introduction
Many cellular automata (CAs) produce space--time diagrams with extended periodic domains threaded by particles, gliders, and domain interfaces. The domain is the background against which such structures are defined; we ask which temporal period and spatial displacement give the simplest adequate domain model for a finite observation. Local causal-state methods reconstruct such organization in detail (Rupe and Crutchfield, 2024); taxonomies, transient analyses, and compression-based methods characterize whole rules (Vispoel et al., 2022; Rollier et al., 2024; Hudcova and Mikolov, 2021; Alfaro and Sanjuan, 2024; Cisneros, 2023). Winnower instead fits global periodic templates with a complexity penalty, for broad rule-space sweeps.

= Method
Given a binary space--time block $U$, period $p$, displacement $bold(s)$, and lattice extents $bold(D)$, Winnower fits templates with $B[t+p, bold(x)+bold(s) mod bold(D)] = B[t,bold(x)]$. This partitions observed sites into orbits ${O_j}$; each orbit's majority state gives the minimum-Hamming template, and mismatches form the defect mask (Fig. 1). Candidates are ranked by the Bernoulli NML criterion
$ "NML"(p, bold(s)) = sum_j n_j H_b (hat(theta)_j) + sum_j cal(C)(n_j), $
with $n_j = |O_j|$, $hat(theta)_j = n_j^((1)) \/ n_j$, $H_b$ the binary entropy, and $cal(C)(n) = log_2 sum_(k=0)^n binom(n,k) (k\/n)^k ((n-k)\/n)^(n-k)$ the exact Bernoulli NML (Shtarkov) complexity of an $n$-observation class; the code evaluates $cal(C)$ exactly for small classes and by its asymptote $1/2 log_2 (n pi\/2)$ for larger ones (Shtarkov, 1987; Grunwald, 2007; Yamanishi, 2023).

The penalty is essential: a velocity-matched longer period refines a shorter candidate's orbits, which cannot worsen fit, so unpenalized selection inflates the period. We verified this divisibility/refinement relation in Lean 4 (Achim et al., 2025). Once per-site NLL rates differ, the linear fit gap dominates the logarithmic penalty gap, giving stable selection as $T$ grows.

#place(top + center, scope: "parent", float: true, clearance: 0.5em)[
  #align(center)[#image("lba_results.png", width: FIG2W)]
  #text(size: 8.6pt)[*Figure 2.* Winnower on the elementary rules ECA-54 (top) and ECA-110 (bottom). _Left three columns:_ observed space--time, the selected shift-0 domain template, and the defect mask. ECA-54 selects period 4; ECA-110 selects the period-7 ether domain, whose defect mask traces the propagating particles. _Right two columns:_ selected temporal period and the Bernoulli NML margin to the second-ranked candidate versus horizon T. ECA-54 is stable from the first horizon; ECA-110 changes once (1 -> 7, marked), its margin growing thereafter.]
]

= Preliminary Results
We evaluated Winnower on elementary CA Rules 30, 54, and 110; two-dimensional Life-like and totalistic rules; and three-dimensional Life-like rule B5/S45 (Bays, 1987; Bays, 2006). Fig. 2 pairs the decomposition and horizon sweep for ECA-54 and ECA-110; 2D and 3D runs use seed 11 (1D/2D) and seed 42 ($T <= 50$, 3D). Rule 54 selected period 4 throughout (margin 681 to 2318 bits) and B5/S45 period 1 (3324 to 7403 bits). Rule 110 changed from period 1 to 7, consistent with its periodic ether background, and S24/B11 from 1 to 2; margins increased after each transition.

At $T = 100$ over 105 nontrivial Life-like rules, unpenalized NLL selected the largest scanned period for every rule, whereas NML selected period 1 for 97. Entropy-rate comparisons indicate the template captures a predictable component of the observation while the defect mask retains structured variation. In rules such as S37/B11 the defect population persisted and grew with lattice size (Seck-Tuoh-Mora et al., 2023); these defects are candidate departures from the domain, not identified particles.

*Reproducibility.* The released code regenerates all results: `analyze`, `analyze2d`, `analyze3d` reproduce individual runs, and Fig. 2 is produced by `alife_lba_figures.py` after `convergence_all_dims.py`.

= Discussion and Future Work
Winnower returns a global periodic domain template and defect mask. It assumes binary states, periodic boundaries, a supplied candidate set, and one global symmetry, and so complements rather than replaces local causal-state or particle analysis (Rupe and Crutchfield, 2024; Rupe et al., 2025). Future work will test sensitivity to observation length, boundaries, noise, and candidate-set size; connect defect masks to local tracking; and extend to multistate, continuous-state, and neural cellular automata (Hamon et al., 2024; Plantec et al., 2025; Niklasson et al., 2021).

*Acknowledgements.* We thank Editage (`www.editage.com`) for language editing. ChatGPT and Claude Code assisted with software development; Aristotle and Claude assisted with Lean proof development and verification.

#v(0.3em)
#text(size: 10.5pt, weight: "bold")[References]
#set text(size: REFPT)
#set par(hanging-indent: 1em, spacing: REFSPACE, leading: REFLEAD)
Achim, T. et al. (2025). Aristotle: IMO-level automated theorem proving. _arXiv:2510.01346_.

Alfaro, G. and Sanjuan, M. A. F. (2024). Classification of cellular automata based on the Hamming distance. _Chaos_, 34(8):083129.

Bays, C. (1987). Candidates for the game of life in three dimensions. _Complex Systems_, 1(3):373--400.

Bays, C. (2006). A note about the discovery of many new rules for the game of three-dimensional life. _Complex Systems_, 16:381--386.

Cisneros, H. (2023). _Unsupervised Learning in Complex Systems_. PhD thesis; arXiv:2307.10993.

Grunwald, P. (2007). _The Minimum Description Length Principle_. MIT Press.

Hamon, G., Etcheverry, M., Chan, B. W.-C., Moulin-Frier, C., and Oudeyer, P.-Y. (2024). Discovering sensorimotor agency in cellular automata using diversity search. _Science Advances_, 10:eadp0834.

Hudcova, B. and Mikolov, T. (2021). Classification of discrete dynamical systems based on transients. _Artificial Life_, 27(3--4):220--245.

Niklasson, E., Mordvintsev, A., Randazzo, E., and Levin, M. (2021). Self-organising textures. _Distill_, 6(2).

Plantec, E., Hamon, G., Etcheverry, M., Oudeyer, P.-Y., Moulin-Frier, C., and Chan, B. W.-C. (2025). Flow-Lenia: Emergent evolutionary dynamics in mass conservative continuous cellular automata. _Artificial Life_. arXiv:2506.08569.

Rollier, M., Zielinski, K. M. C., Daly, A. J., Bruno, O. M., and Baetens, J. M. (2024). A comprehensive taxonomy of cellular automata. _Communications in Nonlinear Science and Numerical Simulation_. arXiv:2401.08408.

Rupe, A. and Crutchfield, J. P. (2024). On principles of emergent organization. _Physics Reports_, 1071:1--47.

Rupe, A., Kashinath, K., Kumar, N., and Crutchfield, J. P. (2025). Unsupervised discovery of extreme weather events using universal representations of emergent organization. _Chaos_, 35(8):083110.

Seck-Tuoh-Mora, J. C., Medina-Marin, J., Hernandez-Romero, N., and Martinez, G. J. (2023). Mean-field analysis with random perturbations to detect gliders in cellular automata. _Mathematics_, 11(20):4319.

Shtarkov, Y. M. (1987). Universal sequential coding of single messages. _Problems of Information Transmission_, 23:3--17.

Vispoel, M., Daly, A. J., and Baetens, J. M. (2022). Progress, gaps and obstacles in the classification of cellular automata. _Physica D_, 432:133074.

Yamanishi, K. (2023). Learning with the Minimum Description Length Principle. Springer.
'''

def build(fig1w, fig2w, bodypt, refpt, lead="0.52em", space="0.6em", abspt="9.2pt", refspace="0.32em", reflead="0.4em"):
    doc = (TEMPLATE
        .replace("FIG1W", f"{fig1w*100:.0f}%").replace("FIG2W", f"{fig2w*100:.0f}%")
        .replace("BODYPT", bodypt).replace("ABSPT", abspt)
        .replace("REFPT", refpt).replace("REFSPACE", refspace).replace("REFLEAD", reflead)
        .replace("LEADEM", lead).replace("SPACEEM", space))
    (D/"paper.typ").write_text(doc)
    typst.compile(str(D/"paper.typ"), output=str(D/"paper.pdf"), font_paths=["/usr/share/fonts"])
    pdf = fitz.open(str(D/"paper.pdf"))
    return pdf.page_count

if __name__ == "__main__":
    import itertools
    a=sys.argv[1:]
    n = build(float(a[0]), float(a[1]), a[2], a[3])
    print(f"fig1={a[0]} fig2={a[1]} body={a[2]} refs={a[3]}: pages={n}")
