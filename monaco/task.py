"""Logic for creating Tasks"""
from datetime import datetime
import random


class Task:

    def __init__(self, name=None, due_date=None, est_nom=None,
                 est_min=None, est_max=None, depends_on=[]):
        self.cdate = datetime.now()
        self.name = name
        self.due_date = due_date
        self.est_nom = est_nom
        self.est_min = est_min
        self.est_max = est_max
        self.depends_on = depends_on

    def estimate(self):
        est = random.triangular(self.est_min, self.est_nom,
                                self.est_max)
        return est



