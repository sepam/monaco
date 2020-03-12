from datetime import datetime
from monaco import Task
import pytest


def test_task_init():
    t1 = Task(name="write PRD",
              due_date='2020-01-25',
              median='2020-01-20',
              min='2020-01-10',
              max='2020-01-30',
              )

    t2 = Task(name="write PRD",
              due_date='2020-01-25',
              median='2020-01-20',
              min='2020-01-10',
              max='2020-01-30',
              estimator='uniform'
              )

    t3 = Task(name="write PRD",
              due_date='2020-01-25',
              median='2020-01-20',
              min='2020-01-10',
              max='2020-01-30',
              estimator='triangular'
              )


    assert t1.name == "write PRD"
    assert t1.due_date == "2020-01-25"
    assert t1.min == '2020-01-10'
    assert t1.median == "2020-01-20"
    assert t1.max == "2020-01-30"
    assert t1.depends_on == []

    t2.depends_on.append(t1)
    assert t2.depends_on == [t1]
    assert t2.cdate.date() == datetime.now().date()
    assert t2.estimator == 'uniform'

    t3.depends_on.append(t1)
    assert t3.estimator == 'triangular'


def test_task_invalid_estimator():
    with pytest.raises(Exception):
        Task(estimator='mega')


def test_task_defaults():
    t1 = Task()
    assert not t1.name
    assert not t1.due_date
    assert not t1.median
    assert not t1.min
    assert not t1.max
    assert t1.estimator == 'triangular'
    assert t1.depends_on == []


def test_task_estimate():
    t1 = Task(min=1, median=2, max=3, estimator='uniform')
    assert type(t1.estimate()) == float
    t2 = Task(min=1, median=2, max=3, estimator='triangular')
    assert type(t1.estimate()) == float
