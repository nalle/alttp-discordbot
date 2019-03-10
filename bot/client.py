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
race = Race()
messages = Messages()
seed = SeedGenerator()

class Client():
    def __init__(self): 
        print(messages.bootup)
        race.state = False 
        race.runners = {}
        race.time = None
        race.remaining = 0

        
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
        def write_json():
            ready = 0
            for runner in race.runners:
                if race.runners[runner]['ready']:
                    ready += 1

            f = open("/tmp/status.json", "w+")
            f.write(json.dumps({"race": race.state,
                                "remaining": len(race.runners)-ready,
                                "ready": ready,
                                "total": len(race.runners),
                                "time": race.time
                               }))
            f.close()

        def startrace():
            race.state = True
            race.runners = {}
            race.time = None

        def stoprace():
            race.state = False
            race.remaining = 0
            #race.runners = {}
            #race.time = None

        def join():
            race.runners[message.author.name] = {"ready": False, "done": False, "time": None}        

        def unjoin():
            del race.runners[message.author.name] 

        def check_done():
            race.done = 0
            for runner in race.runners:
                if not race.runners[runner]['done']:
                    race.done += 1

        def check_remaining():
            race.remaining = 0
            for runner in race.runners:
                if not race.runners[runner]['ready']:
                    race.remaining += 1
 
        def ready():
            race.runners[message.author.name]['ready'] = True

        def done():
            race.runners[message.author.name]['done'] = True
            race.runners[message.author.name]['time'] = round(time.time())


        if not os.path.isfile("/tmp/status.json"):
            write_json()
            
        if message.author.name == client.user: 
            return
    
        if message.content.startswith(".startrace"):
            if race.state:
                yield from client.send_message(message.channel, messages.alreadystarted)
            else:
                startrace()
                yield from client.send_message(message.channel, messages.startrace)

        if message.content.startswith(".stoprace"):
            if race.state:
                stoprace()
                yield from client.send_message(message.channel, messages.stoprace) 
            else:
                yield from client.send_message(message.channel, messages.norace) 
    
        if message.content.startswith(".join") or message.content.startswith(".enter"):
            if race.state:
                join()
                yield from client.send_message(message.channel, messages.joinrace(message.author.name))
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".unjoin") or message.content.startswith(".quit") or message.content.startswith(".forfeit"):
            if race.state:
                unjoin()
                check_remaining()
                check_done()
                yield from client.send_message(message.channel, messages.quitrace(message.author.name))
    
                if race.done == 0 and race.time is not None:
                    stoprace()
                    yield from client.send_message(message.channel, race.results())

                if len(race.runners) > 0 and race.done > 0:
                    if race.remaining == 0:
                        write_json()
                        yield from client.send_message(message.channel, messages.countdown)
                        time.sleep(5)

                        for i in range(1, 6)[::-1]:
                            yield from client.send_message(message.channel, "{}".format(i))
                            time.sleep(1)

                        race.time = round(time.time())

                        yield from client.send_message(message.channel, messages.go)
            else:
                yield from client.send_message(message.channel, messages.norace)
            
        if message.content.startswith(".ready"):
            if race.state:
                if message.author.name in race.runners:
                    ready()
                    check_remaining()
                    if race.remaining == 0:
                        write_json()
                        yield from client.send_message(message.channel, messages.countdown)

                        time.sleep(5)

                        for i in range(1, 6)[::-1]:
                            yield from client.send_message(message.channel, "{}".format(i))
                            time.sleep(1)

                        race.time = round(time.time())
                        yield from client.send_message(message.channel, messages.go)
                    else:    
                        yield from client.send_message(message.channel, messages.remaining(race.remaining))
                else:
                    yield from client.send_message(message.channel, messages.notinrace)
            else:
                yield from client.send_message(message.channel, messages.norace)
                
            
        if message.content.startswith(".done"):
            if race.state:
                if race.runners[message.author.name]['done']: 
                    yield from client.send_message(message.channel, messages.alreadydone)
                else:
                    if race.time is not None:
                        done() 
                        check_done()
                        if race.done == 0:
                            stoprace()
                            yield from client.send_message(message.channel, race.results())
                        else: 
                            yield from client.send_message(message.channel, messages.done(str(timedelta(seconds=race.runners[message.author.name]['time']-race.time))))
                    else:
                        yield from client.send_message(message.channel, messages.notstarted)
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".runners") or message.content.startswith(".list"):
            if race.state:
                for runner in race.runners:
                    yield from client.send_message(message.channel, runner)
            else:
                yield from client.send_message(message.channel, messages.norace)

        if message.content.startswith(".persist"):
            race.persist()
        if message.content.startswith(".result"):
            yield from client.send_message(message.channel, race.results())

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
        
        

