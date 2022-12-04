import disnake
from disnake.ext import commands
intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents,help_command=None,command_prefix="ya.")

@bot.event
async def on_message(message):
  if message.author.id == 950679458245926982 and message.channel.id == 1007961295552786462:
    await message.delete()
    files = []
    for a in message.attachments:
      files.append(await a.to_file())
    if message.reference:
      msg = message.channel.fetch_message(message.reference.message_id)
      await msg.reply(content=message.content,files=files)
    else:
      await message.channel.send(content=message.content, files=files)
bot.run("")
