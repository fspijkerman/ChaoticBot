from discord.ext import commands

class Chaos(object):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases=['loot','lootrules'])
  async def rules(self, ctx):
    ''' Loot Rules '''
    a = """Chaotic Intent does not use Personal Loot or a DKP-like system. We ask of all our raiders to maintain an attendance of at least 70%. If you do, you'll be able to roll on items with others who have at least 70% attendance as well. That means that if you drop below that, you lose the privilege to roll on loot unless there is no one else who wants the item. This also means that new recruits will first have to "prove" themselves by attending regularly before they're eligible for loot. Assuming they can attend both raids every week, they'll have to wait 4 lockouts before they can roll with the rest of us. Type !attendance help for more information."""
    await ctx.send(a)

  @commands.command(aliases=['addon'])
  async def addons(self, ctx):
    ''' Addons '''

    a = """**We ask of all our raiders to have the following addons installed**

AngryAssignments: <https://mods.curse.com/addons/wow/angry-assignments>
Lets us summarize tactics like a "post-it" in game. Used for assigning group positions, raid cooldowns, and other rotations.

RCLootCouncil: <https://mods.curse.com/addons/wow/rclootcouncil>
Used to distribute loot with. Without this addon, you're not eligible to receive items in raid.

Deadly Boss Mods: <https://mods.curse.com/addons/wow/deadly-boss-mods>
Keeps track of boss mechanics and helps with tactics."""
    
    await ctx.send(a)

def setup(bot):
  bot.add_cog(Chaos(bot))
