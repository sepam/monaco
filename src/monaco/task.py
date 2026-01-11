"""Logic for creating Tasks."""

import uuid
from typing import Optional

from monaco.distributions import (
    DISTRIBUTION_REGISTRY,
    Distribution,
    create_distribution,
)


class Task:

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
        """Get the distribution object."""
        return self._distribution

    @property
    def estimator(self) -> str:
        """Get the estimator name (for backward compatibility)."""
        if self._distribution is not None:
            return self._distribution.name
        return self._estimator_hint

    @property
    def min_duration(self) -> Optional[float]:
        """Get the minimum duration (for backward compatibility)."""
        if self._distribution is not None:
            if hasattr(self._distribution, "min_value"):
                return self._distribution.min_value
        return self._min_duration

    @property
    def mode_duration(self) -> Optional[float]:
        """Get the mode duration (for backward compatibility)."""
        if self._distribution is not None:
            if hasattr(self._distribution, "mode_value"):
                return self._distribution.mode_value
        return self._mode_duration

    @property
    def max_duration(self) -> Optional[float]:
        """Get the maximum duration (for backward compatibility)."""
        if self._distribution is not None:
            if hasattr(self._distribution, "max_value"):
                return self._distribution.max_value
        return self._max_duration

    def estimate(self) -> float:
        """Estimate duration of a task by sampling from the distribution.

        Returns
        -------
        float
            An estimated duration sampled from the specified probability
            distribution.

        Raises
        ------
        ValueError
            If distribution is not configured.
        """
        if self._distribution is None:
            raise ValueError(
                "Task distribution not configured. "
                "Provide duration parameters or a Distribution object."
            )
        return self._distribution.sample()
