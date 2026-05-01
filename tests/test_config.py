"""Tests for YAML configuration loading."""

from pathlib import Path

import pytest

from planaco import Project
from planaco.config import (
    ConfigError,
    build_project_from_config,
    get_seed_from_config,
    get_template_config,
    load_config,
)

# Get path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config = load_config(str(FIXTURES_DIR / "valid_project.yaml"))

        assert "project" in config
        assert "tasks" in config
        assert config["project"]["name"] == "Test Project"
        assert config["project"]["unit"] == "days"
        assert len(config["tasks"]) == 3

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.yaml")

    def test_load_missing_tasks_section(self):
        """Test loading config without tasks section."""
        with pytest.raises(ConfigError) as excinfo:
            load_config(str(FIXTURES_DIR / "invalid_missing_tasks.yaml"))
        assert "tasks" in str(excinfo.value).lower()

    def test_load_unknown_dependency(self):
        """Test loading config with unknown dependency reference."""
        with pytest.raises(ConfigError) as excinfo:
            load_config(str(FIXTURES_DIR / "invalid_unknown_dep.yaml"))
        assert "nonexistent_task" in str(excinfo.value)


class TestBuildProjectFromConfig:
    """Tests for build_project_from_config function."""

    def test_build_project_basic(self):
        """Test building a project from config."""
        config = load_config(str(FIXTURES_DIR / "valid_project.yaml"))
        project = build_project_from_config(config)

        assert isinstance(project, Project)
        assert project.name == "Test Project"
        assert project.unit == "days"
        assert len(project.tasks) == 3

    def test_build_project_dependencies(self):
        """Test that dependencies are correctly set up."""
        config = load_config(str(FIXTURES_DIR / "valid_project.yaml"))
        project = build_project_from_config(config)

        # Project should have dependencies
        assert project._has_dependencies()

    def test_build_project_can_estimate(self):
        """Test that built project can run estimation."""
        config = load_config(str(FIXTURES_DIR / "valid_project.yaml"))
        project = build_project_from_config(config)

        # Should be able to run simulation
        result = project.estimate()
        assert result > 0

    def test_build_project_statistics(self):
        """Test that built project can generate statistics."""
        config = load_config(str(FIXTURES_DIR / "valid_project.yaml"))
        project = build_project_from_config(config)

        stats = project.statistics(n=100)
        assert "mean" in stats
        assert "percentiles" in stats
        assert stats["unit"] == "days"


class TestGetTemplateConfig:
    """Tests for get_template_config function."""

    def test_template_is_valid_yaml(self):
        """Test that template generates valid YAML."""
        import yaml

        template = get_template_config("Test Project")
        config = yaml.safe_load(template)

        assert "project" in config
        assert "tasks" in config
        assert config["project"]["name"] == "Test Project"

    def test_template_with_custom_name(self):
        """Test template with custom project name."""
        template = get_template_config("My Custom Project")
        assert "My Custom Project" in template

    def test_template_has_example_tasks(self):
        """Test that template includes example tasks."""
        import yaml

        template = get_template_config("Test")
        config = yaml.safe_load(template)

        assert len(config["tasks"]) > 0
        # Check that tasks have required fields based on estimator type
        for _task_id, task_config in config["tasks"].items():
            estimator = task_config.get("estimator", "triangular")
            if estimator in ("normal", "lognormal"):
                assert "mean" in task_config
                assert "std_dev" in task_config
            elif estimator == "beta":
                assert "alpha" in task_config
                assert "beta" in task_config
                assert "max_value" in task_config
            else:
                # triangular, pert, uniform
                assert "min_duration" in task_config
                assert "max_duration" in task_config

    def test_template_has_seed_comment(self):
        """Test that template includes commented seed option."""
        template = get_template_config("Test")
        assert "# seed:" in template
        assert "reproducible" in template.lower()


class TestNormalDistributionConfig:
    """Tests for Normal distribution configuration."""

    def test_load_config_with_normal(self):
        """Test loading config with normal distribution."""
        config = load_config(str(FIXTURES_DIR / "project_with_normal.yaml"))
        assert "tasks" in config
        # Check that normal estimator task exists
        review_task = config["tasks"].get("review")
        assert review_task is not None
        assert review_task["estimator"] == "normal"
        assert review_task["mean"] == 2.0
        assert review_task["std_dev"] == 0.5

    def test_build_project_with_normal(self):
        """Test building project with normal distribution."""
        config = load_config(str(FIXTURES_DIR / "project_with_normal.yaml"))
        project = build_project_from_config(config)

        # Should be able to run simulation
        result = project.estimate()
        assert result > 0

    def test_build_project_with_normal_statistics(self):
        """Test that project with normal distribution can generate statistics."""
        config = load_config(str(FIXTURES_DIR / "project_with_normal.yaml"))
        project = build_project_from_config(config)

        stats = project.statistics(n=100)
        assert "mean" in stats
        assert stats["mean"] > 0

    def test_missing_mean_raises_error(self):
        """Test that missing mean parameter raises error."""
        with pytest.raises(ConfigError) as excinfo:
            load_config(str(FIXTURES_DIR / "invalid_normal_missing_mean.yaml"))
        assert "mean" in str(excinfo.value).lower()

    def test_missing_std_dev_raises_error(self):
        """Test that missing std_dev parameter raises error."""
        with pytest.raises(ConfigError) as excinfo:
            load_config(str(FIXTURES_DIR / "invalid_normal_missing_std.yaml"))
        assert "std_dev" in str(excinfo.value).lower()

    def test_normal_with_bounds(self):
        """Test loading normal distribution with bounds."""
        config = load_config(str(FIXTURES_DIR / "project_with_normal.yaml"))
        final_review = config["tasks"]["final_review"]

        assert final_review["min_value"] == 0.5
        assert final_review["max_value"] == 3.0


class TestGetSeedFromConfig:
    """Tests for get_seed_from_config function."""

    def test_get_seed_when_present(self):
        """Test extracting seed from config that has one."""
        config = load_config(str(FIXTURES_DIR / "project_with_seed.yaml"))
        seed = get_seed_from_config(config)
        assert seed == 42

    def test_get_seed_when_absent(self):
        """Test extracting seed from config without one."""
        config = load_config(str(FIXTURES_DIR / "valid_project.yaml"))
        seed = get_seed_from_config(config)
        assert seed is None

    def test_seed_enables_reproducibility(self):
        """Test that using the same seed produces identical results."""
        import random

        config = load_config(str(FIXTURES_DIR / "project_with_seed.yaml"))
        seed = get_seed_from_config(config)
        project = build_project_from_config(config)

        # Run with seed
        random.seed(seed)
        result1 = project.estimate()

        # Run again with same seed
        random.seed(seed)
        result2 = project.estimate()

        assert result1 == result2


def _write_yaml(tmp_path, content: str) -> str:
    """Helper: write YAML content to a temp file and return its path."""
    path = tmp_path / "config.yaml"
    path.write_text(content)
    return str(path)


class TestValidationEdgeCases:
    """Edge-case tests for _validate_config covering branches not exercised
    by the fixture-based tests."""

    def test_empty_yaml_raises(self, tmp_path):
        """An empty YAML file parses to None and must be rejected."""
        path = _write_yaml(tmp_path, "")
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "empty" in str(excinfo.value).lower()

    def test_missing_project_section_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
tasks:
  a:
    min_duration: 1
    mode_duration: 2
    max_duration: 3
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "project" in str(excinfo.value).lower()

    def test_empty_tasks_dict_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Empty"
tasks: {}
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "at least one task" in str(excinfo.value).lower()

    def test_null_task_config_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Null Task"
tasks:
  broken:
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "broken" in str(excinfo.value)

    def test_unknown_estimator_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Bad Estimator"
tasks:
  a:
    estimator: "magic"
    min_duration: 1
    max_duration: 2
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "magic" in str(excinfo.value)

    def test_triangular_missing_min_duration_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Missing min"
tasks:
  a:
    estimator: "triangular"
    mode_duration: 2
    max_duration: 3
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "min_duration" in str(excinfo.value)

    def test_triangular_missing_max_duration_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Missing max"
tasks:
  a:
    estimator: "triangular"
    min_duration: 1
    mode_duration: 2
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "max_duration" in str(excinfo.value)

    def test_pert_missing_mode_duration_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "PERT missing mode"
tasks:
  a:
    estimator: "pert"
    min_duration: 1
    max_duration: 5
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "mode_duration" in str(excinfo.value)

    def test_beta_missing_alpha_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Beta missing alpha"
tasks:
  a:
    estimator: "beta"
    beta: 2
    max_value: 10
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "alpha" in str(excinfo.value)

    def test_beta_missing_beta_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Beta missing beta"
tasks:
  a:
    estimator: "beta"
    alpha: 2
    max_value: 10
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "beta" in str(excinfo.value)

    def test_beta_missing_max_value_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Beta missing max_value"
tasks:
  a:
    estimator: "beta"
    alpha: 2
    beta: 2
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "max_value" in str(excinfo.value)

    def test_lognormal_missing_mean_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "LogNormal missing mean"
tasks:
  a:
    estimator: "lognormal"
    std_dev: 1.0
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "mean" in str(excinfo.value).lower()

    def test_lognormal_missing_std_dev_raises(self, tmp_path):
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "LogNormal missing std_dev"
tasks:
  a:
    estimator: "lognormal"
    mean: 5.0
""",
        )
        with pytest.raises(ConfigError) as excinfo:
            load_config(path)
        assert "std_dev" in str(excinfo.value).lower()

    def test_uniform_accepts_missing_mode_duration(self, tmp_path):
        """Uniform doesn't need mode_duration; it should validate fine."""
        path = _write_yaml(
            tmp_path,
            """
project:
  name: "Uniform ok"
tasks:
  a:
    estimator: "uniform"
    min_duration: 1
    max_duration: 5
""",
        )
        # No exception
        config = load_config(path)
        assert "a" in config["tasks"]
