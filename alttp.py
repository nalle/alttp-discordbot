import queue
import time
import os
from bot import client


discord = client.Client()
discord.run(os.environ['DISCORD_TOKEN'])
