from collections import Counter

import pytest

from monaco import Project, Task


def test_project_init_default():
    p1 = Project()
    assert not p1.name
    assert isinstance(p1.tasks, list)


def test_project_init_params():
    t1 = Task()
    t2 = Task()
    p2 = Project(name="Experiment")
    p2.add_task(t1)
    p2.add_task(t2)
    assert len(p2.tasks) == 2
    assert p2.name == "Experiment"


def test_project_add_one_task():
    t = Task(name="example")
    p = Project()
    p.add_task(t)
    assert len(p.tasks) == 1
    assert p.tasks[0].name == "example"


def test_project_add_two_task():
    p = Project()
    t1 = Task(name="example")
    t2 = Task(name="example2")
    p.add_task(t1)
    p.add_task(t2)
    assert len(p.tasks) == 2
    assert p.tasks[0].name == "example"
    assert p.tasks[1].name == "example2"


def test_project_estimate():
    t1 = Task(name="Analysis", min_duration=2, mode_duration=3, max_duration=7)
    t2 = Task(name="Experiment", min_duration=30, mode_duration=35, max_duration=40)
    p = Project(name="High Score Bypass")
    p.add_task(t1)
    p.add_task(t2)
    est = p.estimate()
    assert p.p_est
    assert est > 7
    assert isinstance(est, float)


def test_project_simulate(n=1000):
    t1 = Task(name="Analysis", min_duration=2, mode_duration=3, max_duration=7)
    t2 = Task(name="Experiment", min_duration=30, mode_duration=35, max_duration=40)
    p = Project(name="High Score Bypass")
    p.add_task(t1)
    p.add_task(t2)
    sim_runs = p._simulate(n=n)
    assert isinstance(sim_runs, Counter)


def test_plot_hist(n=100):
    """Test histogram plot with save to file"""
    import os
    import tempfile

    t1 = Task(
        name="Analysis",
        min_duration=2,
        mode_duration=3,
        max_duration=7,
        estimator="triangular",
    )
    t2 = Task(
        name="Experiment",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    t3 = Task(
        name="Evaluation",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    t4 = Task(
        name="Monitoring",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    p = Project(name="High Score Bypass")
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    p.add_task(t4)

    # Save to temp file to avoid showing plot in tests
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        fig = p.plot(n=n, save_path=tmp_path)
        assert os.path.exists(tmp_path)
        assert fig is not None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_plot_cumul(n=100):
    """Test cumulative distribution plot with save to file"""
    import os
    import tempfile

    t1 = Task(
        name="Analysis",
        min_duration=2,
        mode_duration=3,
        max_duration=7,
        estimator="triangular",
    )
    t2 = Task(
        name="Experiment",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    t3 = Task(
        name="Evaluation",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    t4 = Task(
        name="Monitoring",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    p = Project(name="High Score Bypass")
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    p.add_task(t4)

    # Save to temp file to avoid showing plot in tests
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        fig = p.plot(hist=False, n=n, save_path=tmp_path)
        assert os.path.exists(tmp_path)
        assert fig is not None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_statistics():
    """Test statistics() method"""
    t1 = Task(
        name="Analysis",
        min_duration=2,
        mode_duration=3,
        max_duration=7,
        estimator="triangular",
    )
    t2 = Task(
        name="Experiment",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    p = Project(name="Test Project")
    p.add_task(t1)
    p.add_task(t2)

    stats = p.statistics(n=1000)

    # Check structure
    assert "n_simulations" in stats
    assert "mean" in stats
    assert "median" in stats
    assert "std_dev" in stats
    assert "min" in stats
    assert "max" in stats
    assert "percentiles" in stats
    assert "confidence_intervals" in stats

    # Check values
    assert stats["n_simulations"] == 1000
    assert stats["mean"] > 0
    assert stats["median"] > 0
    assert stats["std_dev"] > 0
    assert stats["min"] > 0
    assert stats["max"] > stats["min"]

    # Check percentiles
    assert "p10" in stats["percentiles"]
    assert "p50" in stats["percentiles"]
    assert "p85" in stats["percentiles"]
    assert "p90" in stats["percentiles"]
    assert "p95" in stats["percentiles"]

    # Check percentile ordering
    assert stats["percentiles"]["p10"] <= stats["percentiles"]["p50"]
    assert stats["percentiles"]["p50"] <= stats["percentiles"]["p85"]
    assert stats["percentiles"]["p85"] <= stats["percentiles"]["p90"]
    assert stats["percentiles"]["p90"] <= stats["percentiles"]["p95"]

    # Check confidence intervals
    assert "95%" in stats["confidence_intervals"]
    assert len(stats["confidence_intervals"]["95%"]) == 2
    assert (
        stats["confidence_intervals"]["95%"][0]
        < stats["confidence_intervals"]["95%"][1]
    )


def test_export_results_json():
    """Test export_results() method with JSON format"""
    import json
    import os
    import tempfile

    t1 = Task(
        name="Task1",
        min_duration=1,
        mode_duration=2,
        max_duration=3,
        estimator="triangular",
    )
    p = Project(name="Export Test")
    p.add_task(t1)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        p.export_results(n=100, format="json", output=tmp_path)
        assert os.path.exists(tmp_path)

        # Load and verify JSON content
        with open(tmp_path) as f:
            data = json.load(f)

        assert "project_name" in data
        assert data["project_name"] == "Export Test"
        assert "statistics" in data
        assert "simulations" in data
        assert len(data["simulations"]) == 100
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_export_results_csv():
    """Test export_results() method with CSV format"""
    import os
    import tempfile

    t1 = Task(
        name="Task1",
        min_duration=1,
        mode_duration=2,
        max_duration=3,
        estimator="triangular",
    )
    p = Project(name="CSV Test")
    p.add_task(t1)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        p.export_results(n=100, format="csv", output=tmp_path)
        assert os.path.exists(tmp_path)

        # Verify CSV content
        with open(tmp_path) as f:
            content = f.read()
            assert "CSV Test" in content
            assert "Mean" in content
            assert "Median" in content
            assert "Simulation Results" in content
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_export_results_invalid_format():
    """Test export_results() raises error for invalid format"""
    t1 = Task(name="Task1", min_duration=1, mode_duration=2, max_duration=3)
    p = Project(name="Invalid Format Test")
    p.add_task(t1)

    with pytest.raises(ValueError):
        p.export_results(n=100, format="xml", output="test.xml")


def test_plot_with_percentiles():
    """Test plot() method with percentile markers"""
    import os
    import tempfile

    t1 = Task(
        name="Analysis",
        min_duration=2,
        mode_duration=3,
        max_duration=7,
        estimator="triangular",
    )
    t2 = Task(
        name="Experiment",
        min_duration=30,
        mode_duration=35,
        max_duration=40,
        estimator="triangular",
    )
    p = Project(name="Percentile Test")
    p.add_task(t1)
    p.add_task(t2)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        fig = p.plot(
            n=100, show_percentiles=True, percentiles=[50, 85, 95], save_path=tmp_path
        )
        assert os.path.exists(tmp_path)
        assert fig is not None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ============================================================================
# Task Dependency Tests
# ============================================================================


def test_task_has_unique_id():
    """Test that tasks get unique IDs"""
    t1 = Task(name="Task1", min_duration=1, mode_duration=2, max_duration=3)
    t2 = Task(name="Task2", min_duration=1, mode_duration=2, max_duration=3)

    assert hasattr(t1, "task_id")
    assert hasattr(t2, "task_id")
    assert t1.task_id != t2.task_id


def test_parallel_tasks():
    """Test that parallel tasks use max() time, not sum()"""
    # Backend and frontend can run in parallel
    backend = Task(name="Backend", min_duration=10, mode_duration=10, max_duration=10)
    frontend = Task(name="Frontend", min_duration=8, mode_duration=8, max_duration=8)
    integration = Task(
        name="Integration", min_duration=2, mode_duration=2, max_duration=2
    )

    p = Project(name="Parallel Test")
    p.add_task(backend)
    p.add_task(frontend)
    p.add_task(integration, depends_on=[backend, frontend])

    # Should be max(10, 8) + 2 = 12, not 10 + 8 + 2 = 20
    est = p.estimate()
    assert est == 12.0, f"Expected 12.0, got {est}"


def test_sequential_dependencies():
    """Test that sequential dependencies sum correctly"""
    t1 = Task(name="Task1", min_duration=5, mode_duration=5, max_duration=5)
    t2 = Task(name="Task2", min_duration=3, mode_duration=3, max_duration=3)
    t3 = Task(name="Task3", min_duration=2, mode_duration=2, max_duration=2)

    p = Project(name="Sequential Test")
    p.add_task(t1)
    p.add_task(t2, depends_on=[t1])
    p.add_task(t3, depends_on=[t2])

    est = p.estimate()
    assert est == 10.0, f"Expected 10.0 (5+3+2), got {est}"


def test_complex_dependency_graph():
    """Test complex dependency graph with multiple paths"""
    #     ┌─ B(5) ─┐
    # A(2)┤        ├─ D(3)
    #     └─ C(8) ─┘
    # Should be: A + max(B, C) + D = 2 + 8 + 3 = 13

    a = Task(name="A", min_duration=2, mode_duration=2, max_duration=2)
    b = Task(name="B", min_duration=5, mode_duration=5, max_duration=5)
    c = Task(name="C", min_duration=8, mode_duration=8, max_duration=8)
    d = Task(name="D", min_duration=3, mode_duration=3, max_duration=3)

    p = Project(name="Complex Test")
    p.add_task(a)
    p.add_task(b, depends_on=[a])
    p.add_task(c, depends_on=[a])
    p.add_task(d, depends_on=[b, c])

    est = p.estimate()
    assert est == 13.0, f"Expected 13.0 (2+8+3), got {est}"


def test_circular_dependency_detection():
    """Test that circular dependencies are detected"""
    t1 = Task(name="Task1", min_duration=1, mode_duration=2, max_duration=3)
    t2 = Task(name="Task2", min_duration=1, mode_duration=2, max_duration=3)
    t3 = Task(name="Task3", min_duration=1, mode_duration=2, max_duration=3)

    p = Project(name="Circular Test")
    p.add_task(t1)
    p.add_task(t2, depends_on=[t1])

    # Create a cycle: t1 -> t2 -> t3 -> t1
    with pytest.raises(ValueError, match="Circular dependency"):
        p.add_task(t3, depends_on=[t2])
        # Manually create cycle for testing
        p.dependencies[t1.task_id] = [t3.task_id]
        p._validate_dag()


def test_invalid_dependency_not_in_project():
    """Test that dependencies must be added to project first"""
    t1 = Task(name="Task1", min_duration=1, mode_duration=2, max_duration=3)
    t2 = Task(name="Task2", min_duration=1, mode_duration=2, max_duration=3)

    p = Project(name="Invalid Dep Test")
    # Try to add t2 with dependency on t1, but t1 not in project yet
    with pytest.raises(ValueError, match="must be added to the project before"):
        p.add_task(t2, depends_on=[t1])


def test_backward_compat_no_dependencies():
    """Test that projects without dependencies work as before (simple sum)"""
    t1 = Task(name="Task1", min_duration=5, mode_duration=5, max_duration=5)
    t2 = Task(name="Task2", min_duration=3, mode_duration=3, max_duration=3)
    t3 = Task(name="Task3", min_duration=2, mode_duration=2, max_duration=2)

    p = Project(name="Linear Test")
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)

    # No dependencies specified - should sum all tasks
    est = p.estimate()
    assert est == 10.0, f"Expected 10.0 (5+3+2), got {est}"


def test_tasks_property_backward_compat():
    """Test that p.tasks still works as a list for backward compatibility"""
    t1 = Task(name="Task1", min_duration=1, mode_duration=2, max_duration=3)
    t2 = Task(name="Task2", min_duration=1, mode_duration=2, max_duration=3)

    p = Project(name="Property Test")
    p.add_task(t1)
    p.add_task(t2)

    # Should work like a list
    assert len(p.tasks) == 2
    assert p.tasks[0].name == "Task1"
    assert p.tasks[1].name == "Task2"


def test_statistics_with_dependencies():
    """Test that statistics() works correctly with dependencies"""
    backend = Task(name="Backend", min_duration=10, mode_duration=15, max_duration=20)
    frontend = Task(name="Frontend", min_duration=8, mode_duration=12, max_duration=15)
    integration = Task(
        name="Integration", min_duration=2, mode_duration=3, max_duration=5
    )

    p = Project(name="Stats Dep Test")
    p.add_task(backend)
    p.add_task(frontend)
    p.add_task(integration, depends_on=[backend, frontend])

    stats = p.statistics(n=1000)

    # Should have reasonable mean around max(backend, frontend) + integration
    # Rough estimate: max(15, 12) + 3 = 18
    assert stats["mean"] > 15  # Should be more than just integration
    assert stats["mean"] < 30  # Should be less than sum of all
    assert stats["median"] > 15
    assert stats["median"] < 30
