from __future__ import annotations

from pathlib import Path

import typer

from .eca import random_initial_state, simulate_eca
from .plotting import plot_decomposition, plot_spacetime, plot_spectrum, save_figure
from .repair import extract_components, scan_relative_periodicity, summarise_components

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
    best = frame.sort_values(["defect_rate", "rule_error", "run_length_bits"]).iloc[0]
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
