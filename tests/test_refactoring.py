"""
Refactoring Verification Tests
==============================

These tests verify that the legacy code cleanup has been completed successfully.
Run these tests to confirm each refactoring item has been addressed.

Test Status Guide:
- Tests marked with `# BEFORE: FAIL, AFTER: PASS` should fail before refactoring
- Tests marked with `# BEFORE: PASS, AFTER: PASS` should always pass (regression tests)

Usage:
    pytest tests/test_refactoring.py -v
"""

import pytest

# ============================================================================
# ITEM 1: Project should NOT inherit from Task
# ============================================================================


class TestProjectInheritanceRemoval:
    """Verify that Project is no longer a subclass of Task."""

    def test_project_does_not_inherit_from_task(self):
        """Project should be its own class, not a Task subclass.

        # BEFORE: FAIL (Project inherits from Task)
        # AFTER: PASS (Project is standalone)
        """
        from monaco import Project, Task

        assert not issubclass(
            Project, Task
        ), "Project should NOT inherit from Task - a Project contains Tasks, it is not a Task"

    def test_project_has_no_task_id_attribute(self):
        """Project instances should not have task_id (that's a Task thing).

        # BEFORE: FAIL (inherited from Task)
        # AFTER: PASS (no inheritance)
        """
        from monaco import Project

        p = Project(name="Test")
        assert not hasattr(
            p, "task_id"
        ), "Project should not have task_id attribute (that belongs to Task)"

    def test_project_has_no_distribution_attribute(self):
        """Project should not have _distribution attribute.

        # BEFORE: FAIL (inherited from Task)
        # AFTER: PASS (no inheritance)
        """
        from monaco import Project

        p = Project(name="Test")
        assert not hasattr(
            p, "_distribution"
        ), "Project should not have _distribution attribute"

    def test_project_has_no_cdate_attribute(self):
        """Project should not have cdate attribute.

        # BEFORE: FAIL (inherited from Task)
        # AFTER: PASS (no inheritance)
        """
        from monaco import Project

        p = Project(name="Test")
        assert not hasattr(p, "cdate"), "Project should not have cdate attribute"

    def test_project_still_works_after_inheritance_removal(self):
        """Regression: Project core functionality should still work.

        # BEFORE: PASS, AFTER: PASS
        """
        from monaco import Project, Task

        p = Project(name="Test Project", unit="days")
        t1 = Task(name="Task1", min_duration=1, mode_duration=2, max_duration=3)
        t2 = Task(name="Task2", min_duration=2, mode_duration=3, max_duration=4)

        p.add_task(t1)
        p.add_task(t2, depends_on=[t1])

        # Core functionality
        assert p.name == "Test Project"
        assert p.unit == "days"
        assert len(p.tasks) == 2

        # Estimation should work
        estimate = p.estimate()
        assert isinstance(estimate, float)
        assert estimate > 0

        # Statistics should work
        stats = p.statistics(n=100)
        assert "mean" in stats
        assert "percentiles" in stats


# ============================================================================
# ITEM 2: Legacy _simulate() method should be removed
# ============================================================================


class TestSimulateMethodRemoval:
    """Verify that the legacy _simulate() method has been removed."""

    def test_simulate_method_does_not_exist(self):
        """The legacy _simulate() method should be removed.

        # BEFORE: FAIL (_simulate exists)
        # AFTER: PASS (_simulate removed)
        """
        from monaco import Project

        p = Project(name="Test")
        assert not hasattr(
            p, "_simulate"
        ), "_simulate() is legacy code and should be removed (use _run_simulation instead)"

    def test_run_simulation_still_works(self):
        """Regression: _run_simulation should still work.

        # BEFORE: PASS, AFTER: PASS
        """
        from monaco import Project, Task

        p = Project(name="Test")
        t = Task(name="Task", min_duration=1, mode_duration=2, max_duration=3)
        p.add_task(t)

        results = p._run_simulation(n=100)
        assert isinstance(results, list)
        assert len(results) == 100
        assert all(isinstance(r, float) for r in results)


# ============================================================================
# ITEM 3: p_est instance attribute should be removed
# ============================================================================


class TestPEstRemoval:
    """Verify that p_est side effect has been removed from estimate()."""

    def test_estimate_does_not_set_p_est(self):
        """Calling estimate() should not set a p_est attribute.

        # BEFORE: FAIL (estimate() sets self.p_est)
        # AFTER: PASS (no side effect)
        """
        from monaco import Project, Task

        p = Project(name="Test")
        t = Task(name="Task", min_duration=1, mode_duration=2, max_duration=3)
        p.add_task(t)

        # Ensure p_est doesn't exist before
        if hasattr(p, "p_est"):
            delattr(p, "p_est")

        _ = p.estimate()

        assert not hasattr(
            p, "p_est"
        ), "estimate() should return the value, not store it as p_est attribute"

    def test_estimate_returns_value(self):
        """Regression: estimate() should still return the correct value.

        # BEFORE: PASS, AFTER: PASS
        """
        from monaco import Project, Task

        t1 = Task(name="T1", min_duration=5, mode_duration=5, max_duration=5)
        t2 = Task(name="T2", min_duration=3, mode_duration=3, max_duration=3)

        p = Project(name="Test")
        p.add_task(t1)
        p.add_task(t2, depends_on=[t1])

        result = p.estimate()
        assert result == 8.0, "estimate() should return the project duration"


# ============================================================================
# ITEM 4: Task cdate attribute should be removed
# ============================================================================


class TestTaskCdateRemoval:
    """Verify that the unused cdate attribute has been removed from Task."""

    def test_task_has_no_cdate(self):
        """Task should not have cdate attribute (unused legacy code).

        # BEFORE: FAIL (Task has cdate)
        # AFTER: PASS (cdate removed)
        """
        from monaco import Task

        t = Task(name="Test", min_duration=1, mode_duration=2, max_duration=3)
        assert not hasattr(
            t, "cdate"
        ), "cdate is unused and should be removed from Task"

    def test_task_still_has_task_id(self):
        """Regression: Task should still have task_id (that's needed).

        # BEFORE: PASS, AFTER: PASS
        """
        from monaco import Task

        t = Task(name="Test", min_duration=1, mode_duration=2, max_duration=3)
        assert hasattr(t, "task_id"), "task_id is needed for dependency tracking"


# ============================================================================
# ITEM 5: export_results() should not run duplicate simulations
# ============================================================================


class TestExportResultsEfficiency:
    """Verify that export_results doesn't run simulations twice."""

    def test_export_results_simulation_count(self):
        """export_results should run simulations only once, not twice.

        # BEFORE: FAIL (runs 2n simulations)
        # AFTER: PASS (runs n simulations)

        This test uses mocking to count how many times estimate() is called.
        """
        import tempfile
        from unittest.mock import patch

        from monaco import Project, Task

        p = Project(name="Test")
        t = Task(name="Task", min_duration=1, mode_duration=2, max_duration=3)
        p.add_task(t)

        n = 50
        call_count = 0
        original_estimate = p.estimate

        def counting_estimate():
            nonlocal call_count
            call_count += 1
            return original_estimate()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as tmp:  # noqa: SIM117
            with patch.object(p, "estimate", side_effect=counting_estimate):
                p.export_results(n=n, format="json", output=tmp.name)

        # Should call estimate() exactly n times, not 2n
        assert call_count == n, (
            f"export_results called estimate() {call_count} times, "
            f"expected {n} (was running simulations twice)"
        )

    def test_export_results_still_works(self):
        """Regression: export_results should still produce correct output.

        # BEFORE: PASS, AFTER: PASS
        """
        import json
        import tempfile

        from monaco import Project, Task

        p = Project(name="Export Test")
        t = Task(name="Task", min_duration=1, mode_duration=2, max_duration=3)
        p.add_task(t)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        p.export_results(n=100, format="json", output=tmp_path)

        with open(tmp_path) as f:
            data = json.load(f)

        assert data["project_name"] == "Export Test"
        assert "statistics" in data
        assert "simulations" in data
        assert len(data["simulations"]) == 100


# ============================================================================
# ITEM 6: No-op .replace("P", "P") should be removed
# ============================================================================


class TestNoOpCodeRemoval:
    """Verify that meaningless code has been removed."""

    def test_no_noop_replace_in_cli(self):
        """CLI should not have the useless .replace('P', 'P') call.

        # BEFORE: FAIL (code exists)
        # AFTER: PASS (code removed)
        """
        import inspect

        from monaco import cli

        # Get the source code of cli module
        source = inspect.getsource(cli)

        assert (
            '.replace("P", "P")' not in source and ".replace('P', 'P')" not in source
        ), "Found useless .replace('P', 'P') in cli.py - this does nothing and should be removed"


# ============================================================================
# ITEM 7: __init__.py should use explicit imports
# ============================================================================


class TestCleanImports:
    """Verify that __init__.py uses clean, explicit imports."""

    def test_no_star_imports_in_init(self):
        """__init__.py should not use star imports.

        # BEFORE: FAIL (uses `from module import *`)
        # AFTER: PASS (uses explicit imports)
        """
        import os

        # Get path relative to this test file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        init_path = os.path.join(project_root, "src", "monaco", "__init__.py")
        with open(init_path) as f:
            content = f.read()

        assert "import *" not in content, (
            "__init__.py uses star imports (import *) which is discouraged. "
            "Use explicit imports instead."
        )

    def test_module_has_all_defined(self):
        """The monaco module should define __all__ for explicit exports.

        # BEFORE: FAIL (__all__ not defined)
        # AFTER: PASS (__all__ defined)
        """
        import monaco

        assert hasattr(
            monaco, "__all__"
        ), "monaco module should define __all__ to explicitly declare public API"

    def test_public_api_accessible(self):
        """Regression: All expected public classes should be importable.

        # BEFORE: PASS, AFTER: PASS
        """
        from monaco import (
            BetaDistribution,
            Distribution,
            LogNormalDistribution,
            NormalDistribution,
            PERTDistribution,
            Project,
            Task,
            TriangularDistribution,
            UniformDistribution,
        )

        # Just verify they're all importable
        assert Project is not None
        assert Task is not None
        assert Distribution is not None
        assert TriangularDistribution is not None
        assert UniformDistribution is not None
        assert NormalDistribution is not None
        assert PERTDistribution is not None
        assert LogNormalDistribution is not None
        assert BetaDistribution is not None


# ============================================================================
# ITEM 8: Test imports should be consistent
# ============================================================================


class TestTestImportConsistency:
    """Verify that test files use consistent imports."""

    def test_no_src_monaco_imports_in_tests(self):
        """Test files should import from 'monaco', not 'src.monaco'.

        # BEFORE: FAIL (test_task.py uses 'from src.monaco')
        # AFTER: PASS (all tests use 'from monaco')
        """
        import os

        # Get path relative to this test file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        issues = []

        # Pattern to search for (split to avoid self-detection)
        bad_import = "from " + "src.monaco"
        bad_import2 = "import " + "src.monaco"

        for filename in os.listdir(test_dir):
            if filename.startswith("test_") and filename.endswith(".py"):
                # Skip this file (it contains the patterns in string literals)
                if filename == "test_refactoring.py":
                    continue
                filepath = os.path.join(test_dir, filename)
                with open(filepath) as f:
                    content = f.read()
                if bad_import in content or bad_import2 in content:
                    issues.append(filename)

        assert not issues, (
            f"These test files use 'src.monaco' instead of 'monaco': {issues}. "
            "All test imports should use 'from monaco import ...' for consistency."
        )


# ============================================================================
# REGRESSION TESTS: Ensure core functionality still works
# ============================================================================


class TestCoreRegressions:
    """Ensure core functionality is preserved after refactoring."""

    def test_full_workflow(self):
        """Complete workflow should still work after refactoring.

        # BEFORE: PASS, AFTER: PASS
        """
        from monaco import PERTDistribution, Project, Task, TriangularDistribution

        # Create project
        project = Project(name="Regression Test", unit="days")

        # Create tasks with different distribution types
        design = Task(
            name="Design",
            distribution=TriangularDistribution(min_value=2, mode_value=3, max_value=5),
        )
        develop = Task(
            name="Develop",
            distribution=PERTDistribution(min_value=5, mode_value=8, max_value=15),
        )
        test_task = Task(name="Test", min_duration=2, mode_duration=3, max_duration=5)

        # Add tasks with dependencies
        project.add_task(design)
        project.add_task(develop, depends_on=[design])
        project.add_task(test_task, depends_on=[develop])

        # Single estimate
        estimate = project.estimate()
        assert isinstance(estimate, float)
        assert estimate > 0

        # Statistics
        stats = project.statistics(n=500)
        assert stats["n_simulations"] == 500
        assert stats["mean"] > 0
        assert stats["median"] > 0
        assert "p85" in stats["percentiles"]
        assert "p90" in stats["percentiles"]

        # Critical path analysis
        analysis = project.get_critical_path_analysis(n=100)
        assert "Design" in analysis
        assert "Develop" in analysis
        assert "Test" in analysis

    def test_config_loading_still_works(self):
        """Config loading should still work after refactoring.

        # BEFORE: PASS, AFTER: PASS
        """
        import os

        from monaco.config import build_project_from_config, load_config

        # Get path relative to this test file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(test_dir, "fixtures", "valid_project.yaml")
        config = load_config(config_path)
        project = build_project_from_config(config)

        assert project.name == "Test Project"
        assert len(project.tasks) == 3

        stats = project.statistics(n=100)
        assert stats["mean"] > 0

    def test_cli_commands_available(self):
        """CLI commands should still be available.

        # BEFORE: PASS, AFTER: PASS
        """
        from click.testing import CliRunner

        from monaco.cli import main

        runner = CliRunner()

        # Test help
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "stats" in result.output
        assert "plot" in result.output
        assert "init" in result.output


# ============================================================================
# SUMMARY: Quick check to see overall status
# ============================================================================


class TestRefactoringSummary:
    """Run this class alone to get a quick summary of refactoring status."""

    @pytest.mark.parametrize(
        "item,description",
        [
            ("inheritance", "Project does not inherit from Task"),
            ("simulate", "_simulate() method removed"),
            ("p_est", "p_est attribute removed"),
            ("cdate", "Task.cdate removed"),
            ("duplicate_sim", "export_results runs simulations once"),
            ("noop_replace", "No-op .replace() removed"),
            ("star_imports", "No star imports in __init__"),
            ("all_defined", "__all__ is defined"),
            ("test_imports", "Test imports are consistent"),
        ],
    )
    def test_refactoring_item(self, item, description):
        """Parameterized test to check each refactoring item."""
        # This test just serves as documentation
        # The actual tests are in the classes above
        pass
