"""
Task module for representing individual work items with probabilistic durations.

This module provides the Task class, which represents a single unit of work
in a project. Each task has a duration modeled as a probability distribution,
allowing for uncertainty in time estimates.

Key Concepts
------------
A Task represents any discrete unit of work that needs to be completed:
- A development feature
- A testing phase
- A meeting or review
- Any activity with uncertain duration

Tasks can be created in two ways:

1. **Legacy style** (backward compatible): Specify min, mode, and max
   durations with an estimator type.

2. **Modern style**: Provide a Distribution object directly for full
   control over the probability distribution.

Relationship to Distributions
-----------------------------
Tasks delegate duration sampling to Distribution objects. The Task class
provides a convenient wrapper that:
- Generates unique task IDs
- Tracks creation timestamps
- Provides backward-compatible property access
- Can be added to Project objects for simulation

Example
-------
>>> from monaco import Task
>>> # Legacy style: three-point estimate
>>> task = Task(
...     name="Development",
...     min_duration=5,
...     mode_duration=8,
...     max_duration=15
... )
>>> # Sample a duration
>>> duration = task.estimate()

>>> # Modern style: use a Distribution object
>>> from monaco import PERTDistribution
>>> dist = PERTDistribution(minimum=5, mode=8, maximum=15)
>>> task = Task(name="Development", distribution=dist)

See Also
--------
Project : Container for multiple tasks with dependencies.
distributions : Probability distribution classes.
"""

import uuid
from datetime import datetime
from typing import Optional

from monaco.distributions import (
    DISTRIBUTION_REGISTRY,
    Distribution,
    create_distribution,
)


class Task:
    """A single task with probabilistic duration for Monte Carlo simulation.

    Task is the fundamental building block for project planning in Monaco.
    It represents a unit of work with uncertain duration, modeled as a
    probability distribution.

    Tasks can be combined into Projects to simulate complex workflows
    with dependencies.

    Attributes
    ----------
    task_id : str
        Unique identifier (UUID) for the task.
    cdate : datetime
        Creation timestamp.
    name : str or None
        Human-readable name for the task.

    Example
    -------
    >>> task = Task(name="Research", min_duration=2, mode_duration=5, max_duration=10)
    >>> task.name
    'Research'
    >>> task.estimator
    'triangular'
    >>> duration = task.estimate()  # Sample from distribution
    """

    def __init__(
        self,
        name: Optional[str] = None,
        min_duration: Optional[float] = None,
        mode_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        estimator: str = "triangular",
        distribution: Optional[Distribution] = None,
    ) -> None:
        """Task class with flexible distribution specification.

        Parameters
        ----------
        name : str, optional
            Description or name of a task.
        min_duration : float, optional
            The minimum estimated number of units to complete a task.
            Used for triangular and uniform distributions.
        mode_duration : float, optional
            The most likely estimated number of units to complete a task.
            Required for triangular distribution.
        max_duration : float, optional
            The maximum estimated number of units to complete a task.
            Used for triangular and uniform distributions.
        estimator : str, optional
            Distribution type: 'triangular', 'uniform', or 'normal'.
            Default is 'triangular'.
        distribution : Distribution, optional
            A Distribution object. If provided, overrides the legacy
            parameters (min_duration, mode_duration, max_duration, estimator).

        Raises
        ------
        ValueError
            If estimator is unknown or if duration values are invalid.

        Examples
        --------
        Legacy style (backward compatible):

        >>> task = Task(
        ...     name="Development",
        ...     min_duration=5,
        ...     mode_duration=8,
        ...     max_duration=12,
        ...     estimator="triangular"
        ... )

        New style with Distribution object:

        >>> from monaco.distributions import NormalDistribution
        >>> dist = NormalDistribution(mean=8.0, std_dev=2.0)
        >>> task = Task(name="Development", distribution=dist)
        """
        self.task_id = str(uuid.uuid4())
        self.cdate = datetime.now()
        self.name = name

        # Validate estimator early (even if no distribution is created yet)
        if distribution is None and estimator not in DISTRIBUTION_REGISTRY:
            raise ValueError(
                f"Invalid estimator '{estimator}'. "
                f"Valid options: {list(DISTRIBUTION_REGISTRY.keys())}"
            )

        # Store legacy parameters for backward-compatible access
        self._min_duration = min_duration
        self._mode_duration = mode_duration
        self._max_duration = max_duration
        self._estimator_hint = estimator

        if distribution is not None:
            # New-style: Distribution object provided directly
            self._distribution: Optional[Distribution] = distribution
        elif min_duration is not None or max_duration is not None:
            # Legacy-style: create distribution from parameters
            self._distribution = create_distribution(
                estimator=estimator,
                min_duration=min_duration,
                mode_duration=mode_duration,
                max_duration=max_duration,
            )
        else:
            # No parameters provided - defer validation to estimate()
            self._distribution = None

    @property
    def distribution(self) -> Optional[Distribution]:
        """The probability distribution for task duration.

        Returns
        -------
        Distribution or None
            The Distribution object used for sampling durations.
            None if the task was created without duration parameters.

        Example
        -------
        >>> task = Task(min_duration=5, mode_duration=8, max_duration=12)
        >>> task.distribution.name
        'triangular'
        """
        return self._distribution

    @property
    def estimator(self) -> str:
        """The distribution type name (for backward compatibility).

        Returns
        -------
        str
            Name of the distribution type (e.g., 'triangular', 'uniform').

        Example
        -------
        >>> task = Task(min_duration=5, mode_duration=8, max_duration=12)
        >>> task.estimator
        'triangular'
        """
        if self._distribution is not None:
            return self._distribution.name
        return self._estimator_hint

    @property
    def min_duration(self) -> Optional[float]:
        """The minimum duration value (for backward compatibility).

        Returns
        -------
        float or None
            Minimum duration if the distribution has a min_value attribute,
            or the originally provided min_duration parameter.

        Example
        -------
        >>> task = Task(min_duration=5, mode_duration=8, max_duration=12)
        >>> task.min_duration
        5
        """
        if self._distribution is not None:
            if hasattr(self._distribution, "min_value"):
                return self._distribution.min_value
        return self._min_duration

    @property
    def mode_duration(self) -> Optional[float]:
        """The most likely duration value (for backward compatibility).

        Returns
        -------
        float or None
            Mode duration if the distribution has a mode_value attribute,
            or the originally provided mode_duration parameter.

        Example
        -------
        >>> task = Task(min_duration=5, mode_duration=8, max_duration=12)
        >>> task.mode_duration
        8
        """
        if self._distribution is not None:
            if hasattr(self._distribution, "mode_value"):
                return self._distribution.mode_value
        return self._mode_duration

    @property
    def max_duration(self) -> Optional[float]:
        """The maximum duration value (for backward compatibility).

        Returns
        -------
        float or None
            Maximum duration if the distribution has a max_value attribute,
            or the originally provided max_duration parameter.

        Example
        -------
        >>> task = Task(min_duration=5, mode_duration=8, max_duration=12)
        >>> task.max_duration
        12
        """
        if self._distribution is not None:
            if hasattr(self._distribution, "max_value"):
                return self._distribution.max_value
        return self._max_duration

    def estimate(self) -> float:
        """Estimate duration by sampling from the task's distribution.

        Each call returns a new random sample from the probability
        distribution, representing one possible duration for the task.

        Returns
        -------
        float
            An estimated duration sampled from the probability distribution.

        Raises
        ------
        ValueError
            If the task was created without duration parameters or
            a Distribution object.

        Example
        -------
        >>> task = Task(min_duration=5, mode_duration=8, max_duration=12)
        >>> duration = task.estimate()
        >>> 5 <= duration <= 12  # Within bounds
        True
        """
        if self._distribution is None:
            raise ValueError(
                "Task distribution not configured. "
                "Provide duration parameters or a Distribution object."
            )
        return self._distribution.sample()
