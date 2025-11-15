from datetime import datetime
from src.monaco import Task
import pytest


def test_task_init():
    t1 = Task(name="write PRD",
              min_duration=2,
              mode_duration=4,
              max_duration=10,
              )

    t2 = Task(name="write PRD",
              min_duration=3,
              mode_duration=4,
              max_duration=5,
              estimator='uniform'
              )

    t3 = Task(name="write PRD",
              mode_duration=33,
              min_duration=30,
              max_duration=93,
              estimator='triangular'
              )

    assert t1.name == "write PRD"
    assert t1.min_duration == 2
    assert t1.mode_duration == 4
    assert t1.max_duration == 10
    assert t2.cdate.date() == datetime.now().date()
    assert t2.estimator == 'uniform'
    assert t3.estimator == 'triangular'


def test_task_invalid_estimator():
    with pytest.raises(ValueError):
        Task(estimator='mega')


def test_task_defaults():
    t1 = Task()
    assert not t1.name
    assert not t1.mode_duration
    assert not t1.min_duration
    assert not t1.max_duration
    assert t1.estimator == 'triangular'


def test_task_estimate():
    t1 = Task(min_duration=1, mode_duration=2, max_duration=3, estimator='uniform')
    assert type(t1.estimate()) == float
    t2 = Task(min_duration=1, mode_duration=2, max_duration=3, estimator='triangular')
    assert type(t2.estimate()) == float


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
        Task(min_duration=5, mode_duration=3, max_duration=10, estimator='triangular')

    with pytest.raises(ValueError):
        Task(min_duration=1, mode_duration=10, max_duration=5, estimator='triangular')

    with pytest.raises(ValueError):
        Task(min_duration=5, mode_duration=2, max_duration=3, estimator='triangular')


def test_task_validation_ordering_uniform():
    """Test that uniform distribution validates min <= max"""
    with pytest.raises(ValueError):
        Task(min_duration=10, max_duration=5, estimator='uniform')
