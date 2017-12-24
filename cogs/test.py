from discord.ext import commands

class Test(object):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases=['test'])
  async def party(self, ctx):
    ''' Test Party! '''
    await ctx.send('bummer!')

def setup(bot):
  bot.add_cog(Test(bot))
