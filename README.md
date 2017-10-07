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
$ cd discord-bot
$ python3 -mvenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Configuration

```
$ cp config.py-example config.py
```
Edit the config.py and make you to set the following variables correctly:

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
