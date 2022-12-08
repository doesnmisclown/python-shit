import disnake
from disnake.ext import commands
intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents,help_command=None,command_prefix="ya.")
channels = [1007961295552786462,1007961191949275286]
@bot.event
async def on_message(message):
  if message.author.id == 950679458245926982 and message.channel.id in channels:
    await message.delete()
    files = []
    for a in message.attachments:
      files.append(await a.to_file())
    if message.reference:
      msg = await message.channel.fetch_message(message.reference.message_id)
      await msg.reply(content=message.content,files=files,stickers=message.stickers)
    else:
      await message.channel.send(content=message.content, files=files,stickers=message.stickers)
bot.run("")
