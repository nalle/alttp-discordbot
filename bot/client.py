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

client = discord.Client()
race = {}
messages = Messages()
seed = SeedGenerator()

class Client():
    def __init__(self): 
        print(messages.bootup)

    @client.event
    @asyncio.coroutine
    def on_ready():
        print(messages.login_successful)

    def run(self, token):
        while True:
            try:
                client.loop.run_until_complete(client.start(token))
            except KeyboardInterrupt:
                client.loop.run_until_complete(client.logout())
            finally:
                client.close()

    @client.event
    @asyncio.coroutine
    def on_message(message):
        if message.author.name == client.user: 
            return

        if message.channel.name not in race:
            race[message.channel.name] = Race(message.channel.name)
            race[message.channel.name].persist()

        if message.content.startswith(".races"):
            races = {}
            for d, r in race.items():
                races[d.name] = { 
                                "state": r.state,
                                "time": r.time,
                                "runners": {
                                }
                               }
                for runner in r.runners:
                    races[d.name]['runners'][runner] = {"ready": r.runners[runner]['ready'], "done": r.runners[runner]['done'], "time": r.runners[runner]['time']}

            yield from client.send_message(message.channel, races)
    
        if message.content.startswith(".startrace"):
            if race[message.channel.name].state:
                yield from client.send_message(message.channel, messages.alreadystarted)
            else:
                race[message.channel.name].startrace()
                yield from client.send_message(message.channel, messages.startrace)

        if message.content.startswith(".stoprace"):
            if race[message.channel.name].state:
                race[message.channel.name].stoprace()
                yield from client.send_message(message.channel, messages.stoprace) 
            else:
                yield from client.send_message(message.channel, messages.norace) 
    
        if message.content.startswith(".join") or message.content.startswith(".enter"):
            if race[message.channel.name].state:
                race[message.channel.name].join(message.author.name)
                yield from client.send_message(message.channel, messages.joinrace(message.author.name))
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            if race[message.channel.name].state:
                race[message.channel.name].unjoin(message.author.name)
                race[message.channel.name].check_remaining()
                yield from client.send_message(message.channel, messages.quitrace(message.author.name))
    
                if race[message.channel.name].check_done() == 0 and race[message.channel.name].time is not None:
                    race[message.channel.name].stoprace()
                    yield from client.send_message(message.channel, race[message.channel.name].results())

                if len(race[message.channel.name].runners) > 0 and race[message.channel.name].check_done() > 0:
                    if race[message.channel.name].remaining() == 0:
                        race[message.channel.name].persist()
                        yield from client.send_message(message.channel, messages.countdown)
                        time.sleep(5)

                        for i in range(1, 6)[::-1]:
                            yield from client.send_message(message.channel, "{}".format(i))
                            time.sleep(1)

                        race[message.channel.name].time = round(time.time())

                        yield from client.send_message(message.channel, messages.go)
            else:
                yield from client.send_message(message.channel, messages.norace)
            
        if message.content.startswith(".ready"):
            if race[message.channel.name].state:
                if message.author.name in race[message.channel.name].runners:
                    race[message.channel.name].ready(message.author.name)
                    if race[message.channel.name].check_remaining() == 0:
                        race[message.channel.name].persist()
                        yield from client.send_message(message.channel, messages.countdown)

                        time.sleep(5)

                        for i in range(1, 6)[::-1]:
                            yield from client.send_message(message.channel, "{}".format(i))
                            time.sleep(1)

                        race[message.channel.name].time = round(time.time())
                        yield from client.send_message(message.channel, messages.go)
                    else:    
                        yield from client.send_message(message.channel, messages.remaining(race[message.channel.name].remaining))
                else:
                    yield from client.send_message(message.channel, messages.notinrace)
            else:
                yield from client.send_message(message.channel, messages.norace)
                
            
        if message.content.startswith(".done"):
            if race[message.channel.name].state:
                if race[message.channel.name].runners[message.author.name]['done']: 
                    yield from client.send_message(message.channel, messages.alreadydone)
                else:
                    if race[message.channel.name].time is not None:
                        race[message.channel.name].done(message.author.name) 
                        if race[message.channel.name].check_done() == 0:
                            race[message.channel.name].stoprace()
                            yield from client.send_message(message.channel, race[message.channel.name].results())
                        else: 
                            yield from client.send_message(message.channel, messages.done(str(timedelta(seconds=race[message.channel.name].runners[message.author.name]['time']-race[message.channel.name].time))))
                    else:
                        yield from client.send_message(message.channel, messages.notstarted)
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".runners") or message.content.startswith(".list"):
            if race[message.channel.name].state:
                for runner in race[message.channel.name].runners:
                    yield from client.send_message(message.channel, runner)
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".persist"):
            race[message.channel.name].persist()

        if message.content.startswith(".print"):
            yield from client.send_message(message.channel, race[message.channel.name].print())

        if message.content.startswith(".result"):
            yield from client.send_message(message.channel, race[message.channel.name].results())

        if message.content.startswith(".standard"):
            yield from client.send_message(message.channel, messages.generating_seed)
            yield from client.send_message(message.channel, "{}".format(seed.generate()))

        if message.content.startswith(".open"):
            yield from client.send_message(message.channel, messages.generating_seed)
            yield from client.send_message(message.channel, "{}".format(seed.generate(mode="open")))

        if message.content.startswith(".generate"):
            yield from client.send_message(message.channel, messages.generating_seed)
            args = message.content.split(" ")
            kwargs = {}
            for arg in args:
                if ".generate" not in arg:
                    key, value = arg.split("=")
                    kwargs[key] = value

            yield from client.send_message(message.channel, "{}".format(seed.generate(**kwargs)))

        if message.content.startswith("."):
            race[message.channel.name].persist()
