from __future__ import annotations

from pathlib import Path

import typer

from .eca import random_initial_state, simulate_eca
from .plotting import plot_decomposition, plot_spacetime, plot_spectrum, save_figure
from .repair import extract_components, scan_relative_periodicity, summarise_components
from .selection import select_period, select_period_nd, selection_summary
from .experiment_suite import (
    run_all_suite,
    run_null_controls_suite,
    run_seed_stability_suite,
)

from .ca2d import LIFE_RULES, random_initial_grid, simulate_2d, rule_consistency_rate_2d
from .ca3d import RULES_3D, random_initial_volume, simulate_3d, rule_consistency_rate_3d
from .repair_nd import (
    extract_components_nd,
    scan_relative_periodicity_nd,
    summarise_components_nd,
)
from .plotting_nd import (
    plot_2d_decomposition,
    plot_2d_kymograph,
    plot_2d_slices,
    plot_3d_decomposition,
    plot_3d_slices,
    plot_spectrum_nd,
)

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def callback() -> None:
    """Relative symmetry-repair CLI."""
    return None


@app.command("analyze")
def analyze(
    rule: int = typer.Option(..., help="Elementary cellular automaton rule number."),
    width: int = typer.Option(192, help="Ring size."),
    steps: int = typer.Option(144, help="Number of time steps."),
    density: float = typer.Option(0.5, help="Initial Bernoulli density."),
    seed: int = typer.Option(11, help="Random seed."),
    shift_radius: int = typer.Option(6, help="Scan shifts from -shift_radius to +shift_radius."),
    max_period: int = typer.Option(10, help="Maximum period scanned."),
    output_dir: Path = typer.Option(Path("outputs"), help="Directory for CSV and PNG artifacts."),
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    initial = random_initial_state(width=width, density=density, seed=seed)
    spacetime = simulate_eca(rule=rule, initial=initial, steps=steps)

    # Stage A: period-first selection
    result = select_period(
        spacetime,
        shifts=range(-shift_radius, shift_radius + 1),
        periods=range(1, max_period + 1),
        rule=rule,
    )
    best_fit = result.best_fit
    summary = selection_summary(result)

    # Also produce the full scan frame for spectrum plots
    frame, fits = scan_relative_periodicity(
        spacetime,
        shifts=range(-shift_radius, shift_radius + 1),
        periods=range(1, max_period + 1),
        rule=rule,
    )

    labels, _ = extract_components(best_fit.defect_mask, min_size=6)
    components = summarise_components(labels)

    frame.to_csv(output_dir / f"rule_{rule}_spectrum.csv", index=False)
    components.to_csv(output_dir / f"rule_{rule}_components.csv", index=False)

    # Write structured selection summary
    import json
    import math
    safe_summary = {
        k: (str(v) if isinstance(v, float) and not math.isfinite(v) else v)
        for k, v in summary.items()
    }
    with open(output_dir / f"rule_{rule}_selection.json", "w") as f:
        json.dump(safe_summary, f, indent=2, default=str)

    fig, _ = plot_spacetime(spacetime, title=f"Rule {rule} spacetime")
    save_figure(fig, output_dir / f"rule_{rule}_spacetime.png")

    fig, _ = plot_spectrum(frame, value="defect_rate", title=f"Rule {rule} defect-rate spectrum")
    save_figure(fig, output_dir / f"rule_{rule}_defect_rate.png")

    fig, _ = plot_spectrum(frame, value="run_length_bits", title=f"Rule {rule} run-length repair spectrum")
    save_figure(fig, output_dir / f"rule_{rule}_run_length_bits.png")

    fig, _ = plot_decomposition(best_fit, source=spacetime, title_prefix=f"Rule {rule} ")
    save_figure(fig, output_dir / f"rule_{rule}_decomposition.png")

    typer.echo(f"Selected period: {result.selected.period} "
               f"(shift={result.selected.best_shift}, "
               f"status={result.status.value}, "
               f"margin={result.margin:.1f} bits)")
    if result.runner_up:
        typer.echo(f"Runner-up period: {result.runner_up.period} "
                   f"(+{result.margin:.1f} bits)")
    if result.residual is not None:
        typer.echo(f"Residual: {result.residual.n_components} components, "
                   f"RL={result.residual.run_length_bits} bits, "
                   f"defect_rate={result.residual.defect_rate:.4f}")
    typer.echo(f"Wrote outputs to {output_dir.resolve()}")


@app.command("analyze2d")
def analyze2d(
    rule: str = typer.Option("life", help=f"Named 2D rule: {list(LIFE_RULES)}."),
    width: int = typer.Option(64, help="Grid width."),
    height: int = typer.Option(64, help="Grid height."),
    steps: int = typer.Option(48, help="Number of time steps."),
    density: float = typer.Option(0.5, help="Initial Bernoulli density."),
    seed: int = typer.Option(11, help="Random seed."),
    shift_radius: int = typer.Option(3, help="Scan shifts from -r to +r in each spatial dim."),
    max_period: int = typer.Option(6, help="Maximum period scanned."),
    output_dir: Path = typer.Option(Path("outputs"), help="Directory for CSV and PNG artifacts."),
) -> None:
    """Analyze a 2D cellular automaton with relative-periodic repair."""
    output_dir = Path(output_dir) / f"rule2d_{rule}"
    output_dir.mkdir(parents=True, exist_ok=True)

    if rule not in LIFE_RULES:
        raise typer.BadParameter(
            f"Unknown rule {rule!r}. Choose from: {list(LIFE_RULES)}. "
            f"For non-contiguous rules like Diamoeba, use the Python API with simulate_2d_general.",
            param_hint="--rule",
        )

    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d(initial, steps=steps, rule=rule)

    s_lo, s_hi, b_lo, b_hi = LIFE_RULES[rule]
    survive, birth = (s_lo, s_hi), (b_lo, b_hi)

    def rule_error_fn(bg):
        return rule_consistency_rate_2d(bg, survive, birth)

    shift_range = range(-shift_radius, shift_radius + 1)

    # Stage A: period-first selection
    result = select_period_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )
    best_fit = result.best_fit
    summary = selection_summary(result)

    # Also produce full scan for spectrum plots
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    labels, _ = extract_components_nd(best_fit.defect_mask, min_size=4)
    components = summarise_components_nd(labels)

    frame.to_csv(output_dir / f"{rule}_spectrum.csv", index=False)
    components.to_csv(output_dir / f"{rule}_components.csv", index=False)

    import json
    import math
    safe_summary = {
        k: (str(v) if isinstance(v, float) and not math.isfinite(v) else v)
        for k, v in summary.items()
    }
    with open(output_dir / f"{rule}_selection.json", "w") as f:
        json.dump(safe_summary, f, indent=2, default=str)

    fig, _ = plot_2d_slices(spacetime, title=f"2D CA '{rule}' time slices")
    save_figure(fig, output_dir / f"{rule}_slices.png")

    fig, _ = plot_2d_kymograph(spacetime, axis=1, title=f"2D CA '{rule}' kymograph (avg over y)")
    save_figure(fig, output_dir / f"{rule}_kymograph.png")

    fig, _ = plot_spectrum_nd(frame, value="defect_rate", title=f"2D CA '{rule}' defect-rate spectrum")
    save_figure(fig, output_dir / f"{rule}_defect_rate.png")

    fig, _ = plot_spectrum_nd(frame, value="run_length_bits", title=f"2D CA '{rule}' run-length spectrum")
    save_figure(fig, output_dir / f"{rule}_run_length_bits.png")

    fig, _ = plot_2d_decomposition(best_fit, source=spacetime, title_prefix=f"'{rule}' ")
    save_figure(fig, output_dir / f"{rule}_decomposition.png")

    typer.echo(f"Selected period: {result.selected.period} "
               f"(shift={result.selected.best_shift}, "
               f"status={result.status.value}, "
               f"margin={result.margin:.1f} bits)")
    if result.runner_up:
        typer.echo(f"Runner-up period: {result.runner_up.period} "
                   f"(+{result.margin:.1f} bits)")
    typer.echo(f"Wrote outputs to {output_dir.resolve()}")


@app.command("analyze3d")
def analyze3d(
    rule: str = typer.Option("3d-life", help=f"Named 3D rule: {list(RULES_3D)}."),
    sx: int = typer.Option(16, help="Grid size x."),
    sy: int = typer.Option(16, help="Grid size y."),
    sz: int = typer.Option(16, help="Grid size z."),
    steps: int = typer.Option(20, help="Number of time steps."),
    density: float = typer.Option(0.3, help="Initial Bernoulli density."),
    seed: int = typer.Option(11, help="Random seed."),
    shift_radius: int = typer.Option(2, help="Scan shifts from -r to +r in each spatial dim."),
    max_period: int = typer.Option(4, help="Maximum period scanned."),
    output_dir: Path = typer.Option(Path("outputs"), help="Directory for CSV and PNG artifacts."),
) -> None:
    """Analyze a 3D cellular automaton with relative-periodic repair."""
    output_dir = Path(output_dir) / f"rule3d_{rule}"
    output_dir.mkdir(parents=True, exist_ok=True)

    initial = random_initial_volume(sx=sx, sy=sy, sz=sz, density=density, seed=seed)
    spacetime = simulate_3d(initial, steps=steps, rule=rule)

    s_lo, s_hi, b_lo, b_hi = RULES_3D[rule]
    survive, birth = (s_lo, s_hi), (b_lo, b_hi)

    def rule_error_fn(bg):
        return rule_consistency_rate_3d(bg, survive, birth)

    shift_range = range(-shift_radius, shift_radius + 1)

    # Stage A: period-first selection
    result = select_period_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )
    best_fit = result.best_fit
    summary = selection_summary(result)

    # Also produce full scan for spectrum plots
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    labels, _ = extract_components_nd(best_fit.defect_mask, min_size=4)
    components = summarise_components_nd(labels)

    frame.to_csv(output_dir / f"{rule}_spectrum.csv", index=False)
    components.to_csv(output_dir / f"{rule}_components.csv", index=False)

    import json
    import math
    safe_summary = {
        k: (str(v) if isinstance(v, float) and not math.isfinite(v) else v)
        for k, v in summary.items()
    }
    with open(output_dir / f"{rule}_selection.json", "w") as f:
        json.dump(safe_summary, f, indent=2, default=str)

    fig, _ = plot_3d_slices(spacetime, title=f"3D CA '{rule}' time slices (z-midplane)")
    save_figure(fig, output_dir / f"{rule}_slices.png")

    fig, _ = plot_spectrum_nd(frame, value="defect_rate", title=f"3D CA '{rule}' defect-rate spectrum")
    save_figure(fig, output_dir / f"{rule}_defect_rate.png")

    fig, _ = plot_spectrum_nd(frame, value="run_length_bits", title=f"3D CA '{rule}' run-length spectrum")
    save_figure(fig, output_dir / f"{rule}_run_length_bits.png")

    fig, _ = plot_3d_decomposition(best_fit, source=spacetime, title_prefix=f"'{rule}' ")
    save_figure(fig, output_dir / f"{rule}_decomposition.png")

    typer.echo(f"Selected period: {result.selected.period} "
               f"(shift={result.selected.best_shift}, "
               f"status={result.status.value}, "
               f"margin={result.margin:.1f} bits)")
    if result.runner_up:
        typer.echo(f"Runner-up period: {result.runner_up.period} "
                   f"(+{result.margin:.1f} bits)")
    typer.echo(f"Wrote outputs to {output_dir.resolve()}")


@app.command("alife-null-controls")
def alife_null_controls(
    output_root: Path = typer.Option(Path("outputs/alife_2026"), help="Root directory for ALIFE outputs."),
    base_seed: int = typer.Option(11, help="Base seed for deterministic seed iteration."),
    n_seeds: int = typer.Option(1, help="Number of original spacetimes per rule."),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reuse existing per-run CSV rows."),
    save_decompositions: bool = typer.Option(False, "--save-decompositions/--no-save-decompositions", help="Save a small decomposition subset."),
) -> None:
    manifest = run_null_controls_suite(
        output_root=output_root,
        base_seed=base_seed,
        n_seeds=n_seeds,
        resume=resume,
        save_decompositions=save_decompositions,
    )
    typer.echo(f"Wrote ALIFE null-controls outputs to {Path(manifest['output_dir']).resolve()}")


@app.command("alife-seed-stability")
def alife_seed_stability(
    output_root: Path = typer.Option(Path("outputs/alife_2026"), help="Root directory for ALIFE outputs."),
    base_seed: int = typer.Option(11, help="Base seed for deterministic seed iteration."),
    n_seeds: int = typer.Option(10, help="Number of seeds for the representative panel."),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reuse existing per-run CSV rows."),
) -> None:
    manifest = run_seed_stability_suite(
        output_root=output_root,
        base_seed=base_seed,
        n_seeds=n_seeds,
        resume=resume,
    )
    typer.echo(f"Wrote ALIFE seed-stability outputs to {Path(manifest['output_dir']).resolve()}")


@app.command("alife-run-all")
def alife_run_all(
    output_root: Path = typer.Option(Path("outputs/alife_2026"), help="Root directory for ALIFE outputs."),
    paper_dir: Path = typer.Option(Path("paper"), help="Directory for manuscript-facing markdown summaries."),
    base_seed: int = typer.Option(11, help="Base seed for deterministic seed iteration."),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Reuse existing per-run CSV rows."),
    null_controls: bool = typer.Option(True, "--null-controls/--no-null-controls", help="Enable the null-controls block."),
    seed_stability: bool = typer.Option(True, "--seed-stability/--no-seed-stability", help="Enable the seed-stability block."),
    candidate_range_robustness: bool = typer.Option(True, "--candidate-range-robustness/--no-candidate-range-robustness", help="Enable the search-range robustness block."),
    lifewiki_horizon_sweep: bool = typer.Option(True, "--lifewiki-horizon-sweep/--no-lifewiki-horizon-sweep", help="Enable the LifeWiki horizon sweep."),
    eca_atlas: bool = typer.Option(True, "--eca-atlas/--no-eca-atlas", help="Enable the ECA atlas block."),
    survey_3d: bool = typer.Option(True, "--survey-3d/--no-survey-3d", help="Enable the 3D survey block."),
    counterexample_stress: bool = typer.Option(True, "--counterexample-stress/--no-counterexample-stress", help="Enable the counterexample-stress block."),
    paper_reports: bool = typer.Option(True, "--paper-reports/--no-paper-reports", help="Write manuscript-facing markdown reports."),
    lifewiki_limit: int | None = typer.Option(None, help="Optional cap for the number of LifeWiki rules."),
    eca_limit: int | None = typer.Option(None, help="Optional cap for the number of ECA rules."),
) -> None:
    manifest = run_all_suite(
        output_root=output_root,
        paper_dir=paper_dir,
        base_seed=base_seed,
        resume=resume,
        run_null_controls=null_controls,
        run_seed_stability=seed_stability,
        run_candidate_range_robustness=candidate_range_robustness,
        run_lifewiki_horizon_sweep=lifewiki_horizon_sweep,
        run_eca_atlas=eca_atlas,
        run_3d_survey=survey_3d,
        run_counterexample_stress=counterexample_stress,
        generate_paper_markdown=paper_reports,
        lifewiki_limit=lifewiki_limit,
        eca_limit=eca_limit,
    )
    typer.echo(f"Wrote ALIFE suite outputs to {Path(manifest['output_root']).resolve()}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
