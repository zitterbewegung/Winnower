#!/usr/bin/env python3
"""Build the reviewer-facing evaluation site (review_site/index.html).

Assembles the paper abstract, claim ledger, key figures, and result tables
into a single static HTML page aimed at someone evaluating the paper. Uses only the Python standard library.

Usage:
    python scripts/build_review_site.py                # relative image paths
    python scripts/build_review_site.py --embed-images # portable single file
    python scripts/build_review_site.py --pages _site  # deployable site dir
"""

from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "review_site"
ALIFE = ROOT / "outputs" / "alife_2026"

# --------------------------------------------------------------------------
# Content configuration
# --------------------------------------------------------------------------

FIGURES = [
    dict(
        path=ALIFE / "editable_figures" / "algorithm_detailed.png",
        title="Algorithm overview",
        caption=(
            "A candidate (period, shift) pair induces an orbit partition of the "
            "spacetime. Majority vote on each orbit class gives the best-fitting "
            "background B*; the residual mask M = U ⊕ B* marks every cell the "
            "background cannot explain. Candidates are compared with a "
            "Bernoulli NML score (fit + complexity)."
        ),
        source="scripts/alife/alife_algorithm_figure.py",
    ),
    dict(
        path=ALIFE / "rule_diagrams" / "representative_rules_1d.png",
        title="Representative 1D rules (ECA 30 / 54 / 110)",
        caption=(
            "Spacetime, selected background B*, and residual mask M for the three focus "
            "elementary CA. Rule 54 decomposes cleanly into a periodic background "
            "plus particle-like residuals; Rule 30 stays diffuse."
        ),
        source="scripts/alife/alife_rule_diagrams.py",
    ),
    dict(
        path=ALIFE / "rule_diagrams" / "representative_rules_2d.png",
        title="Representative 2D rules",
        caption=(
            "Life-like rules with structured residuals (e.g. Diamoeba, Maze with "
            "Mice, S37/B11): the selected background absorbs the bulk of the "
            "pattern while the sparse residual mask stays visibly organized."
        ),
        source="scripts/alife/alife_rule_diagrams.py",
    ),
    dict(
        path=ALIFE / "rule_diagrams" / "representative_rules_3d.png",
        title="Representative 3D rules",
        caption="The same decomposition applied to 3D totalistic rules.",
        source="scripts/alife/alife_rule_diagrams.py",
    ),
    dict(
        path=ALIFE / "editable_figures" / "stabilization_summary.png",
        title="Period stabilization",
        caption=(
            "Selected period vs. horizon T for representative rules: the selector "
            "locks onto a period and the NML margin (bits between winner and "
            "runner-up) grows after locking."
        ),
        source="scripts/alife/alife_stabilization_summary.py",
    ),
    dict(
        path=ALIFE / "null_controls" / "null_controls_margin.png",
        title="Null controls — NML margin",
        caption=(
            "Original spacetimes vs. time-shuffled, space-shuffled, and "
            "density-matched Bernoulli controls. Structure found in originals is "
            "not reproduced by the controls."
        ),
        source="scripts/alife/alife_run_all.py (null_controls)",
    ),
    dict(
        path=ALIFE / "null_controls" / "null_controls_defect_rate.png",
        title="Null controls — residual rate",
        caption="Residual (defect) rates for the same control panel.",
        source="scripts/alife/alife_run_all.py (null_controls)",
    ),
    dict(
        path=ALIFE / "eca_atlas" / "eca_atlas_periods.png",
        title="ECA atlas — selected periods",
        caption="Final selected period for all 256 elementary CA rules.",
        source="scripts/alife/alife_run_all.py (eca_atlas)",
    ),
    dict(
        path=ALIFE / "eca_atlas" / "eca_atlas_stability.png",
        title="ECA atlas — stability",
        caption="Stability of the selection across seeds/horizons for the ECA atlas.",
        source="scripts/alife/alife_run_all.py (eca_atlas)",
    ),
    dict(
        path=ALIFE / "seed_stability" / "seed_stability_summary.png",
        title="Seed stability",
        caption=(
            "Representative rules re-run across 10 seeds and 6 horizons: modal "
            "period agreement, transition counts, and residual variability."
        ),
        source="scripts/alife/alife_run_all.py (seed_stability)",
    ),
    dict(
        path=ALIFE / "candidate_range_robustness" / "candidate_range_robustness.png",
        title="Candidate-range robustness",
        caption=(
            "Sensitivity of the selection to the scanned period/shift ranges "
            "(small vs. default vs. large candidate grids)."
        ),
        source="scripts/alife/alife_run_all.py (candidate_range_robustness)",
    ),
    dict(
        path=ALIFE / "lifewiki_horizon_sweep" / "lifewiki_horizon_heatmap.png",
        title="LifeWiki survey — horizon sweep",
        caption=(
            "Selected period vs. horizon across the LifeWiki rule catalog: most "
            "rules stay at low period; a small set reveals longer periodic "
            "organization at larger horizons."
        ),
        source="scripts/alife/alife_run_all.py (lifewiki_horizon_sweep)",
    ),
    dict(
        path=ALIFE / "survey_3d" / "alife_3d_survey.png",
        title="3D survey",
        caption="Survey of 3D totalistic rules with the same pipeline.",
        source="scripts/alife/alife_run_all.py (survey_3d)",
    ),
    dict(
        path=ALIFE / "rule_diagrams_3d_voxel" / "diamoeba3d" / "diamoeba3d_voxel_decomposition.png",
        title="3D voxel decomposition — diamoeba3d",
        caption="Voxel view of spacetime U, selected background B*, and residual mask M for a 3D rule.",
        source="scripts/alife/alife_rule_diagrams.py",
    ),
]

TABLES = [
    dict(
        path=ALIFE / "ground_truth" / "ground_truth_summary.csv",
        title="Ground-truth recovery (planted periodicity)",
        caption=(
            "Spacetimes constructed to be exactly relative-periodic with a known "
            "(period, shift), corrupted by bit flips at rate flip_rate, then run "
            "through the shipped selector. Accuracy = fraction of runs recovering "
            "the planted value."
        ),
        claim="Selector recovers known ground truth",
    ),
    dict(
        path=ALIFE / "mask_structure" / "mask_structure_summary.csv",
        title="Residual-mask organization (vs shuffled baselines)",
        caption=(
            "Run-length codelength and component-count ratios of each selected "
            "residual mask against 20 uniformly shuffled masks of the same "
            "density (ratio 1 = unstructured). Originals of the focal rules sit "
            "far below 1; every Bernoulli control sits at 1.000; ECA-30's "
            "diffuse residual also scores 1.000 — the statistic is calibrated "
            "in both directions. Time-shuffled controls retain per-frame "
            "spatial organization by construction."
        ),
        claim="Residual organization is measured, not eyeballed",
    ),
    dict(
        path=ALIFE / "null_controls" / "null_controls_summary.csv",
        title="Null controls (summary)",
        caption=(
            "Original spacetimes vs. shuffled/Bernoulli controls, same selector. "
            "Large margins and low residual rates for originals — and not for "
            "controls — indicate the method detects real structure. "
            "No null-control false positives were observed."
        ),
        claim="Selector does not hallucinate structure in noise",
    ),
    dict(
        path=ALIFE / "seed_stability" / "seed_stability_summary.csv",
        title="Seed stability (summary)",
        caption=(
            "Per-rule agreement of the final selected period across 10 seeds, "
            "with transition counts and residual-rate coefficient of variation."
        ),
        claim="Selection is stable across random initial conditions",
    ),
    dict(
        path=ALIFE / "candidate_range_robustness" / "candidate_range_robustness_summary.csv",
        title="Candidate-range robustness (summary)",
        caption=(
            "Whether the selected period/shift changes when the scanned candidate "
            "grid is shrunk or enlarged."
        ),
        claim="Results are not an artifact of the scanned candidate range",
    ),
    dict(
        path=ALIFE / "survey_3d" / "alife_3d_survey_summary.csv",
        title="3D survey (summary)",
        caption="Selected periods and margins for the 3D rules.",
        claim="The pipeline generalizes beyond 1D/2D",
    ),
    dict(
        path=ALIFE / "eca_atlas" / "eca_atlas_summary.csv",
        title="ECA atlas (all 256 rules)",
        caption=(
            "Final modal period, stability, margins, and residual rate for every "
            "elementary CA rule. Use the filter box to find a rule."
        ),
        claim="Full 1D coverage, not cherry-picked examples",
        filterable=True,
        collapsed=True,
    ),
    dict(
        path=ALIFE / "lifewiki_horizon_sweep" / "lifewiki_horizon_transition_summary.csv",
        title="LifeWiki horizon sweep (per rule)",
        caption=(
            "Final selected period and per-seed transition counts for each "
            "LifeWiki rule across horizons up to T=800."
        ),
        claim="2D survey coverage across the LifeWiki catalog",
        filterable=True,
        collapsed=True,
    ),
]

CONTRIBUTIONS = [
    ("The Winnower tool",
     "An open-source, deterministic pipeline that splits a CA spacetime into a periodic background B* and a residual mask M, with an in-browser reproduction of every reported number."),
    ("Calibrated accuracy",
     "Recovers planted ground-truth periodicity at realistic noise levels, and selects no periodic structure on time-shuffled, space-shuffled, or Bernoulli null controls — zero false positives."),
    ("Linear-time background fitting",
     "Majority vote on orbit classes: one pass over the data per candidate (period, shift), which is what makes whole-catalog 1D/2D/3D surveys practical."),
    ("Complexity-aware selection via Bernoulli NML",
     "Prevents the period inflation that raw fit criteria demonstrably suffer (plain NLL picks the largest scanned period on every Life-like rule tested). The underlying refinement/monotonicity relationship is an exact characterization — velocity-matched divisibility is necessary as well as sufficient for universal improvement — proved directly and confirmed by an exhaustive test."),
]

LIMITATIONS = [
    "The selector returns the best-compressing global explanation, which need not match a physicist's preferred background when the residual itself carries periodic structure.",
    "At period 1 the reported shift is arbitrary (a tie), so shift values for aperiodic rules carry no information.",
    "Periodicity outside the scanned candidate grid is invisible; the candidate-range robustness runs quantify this.",
    "The residual mask says where structure is, not how it interacts — no particle interaction analysis.",
    "Scaling observations (e.g. S37/B11) rest on limited seeds and sizes; the run-length diagnostic is raster-order dependent.",
]

REPRO_STEPS = [
    ("Install", "pip install -e .", "Python 3.11+; numpy, numba, scipy, pandas, matplotlib, lz4, typer."),
    ("Run the full experiment suite", "make data",
     "Null controls, seed stability, range robustness, LifeWiki survey, ECA atlas, 3D survey, counterexample stress tests. ~30–60 min. Deterministic (base seed 11); outputs land in outputs/alife_2026/."),
    ("Regenerate figures", "make figures", "Rule diagrams, mechanism panels, algorithm figure, stabilization summary."),
    ("Run the test suite", "make test", "364 tests covering simulators, fitting, scoring, selection, and the theory notes (including an exhaustive refinement-equivalence check)."),
    ("Rebuild the paper", "make paper", "Compiles paper/paper_alife2026.tex."),
    ("Rebuild this page", "python scripts/build_review_site.py", "Regenerates review_site/index.html from the current outputs."),
    ("Try a single rule interactively",
     "python -m relative_symmetry_repair analyze --rule 110",
     "Also: analyze2d --rule life, analyze3d --rule diamoeba3d."),
]

REPO_MAP = [
    ("paper/paper_alife2026.pdf", "The submission PDF."),
    ("paper/alife2026_lba.pdf", "ALIFE 2026 late-breaking abstract (2 pages): the component view of the tool and the exact period-inflation characterization."),
    ("paper/paper_alife2026.tex", "LaTeX source; figures pulled from outputs/."),
    ("docs/CLAIM_LEDGER.md", "Claim-by-claim audit: status, caveats, what remains."),
    ("docs/THEORY_NOTE.md", "Extended theory notes."),
    ("src/relative_symmetry_repair/", "Core library: simulators (eca.py, ca2d.py, ca3d.py), fitting (repair.py, repair_nd.py), NML scoring (coding.py), selection (selection.py), CLI."),
    ("scripts/alife/alife_run_all.py", "One-shot driver for every experiment in the paper."),
    ("outputs/alife_2026/", "Generated data behind every figure and table, with per-experiment manifest.json files recording seeds and parameters."),
    ("webdemo/", "In-browser live reproduction (Pyodide bootstrap, page, worker); verified by scripts/verify_webdemo_bootstrap.py."),
    ("proofs/", "Lean 4 proof artifacts (supporting material at documented completeness; see proofs/README.md). The paper's claims rest on the experiments and the reproducible pipeline, not on these artifacts."),
    ("tests/", "364-test suite."),
    ("REPRODUCING.md", "Full reproduction pipeline, step by step."),
]

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def fmt_cell(value: str) -> str:
    """Round long floats for display; leave everything else alone."""
    v = value.strip()
    try:
        f = float(v)
    except ValueError:
        return v
    if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
        return v
    if f == int(f) and abs(f) < 1e15 and "e" not in v.lower() and "." in v:
        return str(int(f))
    return f"{f:.4g}"


def csv_to_table(path: Path, filterable: bool = False, table_id: str = "") -> str:
    if not path.exists():
        return (
            f'<p class="missing">Not generated yet — expected at '
            f'<code>{esc(path.relative_to(ROOT))}</code>. Run <code>make data</code>.</p>'
        )
    with path.open(newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return '<p class="missing">Empty CSV.</p>'
    header, body = rows[0], rows[1:]
    parts = []
    if filterable:
        parts.append(
            f'<input class="tbl-filter" type="search" placeholder="Filter rows…" '
            f'oninput="filterTable(this, \'{table_id}\')">'
        )
    parts.append(f'<div class="tbl-wrap"><table id="{table_id}"><thead><tr>')
    for i, h in enumerate(header):
        parts.append(
            f'<th onclick="sortTable(\'{table_id}\', {i})" title="Click to sort">{esc(h)}</th>'
        )
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>" + "".join(f"<td>{esc(fmt_cell(c))}</td>" for c in row) + "</tr>")
    parts.append("</tbody></table></div>")
    parts.append(f'<p class="tbl-meta">{len(body)} rows · source: <code>{esc(path.relative_to(ROOT))}</code></p>')
    return "".join(parts)


def extract_tex_field(tex: str, name: str) -> str:
    m = re.search(r"\\" + name + r"\{(.+?)\}", tex, re.S)
    return m.group(1).strip() if m else ""


def extract_abstract(tex: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.+?)\\end\{abstract\}", tex, re.S)
    if not m:
        return ""
    text = m.group(1)
    text = re.sub(r"\\citep?\{[^}]*\}", "", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("~", " ").replace("$", "")
    return " ".join(text.split())


def md_inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def md_to_html(md: str) -> str:
    """Minimal Markdown renderer: headings, hr, lists, tables, paragraphs."""
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    para: list[str] = []
    in_list = False

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
            para = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s\-|:]+\|\s*$", lines[i + 1]):
            flush_para()
            close_list()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            out.append('<div class="tbl-wrap"><table><thead><tr>')
            out.extend(f"<th>{md_inline(h)}</th>" for h in header)
            out.append("</tr></thead><tbody>")
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table></div>")
            continue
        if not stripped:
            flush_para()
            close_list()
        elif stripped.startswith("#"):
            flush_para()
            close_list()
            level = min(len(stripped) - len(stripped.lstrip("#")), 4)
            out.append(f"<h{level + 1}>{md_inline(stripped.lstrip('#').strip())}</h{level + 1}>")
        elif stripped in ("---", "***", "___"):
            flush_para()
            close_list()
            out.append("<hr>")
        elif re.match(r"^[-*+]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            flush_para()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + md_inline(re.sub(r"^([-*+]|\d+\.)\s+", "", stripped)) + "</li>")
        else:
            para.append(stripped)
        i += 1
    flush_para()
    close_list()
    return "\n".join(out)


def badge_for_status(text: str) -> str:
    """Wrap claim-ledger status keywords in colored badges."""
    rules = [
        (r"CORRECT AS STATED", "ok"),
        (r"CORRECT AFTER (EDIT|CLARIFICATION)", "ok"),
        (r"CORRECT IN SUBSTANCE", "ok"),
        (r"PLAUSIBLE( BUT ONLY SKETCHED| / SKETCHED)?", "warn"),
        (r"EMPIRICAL ONLY", "info"),
    ]
    for pattern, cls in rules:
        text = re.sub(pattern, lambda m: f'<span class="badge {cls}">{m.group(0)}</span>', text)
    return text


def img_src(path: Path, embed: bool) -> str:
    if embed:
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{data}"
    return "../" + path.relative_to(ROOT).as_posix()


def stress_stats() -> list[tuple[str, str]]:
    path = ALIFE / "counterexample_stress" / "counterexample_stress_summary.md"
    if not path.exists():
        return []
    stats = []
    for line in path.read_text().splitlines():
        m = re.match(r"^- ([^:]+): (\d+)", line.strip())
        if m:
            stats.append((m.group(1), m.group(2)))
    return stats


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------


def _demo_expected_rows() -> dict:
    """Committed run-level rows the in-browser demo compares against."""
    rows: dict[str, dict] = {}
    for rel in (
        "outputs/alife_2026/eca_atlas/eca_atlas_runs.csv",
        "outputs/alife_2026/seed_stability/seed_stability_runs.csv",
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        with path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                key = f"{row['rule']}|{int(row['seed'])}|{int(row['horizon'])}"
                rows[key] = row
    return rows


def write_demo_assets(site: Path) -> None:
    """Copy the interactive reproduction demo into a --pages site dir."""
    webdemo = ROOT / "webdemo"
    for name in ("reproduce.html", "repro_worker.js"):
        shutil.copy2(webdemo / name, site / name)

    zip_path = site / "winnower_src.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(webdemo / "bootstrap.py", "bootstrap.py")
        pkg = ROOT / "src" / "relative_symmetry_repair"
        for py in sorted(pkg.glob("*.py")):
            zf.write(py, f"relative_symmetry_repair/{py.name}")

    (site / "expected_runs.json").write_text(json.dumps(_demo_expected_rows()))


def build(embed: bool, pdf_href: str = "../paper/paper_alife2026.pdf",
          lba_href: str = "../paper/alife2026_lba.pdf", live_demo: bool = False) -> str:
    tex = (ROOT / "paper" / "paper_alife2026.tex").read_text(errors="replace")
    title = extract_tex_field(tex, "title") or "Winnower — reviewer guide"
    abstract = extract_abstract(tex)

    ledger_path = ROOT / "docs" / "CLAIM_LEDGER.md"
    ledger_html = ""
    if ledger_path.exists():
        ledger_md = ledger_path.read_text()
        ledger_md = re.sub(r"^# Claim Ledger\s*", "", ledger_md)
        ledger_html = badge_for_status(md_to_html(ledger_md))

    manifest = {}
    manifest_path = ALIFE / "results_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())

    figures_html = []
    for fig in FIGURES:
        p: Path = fig["path"]
        if not p.exists():
            figures_html.append(
                f'<figure class="card"><div class="missing">Missing: '
                f'<code>{esc(p.relative_to(ROOT))}</code> — run <code>make data figures</code>.</div>'
                f'<figcaption><strong>{esc(fig["title"])}</strong></figcaption></figure>'
            )
            continue
        src = img_src(p, embed)
        figures_html.append(
            '<figure class="card">'
            f'<a href="{src}" target="_blank" rel="noopener"><img loading="lazy" src="{src}" alt="{esc(fig["title"])}"></a>'
            f'<figcaption><strong>{esc(fig["title"])}.</strong> {esc(fig["caption"])} '
            f'<span class="src">Generated by <code>{esc(fig["source"])}</code></span></figcaption>'
            "</figure>"
        )

    tables_html = []
    for idx, tbl in enumerate(TABLES):
        tid = f"tbl{idx}"
        inner = csv_to_table(tbl["path"], tbl.get("filterable", False), tid)
        block = (
            f'<h3>{esc(tbl["title"])}</h3>'
            f'<p class="claim-tag">Supports: <em>{esc(tbl["claim"])}</em></p>'
            f'<p>{esc(tbl["caption"])}</p>{inner}'
        )
        if tbl.get("collapsed"):
            block = (
                f'<details><summary><h3 class="inline">{esc(tbl["title"])}</h3>'
                f'<span class="claim-tag"> — {esc(tbl["claim"])}</span></summary>'
                f'<p>{esc(tbl["caption"])}</p>{inner}</details>'
            )
        tables_html.append(f'<div class="tbl-block">{block}</div>')

    stress = stress_stats()
    stress_html = ""
    if stress:
        tiles = "".join(
            f'<div class="tile"><div class="tile-num">{esc(n)}</div><div class="tile-label">{esc(label)}</div></div>'
            for label, n in stress
        )
        stress_html = (
            "<h3>Counterexample stress report</h3>"
            "<p>The pipeline actively looks for its own failure modes: non-unique winners, "
            "razor-thin margins, candidate-range instability, and false positives on null "
            "controls. Observed counts:</p>"
            f'<div class="tiles">{tiles}</div>'
            '<p class="tbl-meta">Full report: <code>outputs/alife_2026/counterexample_stress/counterexample_stress_summary.md</code>. '
            "Non-unique winners are dominated by trivial/degenerate rules (e.g. ECA-0) where "
            "many shifts fit an empty background equally well; margins ≤ 0.5 bits and "
            "null-control false positives were both zero.</p>"
        )

    contribs = "".join(
        f"<li><strong>{esc(h)}</strong> — {esc(b)}</li>" for h, b in CONTRIBUTIONS
    )
    limits = "".join(f"<li>{esc(x)}</li>" for x in LIMITATIONS)

    repro_rows = "".join(
        f'<div class="step"><div class="step-title">{esc(t)}</div>'
        f"<pre><code>{esc(cmd)}</code></pre><p>{esc(note)}</p></div>"
        for t, cmd, note in REPRO_STEPS
    )

    repo_rows = "".join(
        f"<tr><td><code>{esc(p)}</code></td><td>{esc(d)}</td></tr>" for p, d in REPO_MAP
    )

    seed = manifest.get("base_seed", "?")
    flags = manifest.get("flags", {})
    flags_note = ", ".join(k.replace("run_", "").replace("_", " ") for k, v in flags.items() if v)

    demo_nav = (
        '<a href="reproduce.html" class="demo-link">▶ Live reproduction</a>'
        if live_demo else ""
    )
    demo_overview = (
        '<a href="reproduce.html">Run the pipeline in your browser</a>'
        if live_demo else ""
    )
    demo_repro_note = (
        '<div class="card"><strong>Interactive:</strong> the '
        '<a href="reproduce.html">live reproduction page</a> runs the actual '
        "pipeline (simulation → candidate scan → Bernoulli-NML selection) in "
        "your browser via WebAssembly Python and checks the result against the "
        "committed CSV row for the same rule, seed, and horizon — no install "
        "required. It accepts arbitrary rules (any ECA number, any 2D B/S "
        "rulestring, arbitrary 3D birth/survive count sets like "
        "<code>B5-7,9/S4,6-8</code>) and renders 2D/3D results as rotatable "
        "voxel views with time scrubbing.</div>"
        if live_demo else
        "<p>The hosted version of this page also offers an in-browser live "
        "reproduction (see <code>webdemo/</code> and the GitHub Pages site).</p>"
    )

    pdf_note = ""
    if embed and pdf_href.startswith("../"):
        pdf_note = (
            '<p class="tbl-meta">This is the portable single-file build: the PDF link works '
            "only when the page sits inside the repository at <code>review_site/</code>.</p>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reviewer guide — {esc(title)}</title>
<style>
:root {{
  --bg: #f7f7f5; --fg: #1a1a1a; --muted: #5a5a55; --card: #ffffff;
  --line: #e0dfda; --accent: #305c7a; --accent-soft: #e7eef3;
  --ok: #1c7a45; --ok-bg: #e2f3e8; --warn: #8a6100; --warn-bg: #fdf1d7;
  --info: #305c7a; --info-bg: #e7eef3; --code-bg: #efeeea;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #16181b; --fg: #e6e4df; --muted: #a3a29b; --card: #1e2126;
    --line: #33363c; --accent: #7fb0d0; --accent-soft: #22303a;
    --ok: #6fce96; --ok-bg: #1c3327; --warn: #e5c069; --warn-bg: #38301a;
    --info: #7fb0d0; --info-bg: #22303a; --code-bg: #262a30;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg);
  font: 16px/1.6 Georgia, 'Times New Roman', serif; }}
header {{ background: var(--card); border-bottom: 1px solid var(--line);
  padding: 2rem 1.5rem 1rem; }}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 1.5rem; }}
header .wrap {{ padding: 0; }}
h1 {{ font-size: 1.7rem; line-height: 1.3; margin: 0 0 .4rem; }}
.subtitle {{ color: var(--muted); margin: 0 0 1rem; }}
nav {{ position: sticky; top: 0; z-index: 5; background: var(--card);
  border-bottom: 1px solid var(--line);
  font-family: system-ui, -apple-system, sans-serif; }}
nav .wrap {{ display: flex; gap: .25rem; flex-wrap: wrap; padding: .4rem 1.5rem; }}
nav a {{ padding: .45rem .8rem; border-radius: 6px; text-decoration: none;
  color: var(--fg); font-size: .92rem; }}
nav a:hover {{ background: var(--accent-soft); }}
nav a.active {{ background: var(--accent); color: #fff; }}
nav a.demo-link {{ border: 1.5px solid var(--accent); color: var(--accent);
  font-weight: 600; }}
section {{ display: none; padding: 2rem 0 3rem; }}
section.active {{ display: block; }}
h2 {{ font-size: 1.35rem; border-bottom: 2px solid var(--accent);
  padding-bottom: .3rem; margin-top: 0; }}
h3 {{ font-size: 1.1rem; margin: 1.6rem 0 .4rem; }}
h3.inline {{ display: inline; }}
a {{ color: var(--accent); }}
code {{ background: var(--code-bg); padding: .08em .35em; border-radius: 4px;
  font-size: .86em; font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; }}
pre {{ background: var(--code-bg); padding: .7rem .9rem; border-radius: 8px;
  overflow-x: auto; }}
pre code {{ background: none; padding: 0; }}
.card {{ background: var(--card); border: 1px solid var(--line);
  border-radius: 10px; padding: 1rem; margin: 0 0 1.5rem; }}
figure.card img {{ max-width: 100%; height: auto; border-radius: 6px;
  display: block; margin: 0 auto; }}
figcaption {{ font-size: .92rem; color: var(--muted); margin-top: .6rem; }}
figcaption strong {{ color: var(--fg); }}
.src {{ display: block; margin-top: .25rem; font-size: .85rem; }}
.abstract {{ background: var(--card); border-left: 4px solid var(--accent);
  border-radius: 0 10px 10px 0; padding: 1rem 1.2rem; margin: 1rem 0; }}
.links {{ display: flex; flex-wrap: wrap; gap: .6rem; margin: 1rem 0;
  font-family: system-ui, sans-serif; font-size: .9rem; }}
.links a {{ background: var(--accent); color: #fff; text-decoration: none;
  padding: .5rem .9rem; border-radius: 8px; }}
.links a.secondary {{ background: var(--accent-soft); color: var(--accent); }}
.badge {{ font-family: system-ui, sans-serif; font-size: .72rem; font-weight: 600;
  padding: .15em .55em; border-radius: 999px; white-space: nowrap; vertical-align: middle; }}
.badge.ok {{ color: var(--ok); background: var(--ok-bg); }}
.badge.warn {{ color: var(--warn); background: var(--warn-bg); }}
.badge.info {{ color: var(--info); background: var(--info-bg); }}
.tbl-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px;
  background: var(--card); }}
table {{ border-collapse: collapse; width: 100%; font-size: .82rem;
  font-family: system-ui, sans-serif; }}
th, td {{ padding: .4rem .6rem; border-bottom: 1px solid var(--line);
  text-align: left; white-space: nowrap; }}
th {{ background: var(--accent-soft); position: sticky; top: 0; cursor: pointer;
  user-select: none; }}
tbody tr:hover {{ background: var(--accent-soft); }}
.tbl-meta {{ font-size: .82rem; color: var(--muted); }}
.tbl-filter {{ font: inherit; padding: .45rem .7rem; margin: .4rem 0;
  border: 1px solid var(--line); border-radius: 8px; width: 100%; max-width: 340px;
  background: var(--card); color: var(--fg); }}
.tbl-block {{ margin-bottom: 2rem; }}
.claim-tag {{ font-family: system-ui, sans-serif; font-size: .85rem;
  color: var(--accent); margin: .1rem 0 .3rem; }}
details {{ border: 1px solid var(--line); border-radius: 10px; padding: .8rem 1rem;
  background: var(--card); }}
details summary {{ cursor: pointer; }}
.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: .8rem; margin: 1rem 0; }}
.tile {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px;
  padding: .9rem; text-align: center; }}
.tile-num {{ font-size: 1.6rem; font-weight: 700; font-family: system-ui, sans-serif; }}
.tile-label {{ font-size: .82rem; color: var(--muted);
  font-family: system-ui, sans-serif; }}
.step {{ margin-bottom: 1.2rem; }}
.step-title {{ font-weight: 700; }}
.missing {{ color: var(--warn); background: var(--warn-bg); padding: .6rem .8rem;
  border-radius: 8px; font-size: .9rem; }}
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
@media (max-width: 800px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
footer {{ border-top: 1px solid var(--line); color: var(--muted);
  font-size: .85rem; padding: 1.5rem 0 3rem; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>{esc(title)}</h1>
    <p class="subtitle">Reviewer guide · the <em>Winnower</em> tool and paper artifact</p>
  </div>
</header>
<nav><div class="wrap">
  <a href="#overview" class="active" onclick="return show('overview')">Overview</a>
  <a href="#latebreaking" onclick="return show('latebreaking')">Late-breaking</a>
  <a href="#claims" onclick="return show('claims')">Claims &amp; theory</a>
  <a href="#figures" onclick="return show('figures')">Figures</a>
  <a href="#results" onclick="return show('results')">Results &amp; robustness</a>
  <a href="#reproduce" onclick="return show('reproduce')">Reproduce</a>
  <a href="#repo" onclick="return show('repo')">Repository map</a>
  {demo_nav}
</div></nav>
<main class="wrap">

<section id="overview" class="active">
  <h2>What this paper does</h2>
  <div class="abstract"><strong>Abstract.</strong> {esc(abstract)}</div>
  <div class="links">
    <a href="{pdf_href}" target="_blank" rel="noopener">Open the paper (PDF)</a>
    {demo_overview}
    <a href="#reproduce" class="secondary" onclick="return show('reproduce')">Reproduce the results</a>
    <a href="#claims" class="secondary" onclick="return show('claims')">Audit the claims</a>
  </div>
  {pdf_note}
  <div class="two-col">
    <div>
      <h3>Claimed contributions</h3>
      <ul>{contribs}</ul>
    </div>
    <div>
      <h3>Known limitations (author-acknowledged)</h3>
      <ul>{limits}</ul>
    </div>
  </div>
  <h3>Suggested 20-minute evaluation path</h3>
  <ol>
    <li>Read the abstract above, then skim the <a href="#figures" onclick="return show('figures')">algorithm figure and representative-rule panels</a> to see what the decomposition produces.</li>
    <li>Check the <a href="#results" onclick="return show('results')">null controls</a> — the central sanity check that the selector does not find structure in shuffled data.</li>
    <li>Check the <a href="#results" onclick="return show('results')">ground-truth recovery table</a> — calibration showing the selector finds planted periodicity and reports nothing on noise.</li>
    <li>Skim the <a href="#claims" onclick="return show('claims')">claim ledger</a>, the project's own audit of every mathematical statement. The supporting math is deliberately secondary to the tool, and the ledger says exactly how strong each statement is.</li>
    <li>Optionally run <code>make test</code> and one <code>analyze</code> command from the <a href="#reproduce" onclick="return show('reproduce')">reproduce tab</a>.</li>
  </ol>
</section>

<section id="latebreaking">
  <h2>Late-breaking abstract — ALIFE 2026</h2>
  <p><strong>Inside Winnower: component semantics of CA background
  decomposition, and the exact boundary of period inflation.</strong>
  A two-page late-breaking abstract prepared for
  <a href="https://2026.alife.org/" target="_blank" rel="noopener">ALIFE 2026</a>
  (Waterloo, Ontario, Canada, August 17&ndash;21, 2026 &mdash; theme
  &ldquo;Living and Life-like Complex Adaptive Systems&rdquo;). It gives a
  component view of the tool &mdash; each pipeline stage a diagram element with
  an explicit semantic role &mdash; and an exact characterization of when the
  selector's complexity penalty is needed. The late-breaking track accepts
  work in progress in a <em>maximum of 2 pages excluding references</em>;
  accepted abstracts are presented as posters and are not included in the
  proceedings (submissions due July&nbsp;20, 2026 AoE; notification
  July&nbsp;27, 2026).</p>
  <div class="links">
    <a href="{lba_href}" target="_blank" rel="noopener">Open the late-breaking abstract (PDF, 2 pages)</a>
    <a href="reproduce.html" class="secondary">Reproduce it in the browser</a>
  </div>
  <h3>The result, in plain terms</h3>
  <p>Every fit-based background detector faces <em>period inflation</em>: a
  candidate with a longer period has more parameters, so it can never fit
  worse, and a selector scoring by fit alone drifts to the largest model
  scanned. The late-breaking result pins down <em>exactly</em> when that
  pressure exists. For two constant-velocity candidates, five natural
  conditions are all equivalent: velocity-matched divisibility of the
  periods and shifts; one translation being a power of the other;
  orbit-partition refinement; model-class nesting; and universal
  improvement (on <em>every</em> spacetime) of both the residual count and
  the Bernoulli negative log-likelihood. Divisibility is
  <em>necessary</em>, not just sufficient &mdash; whenever it fails, some
  spacetime makes the longer-period candidate strictly worse. That makes
  divisibility the precise frontier of the guaranteed-improvement regime,
  and therefore the precise set of comparisons Winnower's NML complexity
  penalty exists to neutralize.</p>
  <h3>How it connects to the tool on this site</h3>
  <ul>
    <li><strong>A component view:</strong> the abstract's figure names each
    stage of the pipeline &mdash; candidate, orbit classes, majority-vote fit,
    background, residual mask, and the Bernoulli-NML score &mdash; and pairs it
    with the object it computes, so the diagram doubles as a legend for the
    <a href="#overview" onclick="return show('overview')">tool overview</a>.</li>
    <li><strong>Exhaustively tested:</strong>
    <code>tests/test_theory.py::test_refinement_iff_velocity_matched_multiple</code>
    checks the finite-window form of the equivalence over every candidate
    pair on a 6&times;4 grid.</li>
    <li><strong>Visible in the live demo:</strong> the
    <a href="reproduce.html">in-browser reproduction</a> reports, for any
    supported rule, seed, and horizon, the per-period fit (NLL) and
    penalized (NML) scores side by side &mdash; the fit column improves
    along velocity-matched chains exactly as predicted, while the penalized
    column resists.</li>
    <li><strong>At survey scale:</strong> the
    <a href="#figures" onclick="return show('figures')">selector-ablation figure</a>
    shows the practical stakes: at horizon 100, plain NLL selects the
    largest scanned period on all 105 non-degenerate Life-like rules,
    while Bernoulli NML concentrates at low period.</li>
  </ul>
  <p class="tbl-meta">Source: <code>paper/alife2026_lba.tex</code> &mdash; US-letter,
  two pages excluding references, abstract under 250 words, built with the
  official <code>alifeconf</code> LaTeX style and matching the format of
  accepted ALIFE&nbsp;2025 submissions. Re-anonymize the author block if the
  late-breaking track is double-blind, and paste the body into the
  conference's 2026 template if one is released.</p>
</section>

<section id="claims">
  <h2>Claims &amp; theory — audit ledger</h2>
  <p>This is the project's own claim-by-claim audit (<code>docs/CLAIM_LEDGER.md</code>),
  rendered verbatim. It records, for every theorem and empirical claim, its current
  status, why it holds, what was weakened relative to earlier drafts, and what remains
  open. Lean 4 proof artifacts under <code>proofs/</code> provide supporting
  formal material at documented levels of completeness (see
  <code>proofs/README.md</code> for the per-file inventory). The math is
  supporting material for the tool; the paper's claims rest on the experiments
  and the reproducible pipeline.</p>
  {ledger_html}
</section>

<section id="figures">
  <h2>Figures</h2>
  <p>Every figure is generated from code in this repository; the generating script is
  noted under each caption. Click any figure to open it full size.</p>
  {''.join(figures_html)}
</section>

<section id="results">
  <h2>Results &amp; robustness</h2>
  <p>Each table below is loaded from the CSVs in <code>outputs/alife_2026/</code> —
  the same files the paper's tables are built from. Column names come straight from
  the code (<code>defect_*</code> columns are the paper's <em>residual</em> quantities).
  Click a column header to sort.</p>
  {stress_html}
  {''.join(tables_html)}
</section>

<section id="reproduce">
  <h2>Reproduce</h2>
  {demo_repro_note}
  <p>The full pipeline is deterministic: every experiment records its parameters in a
  <code>manifest.json</code>, and the suite runs from base seed <strong>{esc(seed)}</strong>.
  Experiments included: {esc(flags_note or 'see results_manifest.json')}.</p>
  {repro_rows}
  <p>See <code>REPRODUCING.md</code> for the complete step-by-step pipeline including
  TikZ figure compilation.</p>
</section>

<section id="repo">
  <h2>Repository map</h2>
  <div class="tbl-wrap"><table>
    <thead><tr><th>Path</th><th>What it is</th></tr></thead>
    <tbody>{repo_rows}</tbody>
  </table></div>
</section>

</main>
<footer><div class="wrap">
  Generated by <code>scripts/build_review_site.py</code> from the repository's
  committed outputs. Rebuild with <code>python scripts/build_review_site.py</code>.
</div></footer>
<script>
function show(id) {{
  document.querySelectorAll('section').forEach(s => s.classList.toggle('active', s.id === id));
  document.querySelectorAll('nav a').forEach(a =>
    a.classList.toggle('active', a.getAttribute('href') === '#' + id));
  window.scrollTo(0, 0);
  history.replaceState(null, '', '#' + id);
  return false;
}}
if (location.hash) {{
  const id = location.hash.slice(1);
  if (document.getElementById(id)) show(id);
}}
function filterTable(input, id) {{
  const q = input.value.toLowerCase();
  document.querySelectorAll('#' + id + ' tbody tr').forEach(tr => {{
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
function sortTable(id, col) {{
  const table = document.getElementById(id);
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);
  const asc = table.dataset.sortCol == col ? table.dataset.sortDir !== 'asc' : true;
  rows.sort((a, b) => {{
    const x = a.cells[col].textContent, y = b.cells[col].textContent;
    const nx = parseFloat(x), ny = parseFloat(y);
    const cmp = (!isNaN(nx) && !isNaN(ny)) ? nx - ny : x.localeCompare(y);
    return asc ? cmp : -cmp;
  }});
  rows.forEach(r => tbody.appendChild(r));
  table.dataset.sortCol = col;
  table.dataset.sortDir = asc ? 'asc' : 'desc';
}}
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--embed-images", action="store_true",
        help="Base64-embed figures for a portable single-file page "
             "(written to review_site/index_portable.html).",
    )
    parser.add_argument(
        "--pages", metavar="DIR",
        help="Build a standalone deployable site (e.g. for GitHub Pages) into "
             "DIR: index.html with embedded figures plus the paper PDF.",
    )
    args = parser.parse_args()

    if args.pages:
        site = Path(args.pages)
        if not site.is_absolute():
            site = ROOT / site
        site.mkdir(parents=True, exist_ok=True)
        pdf = ROOT / "paper" / "paper_alife2026.pdf"
        if pdf.exists():
            shutil.copy2(pdf, site / pdf.name)
        lba = ROOT / "paper" / "alife2026_lba.pdf"
        if lba.exists():
            shutil.copy2(lba, site / lba.name)
        write_demo_assets(site)
        out = site / "index.html"
        out.write_text(build(embed=True, pdf_href=pdf.name, lba_href=lba.name, live_demo=True))
    else:
        OUT_DIR.mkdir(exist_ok=True)
        out = OUT_DIR / ("index_portable.html" if args.embed_images else "index.html")
        out.write_text(build(embed=args.embed_images))
    size_kb = out.stat().st_size / 1024
    print(f"Wrote {out} ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
