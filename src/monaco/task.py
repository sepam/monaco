"""Logic for creating Tasks"""
from datetime import datetime
import random


class Task:

    def __init__(self, name=None, min_duration=None, mode_duration=None,
                 max_duration=None, estimator='triangular'):
        """ Task class.

        Parameters
        ----------
        name : str, optional
            Description or name of a task
        min_duration : float
            The minimum estimated number of units to complete a task
        mode_duration : float
            The most likely estimated number of units to complete a task
        max_duration : float
            The maximum estimated number of units to complete a task
        estimator : str
            An estimator in form of a probability distribution ('triangular' or 'uniform')

        Raises
        ------
        ValueError
            If estimator is not 'triangular' or 'uniform'
            If duration values are invalid (negative or not ordered correctly)
        """
        self.cdate = datetime.now()
        self.name = name
        self.mode_duration = mode_duration
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.estimator = estimator

        # Validate estimator
        if self.estimator not in ['triangular', 'uniform']:
            raise ValueError(f"Invalid estimator '{self.estimator}'. Must be 'triangular' or 'uniform'")

        # Validate duration values
        if min_duration is not None and min_duration < 0:
            raise ValueError(f"min_duration must be non-negative, got {min_duration}")

        if max_duration is not None and max_duration < 0:
            raise ValueError(f"max_duration must be non-negative, got {max_duration}")

        if mode_duration is not None and mode_duration < 0:
            raise ValueError(f"mode_duration must be non-negative, got {mode_duration}")

        # Validate ordering for triangular distribution
        if self.estimator == 'triangular':
            if min_duration is not None and max_duration is not None and mode_duration is not None:
                if not (min_duration <= mode_duration <= max_duration):
                    raise ValueError(
                        f"For triangular distribution, must have min_duration <= mode_duration <= max_duration. "
                        f"Got min={min_duration}, mode={mode_duration}, max={max_duration}"
                    )

        # Validate ordering for uniform distribution
        if self.estimator == 'uniform':
            if min_duration is not None and max_duration is not None:
                if min_duration > max_duration:
                    raise ValueError(
                        f"For uniform distribution, must have min_duration <= max_duration. "
                        f"Got min={min_duration}, max={max_duration}"
                    )

    def estimate(self):
        """Estimate duration of a task following a probability
        distribution.

        Returns
        -------
        float
            An estimated duration sampled from the specified probability distribution
        """
        if self.estimator == 'triangular':
            est = random.triangular(low=self.min_duration, mode=self.mode_duration,
                                    high=self.max_duration)

        elif self.estimator == 'uniform':
            est = random.uniform(self.min_duration, self.max_duration)

        return est
