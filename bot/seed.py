import requests
import json

class SeedGenerator():
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
                    'Connection': 'keep-alive' 
                  }

    def generate(self, **kwargs):
        data = {
                "logic":"NoGlitches",
                "difficulty":"normal",
                "variation":"none",
                "mode":"standard",
                "goal":"ganon",
                "weapons":"randomized",
                "tournament": True,
                "spoilers": False,
                "enemizer": False,
                "lang":"en"
               }
        
        for key, value in kwargs.items():
            data[key] = value
        
        r = requests.get("https://alttpr.com/seed", data=json.dumps(data), headers=self.headers)

        if r.status_code == 200:
            return "https://alttpr.com/en/h/{}".format(json.loads(r.text)['hash'])
        else: 
            return False
