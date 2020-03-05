"""Logic for creating Tasks"""
from datetime import datetime
import random


class Task:

    def __init__(self, text=None, due_date=None, est_done=None,
                 est_min=None, est_max=None, depends_on=[]):
        self.cdate = datetime.now()
        self.text = text
        self.due_date = due_date
        self.est_done = est_done
        self.est_min = est_min
        self.est_max = est_max
        self.depends_on = depends_on

    def estimate(self):
        est = random.triangular(self.est_min, self.est_done,
                                self.est_max)
        return est



class Project:

    def __init__(self):
        pass