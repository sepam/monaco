import math
from collections import Counter
from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.figure
import numpy as np
import seaborn as sns
from monaco import Task


class Project(Task):

    def __init__(self, name: Optional[str] = None) -> None:
        """ Project class

        Parameters
        ----------
        name : str, optional
            Name of the project

        """
        super().__init__()
        self.name = name
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """ Add a task to the project.

        Parameters
        ----------
        task : Task Object
            A subtask instantiated with monaco.Task()
        """
        self.tasks.append(task)

    def estimate(self) -> float:
        """ Estimate the duration of a project given uncertainty estimates.

        Returns
        -------
        p_est : float
            An estimated duration in measured in units
        """
        self.p_est = sum([t.estimate() for t in self.tasks])
        return self.p_est

    def _simulate(self, n: int = 1000) -> Counter:
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

    def plot(
        self,
        n: int = 1000,
        hist: bool = True,
        kde: bool = False,
        save_path: Optional[str] = None
    ) -> matplotlib.figure.Figure:
        """ Plot the resulting histogram or cumulative distribution

        Parameters
        ----------
        n : int
            Number of estimations to run in the simulation
        hist : bool
            Whether to plot a histogram or cumulative distribution plot
        kde : bool
            Whether to plot the kernel density estimation on the histogram
        save_path : str, optional
            Path to save the plot. If None, the plot will be displayed instead

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object containing the plot

        """
        sns.set_theme(rc={"xtick.bottom": True, "ytick.left": True})
        sims = [self.estimate() for i in range(n)]
        fig, ax = plt.subplots(figsize=(10, 8))

        if hist:
            # Use modern histplot instead of deprecated distplot
            sns.histplot(sims, bins=math.floor(max(sims)),
                        stat='count', kde=kde, edgecolor='k',
                        linewidth=1, ax=ax)
            ax.set_title('Histogram - days to project completion '
                        '- n = {}'.format(n))
            ax.axvline(x=np.median(sims), color='red', label='50%')
            ax.text(np.median(sims)-0.5, ax.get_ylim()[0], '50%', color='red')
            ax.legend()

        else:
            # Use modern histplot with cumulative option
            sns.histplot(sims, bins=math.floor(max(sims)),
                        stat='probability', cumulative=True,
                        edgecolor='k', linewidth=1, ax=ax)
            ax.set_title('Cumulative histogram - days project to completion '
                        '- n = {}'.format(n))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

        return fig
