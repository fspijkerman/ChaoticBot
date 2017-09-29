from discord.ext import commands
from discord import Embed, Colour
from .utils import cache
from .utils.checks import *
from .utils.formats import Plural
from fuzzywuzzy import process
import iso8601
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

class Attendance(object):
  def __init__(self, bot):
    self.bot = bot

    scope = ['https://spreadsheets.google.com/feeds']
    self.spread_cred = ServiceAccountCredentials.from_json_keyfile_name(self.bot.config.google_oauth, scope)
    self.spread_auth = gspread.authorize(self.spread_cred)
    self.spread = self.spread_auth.open_by_key(self.bot.config.spread_id)
    self.overview = self.spread.worksheet('Overview')

  @cache.cache()
  def getEligible(self):
    if self.spread_cred.access_token_expired:
      self.spread_auth.login()

    users = {}
    idx = 3 # Skipping first rows
    for i in self.spread.worksheet('Overview').col_values('5')[3:]:
      if i == '':
        break
      idx +=1
      if i == '✓':
        users[idx] = True
      else:
        users[idx] = False
    return users

  @cache.cache()
  def getUsers(self):
    if self.spread_cred.access_token_expired:
      self.spread_auth.login()

    users = {}
    idx = 3 # Skipping first rows
    for i in self.spread.worksheet('Overview').col_values('4')[3:]:
      if i == '':
        break
      idx +=1
      users[i.lower()] = {'name': i, 'col': 4, 'row': idx}
    return users

  def mapRole(self, raw_role):
    if 'R16C2' in raw_role:
      return {'role': 'Tank', 'img': 'http://cdn-wow.mmoui.com/images/icons/m143.jpg'}
    if 'R17C2' in raw_role:
      return {'role': 'DPS', 'img': 'http://cdn-wow.mmoui.com/images/icons/m142.jpg'}
    if 'R18C2' in raw_role:
      return {'role': 'Healer', 'img': 'http://cdn-wow.mmoui.com/images/icons/m141.jpg'}

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

      #await ctx.send("%s" % avatar_img)
      await ctx.send(fmt)

  @commands.command(aliases=['fuzz'])
  @commands.guild_only()
  async def fuzzy(self, ctx, name : str):
    from fuzzywuzzy import process
    choices = self.getUsers().keys()
    rv = process.extractOne(name, choices)
    await ctx.send("%s (%s)" % (rv[0], rv[1]))

  def fuzzySearch(self, name : str, choices : list):
    return process.extractOne(name, choices)

  @commands.command()
  @commands.guild_only()
  async def avatar(self, ctx, realm : str, name : str):
      avatar_img = await self.getAvatar(ctx, realm, name) 
      if avatar_img is None:
        raise commands.BadArgument("Avatar not found")

      await ctx.send("%s" % avatar_img)

  @cache.cache()
  def getSheetRange(self, search : str):
    '''
      <Cell R6C1 'Ranged DPS'>
      <Cell R6C2 ''>
      <Cell R6C3 ''>
      <Cell R6C4 'Aart'>
      <Cell R6C5 '✓'>
      <Cell R6C6 '100%'>
      <Cell R6C7 '94%'>
      <Cell R6C8 '57%'>
      <Cell R6C9 '58.0'>
      <Cell R6C10 'Needed'>
      <Cell R6C11 'MissAllow'>
      <Cell R6C12 'Hunter'>
      <Cell R6C13 'realm'>
    '''
    if self.spread_cred.access_token_expired:
      self.spread_auth.login()

    return self.overview.range(search) 

  @cache.cache()
  def getSheetCell(self, cell : str):
    if self.spread_cred.access_token_expired:
      self.spread_auth.login()
    return self.overview.acell(cell) 

  @commands.command()
  @commands.guild_only()
  async def attnlist(self, ctx, *, entries : str):
    users = self.getUsers()
    eligible = self.getEligible()
    e = Embed()
    allowed, denied = [], []
    for user in entries.split(';'):
      if user.strip() != "":
        print(":%s:" % user)
        fuzzy_name = self.fuzzySearch(re.sub('\-.*$','', user).replace('(p)',''), users.keys())
        if fuzzy_name[1] < 90:
          await ctx.send('User %s not found in the sheet' % user)

        if eligible[users[fuzzy_name[0]]['row']]:
          allowed.append(re.sub('\-\w+', '', user)) 
        else:
          denied.append(re.sub('\-\w+', '', user)) 

    if not denied:
      await ctx.send('Everybody is eligible! :tada:') 
      return

    e.add_field(name='Eligible', value='\n'.join(allowed))
    e.add_field(name='Not Eligible', value='\n'.join(denied))
    await ctx.send(embed=e)

  @commands.command(aliases=['attn', 'attendence'])
  @commands.guild_only()
  async def attendance(self, ctx, name : str):
    ''' Attendance '''

    if name == 'help':
      return await ctx.send("```!attendance <character>\n\nPlease make sure you use the same character name as registered in the Attendance speadsheet on our website: https://docs.google.com/spreadsheets/d/1iwgTwXHC6q575w7lUVbNksunlHAbzOtVSpdnGF8xA5s/pubhtml?gid=0&single=true```")

    users = self.getUsers()
    if not name.lower() in map(str.lower, users):
      fuzzy_name = self.fuzzySearch(name, users.keys())
      if fuzzy_name[1] >= 60:
        name = fuzzy_name[0]
      else:
        raise commands.BadArgument("""Oops! Character "%s" was not found in the Attendance spreadsheet. If you'd rather search manually, here is the link to the spreadsheet: <https://goo.gl/X7LU1x>""" % name)
      #raise commands.BadArgument('Character "%s" not found in datasheet' % name)

    name = name.lower()
    data = self.getSheetRange('A%s:M%s' % (users[name]['row'], users[name]['row']))

    color = Colour.red() 
    loot = data[4].value
    # u"\u2713"
    if loot == '✓': color = Colour.green()

    last_update = iso8601.parse_date(self.overview.updated)
    role = self.mapRole(data[1].input_value)
    nick = data[3].value
    last_10 = data[5].value
    last_25 = data[6].value
    last_all = data[7].value
    last_total = data[8].value
    threshold_needed = data[9].value 
    miss_allow = data[10].value 
    realm = data[12].value.lower()

    last_raid = self.getSheetCell('N3').value

    thumbnail_image = role['img']
    avatar = await self.getAvatar(ctx, realm, name)

    if avatar:
      thumbnail_image = avatar

    txt_fmt = ''
    if len(threshold_needed) == 0:
      txt_fmt = 'It is unknown how many raids %s needs. Maybe he\'s not raiding?' % nick
    elif threshold_needed == "0":
      txt_fmt = '%s can miss **%s** consecutive %s before dropping below the loot threshhold.' % (nick, miss_allow, str(Plural(raid=int(miss_allow))))
    else:
      txt_fmt = '%s needs to join **%s** more consecutive %s to be eligible for loot.' % (nick, threshold_needed, str(Plural(raid=int(threshold_needed))))

    if last_10 == '100%' and last_25 == '100%':
      nick += ' :trophy:'
    
    embed=Embed(title="Attendance of %s" % nick, color=color, description=txt_fmt, url=self.bot.config.spread_public_url)
    embed.set_footer(text="Last attendance update was on %s" % last_raid)
    embed.set_thumbnail(url=thumbnail_image)
    embed.add_field(name="Last 10",    value=last_10, inline=True)
    embed.add_field(name="Last 25",    value=last_25, inline=True)
    #embed.add_field(name="All raid(s)",   value=last_all, inline=True)
    #embed.add_field(name="Total points", value=last_total, inline=True)
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Attendance(bot))
