from monaco import Task
from monaco import Project
from collections import Counter
import matplotlib.pyplot as plt


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
    return


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
    t1 = Task(name='Analysis', est_min=2, est_nom=3, est_max=7)
    t2 = Task(name='Experiment', est_min=30, est_nom=35, est_max=40)
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    est = p.estimate()
    assert p.p_est
    assert est > 7
    assert type(est) == int


def test_project_simulate():
    t1 = Task(name='Analysis', est_min=2, est_nom=3, est_max=7)
    t2 = Task(name='Experiment', est_min=30, est_nom=35, est_max=40)
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    sim_runs = p._simulate(n=100)
    assert type(sim_runs) == Counter


def test_plot_hist():
    t1 = Task(name='Analysis', est_min=2, est_nom=3, est_max=7, estimator='triangular')
    t2 = Task(name='Experiment', est_min=30, est_nom=35, est_max=40, estimator='triangular')
    t3 = Task(name='Evaluation', est_min=30, est_nom=35, est_max=40, estimator='triangular')
    t4 = Task(name='Monitoring', est_min=30, est_nom=35, est_max=40, estimator='triangular')
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    p.add_task(t4)
    p.plot()


def test_plot_cumul():
    t1 = Task(name='Analysis', est_min=2, est_nom=3, est_max=7, estimator='triangular')
    t2 = Task(name='Experiment', est_min=30, est_nom=35, est_max=40, estimator='triangular')
    t3 = Task(name='Evaluation', est_min=30, est_nom=35, est_max=40, estimator='triangular')
    t4 = Task(name='Monitoring', est_min=30, est_nom=35, est_max=40, estimator='triangular')
    p = Project(name='High Score Bypass')
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    p.add_task(t4)
    p.plot(hist=False)
