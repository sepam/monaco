from monaco import Task, Project


t1 = Task(name='Analysis', est_min=2, est_nom=3, est_max=7)
t2 = Task(name='Experiment', est_min=30, est_nom=35, est_max=40)
p = Project(name='High Score Bypass')
p.add_task(t1)
p.add_task(t2)
p.plot()
