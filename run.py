#!/usr/bin/env python
  
from discord.ext import commands
import discord
from cogs.utils import checks, context
from cogs.utils.config import Config
import json, asyncio
import copy
import logging
import traceback
import sys
import aiohttp

import config

try:
  import uvloop
except ImportError:
  pass
else:
  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

initial_extensions = [
  'cogs.test',
  'cogs.chaos',
  'cogs.admin',
  'cogs.webhook',
  'cogs.meta',
  'cogs.attendance',
  'cogs.poll',
  'cogs.buttons',
]

class ChaoticBot(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(command_prefix=self._command_prefix, description="ChaoticBot",
                     pm_help=None, help_attrs=dict(hidden=True))
    self.session = aiohttp.ClientSession(loop=self.loop)
    self.client_id = config.client_id

    for extension in initial_extensions:
      try:
        self.load_extension(extension)
      except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()
    self.add_command(self.sleep)

  def _command_prefix(self, ctx, msg):
    if msg.content.startswith(tuple(config.allowed_commands)):
      return ['!']
    else:
      return ['?']

  def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
      base.append('!')
      base.append('?')
    else:
      base.extend(bot.prefixes.get(msg.guild.id, ['?', '!']))
    return base
  
  async def on_ready(self):
    print('Logged in as: {0} (ID: {0.id})'.format(bot.user))
  async def on_resumed(self):
    print('resumed...')

  async def close(self):
    await super().close()
    await self.session.close()

  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
      await ctx.author.send('This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
      await ctx.author.send('Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.BadArgument):
      await ctx.send(error)
    elif isinstance(error, commands.CommandInvokeError):
      print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
      traceback.print_tb(error.original.__traceback__)
      print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

  async def on_message(self, message):
    ctx = await self.get_context(message, cls=context.Context)

    if ctx.command is None:
      return

    #async with ctx.acquire():
    await self.invoke(ctx)

  def run(self):
    super().run(config.token, reconnect=True)  

  @property
  def config(self):
    return __import__('config')

  @commands.command()
  async def sleep(self, ctx):
    await ctx.send('Sleeping...')
    await asyncio.sleep(5)
    await ctx.send('Done sleeping')

  def load_credentials():
    with open('credentials.json') as f:
      return json.load(f)

if __name__ == '__main__':
  discord_logger = logging.getLogger('discord')
  discord_logger.setLevel(logging.INFO)

  log = logging.getLogger()
  log.setLevel(logging.INFO)

  handler = logging.FileHandler(filename='chaoticbot.log', encoding='utf-8', mode='w')
  log.addHandler(handler)
  out = logging.StreamHandler(sys.stdout)
  log.addHandler(out)
  
  bot = ChaoticBot()
  bot.run()

  handlers = log.handlers[:]
  for hdlr in handlers:
    hdlr.close()
    log.removeHandler(hdlr)
