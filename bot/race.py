import time
import json
import operator
import os
from redis import Redis
from tabulate import tabulate
from datetime import timedelta

class Race():
    def __init__(self, channel):
        self.r = Redis(host='10.233.56.41', port=6379, password=os.environ.get('REDIS_PASSWORD'))
        race = self.r.get(channel)
        if race:
            race = json.loads(race)[channel]
            self.state = race['state']
            self.runners = race['runners']
            self.time = race['time']
        else:
            self.state = False
            self.runners = {}
            self.time = None
        self.channel = channel

    def results(self):
        result = []
        for runner in sorted(self.runners, key=operator.itemgetter(1)):
            result.append([runner, str(timedelta(seconds=self.runners[runner]['time']-self.time))])

        return "```{}```".format(tabulate(result, ["Runner", "Finish time"], tablefmt="grid"))

    def persist(self):
        data = {
                 self.channel: {
                   "state": self.state, 
                   "time": self.time,
                   "runners": {
                   }
                 }
               }
        for runner in self.runners:
            data[self.channel]['runners'][runner] = {"ready": self.runners[runner]['ready'], "done": self.runners[runner]['done'], "time": self.runners[runner]['time']}
        self.r.set(self.channel, json.dumps(data))
     
    def print(self):
        return json.loads(self.r.get(self.channel))

