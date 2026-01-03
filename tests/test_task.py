from datetime import datetime

import pytest

from monaco.distributions import (
    NormalDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from src.monaco import Task


def test_task_init():
    t1 = Task(
        name="write PRD",
        min_duration=2,
        mode_duration=4,
        max_duration=10,
    )

    t2 = Task(
        name="write PRD",
        min_duration=3,
        mode_duration=4,
        max_duration=5,
        estimator="uniform",
    )

    t3 = Task(
        name="write PRD",
        mode_duration=33,
        min_duration=30,
        max_duration=93,
        estimator="triangular",
    )

    assert t1.name == "write PRD"
    assert t1.min_duration == 2
    assert t1.mode_duration == 4
    assert t1.max_duration == 10
    assert t2.cdate.date() == datetime.now().date()
    assert t2.estimator == "uniform"
    assert t3.estimator == "triangular"


def test_task_invalid_estimator():
    with pytest.raises(ValueError):
        Task(estimator="mega")


def test_task_defaults():
    t1 = Task()
    assert not t1.name
    assert not t1.mode_duration
    assert not t1.min_duration
    assert not t1.max_duration
    assert t1.estimator == "triangular"


def test_task_estimate():
    t1 = Task(min_duration=1, mode_duration=2, max_duration=3, estimator="uniform")
    assert isinstance(t1.estimate(), float)
    t2 = Task(min_duration=1, mode_duration=2, max_duration=3, estimator="triangular")
    assert isinstance(t2.estimate(), float)


def test_task_validation_negative():
    """Test that negative durations raise ValueError"""
    with pytest.raises(ValueError):
        Task(min_duration=-1, mode_duration=2, max_duration=3)

    with pytest.raises(ValueError):
        Task(min_duration=1, mode_duration=-2, max_duration=3)

    with pytest.raises(ValueError):
        Task(min_duration=1, mode_duration=2, max_duration=-3)


def test_task_validation_ordering_triangular():
    """Test that triangular distribution validates min <= mode <= max"""
    with pytest.raises(ValueError):
        Task(min_duration=5, mode_duration=3, max_duration=10, estimator="triangular")

    with pytest.raises(ValueError):
        Task(min_duration=1, mode_duration=10, max_duration=5, estimator="triangular")

    with pytest.raises(ValueError):
        Task(min_duration=5, mode_duration=2, max_duration=3, estimator="triangular")


def test_task_validation_ordering_uniform():
    """Test that uniform distribution validates min <= max"""
    with pytest.raises(ValueError):
        Task(min_duration=10, max_duration=5, estimator="uniform")


# New tests for Distribution object support


def test_task_with_triangular_distribution():
    """Test creating Task with TriangularDistribution object."""
    dist = TriangularDistribution(1.0, 2.0, 3.0)
    task = Task(name="Test Task", distribution=dist)

    assert task.distribution == dist
    assert task.estimator == "triangular"
    assert task.min_duration == 1.0
    assert task.mode_duration == 2.0
    assert task.max_duration == 3.0
    assert 1.0 <= task.estimate() <= 3.0


def test_task_with_uniform_distribution():
    """Test creating Task with UniformDistribution object."""
    dist = UniformDistribution(2.0, 5.0)
    task = Task(name="Uniform Task", distribution=dist)

    assert task.distribution == dist
    assert task.estimator == "uniform"
    assert task.min_duration == 2.0
    assert task.max_duration == 5.0
    assert 2.0 <= task.estimate() <= 5.0


def test_task_with_normal_distribution():
    """Test creating Task with NormalDistribution object."""
    dist = NormalDistribution(mean=5.0, std_dev=1.0)
    task = Task(name="Normal Task", distribution=dist)

    assert task.distribution == dist
    assert task.estimator == "normal"
    sample = task.estimate()
    assert sample >= 0  # Truncated at 0


def test_task_with_normal_distribution_bounded():
    """Test Task with bounded NormalDistribution."""
    dist = NormalDistribution(mean=5.0, std_dev=1.0, min_value=3.0, max_value=7.0)
    task = Task(name="Bounded Normal", distribution=dist)

    for _ in range(50):
        sample = task.estimate()
        assert 3.0 <= sample <= 7.0


def test_task_distribution_overrides_legacy_params():
    """Test that distribution parameter overrides legacy params."""
    dist = UniformDistribution(10.0, 20.0)
    task = Task(
        name="Override Task",
        min_duration=1,  # Should be ignored
        max_duration=5,  # Should be ignored
        distribution=dist,
    )

    assert task.min_duration == 10.0
    assert task.max_duration == 20.0
    assert task.estimator == "uniform"


def test_task_backward_compatibility():
    """Test that legacy parameters still work correctly."""
    task = Task(
        name="Legacy Task",
        min_duration=1,
        mode_duration=2,
        max_duration=3,
        estimator="triangular",
    )

    assert task.min_duration == 1
    assert task.mode_duration == 2
    assert task.max_duration == 3
    assert task.estimator == "triangular"
    assert task.distribution is not None
    assert isinstance(task.distribution, TriangularDistribution)


def test_task_normal_estimator_string():
    """Test that 'normal' is now a valid estimator string."""
    # Note: This should not raise since 'normal' is valid
    # But we can't use legacy params with normal estimator
    task = Task(name="Normal via string", estimator="normal")
    assert task.estimator == "normal"
    # Distribution is None since no params provided
    assert task.distribution is None
