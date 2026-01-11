"""
YAML configuration loader for Monaco projects.

This module provides functions for loading, validating, and building
Project instances from YAML configuration files. Configuration files
provide a declarative way to define projects, making them easy to
version control and share.

Key Functions
-------------
load_config(path)
    Load and validate a YAML configuration file.

build_project_from_config(config)
    Convert a configuration dictionary to a Project instance.

get_template_config()
    Generate a template YAML configuration with examples.

Configuration Structure
-----------------------
A valid configuration file has two main sections:

1. **project**: Project-level settings
   - name: Project name
   - unit: Time unit (days, weeks, hours)
   - seed: (optional) Random seed for reproducibility

2. **tasks**: Dictionary of task definitions
   - Each task has a unique ID (the dictionary key)
   - Each task specifies a distribution type and parameters
   - Dependencies are specified by referencing other task IDs

Example
-------
>>> from monaco.config import load_config, build_project_from_config
>>> config = load_config("project.yaml")
>>> project = build_project_from_config(config)
>>> stats = project.statistics(n=10000)

See Also
--------
Project : The Project class built from configurations.
distributions : Available distribution types.
cli : Command-line interface for running configurations.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from monaco.distributions import DISTRIBUTION_REGISTRY, create_distribution
from monaco.project import Project
from monaco.task import Task


class ConfigError(Exception):
    """Exception raised when configuration validation fails.

    This exception is raised by load_config() and related functions
    when the YAML configuration file has structural errors, missing
    required fields, invalid distribution types, or broken references.

    Attributes
    ----------
    message : str
        Human-readable description of the configuration error.

    Example
    -------
    >>> from monaco.config import load_config, ConfigError
    >>> try:
    ...     config = load_config("invalid.yaml")
    ... except ConfigError as e:
    ...     print(f"Config error: {e}")
    """

    pass


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and validate a YAML configuration file.

    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file

    Returns
    -------
    Dict[str, Any]
        Parsed configuration dictionary

    Raises
    ------
    ConfigError
        If the configuration is invalid
    FileNotFoundError
        If the config file doesn't exist
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path) as f:
        config = yaml.safe_load(f)

    _validate_config(config)
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure and required fields.

    Performs comprehensive validation of the configuration dictionary
    to catch errors before attempting to build a Project.

    Validation Rules
    ----------------
    **Structure validation:**
    - Config must not be empty/None
    - Must have 'project' section
    - Must have 'tasks' section with at least one task

    **Task validation (for each task):**
    - Task config must not be None
    - Estimator must be a valid distribution type
    - Required fields depend on estimator:
      - triangular/pert: min_duration, mode_duration, max_duration
      - uniform: min_duration, max_duration
      - normal/lognormal: mean, std_dev
      - beta: alpha, beta, max_value

    **Dependency validation:**
    - All tasks in depends_on must exist in the tasks section

    Parameters
    ----------
    config : Dict[str, Any]
        Parsed YAML configuration dictionary.

    Raises
    ------
    ConfigError
        If any validation rule is violated.
    """
    if config is None:
        raise ConfigError("Configuration file is empty")

    if "project" not in config:
        raise ConfigError("Configuration must have 'project' section")

    if "tasks" not in config:
        raise ConfigError("Configuration must have 'tasks' section")

    if not config["tasks"]:
        raise ConfigError("At least one task must be defined")

    # Validate task references
    task_ids = set(config["tasks"].keys())
    for task_id, task_config in config["tasks"].items():
        if task_config is None:
            raise ConfigError(f"Task '{task_id}' has no configuration")

        # Validate estimator
        estimator = task_config.get("estimator", "triangular")
        if estimator not in DISTRIBUTION_REGISTRY:
            raise ConfigError(
                f"Task '{task_id}' has unknown estimator '{estimator}'. "
                f"Valid options: {list(DISTRIBUTION_REGISTRY.keys())}"
            )

        # Validate required fields based on estimator type
        if estimator in ("normal", "lognormal"):
            # Normal and LogNormal distributions use mean and std_dev
            if "mean" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' uses {estimator} estimator but missing 'mean'"
                )
            if "std_dev" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' uses {estimator} estimator but missing 'std_dev'"
                )
        elif estimator == "beta":
            # Beta distribution uses alpha, beta, and max_value
            if "alpha" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' uses beta estimator but missing 'alpha'"
                )
            if "beta" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' uses beta estimator but missing 'beta'"
                )
            if "max_value" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' uses beta estimator but missing 'max_value'"
                )
        else:
            # Triangular, uniform, and PERT use min_duration/max_duration
            if "min_duration" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' missing required field 'min_duration'"
                )
            if "max_duration" not in task_config:
                raise ConfigError(
                    f"Task '{task_id}' missing required field 'max_duration'"
                )
            if (
                estimator in ("triangular", "pert")
                and "mode_duration" not in task_config
            ):
                raise ConfigError(
                    f"Task '{task_id}' uses {estimator} estimator but missing 'mode_duration'"
                )

        # Validate dependency references
        if "depends_on" in task_config:
            for dep_id in task_config["depends_on"]:
                if dep_id not in task_ids:
                    raise ConfigError(
                        f"Task '{task_id}' depends on unknown task '{dep_id}'"
                    )


def build_project_from_config(config: Dict[str, Any]) -> Project:
    """Build a Project instance from a configuration dictionary.

    Creates all Task objects from the configuration, establishes
    dependencies between them, and returns a ready-to-simulate
    Project instance.

    Parameters
    ----------
    config : Dict[str, Any]
        Parsed and validated configuration dictionary from load_config().

    Returns
    -------
    Project
        Configured Project instance with all tasks and dependencies.

    Example
    -------
    >>> config = load_config("my_project.yaml")
    >>> project = build_project_from_config(config)
    >>> print(f"Project: {project.name}")
    >>> print(f"Tasks: {len(project.tasks)}")
    >>> stats = project.statistics(n=10000)
    """
    project_config = config["project"]
    project = Project(
        name=project_config.get("name"), unit=project_config.get("unit", "days")
    )

    # Build task instances
    tasks: Dict[str, Task] = {}

    for task_id, task_config in config["tasks"].items():
        estimator = task_config.get("estimator", "triangular")

        # Create distribution using factory
        distribution = create_distribution(
            estimator=estimator,
            min_duration=task_config.get("min_duration"),
            mode_duration=task_config.get("mode_duration"),
            max_duration=task_config.get("max_duration"),
            mean=task_config.get("mean"),
            std_dev=task_config.get("std_dev"),
            min_value=task_config.get("min_value"),
            max_value=task_config.get("max_value"),
            alpha=task_config.get("alpha"),
            beta=task_config.get("beta"),
            lamb=task_config.get("lamb"),
        )

        task = Task(
            name=task_config.get("name", task_id),
            distribution=distribution,
        )
        tasks[task_id] = task

    # Track which tasks have been added to avoid duplicates
    added_tasks: Dict[str, Task] = {}

    def add_task_with_deps(task_id: str) -> None:
        """Recursively add a task and all its dependencies to the project.

        Uses depth-first traversal to ensure dependencies are added before
        the tasks that depend on them. Tracks already-added tasks to handle
        diamond dependencies (A depends on B and C, both depend on D).

        Parameters
        ----------
        task_id : str
            The ID of the task to add (key in config["tasks"]).
        """
        # Skip if already added (handles diamond dependencies)
        if task_id in added_tasks:
            return

        task_config = config["tasks"][task_id]

        # Recursively add all dependencies first (DFS)
        deps = task_config.get("depends_on", [])
        for dep_id in deps:
            add_task_with_deps(dep_id)

        # Now add this task (all dependencies are guaranteed to be in project)
        dep_tasks = [added_tasks[dep_id] for dep_id in deps] if deps else None
        project.add_task(tasks[task_id], depends_on=dep_tasks)
        added_tasks[task_id] = tasks[task_id]

    # Add all tasks (order doesn't matter due to recursive dependency handling)
    for task_id in config["tasks"]:
        add_task_with_deps(task_id)

    return project


def get_seed_from_config(config: Dict[str, Any]) -> Optional[int]:
    """Extract the seed value from configuration.

    Parameters
    ----------
    config : Dict[str, Any]
        Parsed configuration dictionary

    Returns
    -------
    Optional[int]
        The seed value if specified, None otherwise
    """
    project_config = config.get("project", {})
    seed = project_config.get("seed")
    if seed is not None:
        return int(seed)
    return None


def get_template_config(project_name: str = "My Project") -> str:
    """Generate a template YAML configuration.

    Parameters
    ----------
    project_name : str
        Name for the project in the template

    Returns
    -------
    str
        YAML configuration template as a string
    """
    return f"""# Monaco Project Configuration
# Documentation: https://github.com/sepam/monaco
#
# Available distributions:
#   - triangular: min_duration, mode_duration, max_duration (most common)
#   - pert: min_duration, mode_duration, max_duration (smoother than triangular)
#   - uniform: min_duration, max_duration (equal probability)
#   - normal: mean, std_dev (bell curve, for well-understood tasks)
#   - lognormal: mean, std_dev (right-skewed, for tasks with delay risk)
#   - beta: alpha, beta, max_value (flexible shape)

project:
  name: "{project_name}"
  unit: "days"
  # seed: 42  # Uncomment for reproducible results

tasks:
  # Triangular: Classic 3-point estimate (optimistic, most likely, pessimistic)
  design:
    name: "Design Phase"
    min_duration: 2
    mode_duration: 3
    max_duration: 5
    estimator: "triangular"

  # PERT: Smoother than triangular, widely used in project management
  # Gives more weight to the mode (most likely) value
  development:
    name: "Development"
    min_duration: 5
    mode_duration: 8
    max_duration: 12
    estimator: "pert"
    # lamb: 4  # Optional shape parameter (default: 4)
    depends_on:
      - design

  # Normal: For well-understood, predictable tasks
  code_review:
    name: "Code Review"
    estimator: "normal"
    mean: 2.0
    std_dev: 0.5
    # min_value: 0.5  # Optional lower bound
    # max_value: 5.0  # Optional upper bound
    depends_on:
      - development

  # LogNormal: For tasks with potential for delays (right-skewed)
  testing:
    name: "Testing"
    estimator: "lognormal"
    mean: 3.0
    std_dev: 1.0
    depends_on:
      - code_review

  # Beta: Flexible distribution for custom uncertainty profiles
  # alpha=2, beta=5 creates right-skewed (more likely to finish early)
  integration:
    name: "Integration"
    estimator: "beta"
    alpha: 2.0
    beta: 5.0
    min_value: 1.0
    max_value: 5.0
    depends_on:
      - testing

  # Uniform: When all durations equally likely
  deployment:
    name: "Deployment"
    min_duration: 1
    max_duration: 2
    estimator: "uniform"
    depends_on:
      - integration
"""
