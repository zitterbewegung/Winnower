#!/usr/bin/env python3
"""Build reusable Aristotle submission bundles for the theorem package."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from zipfile import ZIP_DEFLATED, ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
PROMPT_DIR = PAPER_DIR / "aristotle_prompts_v15"
DEFAULT_OUTPUT_DIR = PAPER_DIR / "aristotle_submissions_v15"


@dataclass(frozen=True)
class ClaimSpec:
    name: str
    title: str
    prompt_file: str
    tex_label: str | None
    env_name: str
    priority: int
    recommended_mode: str
    dependencies: tuple[str, ...] = ()
    notes: str = ""


CLAIMS: tuple[ClaimSpec, ...] = (
    ClaimSpec(
        name="theorem_1",
        title="Theorem 1: Optimal Hamming Projection",
        prompt_file="theorem_1.md",
        tex_label="thm:projection",
        env_name="theorem",
        priority=3,
        recommended_mode="Direct Aristotle in English",
        notes="Clean finite combinatorics. Good sanity-check target.",
    ),
    ClaimSpec(
        name="theorem_2",
        title="Theorem 2: Six-Way Equivalence / Monotonicity",
        prompt_file="theorem_2.md",
        tex_label="thm:monotonicity",
        env_name="theorem",
        priority=1,
        recommended_mode="Direct Aristotle in English",
        notes="Highest-priority theorem-level novelty claim. Check the necessity directions carefully.",
    ),
    ClaimSpec(
        name="theorem_3",
        title="Theorem 3: Stabilization",
        prompt_file="theorem_3.md",
        tex_label="thm:stabilization",
        env_name="theorem",
        priority=4,
        recommended_mode="Direct Aristotle in English",
        notes="Hardest claim. It is acceptable to formalize only the algebraic core or pairwise-comparison layer.",
    ),
    ClaimSpec(
        name="theorem_4",
        title="Theorem 4: Nonidentifiability",
        prompt_file="theorem_4.md",
        tex_label="thm:nonident",
        env_name="theorem",
        priority=5,
        recommended_mode="Direct Aristotle in English",
        dependencies=("theorem_3",),
        notes="Best submitted after a trustworthy pairwise-comparison result from Theorem 3 exists.",
    ),
    ClaimSpec(
        name="theorem_5",
        title="Theorem 5: Identifiability for Eventually Exact Backgrounds",
        prompt_file="theorem_5.md",
        tex_label="thm:ident",
        env_name="theorem",
        priority=2,
        recommended_mode="Direct Aristotle in English",
        notes="Strong finite-transient target. Usually cleaner than Theorem 3 or 4.",
    ),
    ClaimSpec(
        name="corollary_d3",
        title="Corollary D.3: Unconditional NML Convergence",
        prompt_file="corollary_d3.md",
        tex_label=None,
        env_name="corollary",
        priority=6,
        recommended_mode="Direct Aristotle in English",
        notes="Appendix-level follow-up. Do this only after the main theorem block is stable.",
    ),
)

CLAIM_BY_NAME = {claim.name: claim for claim in CLAIMS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare Aristotle submission bundles for the theorem package."
    )
    parser.add_argument(
        "--claim",
        action="append",
        choices=sorted(CLAIM_BY_NAME),
        help="Claim(s) to package. Defaults to the full theorem set.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where the submission bundles will be written.",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create zip archives for each claim bundle and the full packet.",
    )
    return parser.parse_args()


def selected_claims(names: list[str] | None) -> list[ClaimSpec]:
    if not names:
        return list(CLAIMS)
    return [CLAIM_BY_NAME[name] for name in names]


def safe_rmtree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def extract_latex_block(tex_source: str, env_name: str, label: str) -> str:
    pattern = re.compile(
        rf"\\begin\{{{env_name}\}}(?:\[(?P<title>[^\]]+)\])?\\label\{{{re.escape(label)}\}}(?P<body>.*?)\\end\{{{env_name}\}}",
        re.DOTALL,
    )
    match = pattern.search(tex_source)
    if not match:
        raise ValueError(f"Could not find {env_name} with label {label!r} in paper_alife2026.tex")
    title = match.group("title")
    body = match.group("body").strip()
    heading = f"{env_name.title()}"
    if title:
        heading += f" [{title}]"
    return f"\\begin{{{env_name}}}[{title}]\\label{{{label}}}\n{body}\n\\end{{{env_name}}}\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_claim_readme(claim: ClaimSpec, excerpt_filename: str) -> str:
    dependencies = ", ".join(claim.dependencies) if claim.dependencies else "none"
    return dedent(
        f"""\
        # {claim.title}

        Use `paper_v15.md` as the source of truth for this prompt.
        Use `{excerpt_filename}` only to compare the ALIFE submission wording.

        ## What to do

        1. Paste `prompt.md` into Aristotle using `{claim.recommended_mode}` mode.
        2. Attach `../shared_context/paper_v15.md`.
        3. Submit.
        4. Save the returned Lean file.
        5. Run `lake build` or compile the file directly.
        6. Record the exact theorem statement and any weakening in `../shared_context/CLAIM_LEDGER.md`.

        ## Files in this bundle

        - `prompt.md`
        - `{excerpt_filename}`
        - `notes.md`

        ## Claim metadata

        - Priority: {claim.priority}
        - Dependencies: {dependencies}
        - Notes: {claim.notes}
        """
    )


def build_claim_notes(claim: ClaimSpec) -> str:
    dependencies = ", ".join(claim.dependencies) if claim.dependencies else "none"
    return dedent(
        f"""\
        title: {claim.title}
        name: {claim.name}
        priority: {claim.priority}
        recommended_mode: {claim.recommended_mode}
        dependencies: {dependencies}
        prompt_file: {claim.prompt_file}
        notes: {claim.notes}
        """
    )


def build_top_level_readme(claims: list[ClaimSpec]) -> str:
    lines = [
        "# Aristotle submission packet",
        "",
        "This directory was generated automatically from `paper/aristotle_prompts_v15`.",
        "",
        "Use `shared_context/paper_v15.md` as the source of truth for Aristotle.",
        "Use `paper_alife2026.tex` and the per-claim `manuscript_excerpt.tex` files only to compare the current ALIFE submission wording.",
        "",
        "## Shared context",
        "",
        "- `shared_context/paper_v15.md`",
        "- `shared_context/paper_alife2026.tex`",
        "- `shared_context/README.md`",
        "- `shared_context/INSTRUCTIONS.md`",
        "- `shared_context/SUBMISSION_CHECKLIST.md`",
        "- `shared_context/CLAIM_LEDGER.md`",
        "",
        "## Claim bundles",
        "",
    ]
    for claim in sorted(claims, key=lambda item: item.priority):
        lines.append(f"- `{claim.name}/`: {claim.title} (priority {claim.priority})")
    lines.extend(
        [
        "",
        "## Suggested workflow",
        "",
        "1. Start with `theorem_2/`.",
        "2. Paste that bundle's `prompt.md` into Aristotle in `Direct Aristotle in English` mode.",
        "3. Attach `shared_context/paper_v15.md`.",
        "4. Record every result in `shared_context/CLAIM_LEDGER.md`.",
        "5. Regenerate this packet whenever the manuscript or prompt files change.",
        ]
    )
    return "\n".join(lines) + "\n"


def zip_path(source_dir: Path, archive_path: Path) -> None:
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source_dir))


def build_bundles(output_dir: Path, claims: list[ClaimSpec], make_zip: bool) -> dict[str, object]:
    tex_path = PAPER_DIR / "paper_alife2026.tex"
    markdown_path = PAPER_DIR / "paper_v15.md"
    tex_source = tex_path.read_text(encoding="utf-8")

    safe_rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    shared_context = output_dir / "shared_context"
    shared_context.mkdir(parents=True, exist_ok=True)
    for filename in (
        "paper_v15.md",
        "paper_alife2026.tex",
        "README.md",
        "INSTRUCTIONS.md",
        "SUBMISSION_CHECKLIST.md",
        "CLAIM_LEDGER.md",
    ):
        copy_file(PROMPT_DIR / filename if filename != "paper_v15.md" and filename != "paper_alife2026.tex" else PAPER_DIR / filename, shared_context / filename)

    bundles: list[dict[str, object]] = []
    for claim in claims:
        claim_dir = output_dir / claim.name
        claim_dir.mkdir(parents=True, exist_ok=True)

        prompt_src = PROMPT_DIR / claim.prompt_file
        prompt_dst = claim_dir / "prompt.md"
        copy_file(prompt_src, prompt_dst)

        excerpt_name = "manuscript_excerpt.tex"
        if claim.tex_label:
            excerpt_content = extract_latex_block(tex_source, claim.env_name, claim.tex_label)
        else:
            excerpt_content = (
                "% Corollary D.3 is present in paper_v15.md and the prompt set, but not in paper_alife2026.tex.\n"
                f"% Attach {markdown_path.name} for the appendix-level context.\n"
            )
        write_text(claim_dir / excerpt_name, excerpt_content)
        write_text(claim_dir / "README.md", build_claim_readme(claim, excerpt_name))
        write_text(claim_dir / "notes.md", build_claim_notes(claim))

        if make_zip:
            zip_path(claim_dir, output_dir / f"{claim.name}.zip")

        bundles.append(
            {
                "name": claim.name,
                "title": claim.title,
                "priority": claim.priority,
                "directory": str(claim_dir.relative_to(REPO_ROOT)),
                "prompt": str(prompt_dst.relative_to(REPO_ROOT)),
                "excerpt": str((claim_dir / excerpt_name).relative_to(REPO_ROOT)),
                "dependencies": list(claim.dependencies),
            }
        )

    write_text(output_dir / "README.md", build_top_level_readme(claims))

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_prompt_dir": str(PROMPT_DIR.relative_to(REPO_ROOT)),
        "source_files": {
            "paper_v15_md": str(markdown_path.relative_to(REPO_ROOT)),
            "paper_alife2026_tex": str(tex_path.relative_to(REPO_ROOT)),
        },
        "claims": bundles,
    }
    write_text(output_dir / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    if make_zip:
        zip_path(output_dir, output_dir.with_suffix(".zip"))

    return manifest


def main() -> None:
    args = parse_args()
    claims = selected_claims(args.claim)
    build_bundles(args.output_dir, claims, args.zip)


if __name__ == "__main__":
    main()
