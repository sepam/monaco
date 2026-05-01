import pytest

from planaco import Project, Task


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
    assert est > 7
    assert isinstance(est, float)


def test_project_run_simulation(n=1000):
    t1 = Task(name="Analysis", min_duration=2, mode_duration=3, max_duration=7)
    t2 = Task(name="Experiment", min_duration=30, mode_duration=35, max_duration=40)
    p = Project(name="High Score Bypass")
    p.add_task(t1)
    p.add_task(t2)
    sim_runs = p._run_simulation(n=n)
    assert isinstance(sim_runs, list)
    assert len(sim_runs) == n


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


# ============================================================================
# Critical Path Analysis Tests
# ============================================================================


def test_critical_path_simple_sequential():
    """All tasks in a sequential chain should be 100% critical"""
    task1 = Task(name="Task1", min_duration=5, mode_duration=5, max_duration=5)
    task2 = Task(name="Task2", min_duration=3, mode_duration=3, max_duration=3)
    task3 = Task(name="Task3", min_duration=2, mode_duration=2, max_duration=2)

    p = Project(name="Sequential")
    p.add_task(task1)
    p.add_task(task2, depends_on=[task1])
    p.add_task(task3, depends_on=[task2])

    analysis = p.get_critical_path_analysis(n=100, seed=42)

    # All tasks should be 100% critical in a sequential chain
    assert analysis["Task1"]["frequency"] == 1.0
    assert analysis["Task2"]["frequency"] == 1.0
    assert analysis["Task3"]["frequency"] == 1.0


def test_critical_path_parallel_branches_longer_wins():
    """The longer parallel branch should be critical more often"""
    # Short branch: 5 days fixed
    short = Task(name="Short", min_duration=5, mode_duration=5, max_duration=5)
    # Long branch: 10 days fixed
    long_task = Task(name="Long", min_duration=10, mode_duration=10, max_duration=10)
    # Final task depends on both
    final = Task(name="Final", min_duration=1, mode_duration=1, max_duration=1)

    p = Project(name="Parallel")
    p.add_task(short)
    p.add_task(long_task)
    p.add_task(final, depends_on=[short, long_task])

    analysis = p.get_critical_path_analysis(n=100, seed=42)

    # Long task should always be critical (it's always longer)
    assert analysis["Long"]["frequency"] == 1.0
    # Short task should never be critical
    assert analysis["Short"]["frequency"] == 0.0
    # Final task is always on critical path
    assert analysis["Final"]["frequency"] == 1.0


def test_critical_path_equal_parallel_branches():
    """Equal parallel branches should each be critical ~50% of the time"""
    # Two branches with same distribution
    branch_a = Task(name="BranchA", min_duration=5, mode_duration=10, max_duration=15)
    branch_b = Task(name="BranchB", min_duration=5, mode_duration=10, max_duration=15)
    final = Task(name="Final", min_duration=1, mode_duration=1, max_duration=1)

    p = Project(name="Equal Parallel")
    p.add_task(branch_a)
    p.add_task(branch_b)
    p.add_task(final, depends_on=[branch_a, branch_b])

    analysis = p.get_critical_path_analysis(n=1000, seed=42)

    # Both branches should be critical roughly 50% of the time
    # Allow some variance due to randomness
    assert 0.3 < analysis["BranchA"]["frequency"] < 0.7
    assert 0.3 < analysis["BranchB"]["frequency"] < 0.7
    # Final task is always critical
    assert analysis["Final"]["frequency"] == 1.0


def test_critical_path_no_dependencies():
    """Without dependencies, all tasks are 'critical' (backward compat mode)"""
    task1 = Task(name="Task1", min_duration=5, mode_duration=5, max_duration=5)
    task2 = Task(name="Task2", min_duration=3, mode_duration=3, max_duration=3)

    p = Project(name="No Deps")
    p.add_task(task1)
    p.add_task(task2)

    analysis = p.get_critical_path_analysis(n=100, seed=42)

    # All tasks should be 100% critical when no dependencies
    assert analysis["Task1"]["frequency"] == 1.0
    assert analysis["Task2"]["frequency"] == 1.0


def test_critical_path_analysis_returns_correct_structure():
    """Verify the structure of returned analysis data"""
    task = Task(name="MyTask", min_duration=5, mode_duration=5, max_duration=5)

    p = Project(name="Structure Test")
    p.add_task(task)

    analysis = p.get_critical_path_analysis(n=10, seed=42)

    assert "MyTask" in analysis
    assert "task_id" in analysis["MyTask"]
    assert "count" in analysis["MyTask"]
    assert "frequency" in analysis["MyTask"]
    assert analysis["MyTask"]["count"] == 10
    assert analysis["MyTask"]["frequency"] == 1.0


def test_critical_path_complex_dag():
    """Test a more complex DAG structure"""
    #       A (2)
    #      / \
    #   B(5)  C(8)
    #      \ /
    #      D(3)
    a = Task(name="A", min_duration=2, mode_duration=2, max_duration=2)
    b = Task(name="B", min_duration=5, mode_duration=5, max_duration=5)
    c = Task(name="C", min_duration=8, mode_duration=8, max_duration=8)
    d = Task(name="D", min_duration=3, mode_duration=3, max_duration=3)

    p = Project(name="Complex DAG")
    p.add_task(a)
    p.add_task(b, depends_on=[a])
    p.add_task(c, depends_on=[a])
    p.add_task(d, depends_on=[b, c])

    analysis = p.get_critical_path_analysis(n=100, seed=42)

    # A, C, D should be critical (A->C->D is longest path = 2+8+3 = 13)
    # B is not critical (A->B->D = 2+5+3 = 10)
    assert analysis["A"]["frequency"] == 1.0
    assert analysis["C"]["frequency"] == 1.0
    assert analysis["D"]["frequency"] == 1.0
    assert analysis["B"]["frequency"] == 0.0


def test_plot_dependency_graph_with_criticality(tmp_path):
    """Test that plot_dependency_graph works with criticality coloring"""
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend for testing

    task1 = Task(name="Task1", min_duration=5, mode_duration=5, max_duration=5)
    task2 = Task(name="Task2", min_duration=3, mode_duration=3, max_duration=3)

    p = Project(name="Plot Test")
    p.add_task(task1)
    p.add_task(task2, depends_on=[task1])

    # Test with criticality
    save_path = tmp_path / "graph_criticality.png"
    fig = p.plot_dependency_graph(
        save_path=str(save_path),
        show_criticality=True,
        criticality_n=100,
        criticality_seed=42,
    )

    assert save_path.exists()
    assert fig is not None


# ============================================================================
# Project-level statistical correctness
# ============================================================================
#
# These tests verify that Monte Carlo simulation produces results that match
# analytical expectations for known distributions and dependency graphs. They
# guard against regressions in _calculate_critical_path, _run_simulation,
# and _compute_statistics.
# ----------------------------------------------------------------------------


def test_sequential_sum_matches_analytical_mean():
    """Two sequential uniform(0, 10) tasks: E[total] = 10.0

    No dependencies declared, so Project falls back to simple-sum mode.
    """
    import random

    random.seed(42)
    from planaco.distributions import UniformDistribution

    p = Project(name="Sequential Mean")
    p.add_task(Task(name="A", distribution=UniformDistribution(0.0, 10.0)))
    p.add_task(Task(name="B", distribution=UniformDistribution(0.0, 10.0)))

    stats = p.statistics(n=20000)
    # E[U(0,10) + U(0,10)] = 10.0; std ≈ sqrt(2 * 100/12) ≈ 4.08
    assert 9.8 <= stats["mean"] <= 10.2
    assert stats["min"] >= 0.0
    assert stats["max"] <= 20.0


def test_parallel_max_matches_analytical_mean():
    """Diamond with parallel uniform(0, 1) middle tasks.

    start -> {a, b} -> end, where start = end = 0 durations is not
    possible (min >= 0 is enforced but a deterministic "1.0 duration"
    task works). With start = 0, end = 0 we just measure max(a, b).
    Here we use fixed start/end durations and verify the parallel max.

    For U(0, 1), E[max(a, b)] = 2/3.
    """
    import random

    random.seed(123)
    from planaco.distributions import UniformDistribution

    p = Project(name="Parallel Max")
    start = Task(name="S", distribution=UniformDistribution(0.0, 0.0))
    a = Task(name="A", distribution=UniformDistribution(0.0, 1.0))
    b = Task(name="B", distribution=UniformDistribution(0.0, 1.0))
    end = Task(name="E", distribution=UniformDistribution(0.0, 0.0))

    p.add_task(start)
    p.add_task(a, depends_on=[start])
    p.add_task(b, depends_on=[start])
    p.add_task(end, depends_on=[a, b])

    stats = p.statistics(n=20000)
    # E[max(U(0,1), U(0,1))] = 2/3 ≈ 0.6667
    assert 0.64 <= stats["mean"] <= 0.70


def test_percentiles_are_monotonic():
    """P10 <= median <= P85 <= P90 <= P95 must always hold."""
    import random

    random.seed(7)
    p = Project(name="Monotonic")
    p.add_task(Task(name="X", min_duration=1, mode_duration=5, max_duration=20))
    stats = p.statistics(n=5000)
    pcts = stats["percentiles"]
    assert pcts["p10"] <= stats["median"] <= pcts["p85"] <= pcts["p90"] <= pcts["p95"]
    assert stats["min"] <= pcts["p10"]
    assert pcts["p95"] <= stats["max"]


def test_statistics_reproducibility_with_seed():
    """Seeding the same starting state must produce identical stats dicts."""
    import random

    p = Project(name="Seeded")
    p.add_task(Task(name="X", min_duration=1, mode_duration=2, max_duration=5))
    p.add_task(Task(name="Y", min_duration=2, mode_duration=3, max_duration=6))

    random.seed(999)
    stats1 = p.statistics(n=2000)
    random.seed(999)
    stats2 = p.statistics(n=2000)

    assert stats1 == stats2


def test_json_export_round_trips_with_statistics():
    """JSON export must contain the exact statistics that statistics() returns
    for the same simulation count.

    Note: export_results runs its own simulation internally; with identical
    seeds before each call the two runs should produce the same numbers.
    """
    import json
    import random
    import tempfile

    p = Project(name="Export Integrity", unit="days")
    p.add_task(Task(name="X", min_duration=1, mode_duration=2, max_duration=3))
    p.add_task(Task(name="Y", min_duration=2, mode_duration=3, max_duration=4))

    random.seed(314)
    stats_ref = p.statistics(n=1000)

    random.seed(314)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        out_path = f.name
    p.export_results(n=1000, format="json", output=out_path)

    with open(out_path) as f:
        exported = json.load(f)

    assert exported["project_name"] == "Export Integrity"
    assert exported["unit"] == "days"
    assert len(exported["simulations"]) == 1000

    # Compare numerically (JSON round-trips tuples as lists, so we can't
    # use a direct dict equality check on the full stats dict).
    stats_exported = exported["statistics"]
    for key in ("mean", "median", "std_dev", "min", "max", "n_simulations"):
        assert stats_exported[key] == stats_ref[key]
    for pkey in ("p10", "p50", "p85", "p90", "p95"):
        assert stats_exported["percentiles"][pkey] == stats_ref["percentiles"][pkey]
    ci_exp = stats_exported["confidence_intervals"]["95%"]
    ci_ref = stats_ref["confidence_intervals"]["95%"]
    assert list(ci_exp) == list(ci_ref)


def test_csv_export_simulation_row_count():
    """CSV export must contain exactly n simulation data rows."""
    import csv
    import tempfile

    p = Project(name="CSV rows")
    p.add_task(Task(name="X", min_duration=1, mode_duration=2, max_duration=3))

    n = 500
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        out_path = f.name
    p.export_results(n=n, format="csv", output=out_path)

    with open(out_path) as f:
        rows = list(csv.reader(f))

    # Find the "Run","Duration" header and count rows after it
    header_idx = next(
        i for i, r in enumerate(rows) if r and r[0] == "Run" and r[1] == "Duration"
    )
    data_rows = [r for r in rows[header_idx + 1 :] if r]
    assert len(data_rows) == n


def test_critical_path_analysis_deterministic_under_python_random_seed():
    """Running critical path analysis twice after identical random.seed calls
    yields identical frequencies.

    Note: `get_critical_path_analysis`'s own `seed=` parameter only seeds
    numpy, but the Distribution classes sample via Python's `random` module.
    So to get determinism we seed `random` explicitly before each call.
    """
    import random

    p = Project(name="CP determinism")
    a = Task(name="A", min_duration=1, mode_duration=2, max_duration=5)
    b = Task(name="B", min_duration=1, mode_duration=3, max_duration=6)
    c = Task(name="C", min_duration=1, mode_duration=2, max_duration=4)
    p.add_task(a)
    p.add_task(b, depends_on=[a])
    p.add_task(c, depends_on=[a])

    random.seed(2024)
    first = p.get_critical_path_analysis(n=500)
    random.seed(2024)
    second = p.get_critical_path_analysis(n=500)

    for name in first:
        assert first[name]["count"] == second[name]["count"]
        assert first[name]["frequency"] == second[name]["frequency"]


def test_empty_project_estimate_returns_zero():
    """A project with no tasks must estimate 0 without crashing."""
    p = Project(name="Empty")
    assert p.estimate() == 0.0
