from discord.ext import commands
import asyncio

class Context(commands.Context):
  async def entry_to_code(self, entries):
    width = max(len(a) for a, b in entries)
    output = ['```']
    for name, entry in entries:
      output.append(f'{name:<{width}}: {entry}')
    output.append('```')
    await self.send('\n'.join(output))

  async def indented_entry_to_code(self, entries):
    width = max(len(a) for a, b in entries)
    output = ['```']
    for name, entry in entries:
      output.append(f'\u200b{name:>{width}}: {entry}')
    output.append('```')
    await self.send('\n'.join(output))

  async def show_help(self, command=None):
    """Shows the help command for the specified command if given.

    If no command is given, then it'll show help for the current
    command.
    """
    cmd = self.bot.get_command('help')
    command = command or self.command.qualified_name
    await self.invoke(cmd, command)

  async def prompt(self, message, *, timeout=60.0, delete_after=True, author_id=None):
    """An interactive reaction confirmation dialog.
    Parameters
    -----------
    message: str
      The message to show along with the prompt.
    timeout: float
      How long to wait before returning.
    delete_after: bool
      Whether to delete the confirmation message after we're done.
    author_id: Optional[int]
      The member who should respond to the prompt. Defaults to the author of the
      Context's message.
    Returns
    --------
    Optional[bool]
      ``True`` if explicit confirm,
      ``False`` if explicit deny,
      ``None`` if deny due to timeout
    """

    if not self.channel.permissions_for(self.me).add_reactions:
      raise RuntimeError('Bot does not have Add Reactions permission.')

    fmt = f'{message}\n\nReact with \N{WHITE HEAVY CHECK MARK} to confirm or \N{CROSS MARK} to deny.'

    author_id = author_id or self.author.id
    msg = await self.send(fmt)

    confirm = None

    def check(emoji, message_id, channel_id, user_id):
      nonlocal confirm

      if message_id != msg.id or user_id != author_id:
        return False

      codepoint = str(emoji)

      if codepoint == '\N{WHITE HEAVY CHECK MARK}':
        confirm = True
        return True
      elif codepoint == '\N{CROSS MARK}':
        confirm = False
        return True

      return False

    for emoji in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
      await msg.add_reaction(emoji)

    try:
      await self.bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
    except asyncio.TimeoutError:
      confirm = None

    try:
      if delete_after:
        await msg.delete()
    finally:
      return confirm

  def tick(self, opt, label=None):
    emoji = '<:greenTick:330090705336664065>' if opt else '<:redTick:330090723011592193>'
    if label is not None:
      return f'{emoji}: {label}'
    return emoji

  def __repr__(self):
    # we need this for our cache key strategy
    return '<Context>'

  @property
  def session(self):
    return self.bot.session 


