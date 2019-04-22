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



class Client(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(messages.bootup)

    async def on_ready(self):
        print(f'Logged on as {self.user}')

        redis_host = os.environ.get('REDIS_HOST') or None
        redis_password = os.environ.get('REDIS_PASSWORD') or None

        self.redis = await aioredis.create_redis('redis://localhost', loop=self.loop)

        print(f'Database connection to redis established : {redis_host}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        main_loop = self.main_loop(message)

        async for return_message in main_loop:
            print(f"Returning message : {return_message}")
            await message.channel.send(return_message)

    async def main_loop(self, message):
        channel_name = message.channel.name

        race = all_races.get(channel_name, None)

        if not race:
            race = Race(channel_name, self.redis)
            await race.initialize(channel_name)
            race.persist()

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
