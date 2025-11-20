import math
from collections import Counter
from typing import List, Optional, Dict, Any, Tuple
import json
import csv
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

    def _run_simulation(self, n: int = 1000) -> List[float]:
        """ Internal method to run simulations and return raw results.

        Parameters
        ----------
        n : int
            Number of estimations to run in the simulation

        Returns
        -------
        List[float]
            List of simulation results
        """
        return [self.estimate() for i in range(n)]

    def statistics(self, n: int = 10000) -> Dict[str, Any]:
        """ Calculate comprehensive statistics from Monte Carlo simulation.

        Parameters
        ----------
        n : int
            Number of simulations to run (default: 10000)

        Returns
        -------
        Dict[str, Any]
            Dictionary containing:
            - n_simulations: Number of simulations run
            - mean: Average completion time
            - median: Median completion time (P50)
            - std_dev: Standard deviation
            - min: Minimum observed completion time
            - max: Maximum observed completion time
            - percentiles: Dictionary with P10, P50, P85, P90, P95
            - confidence_intervals: Dictionary with 95% confidence interval

        Examples
        --------
        >>> project = Project(name='My Project')
        >>> project.add_task(Task(min_duration=1, mode_duration=2, max_duration=3))
        >>> stats = project.statistics(n=10000)
        >>> print(f"P85: {stats['percentiles']['p85']:.1f} days")
        """
        sims = self._run_simulation(n)
        sims_array = np.array(sims)

        # Calculate percentiles
        p10 = np.percentile(sims_array, 10)
        p50 = np.percentile(sims_array, 50)
        p85 = np.percentile(sims_array, 85)
        p90 = np.percentile(sims_array, 90)
        p95 = np.percentile(sims_array, 95)

        # Calculate 95% confidence interval (mean ± 1.96 * std)
        mean = np.mean(sims_array)
        std = np.std(sims_array)
        ci_95_lower = mean - 1.96 * std
        ci_95_upper = mean + 1.96 * std

        return {
            'n_simulations': n,
            'mean': float(mean),
            'median': float(p50),
            'std_dev': float(std),
            'min': float(np.min(sims_array)),
            'max': float(np.max(sims_array)),
            'percentiles': {
                'p10': float(p10),
                'p50': float(p50),
                'p85': float(p85),
                'p90': float(p90),
                'p95': float(p95)
            },
            'confidence_intervals': {
                '95%': (float(ci_95_lower), float(ci_95_upper))
            }
        }

    def export_results(
        self,
        n: int = 10000,
        format: str = 'json',
        output: str = 'monaco_results.json'
    ) -> None:
        """ Export simulation results and statistics to file.

        Parameters
        ----------
        n : int
            Number of simulations to run (default: 10000)
        format : str
            Output format: 'json' or 'csv' (default: 'json')
        output : str
            Output file path (default: 'monaco_results.json')

        Raises
        ------
        ValueError
            If format is not 'json' or 'csv'

        Examples
        --------
        >>> project.export_results(n=10000, format='json', output='results.json')
        >>> project.export_results(n=10000, format='csv', output='results.csv')
        """
        if format not in ['json', 'csv']:
            raise ValueError(f"Invalid format '{format}'. Must be 'json' or 'csv'")

        stats = self.statistics(n)
        sims = self._run_simulation(n)

        if format == 'json':
            # Export comprehensive JSON with stats and raw data
            output_data = {
                'project_name': self.name,
                'statistics': stats,
                'simulations': sims
            }
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)

        elif format == 'csv':
            # Export CSV with simulations and summary stats
            with open(output, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Project Name', self.name])
                writer.writerow(['Number of Simulations', stats['n_simulations']])
                writer.writerow(['Mean', stats['mean']])
                writer.writerow(['Median (P50)', stats['median']])
                writer.writerow(['Std Dev', stats['std_dev']])
                writer.writerow(['Min', stats['min']])
                writer.writerow(['Max', stats['max']])
                writer.writerow(['P10', stats['percentiles']['p10']])
                writer.writerow(['P85', stats['percentiles']['p85']])
                writer.writerow(['P90', stats['percentiles']['p90']])
                writer.writerow(['P95', stats['percentiles']['p95']])
                writer.writerow(['95% CI Lower', stats['confidence_intervals']['95%'][0]])
                writer.writerow(['95% CI Upper', stats['confidence_intervals']['95%'][1]])
                writer.writerow([])
                writer.writerow(['Simulation Results'])
                writer.writerow(['Run', 'Duration'])
                for i, sim in enumerate(sims, 1):
                    writer.writerow([i, sim])

    def plot(
        self,
        n: int = 1000,
        hist: bool = True,
        kde: bool = False,
        save_path: Optional[str] = None,
        show_percentiles: bool = False,
        percentiles: Optional[List[int]] = None
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
        show_percentiles : bool
            Whether to show percentile markers on the plot (default: False)
        percentiles : List[int], optional
            List of percentiles to show (default: [50, 85, 95])

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object containing the plot

        Examples
        --------
        >>> project.plot(n=10000, show_percentiles=True, percentiles=[50, 85, 95])
        """
        if percentiles is None:
            percentiles = [50, 85, 95]

        sns.set_theme(rc={"xtick.bottom": True, "ytick.left": True})
        sims = self._run_simulation(n)
        fig, ax = plt.subplots(figsize=(10, 8))

        if hist:
            # Use modern histplot instead of deprecated distplot
            sns.histplot(sims, bins=math.floor(max(sims)),
                        stat='count', kde=kde, edgecolor='k',
                        linewidth=1, ax=ax)
            ax.set_title('Histogram - days to project completion '
                        '- n = {}'.format(n))

            # Add percentile markers
            if show_percentiles:
                colors = ['red', 'orange', 'purple', 'green', 'blue']
                for i, p in enumerate(percentiles):
                    p_value = np.percentile(sims, p)
                    color = colors[i % len(colors)]
                    ax.axvline(x=p_value, color=color, linestyle='--',
                              linewidth=2, label=f'P{p}')
                    ax.text(p_value - 0.5, ax.get_ylim()[1] * 0.95 - i * ax.get_ylim()[1] * 0.05,
                           f'P{p}', color=color, fontweight='bold')
            else:
                # Default: show only median
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
