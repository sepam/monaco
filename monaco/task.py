"""Logic for creating Tasks"""
from datetime import datetime
import random
import math


class Task:

    def __init__(self, name=None, due_date=None, est_nom=None,
                 est_min=None, est_max=None, estimator='triangular'):
        self.cdate = datetime.now()
        self.name = name
        self.due_date = due_date
        self.est_nom = est_nom
        self.est_min = est_min
        self.est_max = est_max
        self.estimator = estimator
        self.depends_on = []

        if self.estimator not in ['triangular', 'uniform']:
            raise Exception('not a valid estimator')


    def estimate(self, estimator='triangular'):

        if estimator == 'triangular':
            est = random.triangular(low=self.est_min, mode=self.est_nom,
                                    high=self.est_max)

        elif estimator == 'uniform':
            est = random.uniform(self.est_min, self.est_max)

        else:
            raise Exception("Unknown estimation method, please use 'uniform' or 'triangular'")

        return math.floor(est)



