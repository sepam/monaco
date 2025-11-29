"""YAML configuration loader for Monaco projects."""
from pathlib import Path
from typing import Dict, Any, List

import yaml

from monaco.task import Task
from monaco.project import Project


class ConfigError(Exception):
    """Raised when configuration is invalid."""
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

    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    _validate_config(config)
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure and values."""
    if config is None:
        raise ConfigError("Configuration file is empty")

    if 'project' not in config:
        raise ConfigError("Configuration must have 'project' section")

    if 'tasks' not in config:
        raise ConfigError("Configuration must have 'tasks' section")

    if not config['tasks']:
        raise ConfigError("At least one task must be defined")

    # Validate task references
    task_ids = set(config['tasks'].keys())
    for task_id, task_config in config['tasks'].items():
        if task_config is None:
            raise ConfigError(f"Task '{task_id}' has no configuration")

        # Check required fields
        if 'min_duration' not in task_config:
            raise ConfigError(f"Task '{task_id}' missing required field 'min_duration'")
        if 'max_duration' not in task_config:
            raise ConfigError(f"Task '{task_id}' missing required field 'max_duration'")

        # Validate estimator
        estimator = task_config.get('estimator', 'triangular')
        if estimator == 'triangular' and 'mode_duration' not in task_config:
            raise ConfigError(
                f"Task '{task_id}' uses triangular estimator but missing 'mode_duration'"
            )

        # Validate dependency references
        if 'depends_on' in task_config:
            for dep_id in task_config['depends_on']:
                if dep_id not in task_ids:
                    raise ConfigError(
                        f"Task '{task_id}' depends on unknown task '{dep_id}'"
                    )


def build_project_from_config(config: Dict[str, Any]) -> Project:
    """Build a Project instance from configuration.

    Parameters
    ----------
    config : Dict[str, Any]
        Parsed configuration dictionary

    Returns
    -------
    Project
        Configured Project instance with all tasks added
    """
    project_config = config['project']
    project = Project(
        name=project_config.get('name'),
        unit=project_config.get('unit', 'days')
    )

    # Build task instances
    tasks: Dict[str, Task] = {}

    for task_id, task_config in config['tasks'].items():
        task = Task(
            name=task_config.get('name', task_id),
            min_duration=task_config.get('min_duration'),
            mode_duration=task_config.get('mode_duration'),
            max_duration=task_config.get('max_duration'),
            estimator=task_config.get('estimator', 'triangular')
        )
        tasks[task_id] = task

    # Track which tasks have been added
    added_tasks: Dict[str, Task] = {}

    def add_task_with_deps(task_id: str) -> None:
        """Recursively add task and its dependencies."""
        if task_id in added_tasks:
            return

        task_config = config['tasks'][task_id]

        # First add all dependencies
        deps = task_config.get('depends_on', [])
        for dep_id in deps:
            add_task_with_deps(dep_id)

        # Now add this task
        dep_tasks = [added_tasks[dep_id] for dep_id in deps] if deps else None
        project.add_task(tasks[task_id], depends_on=dep_tasks)
        added_tasks[task_id] = tasks[task_id]

    # Add all tasks
    for task_id in config['tasks']:
        add_task_with_deps(task_id)

    return project


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
    return f'''# Monaco Project Configuration
# Documentation: https://github.com/sepam/monaco

project:
  name: "{project_name}"
  unit: "days"

tasks:
  # Task ID is used for dependencies
  design:
    name: "Design Phase"
    min_duration: 2
    mode_duration: 3
    max_duration: 5
    estimator: "triangular"

  development:
    name: "Development"
    min_duration: 5
    mode_duration: 8
    max_duration: 12
    estimator: "triangular"
    depends_on:
      - design

  testing:
    name: "Testing"
    min_duration: 2
    mode_duration: 3
    max_duration: 5
    estimator: "triangular"
    depends_on:
      - development

  deployment:
    name: "Deployment"
    min_duration: 1
    max_duration: 2
    estimator: "uniform"
    depends_on:
      - testing
'''
