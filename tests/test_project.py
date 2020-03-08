from monaco.project import Project
from monaco.task import Task


def test_project_init_default():
    p = Project()
    assert p.name == None
    assert p.tasks == []
    assert type(p.tasks) == list


def test_project_init_params():
    t1 = Task()
    t2 = Task()
    p = Project(name='Experiment', tasks=[t1, t2])
    assert len(p.tasks) == 2


def test_project_add_task():
    t1 = Task(name='example')
    p = Project()
    p.add(t1)
    assert len(p.tasks) == 1
    assert p.tasks[0].name == 'example'


def test_project_estimate():
    t1 = Task(name='Analysis', est_min=2, est_nom=3, est_max=7)
    t2 = Task(name='Experiment', est_min=30, est_nom=35, est_max=40)
    p = Project(name='High Score Bypass')
    p.add(t1)
    p.add(t2)
    est = p.estimate()
    assert est > 7








