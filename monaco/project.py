import math
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from monaco import Task


class Project(Task):

    def __init__(self, name=None):
        super().__init__()
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

    def plot(self, n=1000, hist=True, kde=False):
        # TODO: add 95%, 75%, 50%, 25% CI indicator lines
        # TODO: add number (n) of iterations on plot
        sns.set(rc={"xtick.bottom": True, "ytick.left": True})
        sims = [self.estimate() for i in range(n)]
        fig, ax = plt.subplots(figsize=(10, 8))

        if hist:
            kwargs = {'cumulative': False, 'edgecolor': "k", 'linewidth': 1}
            plot = sns.distplot(sims, bins=math.floor(max(sims)), hist=True,
                                kde=kde,norm_hist=False, hist_kws=kwargs,
                                ax=ax)
            plt.title('Histogram - days to completion')
            plt.xticks()
            plt.show()

        else:
            kwargs = {'cumulative': True, 'edgecolor': "k", 'linewidth': 1}
            plot = sns.distplot(sims, bins=math.floor(max(sims)),
                                hist=True, kde=False, norm_hist=True,
                                hist_kws=kwargs)
            plt.title('Cumulative histogram - days to completion')
            plt.show()

        return plot
