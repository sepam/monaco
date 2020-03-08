class Project:

    def __init__(self, name=None):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def estimate(self):
        self.p_est = sum([t.estimate() for t in self.tasks])
        return self.p_est