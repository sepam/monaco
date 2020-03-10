from collections import Counter
import matplotlib.pyplot as plt


class Project:

    def __init__(self, name=None):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def estimate(self):
        self.p_est = sum([t.estimate() for t in self.tasks])
        return self.p_est

    def _simulate(self, n=1000):
        sims = [self.estimate() for i in range(n)]
        c = Counter(sims)
        return c

    def plot(self):
        val, weight = zip(*[(k, v) for k, v in self._simulate().items()])
        plot = plt.hist(val, weights=weight)
        plt.show()
