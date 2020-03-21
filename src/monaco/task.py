"""Logic for creating Tasks"""
from datetime import datetime
import random


class Task:

    def __init__(self, name=None, min=None, mode=None,
                 max=None, estimator='triangular'):
        """ Task class.

        Parameters
        ----------
        name : str, optional
            Description or name of a task
        min : int
            The minimum estimated number of units to complete a task
        mode : int
            The most likely estimated number of units to complete a task
        max : int
            The maximum estimated number of units to complete a task
        estimator : str
            An estimator in form of a probability distribution

        """
        self.cdate = datetime.now()
        self.name = name
        self.mode = mode
        self.min = min
        self.max = max
        self.estimator = estimator

        if self.estimator not in ['triangular', 'uniform']:
            raise Exception('not a valid estimator')

    def estimate(self):
        """Estimate duration of a task following a probability
        distribution."""
        if self.estimator == 'triangular':
            est = random.triangular(low=self.min, mode=self.mode,
                                    high=self.max)

        elif self.estimator == 'uniform':
            est = random.uniform(self.min, self.max)

        return est
