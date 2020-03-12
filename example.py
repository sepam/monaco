from monaco import Task, Project


t1 = Task(name='Analysis', min=2, median=3, max=7)
t2 = Task(name='Experiment', min=30, median=35, max=40)
p = Project(name='High Score Bypass')
p.add_task(t1)
p.add_task(t2)
p.plot()
