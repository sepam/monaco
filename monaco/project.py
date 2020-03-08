class Project:

    def __init__(self, name=None, tasks=[]):
        self.name = name
        self.tasks = tasks

    def add(self, task):
        self.tasks.append(task)

    def estimate(self):
        self.p_est = sum([t.estimate() for t in self.tasks])
        return self.p_est