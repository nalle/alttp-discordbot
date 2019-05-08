import discord
import os
import json
import asyncio
import time
from datetime import timedelta
from bot.runner import Runner
from bot.race import Race
from bot.messages import Messages
from bot.seed import SeedGenerator

import aioredis

all_races = {}
messages = Messages()
seed = SeedGenerator()

# Allow for devs to speedup the timer execution time if needed
if 'DEV' in os.environ:
    DEV_MULTIPLIER = 0.0083
else:
    DEV_MULTIPLIER = 1


class Client(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(messages.bootup)

    async def on_ready(self):
        print(f'Logged on as {self.user}')

        redis_host = os.environ.get('REDIS_HOST') or "redis://localhost"
        redis_password = os.environ.get('REDIS_PASSWORD') or None

        self.redis = await aioredis.create_redis(redis_host, loop=self.loop, password=redis_password)

        print(f'Database connection to redis established : {redis_host}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        main_loop = self.main_loop(message)

        async for return_message in main_loop:
            print(f" - Returning message : {return_message}")
            await message.channel.send(return_message)

    async def main_loop(self, message):
        channel_name = message.channel.name

        race = all_races.get(channel_name, None)

        if not race:
            race = Race(channel_name, self.redis)
            await race.initialize(channel_name)
            await race.persist()

        if message.content.startswith(".races"):
            current_races = {}

            for d, r in all_races.items():
                current_races[d.name] = {
                    "state": r.state,
                    "time": r.time,
                    "runners": {}
                }

                for runner in r.runners:
                    current_races[d.name]['runners'][runner] = {
                        "ready": r.runners[runner]['ready'],
                        "done": r.runners[runner]['done'],
                        "time": r.runners[runner]['time'],
                    }

            yield current_races

        if message.content.startswith(".startrace"):
            if race.state:
                yield messages.alreadystarted
            else:
                await race.startrace()
                yield messages.startrace

        if message.content.startswith(".stoprace"):
            if not race.state:
                yield messages.norace
                return

            await race.stoprace()
            yield messages.stoprace

        #
        # Send the command to the race to allow for it to process and to run any specific action for the given race type
        #
        # await race.parse_message(message.content)
        async for return_message in race.parse_message(message):
            yield return_message

        if message.content.startswith(".runners") or message.content.startswith(".list"):
            if race.state:
                for runner in race.runners:
                    yield runner
            else:
                yield messages.norace

        # if message.content.startswith(".msgme"):
        #     await message.author.send('hello...', file=discord.File('foobar.txt', 'foobar.txt'))

        if message.content.startswith(".persist"):
            await race.persist()

        if message.content.startswith(".print"):
            print_result = await race.print()
            yield print_result

        if message.content.startswith(".result"):
            race_result = await race.results()
            yield race_result

        if message.content.startswith(".standard"):
            yield messages.generating_seed
            yield f"{seed.generate_standard()}"
            race.type = "standard"
            await race.persist()

        if message.content.startswith(".open"):
            yield messages.generating_seed
            yield f"{seed.generate_open()}"
            race.type = "open"
            await race.persist()

        if message.content.startswith(".spoiler"):
            yield messages.generating_seed
            yield f"{seed.generate_spoiler()}"
            race.type = "spoiler"
            await race.persist()

        if message.content.startswith(".generate"):
            yield messages.generating_seed

            args = message.content.split(" ")
            kwargs = {}

            for arg in args:
                if ".generate" not in arg:
                    key, value = arg.split("=")
                    kwargs[key] = value

                    yield f"{seed.generate_seed(**kwargs)}"

            race.type = "custom"
            await race.persist()

        if message.content.startswith("."):
            await race.persist()
