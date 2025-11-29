"""Tests for Monaco CLI commands."""
import os
import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from monaco.cli import main


# Get path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def valid_config_path():
    """Path to valid test configuration."""
    return str(FIXTURES_DIR / "valid_project.yaml")


class TestMainGroup:
    """Tests for main CLI group."""

    def test_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Monaco" in result.output

    def test_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.2" in result.output


class TestInitCommand:
    """Tests for monaco init command."""

    def test_init_creates_file(self, runner):
        """Test that init creates a YAML file."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "test_project.yaml"])
            assert result.exit_code == 0
            assert Path("test_project.yaml").exists()
            assert "Created" in result.output

    def test_init_with_custom_name(self, runner):
        """Test init with custom project name."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "test.yaml", "--name", "My Project"])
            assert result.exit_code == 0

            with open("test.yaml") as f:
                content = f.read()
            assert "My Project" in content

    def test_init_fails_if_file_exists(self, runner):
        """Test that init fails if file already exists."""
        with runner.isolated_filesystem():
            Path("existing.yaml").touch()
            result = runner.invoke(main, ["init", "existing.yaml"])
            assert result.exit_code == 1
            assert "already exists" in result.output


class TestStatsCommand:
    """Tests for monaco stats command."""

    def test_stats_basic(self, runner, valid_config_path):
        """Test basic stats command."""
        result = runner.invoke(main, ["stats", valid_config_path, "-n", "100"])
        assert result.exit_code == 0
        assert "Project:" in result.output
        assert "Mean:" in result.output
        assert "Percentiles:" in result.output

    def test_stats_json_output(self, runner, valid_config_path):
        """Test stats with JSON output."""
        result = runner.invoke(main, ["stats", valid_config_path, "-n", "100", "--json"])
        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.output)
        assert "mean" in data
        assert "percentiles" in data

    def test_stats_nonexistent_file(self, runner):
        """Test stats with nonexistent file."""
        result = runner.invoke(main, ["stats", "nonexistent.yaml"])
        # Click returns exit code 2 for file not found errors
        assert result.exit_code != 0
        assert "Error" in result.output or "does not exist" in result.output


class TestRunCommand:
    """Tests for monaco run command."""

    def test_run_to_stdout(self, runner, valid_config_path):
        """Test run command outputs to stdout."""
        result = runner.invoke(main, ["run", valid_config_path, "-n", "100"])
        assert result.exit_code == 0
        assert "Project:" in result.output

    def test_run_to_json_file(self, runner, valid_config_path):
        """Test run command exports to JSON file."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "run", valid_config_path,
                "-n", "100",
                "-o", "results.json",
                "-f", "json"
            ])
            assert result.exit_code == 0
            assert Path("results.json").exists()

            with open("results.json") as f:
                data = json.load(f)
            assert "statistics" in data
            assert "simulations" in data

    def test_run_to_csv_file(self, runner, valid_config_path):
        """Test run command exports to CSV file."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "run", valid_config_path,
                "-n", "100",
                "-o", "results.csv",
                "-f", "csv"
            ])
            assert result.exit_code == 0
            assert Path("results.csv").exists()

    def test_run_with_seed(self, runner, valid_config_path):
        """Test run command with random seed for reproducibility."""
        result = runner.invoke(main, [
            "run", valid_config_path, "-n", "100", "--seed", "42"
        ])
        # Should run successfully with seed
        assert result.exit_code == 0
        assert "Project:" in result.output


class TestPlotCommand:
    """Tests for monaco plot command."""

    def test_plot_to_file(self, runner, valid_config_path):
        """Test plot command saves to file."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "plot", valid_config_path,
                "-n", "100",
                "-o", "chart.png"
            ])
            assert result.exit_code == 0
            assert Path("chart.png").exists()
            assert "saved" in result.output.lower()

    def test_plot_with_percentiles(self, runner, valid_config_path):
        """Test plot with percentile markers."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "plot", valid_config_path,
                "-n", "100",
                "-o", "chart.png",
                "-p", "50", "-p", "85", "-p", "95"
            ])
            assert result.exit_code == 0

    def test_plot_cumulative(self, runner, valid_config_path):
        """Test cumulative plot option."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "plot", valid_config_path,
                "-n", "100",
                "-o", "chart.png",
                "--cumulative"
            ])
            assert result.exit_code == 0


class TestGraphCommand:
    """Tests for monaco graph command."""

    def test_graph_to_file(self, runner, valid_config_path):
        """Test graph command saves to file."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "graph", valid_config_path,
                "-o", "graph.png"
            ])
            assert result.exit_code == 0
            assert Path("graph.png").exists()

    def test_graph_no_durations(self, runner, valid_config_path):
        """Test graph with --no-durations flag."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "graph", valid_config_path,
                "-o", "graph.png",
                "--no-durations"
            ])
            assert result.exit_code == 0
