import requests
import json

class SeedGenerator():
    def __init__(self):
        self.headers = {     
                    'Origin': 'https://alttpr.com',
                    'X-XSRF-TOKEN': 'eyJpdiI6Ik5rUE1yays0TGcxU3ZlQW15bWR4REE9PSIsInZhbHVlIjoiQUFcLzhRcW9BVmRuRDBPSTl5Z1ZvTk9hc3FzZHdDamFcLzU2aElndmRWZXZTOThhcjVMak15clF4aUNWV1RLUlJtIiwibWFjIjoiMzA5NDAzNWFjYzUzNTNlMjk3NWRiZTRhZjBkYTJjMDdlYWZiZjgxYjk5NGRmNzE4MTA4NzYxNWU1NjdlMjAyMiJ9',
                    'X-CSRF-TOKEN': 'GXGdvDspxXnaSp7BcD2Zjd33pHsE5CwfCCDQ7sUU',
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
