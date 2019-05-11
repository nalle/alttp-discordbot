class Messages():
    @property
    def bootup(self):
        return "ALTTP Racebot is booting up"

    @property
    def login_successful(self):
        return "Login successful"

    @property
    def alreadystarted(self):
        return "My dude :( a race is already started!"

    @property
    def startrace(self):
        return "A race! Nice my dude, type .join to participate!"

    @property
    def stoprace(self):
        return "Ooh no my dude :( the race is no more"

    @property
    def norace(self):
        return "Duuuude, no race is running.. better got up on that"

    def joinrace(self, name):
        return "Welcome my dude {}!".format(name)

    def quitrace(self, name):
        return "Sad to see you go my dude {}!".format(name)

    @property
    def countdown(self):
        return "Aww yeah! Lets get this party started! Counting down from 10.."

    @property
    def go(self):
        return "GO GO GO"

    def remaining(self, num):
        return "My dude, we're so pumped! Waiting for {} players".format(num)

    @property
    def alreadydone(self):
        return "But dude, you're already finished?!"

    def done(self, time):
        return "Dude, {}! SICK, gg wp".format(time)

    @property
    def notstarted(self):
        return "Dude, don't jump the gun.. race hasn't even started yet!"

    @property
    def generating_seed(self):
        return "Imma let you finish but there's a seed coming your way soon"


message_mapping = {
    'bootup': 'ALTTP Racebot is booting up',
    'login_successful': 'Login successful',
    'startrace': "A race! Nice my dude, type .join to participate!",
    'alreadystarted': "My dude :( a race is already started!",
    'unknown_race_type': "ERROR: Unknown race type set on race...",
    'norace': "Duuuude, no race is running.. better got up on that",
    'player_joinrace': "Welcome my dude {name}!",
    'quitrace': "Sad to see you go my dude {name}!",
    'countdown': "Aww yeah! Lets get this party started! Counting down from 10..",
    'go': "GO GO GO",
    'remaining': "My dude, we're so pumped! Waiting for {num} players",
    'done': "Dude, {time}! SICK, gg wp",
    'spoiler_starting_planning': "Starting planning phase spoiler log race. Download the spoiler log file and you have 30 minutes to study it",
    'spoiler_starting_timer': "Starting timer in 5 seconds",
    'stoprace': "Ooh no my dude :( the race is no more",

    'multiworld_alreadystarted': 'There is already a multiworld seed running...',
    'multiworld_startrace': 'Starting multiworld race...',
    'multiworld_notstarted': "Dude, don't jump the gun.. race hasn't even started yet!",
    'multiworld_seed_generation_done': 'Seed generation and server is started. Starting to send out roms and configuraation',
    'multiworld_tell_player_to_start': 'Now when you have all information sent to all of the participants, start you emulator and load the provided rom, and start your multiworld client with the provided command',
}


async def reply_channel(message_instance, message_key, **kwargs):
    print("Printing message : ", message_instance, message_key, kwargs)
    await message_instance.channel.send(message_mapping[message_key].format(**kwargs))

async def reply_channel_string(message_instance, message_string, **kwargs):
    print("Printing message string : ", message_instance, kwargs)
    await message_instance.channel.send(message_string)
