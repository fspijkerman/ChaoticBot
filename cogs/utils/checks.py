from discord.ext import commands

#def is_owner_check(message):
#  print(message.author.id)
#  return message.author.id == '311938778866647080'

#def is_owner():
#  return commands.check(lambda ctx: is_owner_check(ctx.message))

# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# Certain permissions signify if the person is a moderator (Manage Server) or an
# admin (Administrator). Having these signify certain bypasses.
# Of course, the owner will always be able to execute commands.

async def check_permissions(ctx, perms, *, check=all):
  print('Checking perms')
  is_owner = await ctx.bot.is_owner(ctx.author)
  if is_owner:
    return True

  resolved = ctx.channel.permissions_for(ctx.author)
  return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms):
  async def predicate(ctx):
    return await check_permissions(ctx, perms, check=check)
  return commands.check(predicate)

async def check_guild_permissions(ctx, perms, *, check=all):
  is_owner = await ctx.bot.is_owner(ctx.author)
  if is_owner:
    return True

  if ctx.guild is None:
    return False

  resolved = ctx.author.guild_permissions
  return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_guild_permissions(*, check=all, **perms):
  async def pred(ctx):
    return await check_guild_permissions(ctx, perms, check=check)
  return commands.check(pred)

# These do not take channel overrides into account

def is_mod():
  async def predicate(ctx):
    return await check_guild_permissions(ctx, {'manage_guild': True})
  return commands.check(predicate)

def is_admin():
  async def predicate(ctx):
    return await check_guild_permissions(ctx, {'administrator': True})
  return commands.check(predicate)

def mod_or_permissions(**perms):
  perms['manage_guild'] = True
  async def predicate(ctx):
    return await check_guild_permissions(ctx, perms, check=any)
  return commands.check(predicate)

def admin_or_permissions(**perms):
  perms['administrator'] = True
  async def predicate(ctx):
    return await check_guild_permissions(ctx, perms, check=any)
  return commands.check(predicate)