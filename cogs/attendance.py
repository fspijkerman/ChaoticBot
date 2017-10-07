from discord.ext import commands
from discord import Embed, Colour
from .utils import cache
from .utils.checks import *
from .utils.formats import Plural
from fuzzywuzzy import process
import iso8601
import gspread
import re
import collections
import asyncio
from oauth2client.service_account import ServiceAccountCredentials

class AttendanceDB(object):
  def __init__(self, bot):
    scope = ['https://spreadsheets.google.com/feeds']
    self.bot = bot
    self.spread_cred = ServiceAccountCredentials.from_json_keyfile_name(self.bot.config.google_oauth, scope)
    self.spread_auth = gspread.authorize(self.spread_cred)
    self.spread = self.spread_auth.open_by_key(self.bot.config.spread_id)
    self.overview = self.spread.worksheet('Overview')
    self._db = {}

    # Setup background task
    self._task = self.bot.loop.create_task(self.taskUpdate())

  def unload(self):
    self._task.cancel()
    print("Canceled Attendance Update Task")

  def keys(self):
    return self._db.keys()

  async def taskUpdate(self):
    await self.bot.wait_until_ready()
    try:
      while not self.bot.is_closed():
        print('Updating attendance...')
        await self.update()
        print('Done updating attendance...')
        await asyncio.sleep(self.bot.config.update_interval)
    except asyncio.CancelledError:
      pass
    

  def getLastRaid(self):
    return self.last_raid

  @cache.cache()
  async def getAvatar(self, realm, char):
    resource = 'character/%s/%s' % (realm, char)
    url = 'https://{0}/wow/{1}'.format(self.bot.config.wow_api_url, resource)
    params = [('apikey', self.bot.config.wow_api_key)]

    async with self.bot.session.get(url, params=params) as resp:
      if resp.status == 200:
        avatar_img = 'http://render-eu.worldofwarcraft.com/character/'
        data = await resp.json()
        avatar_img += data['thumbnail']
        return avatar_img
      else:
        return None

  def __getitem__(self, name):
    if name in self._db:
      return self._db[name]
    else:
      raise AttributeError("No such user: " + name)

  def search(self, name, fuzzy=False, threshold=70):
    if fuzzy:
      result = process.extractOne(name, self._db.keys())
      if result[1] >= threshold:
        return self._db[result[0]]
      else:
        return None
    else:
      if name in self._db:
        return self._db[name]
      else:
        return None

  def mapRole(self, raw_role):
    if 'Tank' in raw_role:
      return {'role': raw_role, 'img': 'http://cdn-wow.mmoui.com/images/icons/m143.jpg'}
    if 'DPS' in raw_role:
      return {'role': raw_role, 'img': 'http://cdn-wow.mmoui.com/images/icons/m142.jpg'}
    if 'Healer' in raw_role:
      return {'role': raw_role, 'img': 'http://cdn-wow.mmoui.com/images/icons/m141.jpg'}

  def mapEligible(self, raw):
    if raw == u'\u2713': #  '✓':
      return True
    else:
      return False

  async def update(self):
    Player = collections.namedtuple("Player", [
      "name",
      "eligible",
      "role",
      "last_10",
      "last_25",
      "last_all",
      "last_total",
      "threshold_needed",
      "missed_allowed",
      "role_class",
      "realm",
      "avatar",
    ])

    if self.spread_cred.access_token_expired:
      self.spread_auth.login()
    rv = self.overview.get_all_values()

    ''' ['Ranged DPS', '', '', 'Magentatears', '✓', '100%', '100%', '92%', '97.0', '0', '7', 'Mage', 'Wildhammer', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '0.5', '1', '1', '1', '1', '1', '1', '1', '1', '', '', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '', '1', '1', '1', '0.5', '1', '1', '1', '1', '1', '1', '1', '1', '', '1', '1', '1', '1', '1', '1', '0.5', '1', '0.5', '1', '1', '1', '1']
    '''
    db = {}
    for i in rv[3:]:
      if i[3] == '':
        break
      
      avatar = await self.getAvatar(i[12], i[3])
      player = Player(
        role=self.mapRole(i[0]),
        name=i[3],
        eligible=self.mapEligible(i[4]),
        last_10=i[5],
        last_25=i[6],
        last_all=i[7],
        last_total=i[8],
        threshold_needed=i[9],
        missed_allowed=i[10],
        role_class=i[11],
        realm=i[12],
        avatar=avatar
      )
      db[i[3]] = player
    self._db = db

    # Update last_raid
    self.last_raid = self.overview.acell('N3').value

class Attendance(object):
  def __init__(self, bot):
    self.bot = bot
    self.db = AttendanceDB(bot)

  def __unload(self):
    self.db.unload()

  @commands.command()
  @commands.guild_only()
  async def update(self, ctx):
    await ctx.send('Updating cache...')
    await self.db.update()
    await ctx.send('Done.')

  @cache.cache()
  async def getAvatar(self, ctx, realm, char):
    # TODO: make a generic function for this
    resource = 'character/%s/%s' % (realm, char)
    url = 'https://{0}/wow/{1}'.format(self.bot.config.wow_api_url, resource)
    params = [('apikey', self.bot.config.wow_api_key)]

    async with ctx.session.get(url, params=params) as resp:
      if resp.status == 200:
        avatar_img = 'http://render-eu.worldofwarcraft.com/character/'
        data = await resp.json()
        avatar_img += data['thumbnail']
        return avatar_img
      else:
        return None

  @commands.command()
  @commands.guild_only()
  async def wow(self, ctx):
      avatar_img = await self.getAvatar(ctx, 'wildhammer', 'Aart') 
      from .utils.formats import TabularData
      table = TabularData()
      table.set_columns(['Test1','Test2','Blaat'])
      table.add_rows([['1','2','3'],['bla','mekker','pom']])
      render = table.render()
      fmt = f'```\n{render}\n```'

      await ctx.send(fmt)

  @commands.command(aliases=['fuzz'])
  @commands.guild_only()
  async def fuzzy(self, ctx, name : str):
    user = self.db.search(name, fuzzy=True, threshold=0)
    await ctx.send("Found: %s" % user.name)

  @commands.command()
  @commands.guild_only()
  async def avatar(self, ctx, name : str):
      avatar_img = self.db[name].avatar
      if avatar_img is None:
        raise commands.BadArgument("Avatar not found")

      await ctx.send("%s" % avatar_img)

  @commands.command()
  @commands.guild_only()
  async def attnlist(self, ctx, *, entries : str):
    e = Embed(colour=Colour.blue(), title="Hello! This is the loot eligibility status of the list you gave me, as of %s:"  % self.db.getLastRaid(), url=self.bot.config.spread_public_url)
    allowed, denied = [], []
    for user in entries.split(';'):
      if user.strip() != "":
        db_user = self.db.search(re.sub('\-.*$','', user).replace('(p)',''), fuzzy=True, threshold=90)
        if db_user is None:
          await ctx.send('User %s not found in the sheet' % user)
          continue

        if db_user.eligible:
          allowed.append(re.sub('\-\w+', '', user)) 
        else:
          denied.append(re.sub('\-\w+', '', user)) 

    if not denied:
      await ctx.send('Everybody is eligible! :tada:') 
      return
    e.add_field(name=':white_check_mark: Eligible', value='\n'.join(allowed))
    e.add_field(name=':x: Not Eligible', value='\n'.join(denied))
    await ctx.send(embed=e)

  @commands.command(aliases=['attn', 'attendence'])
  @commands.guild_only()
  async def attendance(self, ctx, name : str):
    ''' Attendance '''

    if name == 'help':
      return await ctx.send("```!attendance <character>\n\nPlease make sure you use the same character name as registered in the Attendance speadsheet on our website: https://docs.google.com/spreadsheets/d/1iwgTwXHC6q575w7lUVbNksunlHAbzOtVSpdnGF8xA5s/pubhtml?gid=0&single=true```")
    
    user = self.db.search(name, True, 60)
    if not user:
      raise commands.BadArgument("""Oops! Character "%s" was not found in the Attendance spreadsheet. If you'd rather search manually, here is the link to the spreadsheet: <https://goo.gl/X7LU1x>""" % name)

    thumbnail_image = user.role['img']
    if user.avatar:
      thumbnail_image = user.avatar

    txt_fmt = ''
    if len(user.threshold_needed) == 0:
      txt_fmt = 'It is unknown how many raids %s needs. Maybe he\'s not raiding?' % user.name
    elif user.threshold_needed == "0":
      txt_fmt = '%s can miss **%s** consecutive %s before dropping below the loot threshhold.' % (user.name, user.missed_allowed, str(Plural(raid=int(user.missed_allowed))))
    else:
      txt_fmt = '%s needs to join **%s** more consecutive %s to be eligible for loot.' % (user.name, user.threshold_needed, str(Plural(raid=int(user.threshold_needed))))

    color = Colour.red() 
    if user.eligible:
      color = Colour.green() 

    throphy = ''
    if user.last_10 == '100%' and user.last_25 == '100%':
      throphy = ' :trophy:'
     
    embed=Embed(title="Attendance of %s %s" % (user.name, throphy), color=color, description=txt_fmt, url=self.bot.config.spread_public_url)
    embed.set_footer(text="Last attendance update was on %s" % self.db.getLastRaid())
    embed.set_thumbnail(url=thumbnail_image)
    embed.add_field(name="Last 10",    value=user.last_10, inline=True)
    embed.add_field(name="Last 25",    value=user.last_25, inline=True)
    #embed.add_field(name="All raid(s)",   value=user.last_all, inline=True)
    #embed.add_field(name="Total points", value=user.last_total, inline=True)
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Attendance(bot))
