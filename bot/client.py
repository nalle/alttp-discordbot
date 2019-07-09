import discord
import os
import json
import asyncio
import time
import random
import requests
from datetime import timedelta
from bot.runner import Runner
from bot.race import Race
from bot.messages import reply_channel, message_mapping, reply_channel_string
from bot.seed import SeedGenerator
from bot.sprites import sprites

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

    async def random(self, start, stop):
        r = requests.get("https://www.random.org/integers/?num=1&min={start}&max={stop}&col=1&base=10&format=plain&rnd=new".format(start=start,stop=stop))
        if r.status_code != 200:
            return random.randint(start, stop)

        return r.text

    async def get_dice_face(self, number):
        return chr(9855+int(number))

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

        channel_name = str(message.channel.id)

        race = all_races.get(channel_name, None)

        if not race:
            race = Race(channel_name, self.redis)
            await race.initialize(channel_name, self)
            await race.persist()

        if message.content.startswith(".roll"):
            await reply_channel(message, 'dice_roll', dice=await self.get_dice_face(await self.random(1,6)))

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

        if message.content.startswith(".help"):
            args = message.content.split()
            if len(args) > 1:
                if args[1] == "multiworld":
                    await reply_channel(message, 'multiworld_help')
                    return
                elif args[1] == "settings":
                    await reply_channel(message, 'settings_help')
                    return 
                elif args[1] == "sprites":
                    sprite_help = ""
                    for i, item in enumerate(sorted(sprites.items())):
                        if i % 8 == 1 and i > 1: 
                            sprite_help += "\n"
                        sprite_help += item[0]+", "
                    sprite_help = sprite_help[:-2]
                    await reply_channel(message, 'sprites', sprites=sprite_help)
                    return

            await reply_channel(message, 'basic_help')
            return

        if message.content == ".startrace":
            if race.state:
                await reply_channel(message, 'alreadystarted')
            else:
                await race.startrace()
                await reply_channel(message, 'startrace')

        if message.content.startswith(".startrace multiworld") or message.content.startswith(".startrace mulitworld"):
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

        if message.content.startswith('.unset'):
            arg = message.content.split()
            settings = await self.redis.hgetall(message.author.id)
            if arg[1] in ['notifications','heartbeep','heartcolor','sprite']:
                await self.redis.hdel(message.author.id, arg[1])
                await reply_channel(message, 'unset_setting_successful', setting=arg[1], name=message.author.name)
            else:
                await reply_channel(message, 'unsupported_setting', setting=arg[1])
            return

        if message.content.startswith('.defaults'):
            settings = await self.redis.hgetall(message.author.id)
            await reply_channel(message, 'list_settings', name=message.author.name, settings=settings)
            return

        if message.content.startswith('.set'):
            arg = message.content.split()
            if len(arg) < 3:
                await reply_channel(message, 'missing_arguments')
                return

            if arg[1] not in ['sprite','heartbeep','heartcolor','notifications']:
                await reply_channel(message, 'unsupported_setting', setting=arg[1])
                return

            if arg[1] == "sprite":
                if arg[2] not in sprites:
                    await reply_channel(message, 'no_such_sprite')
                    return
                arg[2] = sprites[arg[2]]

            if arg[1] == "heartbeep":
                if arg[2] not in ['double','normal','half','quarter','off']:
                    await reply_channel(message, 'heartbeep_help')
                    return

            if arg[1] == "heartcolor":
                if arg[2] not in ['red','blue','green','yellow','random']:
                    await reply_channel(message, 'heartcolor_help')
                    return

            if arg[1] == "notifications":
                if arg[2].lower() not in ['true','false','on','off','1','0','yes','no']:
                    await reply_channel(message, 'notifications_help')
                    return

                if arg[2].lower() in ['true','on','1','yes']:
                    arg[2] = "true"
                else: 
                    arg[2] = "false"

            await self.redis.hset(message.author.id, arg[1], arg[2])
            await reply_channel(message, 'set_setting_successful', setting=arg[1], name=message.author.name)
            return

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

        if message.content.startswith(".keysanity"):
            async with message.channel.typing():
                await reply_channel(message, 'generating_seed')
                generated_seed = seed.generate_keysanity()
                await reply_channel_string(message, generated_seed)
                race.type = "keysanity"
                await race.persist()

        if message.content.startswith(".inverted"):
            async with message.channel.typing():
                await reply_channel(message, 'generating_seed')
                generated_seed = seed.generate_inverted()
                await reply_channel_string(message, generated_seed)
                race.type = "inverted"
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
