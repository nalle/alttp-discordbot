import json
import requests


class SeedGenerator():

    valid_seed_commands = {
        'logic': ['NoGlitches'],
        'difficulty': ['normal', 'hard', 'expert'],
        'variation': ['keysanity', 'retro'],
        'mode': ['standard', 'open', 'swordless'],
        'goal': ['ganon', 'pedistal', 'dungeons', 'triforcehunt', 'crystals'],
        'weapons': ['randomized'],
        'tournament': [True, False],
        'spoiler': [True, False],
        'enemizer': [True, False],
        'lang': ['en']
    }

    def __init__(self):
        self.headers = {
            'Origin': 'https://alttpr.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,sv;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://alttpr.com/en/randomizer',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

    def generate_open(self, **kwargs):
        return self.generate_seed(mode='open')

    def generate_standard(self, **kwargs):
        return self.generate_seed(mode='standard')

    def generate_spoiler(self, **kwargs):
        return self.generate_seed(spoiler=True)

    def generate_seed(self,
        logic='NoGlitches', difficulty='normal', variation=None, mode='standard',
        goal='ganon', weapons='randomized', tournament=True, spoilers=False, enemizer=False,
        lang='en',
    ):
        if logic not in self.valid_seed_commands['logic']:
            raise Exception(f"Invalid argument '{logic}' for argument 'logic' when generating a seed")

        data = {}

        data["logic"] = logic
        data["difficulty"] = difficulty
        if variation:
            data["variation"] = variation
        data["mode"] = mode
        data["goal"] = goal
        data["weapons"] = weapons
        data["tournament"] = tournament
        data["spoilers"] = spoilers
        data["enemizer"] = enemizer
        data["lang"] = lang

        # for key, value in kwargs.items():
        #     data[key] = value

        r = requests.get("https://alttpr.com/seed", data=json.dumps(data), headers=self.headers)

        if r.status_code == 200:
            return "https://alttpr.com/en/h/{}".format(json.loads(r.text)['hash'])
        else:
            return False