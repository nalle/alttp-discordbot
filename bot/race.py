import time
import json
import operator
from tabulate import tabulate
from datetime import timedelta

class Race():
    def __init__(self):
        print("Loaded Race class")
        self.state = False
        self.runners = {}
        self.time = None

    def results(self):
        result = []
        for runner in sorted(self.runners, key=operator.itemgetter(1)):
            result.append([runner, str(timedelta(seconds=self.runners[runner]['time']-self.time))])

        return "```{}```".format(tabulate(result, ["Runner", "Finish time"], tablefmt="grid"))

    def persist(self):
        data = {
                 "race": {
                   "state": self.state, 
                   "time": self.time
                 },
                 "runners": {
                 }
               }
        for runner in self.runners:
            data['runners'][runner] = {"ready": self.runners[runner]['ready'], "done": self.runners[runner]['done'], "time": self.runners[runner]['time']}

        print("Persisting data:")
        print(data)
