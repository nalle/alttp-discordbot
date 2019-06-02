# alttp-discordbot

To update sprit list:

TMP=$(find ~/Code/multiworld/multiworld-server/ALttPEntranceRandomizer/ -iname *.zspr | sed -r 's#.*((/data/sprites/official/|/data/)([a-zA-Z0-9_-]+)\.[0-9]?\.?zspr)#"\3": "/opt/ALttPEntranceRandomizer\1",#g'); echo sprites = {$TMP | sed -r 's/,$/}/g' > bot/sprites.py
