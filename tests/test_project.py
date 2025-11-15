from monaco import Task
from monaco import Project
from collections import Counter
import pytest


def test_project_init_default():
    p1 = Project()
    assert not p1.name
    assert type(p1.tasks) == list


def test_project_init_params():
    t1 = Task()
    t2 = Task()
    p2 = Project(name='Experiment')
    p2.add_task(t1)
    p2.add_task(t2)
    assert len(p2.tasks) == 2
    assert p2.name == 'Experiment'


def test_project_add_one_task():
    t = Task(name='example')
    p = Project()
    p.add_task(t)
    assert len(p.tasks) == 1
    assert p.tasks[0].name == 'example'


def test_project_add_two_task():
    p = Project()
    t1 = Task(name='example')
    t2 = Task(name='example2')
    p.add_task(t1)
    p.add_task(t2)
    assert len(p.tasks) == 2
    assert p.tasks[0].name == 'example'
    assert p.tasks[1].name == 'example2'


def test_project_estimate():
    t1 = Task(name='Analysis', min_duration=2, mode_duration=3, max_duration=7)
    t2 = Task(name='Experiment', min_duration=30, mode_duration=35, max_duration=40)
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    est = p.estimate()
    assert p.p_est
    assert est > 7
    assert type(est) == float


def test_project_simulate(n=1000):
    t1 = Task(name='Analysis', min_duration=2, mode_duration=3, max_duration=7)
    t2 = Task(name='Experiment', min_duration=30, mode_duration=35, max_duration=40)
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    sim_runs = p._simulate(n=n)
    assert type(sim_runs) == Counter


def test_plot_hist(n=100):
    """Test histogram plot with save to file"""
    import tempfile
    import os

    t1 = Task(name='Analysis', min_duration=2, mode_duration=3, max_duration=7, estimator='triangular')
    t2 = Task(name='Experiment', min_duration=30, mode_duration=35, max_duration=40, estimator='triangular')
    t3 = Task(name='Evaluation', min_duration=30, mode_duration=35, max_duration=40, estimator='triangular')
    t4 = Task(name='Monitoring', min_duration=30, mode_duration=35, max_duration=40, estimator='triangular')
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    p.add_task(t4)

    # Save to temp file to avoid showing plot in tests
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
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
    import tempfile
    import os

    t1 = Task(name='Analysis', min_duration=2, mode_duration=3, max_duration=7, estimator='triangular')
    t2 = Task(name='Experiment', min_duration=30, mode_duration=35, max_duration=40, estimator='triangular')
    t3 = Task(name='Evaluation', min_duration=30, mode_duration=35, max_duration=40, estimator='triangular')
    t4 = Task(name='Monitoring', min_duration=30, mode_duration=35, max_duration=40, estimator='triangular')
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    p.add_task(t4)

    # Save to temp file to avoid showing plot in tests
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        fig = p.plot(hist=False, n=n, save_path=tmp_path)
        assert os.path.exists(tmp_path)
        assert fig is not None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
