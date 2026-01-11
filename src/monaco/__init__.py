"""
Monaco: Probabilistic Project Planning with Monte Carlo Simulation.

Monaco is a Python library for estimating project completion times using
Monte Carlo simulation. It models task durations as probability distributions
and calculates project timelines while accounting for uncertainty and
task dependencies.

Key Features
------------
- **Multiple distribution types**: Choose from 6 probability distributions
  to model task duration uncertainty.
- **Task dependencies**: Define complex workflows with parallel and
  sequential task execution.
- **Critical path analysis**: Identify which tasks drive your timeline.
- **Monte Carlo simulation**: Run thousands of simulations to understand
  probability distributions.
- **Statistical analysis**: Get mean, median, percentiles, and confidence
  intervals.
- **Visualization**: Generate histograms, cumulative plots, and dependency
  graphs.
- **Configuration files**: Define projects in YAML for easy sharing.
- **CLI tool**: Run simulations from the command line.

Main Components
---------------
Distribution classes (from ``monaco.distributions``):
    - ``TriangularDistribution``: Three-point estimate (min, mode, max).
      Best for tasks where you can estimate optimistic, likely, and
      pessimistic durations.
    - ``UniformDistribution``: Equal probability between bounds.
      Use when all durations in a range are equally likely.
    - ``NormalDistribution``: Gaussian/bell curve with optional truncation.
      Good for well-understood, repeatable tasks.
    - ``PERTDistribution``: Smooth version of triangular (Program Evaluation
      Review Technique). More weight on the mode than triangular.
    - ``LogNormalDistribution``: Right-skewed distribution.
      Good for tasks that may have unexpected delays.
    - ``BetaDistribution``: Highly flexible with alpha/beta parameters.
      For advanced modeling when you need specific shapes.

Task:
    Represents a single task with probabilistic duration. Tasks are the
    building blocks of projects.

Project:
    Collection of tasks with optional dependencies. Provides Monte Carlo
    simulation, statistics, critical path analysis, and visualization.

Quick Start
-----------
>>> from monaco import Project, Task
>>>
>>> # Create tasks with uncertainty (min, mode, max)
>>> design = Task(name="Design", min_duration=5, mode_duration=7, max_duration=14)
>>> develop = Task(name="Develop", min_duration=10, mode_duration=15, max_duration=25)
>>> test = Task(name="Test", min_duration=3, mode_duration=5, max_duration=10)
>>>
>>> # Create project with dependencies
>>> project = Project(name="My Project", unit="days")
>>> project.add_task(design)
>>> project.add_task(develop, depends_on=[design])
>>> project.add_task(test, depends_on=[develop])
>>>
>>> # Run simulation and get statistics
>>> stats = project.statistics(n=10000)
>>> print(f"Expected duration: {stats['mean']:.1f} days")
>>> print(f"P85 estimate: {stats['percentiles']['p85']:.1f} days")

Using Distribution Objects
--------------------------
>>> from monaco import Task, PERTDistribution
>>>
>>> # Use PERT distribution for smoother estimates
>>> dist = PERTDistribution(minimum=5, mode=7, maximum=14)
>>> task = Task(name="Design", distribution=dist)

Configuration Files
-------------------
Projects can be defined in YAML configuration files for easy sharing
and version control. See ``monaco.config`` for loading configurations.

Example YAML::

    project:
      name: "Website Redesign"
      unit: "days"

    tasks:
      - name: "Design"
        distribution:
          type: "pert"
          minimum: 5
          mode: 7
          maximum: 14

      - name: "Development"
        depends_on: ["Design"]
        distribution:
          type: "triangular"
          minimum: 10
          mode: 15
          maximum: 25

Command Line Interface
----------------------
Monaco provides a CLI for running simulations::

    $ monaco init              # Create template config file
    $ monaco run config.yaml   # Run simulation
    $ monaco stats config.yaml # Show statistics
    $ monaco plot config.yaml  # Generate visualization
    $ monaco graph config.yaml # Show dependency graph

See Also
--------
monaco.distributions : Probability distribution classes.
monaco.task : Task class for individual tasks.
monaco.project : Project class for task collections.
monaco.config : YAML configuration loading.
monaco.cli : Command-line interface.

Version
-------
0.1.2
"""

# Import order matters: distributions -> task -> project to avoid circular imports
from monaco.distributions import (
    BetaDistribution,
    Distribution,
    LogNormalDistribution,
    NormalDistribution,
    PERTDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from monaco.task import Task
from monaco.project import Project

__version__ = "0.1.2"

__all__ = [
    # Core classes
    "Project",
    "Task",
    # Distribution base
    "Distribution",
    # Distribution types
    "BetaDistribution",
    "LogNormalDistribution",
    "NormalDistribution",
    "PERTDistribution",
    "TriangularDistribution",
    "UniformDistribution",
    # Version
    "__version__",
]
