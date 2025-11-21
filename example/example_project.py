from monaco import Task, Project
from pprint import pprint

project = Project(name="App development", unit='days')

task1 = Task(name="Design UI", min_duration=1, max_duration=3, estimator='uniform')
task2 = Task(name="Develop app", min_duration=7, max_duration=14, estimator='uniform')
task3 = Task(name="Develop backend", min_duration=5, max_duration=10, estimator='uniform')
task4 = Task(name="Test applciation", min_duration=2, max_duration=5, estimator='uniform')

project.add_task(task1)
project.add_task(task2, depends_on=[task1])
project.add_task(task3, depends_on=[task1])
project.add_task(task4, depends_on=[task2, task3])

results = project.statistics()
pprint(results)
