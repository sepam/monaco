"""Monaco CLI - Monte Carlo simulation for project estimation."""

import json
import sys
from pathlib import Path
from typing import Optional, Tuple

import click

from monaco import __version__
from monaco.config import (
    ConfigError,
    build_project_from_config,
    get_seed_from_config,
    get_template_config,
    load_config,
)


def _setup_seed(config: dict, cli_seed: Optional[int]) -> None:
    """Set up random seed from config or CLI, with warning if none specified.

    Priority: CLI --seed > YAML config seed > random (no seed)

    Parameters
    ----------
    config : dict
        Parsed configuration dictionary
    cli_seed : Optional[int]
        Seed from CLI --seed option (takes priority)
    """
    import random

    # CLI seed takes priority over config seed
    if cli_seed is not None:
        random.seed(cli_seed)
        return

    # Try config seed
    config_seed = get_seed_from_config(config)
    if config_seed is not None:
        random.seed(config_seed)
        return

    # No seed specified - show warning
    click.secho(
        "Note: No seed specified. Results will vary between runs.",
        fg="yellow",
        err=True,
    )
    click.secho(
        "      Add 'seed: <number>' to your project config for reproducible results.",
        fg="yellow",
        err=True,
    )


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Monaco - Monte Carlo simulation for project estimation.

    Define projects and tasks in YAML, run simulations, and get
    probabilistic completion time estimates.

    Examples:

        monaco init my_project.yaml

        monaco stats my_project.yaml

        monaco plot my_project.yaml -o chart.png
    """
    pass


@main.command()
@click.argument("output", default="monaco_project.yaml")
@click.option(
    "--name", "-n", default="My Project", help="Project name for the template"
)
def init(output: str, name: str) -> None:
    """Create a template YAML project file.

    OUTPUT: Path for the new YAML file (default: monaco_project.yaml)

    Example:
        monaco init my_project.yaml --name "Web App Development"
    """
    output_path = Path(output)

    if output_path.exists():
        click.secho(f"Error: File '{output}' already exists", fg="red", err=True)
        sys.exit(1)

    template = get_template_config(name)

    with open(output_path, "w") as f:
        f.write(template)

    click.secho(f"Created template project file: {output}", fg="green")
    click.echo("\nEdit the file to define your tasks, then run:")
    click.echo(f"  monaco stats {output}")


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("-n", "--simulations", default=10000, help="Number of simulations to run")
@click.option(
    "-o", "--output", default=None, help="Output file for results (default: stdout)"
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Output format",
)
@click.option("--seed", default=None, type=int, help="Random seed for reproducibility")
def run(
    config_file: str,
    simulations: int,
    output: Optional[str],
    output_format: str,
    seed: Optional[int],
) -> None:
    """Run Monte Carlo simulation and export results.

    CONFIG_FILE: Path to the YAML project configuration file.

    Example:
        monaco run project.yaml -n 10000 -o results.json
    """
    try:
        config = load_config(config_file)
        _setup_seed(config, seed)
        project = build_project_from_config(config)

        if output:
            project.export_results(n=simulations, format=output_format, output=output)
            click.secho(f"Results exported to {output}", fg="green")
        else:
            stats = project.statistics(n=simulations)
            _print_stats(project.name, stats)

    except (ConfigError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("-n", "--simulations", default=10000, help="Number of simulations to run")
@click.option(
    "--json", "as_json", is_flag=True, help="Output as JSON instead of formatted text"
)
@click.option(
    "--seed",
    default=None,
    type=int,
    help="Random seed for reproducibility (overrides config)",
)
def stats(
    config_file: str, simulations: int, as_json: bool, seed: Optional[int]
) -> None:
    """Calculate and display project statistics.

    CONFIG_FILE: Path to the YAML project configuration file.

    Example:
        monaco stats project.yaml -n 10000
    """
    try:
        config = load_config(config_file)
        _setup_seed(config, seed)
        project = build_project_from_config(config)

        stats_result = project.statistics(n=simulations)

        if as_json:
            click.echo(json.dumps(stats_result, indent=2))
        else:
            _print_stats(project.name, stats_result)

    except (ConfigError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("-n", "--simulations", default=1000, help="Number of simulations to run")
@click.option(
    "-o", "--output", default=None, help="Save plot to file instead of displaying"
)
@click.option(
    "--cumulative",
    is_flag=True,
    help="Show cumulative distribution instead of histogram",
)
@click.option("--kde", is_flag=True, help="Show kernel density estimate on histogram")
@click.option(
    "-p",
    "--percentile",
    "percentiles",
    multiple=True,
    type=int,
    help="Percentile markers to show (e.g., -p 50 -p 85 -p 95)",
)
@click.option(
    "--seed",
    default=None,
    type=int,
    help="Random seed for reproducibility (overrides config)",
)
def plot(
    config_file: str,
    simulations: int,
    output: Optional[str],
    cumulative: bool,
    kde: bool,
    percentiles: Tuple[int, ...],
    seed: Optional[int],
) -> None:
    """Generate visualization of simulation results.

    CONFIG_FILE: Path to the YAML project configuration file.

    Examples:
        monaco plot project.yaml -o chart.png

        monaco plot project.yaml --cumulative

        monaco plot project.yaml -p 50 -p 85 -p 95
    """
    try:
        config = load_config(config_file)
        _setup_seed(config, seed)
        project = build_project_from_config(config)

        percentiles_list = list(percentiles) if percentiles else None
        show_percentiles = bool(percentiles_list)

        project.plot(
            n=simulations,
            hist=not cumulative,
            kde=kde,
            save_path=output,
            show_percentiles=show_percentiles,
            percentiles=percentiles_list,
        )

        if output:
            click.secho(f"Plot saved to {output}", fg="green")

    except (ConfigError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "-o", "--output", default=None, help="Save graph to file instead of displaying"
)
@click.option("--no-durations", is_flag=True, help="Hide duration information on nodes")
def graph(config_file: str, output: Optional[str], no_durations: bool) -> None:
    """Visualize the task dependency graph.

    CONFIG_FILE: Path to the YAML project configuration file.

    Examples:
        monaco graph project.yaml

        monaco graph project.yaml -o dependencies.png
    """
    try:
        config = load_config(config_file)
        project = build_project_from_config(config)

        project.plot_dependency_graph(save_path=output, show_durations=not no_durations)

        if output:
            click.secho(f"Dependency graph saved to {output}", fg="green")

    except (ConfigError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


def _print_stats(project_name: Optional[str], stats: dict) -> None:
    """Print formatted statistics to stdout."""
    click.echo()
    click.secho(f"Project: {project_name or 'Unnamed'}", fg="cyan", bold=True)
    click.secho("=" * 50, fg="cyan")
    click.echo()

    click.echo(f"Simulations: {stats['n_simulations']:,}")
    click.echo(f"Time Unit: {stats['unit']}")
    click.echo()

    click.secho("Duration Estimates:", bold=True)
    click.echo(f"  Mean:              {stats['mean']:.1f} {stats['unit']}")
    click.echo(f"  Median (P50):      {stats['median']:.1f} {stats['unit']}")
    click.echo(f"  Std Deviation:     {stats['std_dev']:.1f} {stats['unit']}")
    click.echo(f"  Min:               {stats['min']:.1f} {stats['unit']}")
    click.echo(f"  Max:               {stats['max']:.1f} {stats['unit']}")
    click.echo()

    click.secho("Percentiles:", bold=True)
    for key, value in stats["percentiles"].items():
        label = key.upper()
        click.echo(f"  {label}:              {value:.1f} {stats['unit']}")
    click.echo()

    ci = stats["confidence_intervals"]["95%"]
    click.secho("Confidence Interval:", bold=True)
    click.echo(f"  95% CI:            [{ci[0]:.1f}, {ci[1]:.1f}] {stats['unit']}")
    click.echo()


if __name__ == "__main__":
    main()
