#!/usr/bin/env python3
"""Render true 3D voxel decomposition figures for the representative 3D rules.

The existing 3D figures (in ``rule_diagrams/representative_rules_3d.png``) only
show midplane z-slices, which loses volumetric structure.  This script uses
``plot_3d_volume_decomposition`` and ``plot_3d_volume_montage`` from
``plotting_nd`` to render proper 3D voxel views of:

  - the observed spacetime,
  - the selected relative-periodic background, and
  - the residual defect mask, overlaid on a faded background volume.

It also stitches the per-rule figures together into a manuscript-ready
composite ``alife_3d_voxel_diagrams.png``.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from relative_symmetry_repair.experiment_suite import (  # noqa: E402
    PLOT_RC,
    REPRESENTATIVE_CASES_3D,
    ALifeCase,
    ensure_output_dir,
    scan_case_spacetime,
    shift_to_string,
    simulate_case,
    write_json_manifest,
)
from relative_symmetry_repair.plotting import save_figure  # noqa: E402
from relative_symmetry_repair.plotting_nd import (  # noqa: E402
    plot_3d_volume_decomposition,
    plot_3d_volume_montage,
)

DEFAULT_HORIZON = 24
DEFAULT_SEED = 42

PAPER_FIGURE_NAME = "alife_3d_voxel_diagrams.png"


@dataclass(slots=True)
class VoxelPayload:
    case: ALifeCase
    horizon: int
    seed: int
    spacetime: np.ndarray
    fit: object  # RelativePeriodicFitND
    selected_period: int
    selected_shift: str
    margin_bits: float
    defect_rate: float


def _rule_label(case: ALifeCase) -> str:
    assert case.survive is not None and case.birth is not None
    s_lo, s_hi = case.survive
    b_lo, b_hi = case.birth
    return f"3D S{s_lo}-{s_hi} / B{b_lo}-{b_hi}"


def _build_payload(case: ALifeCase, *, horizon: int, seed: int) -> VoxelPayload:
    spacetime = simulate_case(case, steps=horizon, seed=seed)
    outcome = scan_case_spacetime(case, spacetime, search=case.search, nml_mode="hybrid")
    return VoxelPayload(
        case=case,
        horizon=horizon,
        seed=seed,
        spacetime=spacetime,
        fit=outcome.best_fit,
        selected_period=int(outcome.selection.selected_period),
        selected_shift=shift_to_string(outcome.selection.selected_shift),
        margin_bits=float(outcome.selection.margin_bits),
        defect_rate=float(outcome.selection.selected_defect_rate),
    )


def _render_per_rule_figures(payload: VoxelPayload, output_dir: Path) -> dict[str, Path]:
    rule_dir = ensure_output_dir(output_dir / payload.case.slug)
    decomp_path = rule_dir / f"{payload.case.slug}_voxel_decomposition.png"
    montage_path = rule_dir / f"{payload.case.slug}_voxel_montage.png"

    with plt.rc_context(PLOT_RC):
        fig_decomp, _ = plot_3d_volume_decomposition(
            payload.fit,
            source=payload.spacetime,
            time_index=payload.spacetime.shape[0] // 2,
            title_prefix=f"{payload.case.name} ",
        )
        save_figure(fig_decomp, decomp_path)
        plt.close(fig_decomp)

        fig_montage, _ = plot_3d_volume_montage(
            payload.fit,
            source=payload.spacetime,
            n_panels=4,
            title=f"{payload.case.name} — residual vs. background ({_rule_label(payload.case)})",
        )
        save_figure(fig_montage, montage_path)
        plt.close(fig_montage)

    return {"decomposition": decomp_path, "montage": montage_path}


def _compose_paper_figure(
    payloads: list[VoxelPayload],
    panel_paths: list[Path],
    path: Path,
) -> None:
    n = len(panel_paths)
    with plt.rc_context({**PLOT_RC, "axes.titlepad": 6}):
        fig, axes = plt.subplots(n, 1, figsize=(11.5, 3.6 * n))
        if n == 1:
            axes = np.asarray([axes])

        for ax, payload, panel_path in zip(axes, payloads, panel_paths):
            ax.imshow(plt.imread(panel_path))
            ax.axis("off")
            caption = (
                f"{payload.case.name}  ({_rule_label(payload.case)})    "
                f"selected (p, s) = ({payload.selected_period}, {payload.selected_shift})    "
                f"margin = {payload.margin_bits:.1f} bits    "
                f"defect rate = {payload.defect_rate:.3f}"
            )
            ax.set_title(caption, fontsize=10)

        fig.suptitle(
            "True 3D voxel decomposition for the representative 3D rules",
            fontsize=13,
        )
        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.97))
        save_figure(fig, path)
        plt.close(fig)


def build_voxel_diagrams(
    *,
    output_root: Path,
    paper_dir: Path,
    horizon: int,
    seed: int,
) -> dict[str, object]:
    output_dir = ensure_output_dir(output_root / "rule_diagrams_3d_voxel")
    paper_figure_dir = ensure_output_dir(paper_dir / "figures")

    payloads: list[VoxelPayload] = []
    decomp_paths: list[Path] = []
    montage_paths: list[Path] = []
    per_rule_files: dict[str, dict[str, str]] = {}

    for case in REPRESENTATIVE_CASES_3D:
        payload = _build_payload(case, horizon=horizon, seed=seed)
        files = _render_per_rule_figures(payload, output_dir)
        payloads.append(payload)
        decomp_paths.append(files["decomposition"])
        montage_paths.append(files["montage"])
        per_rule_files[case.slug] = {kind: str(p.resolve()) for kind, p in files.items()}

    paper_path = paper_figure_dir / PAPER_FIGURE_NAME
    _compose_paper_figure(payloads, decomp_paths, paper_path)

    manifest = {
        "horizon": int(horizon),
        "seed": int(seed),
        "output_dir": str(output_dir.resolve()),
        "paper_figure": str(paper_path.resolve()),
        "per_rule_files": per_rule_files,
        "rules": [
            {
                "name": payload.case.name,
                "rule_label": _rule_label(payload.case),
                "size": list(payload.case.size),
                "density": float(payload.case.density),
                "selected_period": payload.selected_period,
                "selected_shift": payload.selected_shift,
                "margin_bits": payload.margin_bits,
                "defect_rate": payload.defect_rate,
            }
            for payload in payloads
        ],
    }
    write_json_manifest(output_dir / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render proper 3D voxel decomposition figures for representative 3D rules.",
    )
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "alife_2026")
    parser.add_argument("--paper-dir", type=Path, default=ROOT / "paper")
    parser.add_argument("--horizon", type=int, default=DEFAULT_HORIZON,
                        help="Simulation horizon (smaller = faster voxel render).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    manifest = build_voxel_diagrams(
        output_root=args.output_root,
        paper_dir=args.paper_dir,
        horizon=args.horizon,
        seed=args.seed,
    )
    print(f"Wrote 3D voxel diagrams to {manifest['output_dir']}")
    print(f"Composite paper figure: {manifest['paper_figure']}")


if __name__ == "__main__":
    main()
