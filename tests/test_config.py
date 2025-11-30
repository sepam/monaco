"""Tests for YAML configuration loading."""

from pathlib import Path

import pytest

from monaco import Project
from monaco.config import (
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
        # Check that tasks have required fields
        for _task_id, task_config in config["tasks"].items():
            assert "min_duration" in task_config
            assert "max_duration" in task_config

    def test_template_has_seed_comment(self):
        """Test that template includes commented seed option."""
        template = get_template_config("Test")
        assert "# seed:" in template
        assert "reproducible" in template.lower()


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
