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
    'debug': 'One personalization done',
    'no_such_sprite': 'No such sprite available.',
    'heartbeep_help': 'Valid heartbeep settings are double, normal, half, quarter or off.',
    'heartcolor_help': 'Valid heartcolors are red, blue, green, yellow or random.',
    'notifications_help': 'Valid notification settings are true or false.',
    'unsupported_setting': 'Unsupported setting {setting}, valid settings are notifications, sprite, heartbeep and heartcolor.',
    'set_setting_successful': 'Default {setting} for {name} has been set.',
    'unset_setting_successful': 'Default {setting} for {name} has been removed.',
    'missing_arguments': 'Too few arguments, setting and value are required.',
    'list_settings': 'Settings for {name} are:\n{settings}',
    'setting': 'Setting is {setting}',
    'basic_help': '''```
  .startrace                  - Creates a race that players can join.
  .stoprace                   - Stops an already started race.
  .join                       - Joins a race.
  .unjoin                     - Leave a race.
  .quit
  .forfeit
  .ready                      - Ready for race, will start a countdown when all players are marked ready.
  .unready                    - Remove yourself as ready in a race.
  .standard                   - Generates a seed with state Standard
  .open                       - Generates a seed with state Open
  .keysanity                  - Generates a seed with state Open and variation Keysanity
  .inverted                   - Generates a seed with state Inverted
  .generate [type]=[value]    - Generates a seed using settings supplied settings, types can be:
                                        logic: [NoGlitches],
                                        difficulty: [normal, hard, expert],
                                        variation: [keysanity, retro],
                                        mode: [standard, open, swordless,inverted],
                                        goal: [ganon, pedistal, dungeons, triforcehunt, crystals],
                                        weapons: [randomized],
                                        tournament: [True, False],
                                        spoiler: [True, False],
                                        enemizer: [True, False],
                                        lang: [en]

  .help settings              - List settings    
  .help multiworld            - For multiworld specific help
  .help sprites               - List all sprites available
             ```''',
    'settings_help':'''```
   .set [setting] [value]     - Sets a setting to a vaule to use by default, valid settings are:
        sprite [value]        - Sets the seed sprite to use, use .help sprites for a list of valid sprites
        heartbeep [value]     - Sets heartbeep speed, valid settings are [double,normal,half,quarter,off]
        heartcolor [value]    - Sets heartcolor, valid settings are [red,green,blue,yellow,random]
        notifications [value] - Sets notifications on and off, valid settings are [on,off] (multiworld specific setting)
               ```''',
    'multiworld_help': '''```
   .startrace multiworld      - Starts a multiworld race.
   .stoprace                  - Stops an already started race.
   .join                      - Joins a race.
   .unjoin                    - Leave a race.
   .quit
   .forfeit     
   .ready                     - Ready for race, will start a countdown when all players are marked ready. Should never be run before .generate
                                unless you know what you're doing!  
   .generate                  - Starts generating a multiworld seed, once completed it will send these to each player togther with server information.
             ```''',
    'sprites': 'Available sprites are: \n{sprites}',
}


async def reply_channel(message_instance, message_key, **kwargs):
    print("Printing message : ", message_instance, message_key, kwargs)
    await message_instance.channel.send(message_mapping[message_key].format(**kwargs))

async def reply_channel_string(message_instance, message_string, **kwargs):
    print("Printing message string : ", message_instance, kwargs)
    await message_instance.channel.send(message_string)
