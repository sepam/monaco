from monaco import Task, Project
from pprint import pprint

project = Project(name="App development", unit='days')

task1 = Task(name="Design UI", min_duration=1, max_duration=3, estimator='uniform')
task2 = Task(name="Develop frontend", min_duration=7, max_duration=14, estimator='uniform')
task3 = Task(name="Develop backend", min_duration=5, max_duration=10, estimator='uniform')
task4 = Task(name="Test frontend", min_duration=1, max_duration=3, estimator='uniform')
task5 = Task(name="Test backend", min_duration=2, max_duration=4, estimator='uniform')
task6 = Task(name="User Acceptance Testing (UAT)", min_duration=2, max_duration=5, estimator='uniform')
task7 = Task(name="Release app", min_duration=1, max_duration=2, estimator='uniform')
task8 = Task(name="Deploy backend", min_duration=1, max_duration=1.5, estimator='uniform')
task9 = Task(name="Go live", min_duration=0.25, max_duration=0.75, estimator='uniform')


project.add_task(task1)
project.add_task(task2, depends_on=[task1])
project.add_task(task3)
project.add_task(task4, depends_on=[task2])
project.add_task(task5, depends_on=[task3])
project.add_task(task6, depends_on=[task4, task5])
project.add_task(task7, depends_on=[task6])
project.add_task(task8, depends_on=[task6])
project.add_task(task9, depends_on=[task8])

results = project.statistics()
pprint(results)
