from discord.ext import commands

class Chaos(object):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases=['loot', 'lootrules'])
  async def rules(self, ctx):
    ''' Loot Rules '''
    a = """Chaotic Intent does not use Personal Loot or a DKP-like system. We ask of all our raiders to maintain an attendance of at least 70%. If you do, you'll be able to roll on items with others who have at least 70% attendance as well. That means that if you drop below that, you lose the privilege to roll on loot unless there is no one else who wants the item. This also means that new recruits will first have to "prove" themselves by attending regularly before they're eligible for loot. Assuming they can attend both raids every week, they'll have to wait 4 lockouts before they can roll with the rest of us. Type !attendance help for more information."""
    await ctx.send(a)

  @commands.command()
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

  @commands.command()
  async def addon(self, ctx, name: str):

    if name == 'help':
      return await ctx.send("""```!addon <addon name>```\n\nReturns information about a specific addon. Possible values:\nFor Angry Assignments: ```!addon aa``` or ```!addon angryassignments```\n```For RCLootCouncil: !addon rclc``` or ```!addon rclootcouncil```""")

    if (name == 'aa') or (name == 'angryassignments'):
      return await ctx.send("```There are only a couple steps required to set up Angry Assignments:\n1. open the window with the command /aa\n2. at the top left corner you'll see the input field \"Highlight\", insert \"Group'\" in here, this will highlight fields like G# when you are in Group#\n3. (optional) Check \"Display Background\", this should make the assignments more visible\n4. At the bottom of the settings you have the Permissions, here you can either check \"Allow All\" or add both Piocc-Wildhammer and Aart-Wildhammer to the list\nDone! :)```")

    if (name == 'rclc') or (name == 'rclootcouncil'):
      return await ctx.send("```This addon will automatically popup whenever there's loot to distribute, the options available are different for Tier Tokens and \"normal\" loot:\n\nTier Tokens: 4pc | 2pc | Other Item | Normal to HC\nSelect 4pc or 2pc if that item would be the 4th or 2nd respectively, this way we know if you'd be unlocking a set bonus\nOther Item it's for either your 1st, 3rd or 5th+ item. We suggest you put a note in this case like \"3rd\" or \"5th but better combination overall\", \"5th and I can use my BiS legendary\", stuff like that :)\nNormal to HC is self explanatory\n\n\"Normal\" Loot\nMajor | Minor | Major (<70)\nThere's a bit of a debate what kind of upgrade would be Major and what's Minor. Personally, Major is ~7-10% improvement or if said item is my BiS (perfect stats for me) and I could ever only upgrade it with much higher ilvl, Minor is an item I will likely replace in the future.\nMajor (<70) is for people who need the item but don't have the attendance.```")

    raise commands.BadArgument("""Oops! Addon "%s" was not found. Possible values:\nFor Angry Assignments: ```!addon aa``` or ```!addon angryassignments```\n```For RCLootCouncil: !addon rclc``` or ```!addon rclootcouncil```""")

    await ctx.send("")

def setup(bot):
  bot.add_cog(Chaos(bot))
