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
        def createrace(channel):
            race[message.channel] = Race()
            race[message.channel].state = False 
            race[message.channel].runners = {}
            race[message.channel].time = None
            race[message.channel].remaining = 0

        def write_json():
            ready = 0
            for runner in race[message.channel].runners:
                if race[message.channel].runners[runner]['ready']:
                    ready += 1

            f = open("/tmp/status.json", "w+")
            f.write(json.dumps({"race": race[message.channel].state,
                                "remaining": len(race[message.channel].runners)-ready,
                                "ready": ready,
                                "total": len(race[message.channel].runners),
                                "time": race[message.channel].time
                               }))
            f.close()

        def startrace():
            race[message.channel].state = True
            race[message.channel].runners = {}
            race[message.channel].time = None

        def stoprace():
            race[message.channel].state = False
            race[message.channel].remaining = 0
            #race[message.channel].runners = {}
            #race[message.channel].time = None

        def join():
            race[message.channel].runners[message.author.name] = {"ready": False, "done": False, "time": None}        

        def unjoin():
            del race[message.channel].runners[message.author.name] 

        def check_done():
            race[message.channel].done = 0
            for runner in race[message.channel].runners:
                if not race[message.channel].runners[runner]['done']:
                    race[message.channel].done += 1

        def check_remaining():
            race[message.channel].remaining = 0
            for runner in race[message.channel].runners:
                if not race[message.channel].runners[runner]['ready']:
                    race[message.channel].remaining += 1
 
        def ready():
            race[message.channel].runners[message.author.name]['ready'] = True

        def done():
            race[message.channel].runners[message.author.name]['done'] = True
            race[message.channel].runners[message.author.name]['time'] = round(time.time())


        if not os.path.isfile("/tmp/status.json"):
            write_json()
            
        if message.author.name == client.user: 
            return

        if message.channel not in race:
            createrace(message.channel)

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
            if race[message.channel].state:
                yield from client.send_message(message.channel, messages.alreadystarted)
            else:
                startrace()
                yield from client.send_message(message.channel, messages.startrace)

        if message.content.startswith(".stoprace"):
            if race[message.channel].state:
                stoprace()
                yield from client.send_message(message.channel, messages.stoprace) 
            else:
                yield from client.send_message(message.channel, messages.norace) 
    
        if message.content.startswith(".join") or message.content.startswith(".enter"):
            if race[message.channel].state:
                join()
                yield from client.send_message(message.channel, messages.joinrace(message.author.name))
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            if race[message.channel].state:
                unjoin()
                check_remaining()
                check_done()
                yield from client.send_message(message.channel, messages.quitrace(message.author.name))
    
                if race[message.channel].done == 0 and race[message.channel].time is not None:
                    stoprace()
                    yield from client.send_message(message.channel, race[message.channel].results())

                if len(race[message.channel].runners) > 0 and race[message.channel].done > 0:
                    if race[message.channel].remaining == 0:
                        write_json()
                        yield from client.send_message(message.channel, messages.countdown)
                        time.sleep(5)

                        for i in range(1, 6)[::-1]:
                            yield from client.send_message(message.channel, "{}".format(i))
                            time.sleep(1)

                        race[message.channel].time = round(time.time())

                        yield from client.send_message(message.channel, messages.go)
            else:
                yield from client.send_message(message.channel, messages.norace)
            
        if message.content.startswith(".ready"):
            if race[message.channel].state:
                if message.author.name in race[message.channel].runners:
                    ready()
                    check_remaining()
                    if race[message.channel].remaining == 0:
                        write_json()
                        yield from client.send_message(message.channel, messages.countdown)

                        time.sleep(5)

                        for i in range(1, 6)[::-1]:
                            yield from client.send_message(message.channel, "{}".format(i))
                            time.sleep(1)

                        race[message.channel].time = round(time.time())
                        yield from client.send_message(message.channel, messages.go)
                    else:    
                        yield from client.send_message(message.channel, messages.remaining(race[message.channel].remaining))
                else:
                    yield from client.send_message(message.channel, messages.notinrace)
            else:
                yield from client.send_message(message.channel, messages.norace)
                
            
        if message.content.startswith(".done"):
            if race[message.channel].state:
                if race[message.channel].runners[message.author.name]['done']: 
                    yield from client.send_message(message.channel, messages.alreadydone)
                else:
                    if race[message.channel].time is not None:
                        done() 
                        check_done()
                        if race[message.channel].done == 0:
                            stoprace()
                            yield from client.send_message(message.channel, race[message.channel].results())
                        else: 
                            yield from client.send_message(message.channel, messages.done(str(timedelta(seconds=race[message.channel].runners[message.author.name]['time']-race[message.channel].time))))
                    else:
                        yield from client.send_message(message.channel, messages.notstarted)
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".runners") or message.content.startswith(".list"):
            if race[message.channel].state:
                for runner in race[message.channel].runners:
                    yield from client.send_message(message.channel, runner)
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".persist"):
            race[message.channel].persist()
        if message.content.startswith(".result"):
            yield from client.send_message(message.channel, race[message.channel].results())

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
            write_json()
        
        

