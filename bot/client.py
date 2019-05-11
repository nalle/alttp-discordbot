import discord
import os
import json
import asyncio
import time
from datetime import timedelta
from bot.runner import Runner
from bot.race import Race
from bot.messages import reply_channel, message_mapping, reply_channel_string
from bot.seed import SeedGenerator

import aioredis

all_races = {}
seed = SeedGenerator()

# Allow for devs to speedup the timer execution time if needed
if 'DEV' in os.environ:
    DEV_MULTIPLIER = 0.0083
else:
    DEV_MULTIPLIER = 1


class Client(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(message_mapping['bootup'])

    async def on_ready(self):
        print(f'Logged on as {self.user}')

        redis_host = os.environ.get('REDIS_HOST') or "localhost"
        redis_port = os.environ.get('REDIS_PORT') or 6379
        redis_password = os.environ.get('REDIS_PASSWORD') or None

        redis_url = "redis://{}".format(redis_host)

        self.redis = await aioredis.create_redis(redis_url, loop=self.loop, password=redis_password)

        print(f'Database connection to redis established : {redis_host}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        channel_name = message.channel.name

        race = all_races.get(channel_name, None)

        if not race:
            race = Race(channel_name, self.redis)
            await race.initialize(channel_name, self)
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

            await reply_channel_string(message, current_races)

        if message.content == ".startrace":
            if race.state:
                await reply_channel(message, 'alreadystarted')
            else:
                await race.startrace()
                await reply_channel(message, 'startrace')

        if message.content.startswith(".startrace multiworld"):
            if race.state:
                await reply_channel(message, 'multiworld_alreadystarted')
            else:
                await race.startrace()
                race.type = 'multiworld'
                await race.persist()

                await reply_channel(message, 'multiworld_startrace')

        if message.content.startswith(".stoprace"):
            if not race.state:
                await reply_channel(message, 'norace')
                return

            await race.stoprace()
            await reply_channel(message, 'stoprace')

        #
        # Send the command to the race to allow for it to process and to run any specific action for the given race type
        #
        await race.parse_message(message)

        if message.content.startswith(".runners") or message.content.startswith(".list"):
            if race.state:

                runners = ""
                for runner in race.runners:
                    runners += runner + "\n"

                await reply_channel_string(message, runners)
            else:
                await reply_channel(message, 'norace')

        if message.content.startswith(".persist"):
            await race.persist()

        if message.content.startswith(".print"):
            print_result = await race.print()
            await reply_channel_string(message, print_result)

        if message.content.startswith(".result"):
            race_result = await race.results()
            await reply_channel_string(message, race_result)

        if message.content.startswith(".standard"):
            async with message.channel.typing():
                await reply_channel(message, 'generating_seed')
                generated_seed = seed.generate_standard()
                await reply_channel_string(message, generated_seed)
                race.type = "standard"
                await race.persist()

        if message.content.startswith(".open"):
            async with message.channel.typing():
                await reply_channel(message, 'generating_seed')
                generated_seed = seed.generate_open()
                await reply_channel_string(message, generated_seed)
                race.type = "open"
                await race.persist()

        if message.content.startswith(".spoiler"):
            async with message.channel.typing():
                await reply_channel(message, 'generating_seed')
                generated_seed = seed.generate_spoiler()
                await reply_channel_string(message, generated_seed)
                race.type = "spoiler"
                await race.persist()

        # if message.content.startswith(".generate"):
        #     yield messages.generating_seed

        #     args = message.content.split(" ")
        #     kwargs = {}

        #     for arg in args:
        #         if ".generate" not in arg:
        #             key, value = arg.split("=")
        #             kwargs[key] = value

        #             yield f"{seed.generate_seed(**kwargs)}"

        #     race.type = "custom"
        #     await race.persist()

        if message.content.startswith("."):
            await race.persist()
