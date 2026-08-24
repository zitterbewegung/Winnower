# Prior-art audit — synthetic FSM residual/leverage

Audit performed **2026-08-23** (America/Chicago), **before** the frozen
hypothesis and before any development or holdout outcome was generated.

Databases and tools used: general web search (US region) via the session's
search tool, publisher landing pages (Springer Nature Link, Oxford Academic,
Nature/Scientific Reports, ScienceDirect, PNAS), arXiv, PubMed/PMC, and
read-only inspection of two local sibling research repositories
(`zitterbewegung/Winnower` and `aconsapart/ruler`).

Access limitations, stated plainly:

- Several publisher PDFs (Oxford Academic, ScienceDirect) are paywalled from
  this environment; for those the abstract, landing-page metadata, indexed
  full-text excerpts and secondary descriptions were used rather than the
  typeset PDF.
- No subscription bibliographic database (Web of Science, Scopus) was
  available.
- The search is finite. **No absolute novelty claim is made below.**

## Queries actually run

```text
Flajolet Odlyzko "Random Mapping Statistics" EUROCRYPT 1989 functional graph
Xiao Dougherty "impact of function perturbations in Boolean networks" Bioinformatics 2007 attractor basin
minimum description length residual transition table finite deterministic map exposure-matched attractor intervention leverage
"functional graph" edge perturbation attractor change random mapping sensitivity basin size
Zenil "algorithmic information dynamics" perturbation analysis network reprogramming iScience 2019 causal discovery
compression residual causal leverage cellular automata defect mask codelength inverse relationship
```

plus targeted fetches of `arxiv.org/abs/2112.13177` and the Springer/Oxford/
Nature landing pages for the seed references.

## Materially relevant sources

### 1. Flajolet & Odlyzko, "Random Mapping Statistics"

| Field | Content |
|---|---|
| Citation | P. Flajolet, A. M. Odlyzko. *Random Mapping Statistics.* EUROCRYPT '89, LNCS 434, pp. 329–354, 1990. DOI [10.1007/3-540-46885-4_34](https://doi.org/10.1007/3-540-46885-4_34). Also INRIA RR-1114. |
| System | Uniform random mappings `f: S -> S` on a finite set — exactly this study's null family. |
| Structural description | None; the object is the unstructured random functional graph. |
| Intervention | None. |
| Outcome | Asymptotics for ~20 parameters: tail length, rho length, cycle length, tree size, component size, number of cyclic points, diameter. |
| Exposure control | Not applicable — no intervention is performed. |
| Exact overlap | Supplies the exact distributional background for `visitCount`, `on_cycle`, component and cycle-length statistics used here, and establishes that the descriptive functional-graph statistics of this study are classical. |
| Remaining distinction | No compression/description-length model of the map, no edit intervention, no attractor-switch outcome, no matched comparison. |
| Threat to novelty | Any claim about *the distribution* of visit counts, cycle lengths or component sizes in the random family is a restatement of this paper, not a finding. |

### 2. Xiao & Dougherty, "The impact of function perturbations in Boolean networks"

| Field | Content |
|---|---|
| Citation | Y. Xiao, E. R. Dougherty. *Bioinformatics* 23(10):1265–1273, 2007. DOI [10.1093/bioinformatics/btm093](https://doi.org/10.1093/bioinformatics/btm093). PMID 17379691. |
| System | Boolean networks (a structured subclass of finite deterministic maps on `{0,1}^n`). |
| Structural description | The Boolean truth tables / predictor functions themselves. |
| Intervention | Perturbation of a network *function* (a truth-table entry), i.e. a structural edit, not a state flip. |
| Outcome | Change in state transitions, attractors and basins of attraction; "analysis" (predict the impact) and "synthesis" (choose perturbations to preserve or alter attractors). |
| Exposure control | Not controlled. The analysis is over the whole state space; there is no matching of perturbed against unperturbed transitions at equal visitation. |
| Exact overlap | The core mechanic — one structural edit, measure whether the attractor reached changes — is the same mechanic used here. |
| Remaining distinction | No description-length / compression model of the transition table; no notion of a *residual* transition; no matched control transitions; no per-transition conditional leverage ratio `theta = C / w`. |
| Threat to novelty | This precludes any claim of priority for "structural edits change attractors" or for computing attractor change under function perturbation. |

### 3. Hu, Wang, Sun, Xie et al., optimal one-bit perturbation from basin sizes

| Field | Content |
|---|---|
| Citation | M. Hu, L. Shen, X. Zan, X. Shang, W. Zhou. *An efficient algorithm to identify the optimal one-bit perturbation based on the basin-of-state size of Boolean networks.* Scientific Reports 6:26247, 2016. DOI [10.1038/srep26247](https://doi.org/10.1038/srep26247). |
| System | Boolean networks. |
| Structural description | Basin-of-state sizes computed from the state-transition graph. |
| Intervention | One-bit structural perturbation of the network. |
| Outcome | Change in basin-of-state size; identification of the *optimal* perturbation. |
| Exposure control | Basin size is itself the outcome, not a matching covariate. No exposure-matched control transitions. |
| Exact overlap | Efficient exact recomputation of basin/attractor structure after a single elementary edit — same algorithmic problem class as this study's `s_f(u)` computation. |
| Remaining distinction | Optimises over interventions; does not ask whether *model-relative residual* transitions differ from generic ones at equal exposure. |
| Threat to novelty | Precludes priority for efficient one-edit basin recomputation. |

### 4. Hoel, Albantakis & Tononi, causal emergence

| Field | Content |
|---|---|
| Citation | E. P. Hoel, L. Albantakis, G. Tononi. *Quantifying causal emergence shows that macro can beat micro.* PNAS 110(49):19790–19795, 2013. DOI [10.1073/pnas.1314922110](https://doi.org/10.1073/pnas.1314922110). |
| System | Finite discrete Markov/deterministic systems with micro and macro descriptions. |
| Structural description | Coarse-grained macro description (a grouping), not a codelength. |
| Intervention | Exhaustive uniform intervention over the whole micro state space (`do`-style). |
| Outcome | Effective information / effectiveness; causal emergence `CE = EI(macro) - EI(micro)`. |
| Exposure control | Uniform intervention distribution *replaces* the natural occupancy; exposure is imposed, not matched. |
| Exact overlap | Uses exhaustive exact intervention over a finite deterministic system, as here. |
| Remaining distinction | The structural quantity is a coarse-graining, not a compression residual; the outcome is an information measure, not attractor switching; there is no per-transition residual/regular comparison. |
| Threat to novelty | Precludes priority for "exhaustive exact intervention on finite deterministic systems to compare descriptions". Their supplement's XOR example also warns that compact macro description does not by itself imply a favourable causal conclusion — directly relevant to interpreting a *positive* result here. |

### 5–7. Zenil and colleagues, algorithmic information dynamics

| Field | Content |
|---|---|
| Citations | H. Zenil, N. A. Kiani, F. Marabita, Y. Deng, S. Elias, A. Schmidt, G. Ball, J. Tegnér. *An algorithmic information calculus for causal discovery and reprogramming systems.* iScience 19:1160–1172, 2019. DOI [10.1016/j.isci.2019.07.043](https://doi.org/10.1016/j.isci.2019.07.043). — H. Zenil, A. Adams. *Algorithmic Information Dynamics of Cellular Automata.* arXiv [2112.13177](https://arxiv.org/abs/2112.13177), 2021 (also in *Automata and Complexity*, DOI 10.1007/978-3-031-03986-7_8). — H. Zenil, N. A. Kiani, A. A. Zea, J. Tegnér. *Causal deconvolution by algorithmic generative models.* Nature Machine Intelligence 1:58–66, 2019. DOI [10.1038/s42256-018-0005-0](https://doi.org/10.1038/s42256-018-0005-0). |
| System | Networks, cellular automata (1D/2D, incl. Game of Life), generic discrete dynamical systems. |
| Structural description | Approximate algorithmic (Kolmogorov) complexity via the Block Decomposition Method / Coding Theorem Method. |
| Intervention | Element deletion/perturbation ("perturbation analysis in software space"); classify elements as *neutral*, *positive* or *negative* by their effect on estimated algorithmic complexity. |
| Outcome | Change in estimated algorithmic complexity; downstream steering/reprogramming of dynamics. |
| Exposure control | Not controlled. Elements are not matched on how often the dynamics actually visit them. |
| Exact overlap | This is the closest *conceptual* antecedent: it ranks components of a discrete dynamical system by a compression-relative criterion and links that ranking to interventional consequence. |
| Remaining distinction | The outcome is complexity change, not terminal-attractor switching; the structural quantity is an approximate algorithmic-complexity contribution, not an exact MDL residual of a declared parametric family; and there is no exposure-matched control set. |
| Threat to novelty | **Strongest single threat.** If one reads "compression-relative element importance predicts interventional consequence" as the claim, AID already asserts it (with the opposite sign convention in places). What remains distinctive here is the *registered, exposure-matched, exact-attractor* form of the test, and the fact that a null is a publishable outcome. |

### 8. Local sibling study — `aconsapart/ruler`, `research/three-outcome/finite_state_systems`

| Field | Content |
|---|---|
| Citation | Internal, unpublished. Frozen at `94e9d13bcd082a699094942f673f3c0149828bfc`, completed at `512ee42513e287cb984e0ef79be21e911147019b`. Read read-only at `/Users/r2q2/Projects/ruler-worktrees/rsr-three-outcome-2026-08-21/finite_state_systems`. |
| System | Finite deterministic maps (functional graphs), several state sizes, 2,608 systems. |
| Structural description | Exact decodable transition-exception codelength `R` — the same *kind* of quantity as the MDL residual used here. |
| Intervention | One-edge edit of a successor, exactly as here. |
| Outcome | Terminal basin reorganisation after the edit. |
| Exposure control | Yes: reachability mass `E` is an explicit predictor and the registered boundary law is `O = E*C`. |
| Exact overlap | **Very high.** Same system class, same intervention primitive, same exposure factorisation, overlapping codelength concept. |
| Remaining distinction | Its estimand is a *nested predictive-model increment* (does `R` add predictive value once `E`, `C`, `Q`, `P`, `L` are known). This study's estimand is a *matched within-system contrast* of the exposure-free ratio `theta = C / w` between one planted/residual transition and exposure-stratum-matched regular transitions. Different estimand, different matching, different families, different cohort. |
| Threat to novelty | **Decisive for framing.** That study already reported `Delta_R = 0`, isolated `Delta_R:L = 0` and `Delta_joint = 0`, each with 95% interval `[0, 0]`, on 864 identified structured confirmation systems, while a planted-interaction positive control passed. Its interpretation — "exception codelength provides no incremental organization prediction once the exact exposed-boundary baseline is known" — **anticipates a null here**. This study must therefore be presented as a *narrower, differently-estimated reproduction and extension*, never as the first or an unanswered finite-state test. |

### 9. Local sibling study — `research/fsm-local-disagreement-relabel-v2-20260823`

Frozen, outcome-free at `6faca214` in `aconsapart/ruler`. Asks whether a
circular-label localization score is stable under conjugate representations.
Not an exposure-matched residual-leverage experiment; explicitly forbids being
read as graph-invariant or confirmatory evidence. Recorded for completeness.

### 10. Local prior draft — `zitterbewegung/Winnower` Codex worktree

An **untracked, outcome-free** protocol packet
(`research/synthetic_fsm_residual_leverage_v1/`) exists in an unrelated Codex
worktree at `/Users/r2q2/.codex/.chatgpt-projects/.../worktrees/
synthetic-fsm-residual-leverage-v1`, on branch
`research/synthetic-fsm-residual-leverage-v1-20260823` whose tip is still the
audited base `598a774`. It specifies a *different* design (block-structured
64-state generators, SHA-256 ranking instead of a seeded RNG, a system-level
two-sided mean test, equivalence margins). **No implementation, no run, no
outcome.** It was read but not modified, adopted or extended. Its
`ARCHAEOLOGY.md` and `PREFREEZE_REVIEW.md` are the source of items 8 and 9
above.

## Also consulted, non-overlapping but bounding

- Nerode 1958 / Hopcroft 1971 / Park 1981 / Paige–Tarjan 1987 — finite-state
  minimisation and bisimulation. Precludes any claim that compressing a
  transition table is itself new.
- Wuensche 1998 (SFI 98-11-101) — basin-of-attraction fields for discrete
  dynamical networks. Precludes priority for basin portraits as summaries.
- Shalizi–Crutchfield 2001 — computational mechanics / causal states. Precludes
  treating failure of one declared model family as proof that no compressive
  description exists.
- Choo et al. 2019 (DOI 10.1038/s41598-019-49571-6) and NETBOS
  (DOI 10.1049/iet-syb.2017.0091) — basin-boundary control and redirected
  predecessor mass in Boolean networks. Same intervention family as item 3.

## Defensible novelty statement

> The searched literature contains close work on functional-graph statistics,
> Boolean-network structural perturbations, basin and attractor effects, causal
> information, and algorithmic-information perturbation. The search did not
> identify the exact registered comparison between a static compression-residual
> flag and exposure-controlled generic transition-edit leverage in finite
> deterministic maps.

Two mandatory qualifications attach to that sentence:

1. Item 5–7 (Zenil et al.) already assert a compression-relative element
   ranking with interventional meaning, so the contribution here is the
   *registered exposure-matched exact-attractor form of the test*, not the idea
   that compression and intervention are related.
2. Item 8 (the sibling finite-state study) has already reported an exact zero
   incremental effect for a transition-exception codelength on finite maps once
   exposure and the graph condition are known. Any result here that is null is
   a **replication**, and must be described as such.

## Consequence for the frozen design (recorded before freeze)

The prior art changes the *framing* only. It does not change the generator,
the codelength, the estimand, the matching, the seeds, the families, the gates
or the decision rule, all of which are fixed in `PROTOCOL.md`.

One mathematical consequence of the exact factorisation in `PROTOCOL.md`
section 6 was known before freezing and is stated here so it cannot be
presented later as a discovery: because `theta_f(u) = s_f(u) / 63` is
identically free of `visitCount`, the primary estimand compares a purely
structural per-edge quantity, and *pre-treatment* exposure matching therefore
controls the covariate that generates the `O = E*C` boundary reported in item
8. If FSM-H1 is null, the honest reading is that it replicates item 8's null in
a different estimand; if FSM-H1 confirms, the effect must come from the
residual edge's *graph position*, not from its exposure.
