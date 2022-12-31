"""
Message Stats - discord bot that building chart of last 100 messages of channel by authors
Owner: doesnm#8884
"""
import logging
from os import environ
from io import BytesIO
import disnake
from disnake.ext import commands
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix="-",intents=disnake.Intents(guilds=True,guild_messages=True,members=True))
bot.load_extension("jishaku")
@bot.slash_command(description="Display statistic")
async def stats(i,channel: disnake.TextChannel = commands.Param(lambda i: i.channel)):
  await i.response.defer()
  messages = await channel.history(limit=100).flatten()
  top = {}
  for m in messages:
    id = m.author.id
    if m.author.bot or m.is_system(): continue
    if not id in top:
    	top[id] = dict(name=m.author.display_name,count=1,color=str(m.author.color))
    	continue
    top[id]["count"] += 1
  top = dict(sorted(top.items(),key=lambda i: i[1]["count"]))
  stream = BytesIO()
  plt.title(f'Статистика {i.guild.name} в канале {channel.name}')
  plt.barh([top[x]["name"] + " (" + str(top[x]["count"]) + ")" for x in top],[top[x]["count"] for x in top],color=[top[x]["color"] for x in top],linewidth=1,edgecolor="k")
  plt.tight_layout()
  plt.savefig(stream,format="png")
  plt.close()
  stream.seek(0)
  file = disnake.File(stream,filename="chart.png")
  await i.edit_original_message(file=file)
@bot.slash_command(description="Execute code")
async def eval(i):
  if not await bot.is_owner(i.author): return await i.response.send_message(content="Missing access")
  await i.response.send_modal(title="Execute code",custom_id="modal_eval",components=[disnake.ui.TextInput(label="Code",custom_id="code",style=disnake.TextInputStyle.long)])
  inter = await bot.wait_for("modal_submit",check=lambda mi: mi.custom_id == "modal_eval",timeout=300)
  await inter.response.defer()
  code = inter.text_values["code"]
  loc = {'inter':inter}
  loc.update(globals())
  try:
    exec(code,loc)
    output = loc["output"]
    await inter.edit_original_message(content=f'```py\nInput:\n{code}\nOutput:\n{output}```')
  except Exception as e:
    await inter.edit_original_message(content=f'```py\nInput:\n{code}\nOutput:\n{type(e).__name__}: {e}```')
bot.run(environ["TOKEN"])
