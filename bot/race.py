import asyncio
import json
import operator
import os
import time
import uuid

from bot.messages import reply_channel, message_mapping, reply_channel_string
from bot.multiworld import Multiworld
from datetime import timedelta
from redis import Redis
from rq import Queue
from tabulate import tabulate
from worker import conn


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
            self.uuid = race['uuid']
        else:
            self.state = False
            self.runners = {}
            self.time = None
            self.type = "custom"
            self.uuid = ""

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
                "uuid": self.uuid,
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
        self.uuid = str(uuid.uuid4())

    async def stoprace(self):
        self.state = False
        self.remaining = 0
        # self.runners = {}
        # self.time = None
        self.type = "custom"
        self.uuid = ""

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
        await self.persist()

    async def parse_message(self, message):
        print("Parsing race object", self.uuid)
        print(message, message.content, self.type)

        if self.type == 'open':
            await self.parse_message_open_race(message)
        elif self.type == 'custom':
            await self.parse_message_open_race(message)
        elif self.type == 'standard':
            await self.parse_message_standard_race(message)
        elif self.type == 'spoiler':
            await self.parse_message_spoiler_race(message)
        elif self.type == 'multiworld':
            await self.parse_message_multiworld_race(message)
        else:
            await reply_channel(message, 'unkonwn_race_type')

    async def parse_message_open_race(self, message):
        runner_name = message.author.name

        print("parsing open race mssage", message.content)

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            print("Joining race...")
            await self._join_race(message, runner_name)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            await self._unjoin_race(message, runner_name)

        if message.content.startswith(".done"):
            await self._done(message, runner_name)

        if message.content.startswith(".ready"):
            if runner_name not in self.runners:
                await reply_channel(message, 'notstarted')
                return

            await self._ready_basic(message, runner_name)

    async def parse_message_standard_race(self, message):
        runner_name = message.author.name

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            await self._join_race(message, runner_name)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            await self._unjoin_race(message, runner_name)

        if message.content.startswith(".done"):
            await self._done(message, runner_name)

        if message.content.startswith(".ready"):
            if runner_name not in self.runners:
                await reply_channel(message, 'notstarted')
                return

            await self._ready_basic(message, runner_name)

    async def parse_message_spoiler_raace(self, message):
        runner_name = message.author.name

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            await self._join_race(message, runner_name)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            await self._unjoin_race(message, runner_name)

        if message.content.startswith(".done"):
            await self._done(message, runner_name)

        if message.content.startswith(".ready"):
            if runner_name not in self.runners:
                await reply_channel(message, 'notstarted')
                return

            await self._ready_spoiler(message, runner_name)

    async def parse_message_multiworld_race(self, message):
        runner_name = message.author.name

        if message.content.startswith('.join') or message.content.startswith('.enter'):
            await self._join_race(message, runner_name)

        if message.content.startswith('.generate'):
            multiworld = Multiworld()

            redis_host = os.environ.get('REDIS_HOST') or "127.0.0.1"
            redis_port = os.environ.get('REDIS_PORT') or 6379
            redis_password = os.environ.get('REDIS_PASSWORD') or None

            import redis
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
            )

            q = Queue(connection=r)

            q.enqueue(
                multiworld.create_multiworld,
                self.uuid,
                multi=2,
                mode="open",
                shuffle="vanilla",
                goal="ganon",
            )

            while True:
                result = await self.r.get(self.uuid)
                if result:
                    print("RQ worker complete...")
                    print(result)
                    break
                else:
                    # Wait
                    print(f"Waiting for RQ worker to finish up and write to key : {self.uuid}")
                    await asyncio.sleep(10)

            # TODO: Distribute data to channel about seed server

            # TODO: Distribute seed files to each player
            # file_paths = []
            # for file_path in file_paths:
            #     file_name = os.path.basename(file_path)
            #     await message.author.send('hello...', file=discord.File(file_path, file_name))

        if message.content.startswith('.ready'):
            if runner_name not in self.runners:
                await reply_channel(message, 'multiworld_notstarted')
                return

            await self._ready_multiworld(message, runner_name)

    async def _join_race(self, message, runner_name):
        await self.join(runner_name)
        await reply_channel(message, 'player_joinrace', name=runner_name)

    async def _unjoin_race(self, message, runner_name):
        await self.unjoin(message.author.name)
        await self.check_remaining()

        await reply_channel(message, 'player_joinrace', name=message.author.name)

        is_done = await self.check_done()

        if is_done == 0 and self.time is not None:
            await self.stoprace()
            race_result = await self.results()
            await reply_channel_string(message, race_result)

        if len(self.runners) > 0 and is_done > 0:
            remaining = await self.check_remaining()

            if remaining == 0 and self.time is None:
                if self.type in ('open', 'standard', 'custom'):
                    await self.persist()
                    await reply_channel(message, 'countdown')

                    await asyncio.sleep(5)

                    for i in range(5, 0, -1):
                        await reply_channel_string(message, f"{i}")
                        await asyncio.sleep(1)

                    self.time = round(time.time())

                    await reply_channel(message, 'go')

    async def _done(self, message, runner_name):
        if self.runners[message.author.name]['done']:
            await reply_channel(message, 'alreadydone')
        else:
            if self.time is not None:
                await self.done(message.author.name)

                is_done = await self.check_done()
                if is_done == 0:
                    await self.stoprace()
                    result = await self.results()
                    await reply_channel_string(message, result)
                else:
                    await reply_channel(message, 'done', time=str(timedelta(
                        seconds=self.runners[message.author.name]['time'] - self.time
                    )))
            else:
                await reply_channel(message, 'notstarted')

    async def _ready_basic(self, message, runner_name):
        if runner_name in self.runners:
            await self.ready(message.author.name)

            remaining = await self.check_remaining()

            if remaining != 0:
                await reply_channel(message, 'remaining')
                return

            if self.type in ('open', 'standard', 'custom'):
                await self.persist()

                await reply_channel(message, 'countdown')

                await asyncio.sleep(5)

                for i in range(5, 0, -1):
                    await reply_channel_string(message, f"{i}")
                    await asyncio.sleep(1)

                self.time = round(time.time())
                await reply_channel(message, 'go')

    async def _ready_spoiler(self, message, runner_name):
        remaining = await self.check_remaining()

        if remaining != 0:
            await reply_channel_string(message, self.remaining)
            return

        self.time = round(time.time())
        await self.persist()

        await reply_channel(message, 'spoiler_starting_planning')
        await asyncio.sleep(1)
        await reply_channel(message, 'spoiler_starting_timer')

        for i in range(5, 0, -1):
            await reply_channel_string(message, f"{i}")
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        await reply_channel_string(message, "30 minutes left of planning phase")

        await asyncio.sleep(int(600 * DEV_MULTIPLIER))
        await reply_channel_string(message, "20 minutes left of planning phase")

        await asyncio.sleep(int(600 * DEV_MULTIPLIER))
        await reply_channel_string(message, "10 minutes left of planning phase")

        await asyncio.sleep(int(300 * DEV_MULTIPLIER))
        await reply_channel_string(message, "5 minutes left of planning phase")

        await asyncio.sleep(int(240 * DEV_MULTIPLIER))
        await reply_channel_string(message, "60 seconds left of planning phase")

        await asyncio.sleep(int(50 * DEV_MULTIPLIER))
        for i in range(5, 0, -1):
            await reply_channel_string(message, f"{i}")
            await asyncio.sleep(1)

        await reply_channel_string(message, "Planning phase is now completed. Start your Race Rom!")
        self.time = round(time.time())
        await asyncio.sleep(1)
        await reply_channel(message, 'go')

    async def _ready_multiworld(self, message, runner_name):
        remaining = await self.check_remaining()

        if remaining != 0:
            await reply_channel_string(message, self.remaining, num=remainig)
            return

        self.time = round(time.time())
        await self.persist()
