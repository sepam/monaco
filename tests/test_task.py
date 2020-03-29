from datetime import datetime
from src.monaco import Task
import pytest


def test_task_init():
    t1 = Task(name="write PRD",
              min=2,
              mode=4,
              max=10,
              )

    t2 = Task(name="write PRD",
              min=3,
              mode=4,
              max=5,
              estimator='uniform'
              )

    t3 = Task(name="write PRD",
              mode=33,
              min=63,
              max=93,
              estimator='triangular'
              )

    assert t1.name == "write PRD"
    assert t1.min == 2
    assert t1.mode == 4
    assert t1.max == 10
    assert t2.cdate.date() == datetime.now().date()
    assert t2.estimator == 'uniform'
    assert t3.estimator == 'triangular'


def test_task_invalid_estimator():
    with pytest.raises(Exception):
        Task(estimator='mega')


def test_task_defaults():
    t1 = Task()
    assert not t1.name
    assert not t1.mode
    assert not t1.min
    assert not t1.max
    assert t1.estimator == 'triangular'


def test_task_estimate():
    t1 = Task(min=1, mode=2, max=3, estimator='uniform')
    assert type(t1.estimate()) == float
    t2 = Task(min=1, mode=2, max=3, estimator='triangular')
    assert type(t2.estimate()) == float
