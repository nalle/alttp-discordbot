message_mapping = {
    'bootup': 'Discord bot is booting up...',
    'login_successful': 'Login to discord was successful',
    'startrace': "A race has been started.",
    'alreadystarted': "A race is already started.",
    'alreadydone': "You have already been marked as done.",
    'unknown_race_type': "ERROR: Unknown race type set on race...",
    'norace': "There is currently no race started.",
    'player_joinrace': "{name} has joined the race.",
    'player_quitrace': "{name} has quit the race.",
    'countdown': "All players are now ready, counting down from 10...",
    'go': "GO!",
    'remaining': "{name} is ready! {num} players remaining.",
    'done': "{name} has finished at {time}.",
    'spoiler_starting_planning': "Starting planning phase spoiler-log race. Download the spoiler-log file and you have 30 minutes to study it.",
    'spoiler_starting_timer': "Starting timer in 5 seconds.",
    'stoprace': "The race has been stopped.",
    'generating_seed': "Generating seed, please wait.",
    'multiworld_alreadystarted': 'There is already a multiworld race is already started.',
    'multiworld_startrace': 'A multiworld race has been started.',
    'multiworld_notstarted': "There is currently no multiworld race.",
    'multiworld_seed_generation_done': 'Seed generation has completed and server has been started. Sending out server information and ROMs to players.',
    'multiworld_tell_player_to_start': 'Please start you emulator and load the provided rom, start your multiworld client with the provided command.',
}


async def reply_channel(message_instance, message_key, **kwargs):
    print("Printing message : ", message_instance, message_key, kwargs)
    await message_instance.channel.send(message_mapping[message_key].format(**kwargs))

async def reply_channel_string(message_instance, message_string, **kwargs):
    print("Printing message string : ", message_instance, kwargs)
    await message_instance.channel.send(message_string)
