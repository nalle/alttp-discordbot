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

    def startrace(self):
        self.state = True
        self.runners = {}
        self.time = None

    def stoprace(self):
        self.state = False
        self.remaining = 0
        #self.runners = {}
        #self.time = None

    def join(self, name):
        self.runners[name] = {"ready": False, "done": False, "time": None}        

    def unjoin(self, name):
        del self.runners[name] 

    def check_done(self):
        done = 0
        for runner in self.runners:
            if not self.runners[runner]['done']:
                done += 1
        return done

    def check_remaining(self):
        remaining = 0
        for runner in self.runners:
            if not self.runners[runner]['ready']:
                remaining += 1
        return remaining
 
    def ready(self, name):
        self.runners[name]['ready'] = True

    def done(self, name):
        self.runners[name]['done'] = True
        self.runners[name]['time'] = round(time.time())
        self.persist()


