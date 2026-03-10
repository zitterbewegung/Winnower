from __future__ import annotations

from pathlib import Path

import typer

from .eca import random_initial_state, simulate_eca
from .plotting import plot_decomposition, plot_spacetime, plot_spectrum, save_figure
from .repair import extract_components, scan_relative_periodicity, summarise_components

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

    frame, fits = scan_relative_periodicity(
        spacetime,
        shifts=range(-shift_radius, shift_radius + 1),
        periods=range(1, max_period + 1),
        rule=rule,
    )
    best = frame.sort_values(["nml_bits", "defect_rate"]).iloc[0]
    best_key = (int(best["shift"]), int(best["period"]))
    best_fit = fits[best_key]

    labels, _ = extract_components(best_fit.defect_mask, min_size=6)
    components = summarise_components(labels)

    frame.to_csv(output_dir / f"rule_{rule}_spectrum.csv", index=False)
    components.to_csv(output_dir / f"rule_{rule}_components.csv", index=False)

    fig, _ = plot_spacetime(spacetime, title=f"Rule {rule} spacetime")
    save_figure(fig, output_dir / f"rule_{rule}_spacetime.png")

    fig, _ = plot_spectrum(frame, value="defect_rate", title=f"Rule {rule} defect-rate spectrum")
    save_figure(fig, output_dir / f"rule_{rule}_defect_rate.png")

    fig, _ = plot_spectrum(frame, value="run_length_bits", title=f"Rule {rule} run-length repair spectrum")
    save_figure(fig, output_dir / f"rule_{rule}_run_length_bits.png")

    fig, _ = plot_decomposition(best_fit, source=spacetime, title_prefix=f"Rule {rule} ")
    save_figure(fig, output_dir / f"rule_{rule}_decomposition.png")

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

    initial = random_initial_grid(width=width, height=height, density=density, seed=seed)
    spacetime = simulate_2d(initial, steps=steps, rule=rule)

    s_lo, s_hi, b_lo, b_hi = LIFE_RULES[rule]
    survive, birth = (s_lo, s_hi), (b_lo, b_hi)

    def rule_error_fn(bg):
        return rule_consistency_rate_2d(bg, survive, birth)

    shift_range = range(-shift_radius, shift_radius + 1)
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    best = frame.sort_values(["nml_bits", "defect_rate"]).iloc[0]
    best_shift = (int(best["shift_0"]), int(best["shift_1"]))
    best_period = int(best["period"])
    best_fit = fits[(best_shift, best_period)]

    labels, _ = extract_components_nd(best_fit.defect_mask, min_size=4)
    components = summarise_components_nd(labels)

    frame.to_csv(output_dir / f"{rule}_spectrum.csv", index=False)
    components.to_csv(output_dir / f"{rule}_components.csv", index=False)

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

    typer.echo(f"Best fit: shift=({best_shift[0]},{best_shift[1]}), period={best_period}, "
               f"defect_rate={best_fit.defect_rate:.4f}")
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
    frame, fits = scan_relative_periodicity_nd(
        spacetime,
        shift_ranges=[shift_range, shift_range, shift_range],
        periods=range(1, max_period + 1),
        rule_error_fn=rule_error_fn,
    )

    best = frame.sort_values(["nml_bits", "defect_rate"]).iloc[0]
    best_shift = (int(best["shift_0"]), int(best["shift_1"]), int(best["shift_2"]))
    best_period = int(best["period"])
    best_fit = fits[(best_shift, best_period)]

    labels, _ = extract_components_nd(best_fit.defect_mask, min_size=4)
    components = summarise_components_nd(labels)

    frame.to_csv(output_dir / f"{rule}_spectrum.csv", index=False)
    components.to_csv(output_dir / f"{rule}_components.csv", index=False)

    fig, _ = plot_3d_slices(spacetime, title=f"3D CA '{rule}' time slices (z-midplane)")
    save_figure(fig, output_dir / f"{rule}_slices.png")

    fig, _ = plot_spectrum_nd(frame, value="defect_rate", title=f"3D CA '{rule}' defect-rate spectrum")
    save_figure(fig, output_dir / f"{rule}_defect_rate.png")

    fig, _ = plot_spectrum_nd(frame, value="run_length_bits", title=f"3D CA '{rule}' run-length spectrum")
    save_figure(fig, output_dir / f"{rule}_run_length_bits.png")

    fig, _ = plot_3d_decomposition(best_fit, source=spacetime, title_prefix=f"'{rule}' ")
    save_figure(fig, output_dir / f"{rule}_decomposition.png")

    typer.echo(f"Best fit: shift=({best_shift[0]},{best_shift[1]},{best_shift[2]}), period={best_period}, "
               f"defect_rate={best_fit.defect_rate:.4f}")
    typer.echo(f"Wrote outputs to {output_dir.resolve()}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
