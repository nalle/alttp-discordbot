import time
import json
import operator
import os
from redis import Redis
from tabulate import tabulate
from datetime import timedelta
from bot.messages import Messages

messages = Messages()


class Race():

    def __init__(self, channel, redis):
        self.r = redis

    async def initialize(self, channel):
        race = await self.r.get(channel)

        self.channel = channel

        if race:
            race = json.loads(race)[channel]
            self.state = race['state']
            self.runners = race['runners']
            self.time = race['time']
            self.type = race['type']
        else:
            self.state = False
            self.runners = {}
            self.time = None
            self.type = "custom"

    async def results(self):
        result = []
        for runner in sorted(self.runners, key=operator.itemgetter(1)):
            result.append([runner, str(timedelta(seconds=self.runners[runner]['time']-self.time))])

        return "```{}```".format(tabulate(result, ["Runner", "Finish time"], tablefmt="grid"))

    async def persist(self):
        data = {
            self.channel: {
                "state": self.state,
                "time": self.time,
                "runners": {},
                "type": self.type,
            }
        }

        for runner in self.runners:
            data[self.channel]['runners'][runner] = {
                "ready": self.runners[runner]['ready'],
                "done": self.runners[runner]['done'],
                "time": self.runners[runner]['time'],
            }

        await self.r.set(self.channel, json.dumps(data))

    async def print(self):
        return json.loads(self.r.get(self.channel))

    async def startrace(self):
        """
        :seed_type:
            should be either 'standard', 'open', 'spoiler'
        """
        self.state = True
        self.runners = {}
        self.time = None
        self.type = "custom"

    async def stoprace(self):
        self.state = False
        self.remaining = 0
        #self.runners = {}
        #self.time = None
        self.type = "custom"

    async def join(self, name):
        self.runners[name] = {
            "ready": False,
            "done": False,
            "time": None,
        }

    async def unjoin(self, name):
        del self.runners[name]

    async def check_done(self):
        done = 0
        for runner in self.runners:
            if not self.runners[runner]['done']:
                done += 1
        return done

    async def check_remaining(self):
        self.remaining = 0
        for runner in self.runners:
            if not self.runners[runner]['ready']:
                self.remaining += 1
        return self.remaining

    async def ready(self, name):
        self.runners[name]['ready'] = True

    async def done(self, name):
        self.runners[name]['done'] = True
        self.runners[name]['time'] = round(time.time())
        self.persist()

    async def parse_message(self, message):
        if self.type == 'open' or self.type == 'custom':
            # await self.parse_message_open_race(message)
            async for return_msg in self.parse_message_open_race(message):
                yield return_msg
        elif self.type == 'standard':
            # await self.parse_message_standard_race(message)
            async for return_msg in self.parse_message_standard_race(message):
                yield return_msg
        elif self.type == 'spoiler':
            # await self.parse_message_spoiler_race(message)
            async for return_msg in self.parse_message_spoiler_race(message):
                yield return_msg
        else:
            yield "ERROR: Unknown race type set on race..."

    async def parse_message_open_race(self, message):
        runner_name = message.author.name

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            await self._join_race(runner_name)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            await self._unjoin_race(runner_name)

        if message.content.startswith(".done"):
            await self._done(runner_name)

        if message.content.startswith(".ready"):
            if runner_name not in race.runners:
                yield messages.notstarted
                return

            await self._ready_basic(runner_name)

    async def parse_message_standard_race(self, message):
        runner_name = message.author.name

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            await self._join_race(runner_name)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            await self._unjoin_race(runner_name)

        if message.content.startswith(".done"):
            await self._done(runner_name)

        if message.content.startswith(".ready"):
            if runner_name not in race.runners:
                yield messages.notstarted
                return

            await self._ready_basic(runner_name)

    async def parse_message_spoiler_raace(self, message):
        runner_name = message.author.name

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            await self._join_race(runner_name)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            await self._unjoin_race(runner_name)

        if message.content.startswith(".done"):
            await self._done(runner_name)

        if message.content.startswith(".ready"):
            if runner_name not in race.runners:
                yield messages.notstarted
                return

            await self._ready_spoiler(runner_name)

    async def _join_race(self, runner_name):
        await race.join(runner_name)
        yield messages.joinrace(runner_name)

    async def _unjoin_race(self, runner_name):
        await race.unjoin(message.author.name)
        await race.check_remaining()

        yield messages.quitrace(message.author.name)

        is_done = await race.check_done()

        if is_done == 0 and race.time is not None:
            await race.stoprace()
            yield await race.results()

        if len(race.runners) > 0 and is_done > 0:
            remaining = await race.check_remaining()

            if remaining == 0 and race.time is None:
                if race.type in ('open', 'standard', 'custom'):
                    await race.persist()
                    yield messages.countdown

                    await asyncio.sleep(5)

                    for i in range(5, 0, -1):
                        yield f"{i}"
                        await asyncio.sleep(1)

                    race.time = round(time.time())

                    yield messages.go

    async def _done(self, runner_name):
        if race.runners[message.author.name]['done']:
            yield messages.alreadydone
        else:
            if race.time is not None:
                await race.done(message.author.name)

                if race.check_done() == 0:
                    race.stoprace()
                    yield race.results()
                else:
                    yield messages.done(str(timedelta(seconds=race.runners[message.author.name]['time']-race.time)))
            else:
                yield messages.notstarted

    async def _ready_basic(self, runner_name):
        if runner_name in race.runners:
            await race.ready(message.author.name)

            remaining = await race.check_remaining()

            if remaining != 0:
                yield messages.remaining(race.remaining)
                return

            if race.type in ('open', 'standard', 'custom'):
                await race.persist()

                yield messages.countdown

                await asyncio.sleep(5)

                for i in range(5, 0, -1):
                    yield f"{i}"
                    await asyncio.sleep(1)

                race.time = round(time.time())
                yield messages.go

    async def _ready_spoiler(self, runner_name):
        if remaining != 0:
            yield messages.remaining(race.remaining)
            return

        race.time = round(time.time())
        await race.persist()

        yield "Starting planning phase spoiler log race. Download the spoiler log file and you have 30 minutes to study it"
        await asyncio.sleep(1)
        yield "Starting timer in 5 seconds"

        for i in range(5, 0, -1):
            yield f"{i}"
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        yield "30 minutes left of planning phase"

        await asyncio.sleep(int(600 * DEV_MULTIPLIER))
        yield "20 minutes left of planning phase"

        await asyncio.sleep(int(600 * DEV_MULTIPLIER))
        yield "10 minutes left of planning phase"

        await asyncio.sleep(int(300 * DEV_MULTIPLIER))
        yield "5 minutes left of planning phase"

        await asyncio.sleep(int(240 * DEV_MULTIPLIER))
        yield "60 seconds left of planning phase"

        await asyncio.sleep(int(50 * DEV_MULTIPLIER))
        for i in range(5, 0, -1):
            yield f"{i}"
            await asyncio.sleep(1)

        yield "Planning phase is now completed. Start your Race Rom!"
        race.time = round(time.time())
        await asyncio.sleep(1)
        yield messages.go
