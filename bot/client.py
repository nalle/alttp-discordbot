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

race = {}
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

        redis = await aioredis.create_redis('redis://localhost', loop=self.loop)
        self.redis = redis

    async def on_message(self, message):
        if message.author == self.user:
            return

        for return_message in self.main_loop(message):
            print(f"Returning message : {return_message}")
            await message.channel.send(return_message)

    def main_loop(self, message):
        # if message.channel.name not in race:
            # race[message.channel.name] = Race(message.channel.name)
            # race[message.channel.name].persist()

        if message.content.startswith(".races"):
            races = {}

            for d, r in race.items():
                races[d.name] = {
                    "state": r.state,
                    "time": r.time,
                    "runners": {}
                }

                for runner in r.runners:
                    races[d.name]['runners'][runner] = {
                        "ready": r.runners[runner]['ready'],
                        "done": r.runners[runner]['done'],
                        "time": r.runners[runner]['time'],
                    }

            yield races
