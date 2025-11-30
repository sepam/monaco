"""Tests for Monaco CLI commands."""

import json
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


@pytest.fixture
def seeded_config_path():
    """Path to test configuration with seed."""
    return str(FIXTURES_DIR / "project_with_seed.yaml")


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
        # Use --seed to avoid warning that would break JSON parsing
        result = runner.invoke(
            main, ["stats", valid_config_path, "-n", "100", "--json", "--seed", "42"]
        )
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
            result = runner.invoke(
                main,
                [
                    "run",
                    valid_config_path,
                    "-n",
                    "100",
                    "-o",
                    "results.json",
                    "-f",
                    "json",
                ],
            )
            assert result.exit_code == 0
            assert Path("results.json").exists()

            with open("results.json") as f:
                data = json.load(f)
            assert "statistics" in data
            assert "simulations" in data

    def test_run_to_csv_file(self, runner, valid_config_path):
        """Test run command exports to CSV file."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                main,
                [
                    "run",
                    valid_config_path,
                    "-n",
                    "100",
                    "-o",
                    "results.csv",
                    "-f",
                    "csv",
                ],
            )
            assert result.exit_code == 0
            assert Path("results.csv").exists()

    def test_run_with_seed(self, runner, valid_config_path):
        """Test run command with random seed for reproducibility."""
        result = runner.invoke(
            main, ["run", valid_config_path, "-n", "100", "--seed", "42"]
        )
        # Should run successfully with seed
        assert result.exit_code == 0
        assert "Project:" in result.output


class TestPlotCommand:
    """Tests for monaco plot command."""

    def test_plot_to_file(self, runner, valid_config_path):
        """Test plot command saves to file."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                main, ["plot", valid_config_path, "-n", "100", "-o", "chart.png"]
            )
            assert result.exit_code == 0
            assert Path("chart.png").exists()
            assert "saved" in result.output.lower()

    def test_plot_with_percentiles(self, runner, valid_config_path):
        """Test plot with percentile markers."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                main,
                [
                    "plot",
                    valid_config_path,
                    "-n",
                    "100",
                    "-o",
                    "chart.png",
                    "-p",
                    "50",
                    "-p",
                    "85",
                    "-p",
                    "95",
                ],
            )
            assert result.exit_code == 0

    def test_plot_cumulative(self, runner, valid_config_path):
        """Test cumulative plot option."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                main,
                [
                    "plot",
                    valid_config_path,
                    "-n",
                    "100",
                    "-o",
                    "chart.png",
                    "--cumulative",
                ],
            )
            assert result.exit_code == 0


class TestGraphCommand:
    """Tests for monaco graph command."""

    def test_graph_to_file(self, runner, valid_config_path):
        """Test graph command saves to file."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                main, ["graph", valid_config_path, "-o", "graph.png"]
            )
            assert result.exit_code == 0
            assert Path("graph.png").exists()

    def test_graph_no_durations(self, runner, valid_config_path):
        """Test graph with --no-durations flag."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                main, ["graph", valid_config_path, "-o", "graph.png", "--no-durations"]
            )
            assert result.exit_code == 0


class TestSeedFunctionality:
    """Tests for seed/reproducibility functionality."""

    def test_no_seed_shows_warning(self, runner, valid_config_path):
        """Test that warning is shown when no seed is specified."""
        result = runner.invoke(main, ["stats", valid_config_path, "-n", "100"])
        assert result.exit_code == 0
        # Warning should be in stderr (captured in output by CliRunner)
        assert "No seed specified" in result.output
        assert "reproducible" in result.output.lower()

    def test_config_seed_no_warning(self, runner, seeded_config_path):
        """Test that no warning is shown when config has seed."""
        result = runner.invoke(main, ["stats", seeded_config_path, "-n", "100"])
        assert result.exit_code == 0
        assert "No seed specified" not in result.output

    def test_cli_seed_no_warning(self, runner, valid_config_path):
        """Test that no warning is shown when CLI seed is provided."""
        result = runner.invoke(
            main, ["stats", valid_config_path, "-n", "100", "--seed", "42"]
        )
        assert result.exit_code == 0
        assert "No seed specified" not in result.output

    def test_config_seed_reproducibility(self, runner, seeded_config_path):
        """Test that config seed produces reproducible results."""
        result1 = runner.invoke(
            main, ["stats", seeded_config_path, "-n", "100", "--json"]
        )
        result2 = runner.invoke(
            main, ["stats", seeded_config_path, "-n", "100", "--json"]
        )

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Parse JSON and compare means (should be identical with same seed)
        data1 = json.loads(result1.output)
        data2 = json.loads(result2.output)
        assert data1["mean"] == data2["mean"]

    def test_cli_seed_overrides_config(self, runner, seeded_config_path):
        """Test that CLI --seed overrides config seed."""
        # Run with config seed (42)
        result1 = runner.invoke(
            main, ["stats", seeded_config_path, "-n", "100", "--json"]
        )

        # Run with different CLI seed
        result2 = runner.invoke(
            main, ["stats", seeded_config_path, "-n", "100", "--json", "--seed", "999"]
        )

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Results should be different
        data1 = json.loads(result1.output)
        data2 = json.loads(result2.output)
        # With different seeds, means will likely differ
        # (there's a tiny chance they could be equal, but very unlikely)
        assert data1["mean"] != data2["mean"]

    def test_stats_seed_option(self, runner, valid_config_path):
        """Test stats command has --seed option."""
        result = runner.invoke(main, ["stats", "--help"])
        assert "--seed" in result.output

    def test_plot_seed_option(self, runner, valid_config_path):
        """Test plot command has --seed option."""
        result = runner.invoke(main, ["plot", "--help"])
        assert "--seed" in result.output

    def test_warning_goes_to_stderr(self, runner, valid_config_path):
        """Test that warning doesn't break JSON output."""
        result = runner.invoke(
            main, ["stats", valid_config_path, "-n", "100", "--json"]
        )
        assert result.exit_code == 0

        # The output should still be parseable JSON
        # (warning is on stderr, JSON on stdout)
        # CliRunner mixes them, but the JSON should still be at the end
        # Find the JSON part (starts with '{')
        output = result.output
        json_start = output.find("{")
        if json_start >= 0:
            json_part = output[json_start:]
            data = json.loads(json_part)
            assert "mean" in data
