import asyncio
import os
from bot.client import Client


discord_token = os.environ['DISCORD_TOKEN']

# Create our eventloop and put it into discord client
# and the Client class will put it into the aioredis client
loop = asyncio.get_event_loop()

discord = Client(loop=loop)
discord.run(discord_token)
