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

    def __init__(self, name: Optional[str] = None, unit: str = 'days') -> None:
        """ Project class

        Parameters
        ----------
        name : str, optional
            Name of the project
        unit : str, optional
            Time unit for all task durations (default: 'days').
            Common values: 'days', 'weeks', 'hours', 'months'

        """
        super().__init__()
        self.name = name
        self.unit = unit
        self._tasks_dict: Dict[str, Task] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self._task_order: List[str] = []  # Preserve insertion order for backward compat

    @property
    def tasks(self) -> List[Task]:
        """Get tasks as a list (for backward compatibility)."""
        return [self._tasks_dict[tid] for tid in self._task_order]

    def add_task(self, task: Task, depends_on: Optional[List[Task]] = None) -> None:
        """ Add a task to the project.

        Parameters
        ----------
        task : Task Object
            A subtask instantiated with monaco.Task()
        depends_on : List[Task], optional
            List of tasks that must complete before this task can start.
            For sequential/linear projects, leave as None (default behavior).

        Raises
        ------
        ValueError
            If a dependency task hasn't been added to the project yet
            If adding this task creates a circular dependency

        Examples
        --------
        >>> # Simple linear project (backward compatible)
        >>> project.add_task(task1)
        >>> project.add_task(task2)
        >>>
        >>> # Project with dependencies
        >>> project.add_task(research)
        >>> project.add_task(backend, depends_on=[research])
        >>> project.add_task(frontend, depends_on=[research])
        >>> project.add_task(testing, depends_on=[backend, frontend])
        """
        # Add task to internal dict
        self._tasks_dict[task.task_id] = task
        self._task_order.append(task.task_id)

        # Add dependencies if specified
        if depends_on:
            # Validate all dependencies exist in project
            for dep_task in depends_on:
                if dep_task.task_id not in self._tasks_dict:
                    raise ValueError(
                        f"Dependency task '{dep_task.name}' (id: {dep_task.task_id}) "
                        f"must be added to the project before being used as a dependency"
                    )

            self.dependencies[task.task_id] = [t.task_id for t in depends_on]

            # Validate no cycles created
            self._validate_dag()
        else:
            # No dependencies - can use default if not already set
            if task.task_id not in self.dependencies:
                self.dependencies[task.task_id] = []

    def _validate_dag(self) -> None:
        """
        Validate that the task graph is a valid DAG (no cycles).

        Raises
        ------
        ValueError
            If a cycle is detected in the dependency graph
        """
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            # Check all dependencies
            for dep_id in self.dependencies.get(task_id, []):
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        # Check all tasks for cycles
        for task_id in self._tasks_dict:
            if task_id not in visited:
                if has_cycle(task_id):
                    raise ValueError(
                        "Circular dependency detected in project. "
                        "Task dependencies must form a DAG (Directed Acyclic Graph)."
                    )

    def _topological_sort(self) -> List[str]:
        """
        Perform topological sort on the task graph.

        Returns
        -------
        List[str]
            List of task IDs in topological order (dependencies before dependents)
        """
        # in_degree counts how many dependencies each task has (incoming edges)
        in_degree = {task_id: len(self.dependencies.get(task_id, []))
                     for task_id in self._tasks_dict}

        # Queue of tasks with no dependencies (can start immediately)
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Process task with no dependencies
            current = queue.pop(0)
            result.append(current)

            # For each task that depends on current
            for task_id in self._tasks_dict:
                if current in self.dependencies.get(task_id, []):
                    in_degree[task_id] -= 1
                    if in_degree[task_id] == 0:
                        queue.append(task_id)

        return result

    def _calculate_critical_path(self, task_durations: Dict[str, float]) -> float:
        """
        Calculate project duration using critical path method.

        For projects with dependencies, calculates the longest path through the graph.
        Tasks in parallel take max() time, sequential tasks sum.

        Parameters
        ----------
        task_durations : Dict[str, float]
            Mapping of task_id to duration for this simulation run

        Returns
        -------
        float
            Total project duration considering dependencies
        """
        if not self._tasks_dict:
            return 0.0

        # Get tasks in topological order
        sorted_tasks = self._topological_sort()

        # Calculate earliest start time for each task
        earliest_start: Dict[str, float] = {}

        for task_id in sorted_tasks:
            deps = self.dependencies.get(task_id, [])
            if not deps:
                # No dependencies - can start immediately
                earliest_start[task_id] = 0.0
            else:
                # Start after all dependencies complete
                dep_completion_times = [
                    earliest_start[dep_id] + task_durations[dep_id]
                    for dep_id in deps
                ]
                earliest_start[task_id] = max(dep_completion_times)

        # Total duration = latest completion time
        completion_times = [
            earliest_start[tid] + task_durations[tid]
            for tid in sorted_tasks
        ]
        return max(completion_times) if completion_times else 0.0

    def _has_dependencies(self) -> bool:
        """Check if any tasks have dependencies (non-empty dependency lists)."""
        return any(deps for deps in self.dependencies.values())

    def estimate(self) -> float:
        """ Estimate the duration of a project given uncertainty estimates.

        For projects with task dependencies, calculates the critical path.
        For simple linear projects (no dependencies), sums all task durations (backward compatible).

        Returns
        -------
        p_est : float
            An estimated duration measured in units
        """
        # Sample duration for each task
        task_durations = {
            task_id: task.estimate()
            for task_id, task in self._tasks_dict.items()
        }

        # Use critical path if dependencies exist, otherwise simple sum
        if self._has_dependencies():
            self.p_est = self._calculate_critical_path(task_durations)
        else:
            # Backward compatible: simple sum for linear projects
            self.p_est = sum(task_durations.values())

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
            - unit: Time unit for all durations
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
        >>> project = Project(name='My Project', unit='weeks')
        >>> project.add_task(Task(min_duration=1, mode_duration=2, max_duration=3))
        >>> stats = project.statistics(n=10000)
        >>> print(f"P85: {stats['percentiles']['p85']:.1f} {stats['unit']}")
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
            'unit': self.unit,
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
                'unit': self.unit,
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
                writer.writerow(['Unit', self.unit])
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
            ax.set_title(f'Histogram - {self.unit} to project completion '
                        f'- n = {n}')
            ax.set_xlabel(f'Duration ({self.unit})')
            ax.set_ylabel('Count')

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
            ax.set_title(f'Cumulative histogram - {self.unit} to project completion '
                        f'- n = {n}')
            ax.set_xlabel(f'Duration ({self.unit})')
            ax.set_ylabel('Cumulative Probability')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

        return fig
