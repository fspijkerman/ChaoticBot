from discord.ext import commands

class Webhook:
  """ Define commands to trigger a webhook """
  webhooks = {}

  def __init__(self, bot):
    self.bot = bot

  async def __error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send(error)    
    elif isinstance(error, commands.CommandInvokeError):
      await ctx.send(error)    
    else:
      await ctx.send(error)    

  @commands.group()
  async def webhook(self,ctx):
    ''' Webhook '''
    if ctx.invoked_subcommand is None:
      await ctx.show_help('webhook')

  @webhook.command(name="list")
  async def webhook_list(self, ctx):
    ''' List all webhooks '''
    await ctx.send(f'```py\n%s```' % self.webhooks)

  @webhook.command(name="add")
  async def webhook_add(self, ctx, command: str, url, fields: str):
    ''' <command> <url> [field,] :: Add a new webhook '''
    print("Name: %s" % command)
    for field in fields:
      print(" Field: %s" % field)

    if not self.bot.get_command(command) is None:
      await ctx.send('Command already in use')
      return

    self.webhooks[command] = { 'command': command, 'url': url }
    await ctx.send("Webhook %s added for command %s" % (name, command))

    @commands.command(name=command)
    async def _mekker(ctx, test=name, url=url):
      async with ctx.session.post(url, data='{ "user": "test" }') as resp:
        await ctx.send("Executed webhook")
        print(resp)

    self.bot.add_command(_mekker)
    
    

def setup(bot):
  bot.add_cog(Webhook(bot))
