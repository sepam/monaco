import pytest
from datetime import datetime
from monaco.tasks import Task


def test_task_init():
    t1 = Task(text="write PRD",
              due_date='2020-01-25',
              est_done='2020-01-20',
              est_min='2020-01-10',
              est_max='2020-01-30',
              )

    t2 = Task(text="write PRD",
              due_date='2020-01-25',
              est_done='2020-01-20',
              est_min='2020-01-10',
              est_max='2020-01-30',
              depends_on=[t1]
              )

    assert t1.text == "write PRD"
    assert t1.due_date == "2020-01-25"
    assert t1.est_done == "2020-01-20"
    assert t1.est_min == '2020-01-10'
    assert t1.est_max == "2020-01-30"
    assert t1.depends_on == []

    assert t2.depends_on == [t1]

    assert t2.cdate.date() == datetime.now().date()


def test_task_defaults():
    t1 = Task()
    assert not t1.text
    assert not t1.due_date
    assert not t1.est_done
    assert not t1.est_min
    assert not t1.est_max
    assert t1.depends_on == []



def test_task_estimate():
    t1 = Task(est_min=1, est_done=2, est_max=3)
    assert type(t1.estimate()) == float