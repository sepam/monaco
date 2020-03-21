import math
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from src.monaco import Task


class Project(Task):

    def __init__(self, name=None):
        """ Project class

        Parameters
        ----------
        name : str, optional
            Name of the project

        """
        super().__init__()
        self.name = name
        self.tasks = []

    def add_task(self, task):
        """ Add a task to the project.

        Parameters
        ----------
        task : Task Object
            A subtask instantiated with monaco.Task()
        """
        self.tasks.append(task)

    def estimate(self):
        """ Estimate the duration of a project given uncertainty estimates.

        Returns
        -------
        p_est : float
            An estimated duration in measured in units
        """
        self.p_est = sum([t.estimate() for t in self.tasks])
        return self.p_est

    def _simulate(self, n=1000):
        """ Run a monte carlo simulation by simulating n estimation runs.

        Parameters
        ----------
        n : int
            Number of estimations to run in the simulation

        Returns
        -------
        c : Counter() object
            Counter with count of estimation occurences
        """
        sims = [self.estimate() for i in range(n)]
        c = Counter(sims)
        return c

    def plot(self, n=1000, hist=True, kde=False):
        """ Plot the resulting histogram

        Parameters
        ----------
        n : int
            Number of estimations to run in the simulation
        hist : bool
            Whether to plot a histogram or cumulative distribution plot
        kde : bool
            Whether to plot the kernel density estimation on the histogram

        Returns
        -------
        plot : matplotlib.plt() object
            Plot object

        """
        sns.set(rc={"xtick.bottom": True, "ytick.left": True})
        sims = [self.estimate() for i in range(n)]
        fig, ax = plt.subplots(figsize=(10, 8))

        if hist:
            kwargs = {'cumulative': False, 'edgecolor': "k", 'linewidth': 1}
            plot = sns.distplot(sims, bins=math.floor(max(sims)), hist=True,
                                kde=kde,norm_hist=False, hist_kws=kwargs,
                                ax=ax)
            plt.title('Histogram - days to project completion '
                      '- n = {}'.format(n))
            plt.axvline(x=np.median(sims), color='red', label='50%')
            plt.text(np.median(sims)-0.5, -2, '50%', color='red')
            plt.show()

        else:
            kwargs = {'cumulative': True, 'edgecolor': "k", 'linewidth': 1}
            plot = sns.distplot(sims, bins=math.floor(max(sims)),
                                hist=True, kde=False, norm_hist=True,
                                hist_kws=kwargs)
            plt.title('Cumulative histogram - days project to completion '
                      '- n = {}'.format(n))
            plt.show()

        return plot
