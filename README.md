<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sepam/planaco/v0.2.2/brand/planaco-lockup-dark.svg">
    <img src="https://raw.githubusercontent.com/sepam/planaco/v0.2.2/brand/planaco-lockup-light.svg" alt="planaco" width="320">
  </picture>

  **Probabilistic Project Planning with Monte Carlo Simulation**

  [![PyPI version](https://img.shields.io/pypi/v/planaco.svg?style=flat-square)](https://pypi.org/project/planaco/)
  [![Python versions](https://img.shields.io/pypi/pyversions/planaco.svg?style=flat-square)](https://pypi.org/project/planaco/)
  [![License](https://img.shields.io/github/license/sepam/planaco?style=flat-square)](LICENSE.md)
  ![Status](https://img.shields.io/badge/status-alpha-orange?style=flat-square)

  <p align="center">
    <a href="#why-planaco">Why Planaco?</a> •
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#monte-carlo-simulation">Monte Carlo</a> •
    <a href="#command-line-interface">CLI</a> •
    <a href="#probability-distributions">Distributions</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>

---

## Why Planaco?

Estimating the time it takes to complete a task or project is hard. Traditional approaches use fixed estimates, but this ignores any uncertainty and life often gets in the way.

**Planaco helps you make better estimates by modeling tasks as random processes**, accounting for uncertainty and task dependencies through Monte Carlo simulation.

> **Status:** Planaco is in **alpha** (v0.2.2). The public API may still change between releases.

## Features

- **Probabilistic Task Modeling** - Define tasks with min/max/mode duration ranges
- **6 Distribution Types** - Triangular, PERT, Uniform, Normal, LogNormal, and Beta distributions
- **Task Dependencies** - Support for parallel and sequential task execution
- **Monte Carlo Simulation** - Run thousands of simulations to estimate project completion
- **Statistical Analysis** - Get percentiles, confidence intervals, and key metrics
- **Visualization** - Generate histogram and cumulative distribution plots
- **Export Results** - Save results to JSON or CSV for further analysis

---

## Installation

```bash
pip install planaco
```

Or install from source:

```bash
git clone https://github.com/sepam/planaco.git
cd planaco
pip install .
```

---

## Quick Start

### Define Tasks with Uncertainty

Instead of saying "this task takes 5 days", Planaco lets you model uncertainty:

```python
from planaco import Task

task = Task(
    name='Develop Feature',
    min_duration=3,
    mode_duration=5,  # most likely estimate
    max_duration=9,
    estimator='triangular'
)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/sepam/planaco/v0.2.2/example/task_definition.png" alt="Task Definition" width="600"/>
</div>

### Build Projects with Dependencies

Create complex project workflows with parallel and sequential task execution:

```python
from planaco import Task, Project

# Create a project
project = Project(name='Web App Development', unit='days')

# Define tasks
design_ui = Task(name='Design UI', min_duration=2, mode_duration=3, max_duration=5, estimator='triangular')
develop_frontend = Task(name='Develop Frontend', min_duration=5, mode_duration=7, max_duration=10, estimator='triangular')
develop_backend = Task(name='Develop Backend', min_duration=4, mode_duration=6, max_duration=9, estimator='triangular')
testing = Task(name='Testing', min_duration=2, mode_duration=3, max_duration=5, estimator='triangular')
deploy = Task(name='Deploy', min_duration=1, max_duration=2, estimator='uniform')

# Add tasks with dependencies
project.add_task(design_ui)
project.add_task(develop_frontend, depends_on=[design_ui])           # Sequential: frontend needs UI design
project.add_task(develop_backend)                                    # Parallel: backend runs independently
project.add_task(testing, depends_on=[develop_frontend, develop_backend])  # Waits for both tracks
project.add_task(deploy, depends_on=[testing])
```

<div align="center">
  <img src="https://raw.githubusercontent.com/sepam/planaco/v0.2.2/example/project_estimation.png" alt="Project Estimation" width="700"/>
</div>

---

## Monte Carlo Simulation

Planaco uses [Monte Carlo simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method) to estimate project completion time. By running thousands of simulations, it leverages the [Central Limit Theorem](https://en.wikipedia.org/wiki/Central_limit_theorem) to provide probabilistic estimates for the completion of tasks and projects.

### Run Simulation & Get Statistics

```python
# Get comprehensive statistics of the simulation
stats = project.statistics(n=10000)

print(f"Median completion time: {stats['median']:.1f} days")
print(f"90% confidence: {stats['percentiles']['p90']:.1f} days")
print(f"95% confidence: {stats['percentiles']['p95']:.1f} days")
```

`statistics()` returns a dictionary with the full distribution summary:

```python
{
    'n_simulations': 10000,
    'unit': 'days',
    'mean': 18.4,
    'median': 18.1,
    'std_dev': 2.7,
    'min': 11.2,
    'max': 29.8,
    'percentiles': {'p50': 18.1, 'p75': 20.1, 'p85': 21.3, 'p90': 22.1, 'p95': 23.4, 'p99': 25.6},
    'confidence_intervals': {'95%': (13.5, 24.2)},
}
```

### Visualize Results

```python
# Generate histogram
project.plot(n=10000, hist=True)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/sepam/planaco/v0.2.2/example/monte_carlo_estimation.png" alt="Monte Carlo Histogram" width="550"/>
</div>

### Cumulative Distribution

Read the likelihood of completing your project by a given date:

```python
# Generate cumulative distribution
project.plot(n=10000, hist=False)
```

<div align="center">
  <img src="https://raw.githubusercontent.com/sepam/planaco/v0.2.2/example/monte_carlo_cumulative.png" alt="Cumulative Distribution" width="550"/>
</div>

The cumulative distribution shows the probability of completing the project within a given timeframe, accounting for both parallel and sequential task execution.

---

## Advanced Features

### Export Results

```python
# Export to JSON
project.export_results(n=10000, format='json', filename='results.json')

# Export to CSV
project.export_results(n=10000, format='csv', filename='results.csv')
```

### Probability Distributions

Planaco supports six probability distributions, each suited for different estimation scenarios:

#### Triangular Distribution (Default)
Best for **three-point estimates** where you can identify optimistic, most likely, and pessimistic values.

```python
task = Task(
    name="Development",
    min_duration=5,      # Best case
    mode_duration=8,     # Most likely
    max_duration=15,     # Worst case
    estimator="triangular"
)
```

**When to use:** Most common choice. Use when you have a clear "most likely" estimate and can define reasonable bounds.

#### PERT Distribution
A smoother alternative to triangular that **weights the mode more heavily** (by default, 4x). Widely used in project management.

```python
task = Task(
    name="Testing",
    min_duration=2,
    mode_duration=4,
    max_duration=10,
    estimator="pert"
)
```

**When to use:** Industry standard for project estimation. Produces more realistic results than triangular by reducing the influence of extreme values.

#### Uniform Distribution
All values between min and max are **equally likely**. No mode required.

```python
task = Task(
    name="Deployment",
    min_duration=1,
    max_duration=3,
    estimator="uniform"
)
```

**When to use:** When you genuinely don't know the most likely duration, only the range. Good for tasks with high uncertainty.

#### Normal (Gaussian) Distribution
Classic **bell curve** centered on the mean. Best for well-understood, repeatable tasks.

```python
from planaco import Task, NormalDistribution

task = Task(
    name="Code Review",
    distribution=NormalDistribution(
        mean=2.0,
        std_dev=0.5,
        min_value=0.5,  # Optional lower bound
        max_value=4.0   # Optional upper bound
    )
)
```

**When to use:** Tasks you've done many times before with predictable variability. The optional bounds prevent unrealistic negative or extreme values.

#### LogNormal Distribution
**Right-skewed** distribution where delays are more likely than early completion. Realistic for many real-world tasks.

```python
from planaco import Task, LogNormalDistribution

task = Task(
    name="Integration",
    distribution=LogNormalDistribution(
        mean=5.0,
        std_dev=2.0
    )
)
```

**When to use:** Tasks with potential for unexpected delays (debugging, third-party dependencies, approvals). Models the common pattern where things take longer than expected more often than they finish early.

#### Beta Distribution
**Most flexible** distribution with customizable shape via alpha and beta parameters.

```python
from planaco import Task, BetaDistribution

task = Task(
    name="Research",
    distribution=BetaDistribution(
        alpha=2.0,
        beta=5.0,
        min_value=1.0,
        max_value=10.0
    )
)
```

**When to use:** When you need fine-grained control over the distribution shape:
- `alpha < beta`: Right-skewed (more likely to finish early)
- `alpha > beta`: Left-skewed (more likely to finish late)
- `alpha = beta`: Symmetric

---

### Choosing the Right Distribution

| Scenario | Recommended Distribution |
|----------|-------------------------|
| Standard 3-point estimate | PERT or Triangular |
| Well-understood, repeatable task | Normal |
| High uncertainty, unknown mode | Uniform |
| Risk of delays/blockers | LogNormal |
| Custom uncertainty profile | Beta |

**New to Monte Carlo?** Start with **PERT** - it's the industry standard and works well for most project estimation tasks.

---

## Command Line Interface

Planaco also ships with a `planaco` CLI that runs simulations from a YAML project file — useful for CI pipelines, shared team configs, and version-controlled estimates.

```bash
planaco init project.yaml                 # Create a template config
planaco stats project.yaml -n 10000       # Print formatted statistics
planaco run project.yaml -o results.json  # Export results (json or csv)
planaco plot project.yaml -o chart.png    # Histogram or cumulative plot
planaco graph project.yaml                # Visualize the task dependency graph
```

Example YAML config:

```yaml
project:
  name: Website Redesign
  unit: days
  seed: 42  # optional, for reproducible runs

tasks:
  - name: Design
    distribution:
      type: pert
      minimum: 5
      mode: 7
      maximum: 14

  - name: Development
    depends_on: [Design]
    distribution:
      type: triangular
      minimum: 10
      mode: 15
      maximum: 25
```

Run `planaco --help` or `planaco <command> --help` to see all available options, including `--seed` for reproducible results and `-p/--percentile` markers for plots.

---

## Example

A complete, runnable example lives in [`example/example_project.py`](example/example_project.py), with an annotated walkthrough in [`example/example.ipynb`](example/example.ipynb).

```bash
python example/example_project.py
```

---

## Contributing

Contributions are welcome! To set up a development environment:

```bash
git clone https://github.com/sepam/planaco.git
cd planaco
pip install -e ".[dev]"
```

Run the checks before submitting a PR:

```bash
pytest             # run the test suite
ruff check .       # lint
black .            # format
mypy src           # type-check
```

Please open an issue to discuss larger changes before starting work.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with Monte Carlo simulation for better project planning</sub>
</div>
