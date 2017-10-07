# ChaoticBot

## Prerequisites

### Software
* Python 3.6 or newer
* virtualenv
### Tokens and Keys
* google oauth token (json file) [more info here](http://gspread.readthedocs.io/en/latest/oauth2.html)
* wow api token / secret [more info here](https://dev.battle.net/member/register)
* discord token [more info here](https://discordpy.readthedocs.io/en/rewrite/discord.html)

## Installation

```
$ git clone https://github.com/fspijkerman/ChaoticBot.git
$ cd ChaoticBot
$ python3 -mvenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Configuration

```
$ cp config.py-example config.py
```
Edit `config.py` and make sure you set the following variables correctly:

* `token` (discord)
* `client_id` (discord)
* `wow_api_key`
* `wow_api_secret`

Get the google oauth token json file and save it with the name `oauth-credentials.json`

## Running

Make sure you are in the virtualenv, if not:
```
$ source venv/bin/activate
```

Starting:
```
(venv) $ ./run.py
```

## Documentation

### Libraries used

Keep in mind that we're using [discord.py's](https://github.com/Rapptz/discord.py/tree/rewrite) rewrite branch.

```
discord.py[voice] (rewrite branch)
lru_dict
gspread
oauth2client
psutil
fuzzywuzzy[speedup]
```

### Links
* https://discordpy.readthedocs.io/en/rewrite/
* https://gspread.readthedocs.io/en/latest/
* https://docs.python.org/3/library/asyncio.html
* https://aiohttp-json-api.readthedocs.io/en/latest/
* https://github.com/seatgeek/fuzzywuzzy
