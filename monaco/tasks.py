"""Logic for creating Tasks"""

class Task:

    def __init__(self, text, due_date, est_done, est_min, est_max,
                 depends_on=[]):
        self.text = text
        self.due_date = due_date
        self.est_done = est_done
        self.est_min = est_min
        self.est_max = est_max
        self.depends_on = depends_on