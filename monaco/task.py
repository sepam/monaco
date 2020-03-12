"""Logic for creating Tasks"""
from datetime import datetime
import random
import math


class Task:

    def __init__(self, name=None, due_date=None, median=None,
                 min=None, max=None, estimator='triangular'):
        self.cdate = datetime.now()
        self.name = name
        self.due_date = due_date
        self.median = median
        self.min = min
        self.max = max
        self.estimator = estimator
        self.depends_on = []

        if self.estimator not in ['triangular', 'uniform']:
            raise Exception('not a valid estimator')


    def estimate(self):

        if self.estimator == 'triangular':
            est = random.triangular(low=self.min, mode=self.median,
                                    high=self.max)

        elif self.estimator == 'uniform':
            est = random.uniform(self.min, self.max)

        # return math.floor(est)
        return est
