# Submission Plan

Target: **ALIFE 2026** — Waterloo, Ontario, Canada, August 17–21, 2026
Portal: ssl.linklings.net/conferences/ALIFE/
Format: Full Paper, 3–8 pages (excluding references/acknowledgments)
Template: LaTeX/Overleaf/Word available at https://2026.alife.org/call-for-papers/
Proceedings: Open-access, published by MIT Press

---

## Deadlines

| Milestone | Date |
|-----------|------|
| Full Papers & Summaries Submission | **March 30, 2026** |
| Full Papers & Summaries Notification | June 7, 2026 |
| Camera-Ready Papers | June 21, 2026 |
| Late-Breaking Abstracts Submission | July 20, 2026 |
| Late-Breaking Abstracts Notification | July 27, 2026 |
| Conference | August 17–21, 2026 |

---

## Action Plan

### Phase 1: Condense (Now → March 22)

Current paper (paper_v11.md) is ~20 pages with appendices. Must cut to 8 pages.

**Keep:**
- Theorems 1–3 (orbit-class reduction, monotonicity, stabilization)
- One 1D experiment (ECA 30/54/110 convergence)
- One 2D experiment (LifeWiki survey or stabilization sweep)
- Key figures (convergence plot, 2D survey summary)

**Move to supplementary or drop:**
- Appendices A–D (reproducibility, survey tables, RL convergence)
- Theorems 4–5 (nonidentifiability/identifiability)
- 3D results
- Entropy-rate comparison (Section 5.3)
- Full survey tables
- Baseline selector comparison (summarize in one sentence instead)

**Existing ALIFE draft:** `paper/paper_alife2026.tex` and `paper/alifeconf.sty` already exist — build on these.

### Phase 2: Fiverr Editor (March 22–24)

- Hire a Fiverr/Upwork academic editor now, deliver the 8-page draft on March 22
- Budget: ~$150, request 48-hour turnaround
- Instructions to give the editor:
  - "Flag anything that reads as AI-generated or unclear"
  - "Check logical flow between sections"
  - "Note any jargon that wouldn't be clear to a broad ALife audience"
- Look for an editor with published papers in a quantitative field (physics, CS, math)

### Phase 3: Polish + Cold Emails (March 25–28)

- Incorporate editor feedback
- Rewrite intro and discussion in your own voice (no AI assist for these sections)
- Send 3–5 cold emails to researchers cited in the paper:

**Cold email targets (pick 3–5):**
- Peter Grunwald (MDL/NML authority)
- Oded Lachish (distance-to-periodicity, cited as [14])
- James Crutchfield or someone in his group (computational mechanics)
- Cosma Shalizi (coherent-structure filters)
- Adam Rupe (local causal states)

**Cold email template:**
> Dear Prof. X,
>
> I have a short paper on NML model selection for periodic decomposition
> of CA spacetimes that builds on your work on [specific thing]. I prove
> a stabilization theorem showing suboptimal candidates are eventually
> eliminated. Would you be willing to give brief feedback on the
> manuscript? I'd be happy to acknowledge your input.
>
> [Your name]

Don't expect replies before March 30. Any feedback received improves the camera-ready (due June 21).

### Phase 4: Submit (March 29)

- Submit as **Full Paper** (not Summary — this is unpublished work)
- Submit via ssl.linklings.net/conferences/ALIFE/

### Phase 5: After Submission

**Arxiv posting (optional):**
- Post the full paper (paper_v11.md version, not the 8-page cut) to arxiv after ALIFE submission
- Establishes priority for the full result set (Theorems 4–5, surveys, entropy-rate comparison)
- Share on Twitter/Bluesky, r/cellular_automata if comfortable

**While waiting for notification (April–June):**
- Incorporate any cold-email feedback into the full paper
- If accepted: prepare camera-ready (due June 21) incorporating reviewer comments
- If rejected: reviewer comments tell you exactly what to fix; resubmit to Complex Systems or Journal of Cellular Automata (no page limit, full paper fits)

---

## Fallback Options

| Option | Deadline | Format | Notes |
|--------|----------|--------|-------|
| ALIFE Late-Breaking Abstract | July 20, 2026 | 2 pages, poster only | Lower bar, still gets you to the conference |
| Complex Systems (journal) | Rolling | Full paper, no page limit | Published Redeker's particle language paper |
| Journal of Cellular Automata | Rolling | Full paper | Dedicated CA venue |
| Chaos (AIP) | Rolling | Regular article | Ambitious — expects computational mechanics comparison |
| Physica D | Rolling | Regular article | Ambitious — strong theoretical expectations |

---

## What NOT to Do

- Don't skip option 4 (Editage/AJE professional editing) — your English is fine, not worth $400+
- Don't post to arxiv before submission if you're uncomfortable with it — ALIFE proceedings are published by MIT Press, so you'll have a real publication regardless
- Don't try to keep all 20 pages in the 8-page cut — ruthless compression is better than cramped formatting
- Don't use AI to rewrite the intro/discussion — these are the sections where your voice matters most

---

## Budget

| Item | Cost |
|------|------|
| Fiverr/Upwork editor | ~$150 |
| ALIFE registration (if accepted) | TBD |
| Travel to Waterloo (if accepted) | TBD |
| **Total pre-submission** | **~$150** |
