import pytest
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




