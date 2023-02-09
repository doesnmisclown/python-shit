from disnake.ext import commands, tasks
import disnake, traceback, aiohttp, hashlib, re, string, io, os
from datetime import timedelta, date
from textwrap import indent
from random import randint
import akinator
from akinator.async_aki import Akinator
def bar(n, m, l):
    return ("🟦" * round(n / m * l)).ljust(l, "⬛")


class PersistentView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class JaenCat(commands.InteractionBot):
    def __init__(self):
        intents = disnake.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(intents=intents, test_guilds=[812396114648498196])
        self.rp_names = []


class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = 1010578321714724925
        self.emoji = "⭐"
        self.cache = {}

    @commands.Cog.listener("on_reaction_add")
    @commands.Cog.listener("on_reaction_remove")
    async def handler(self, reaction, user):
        if reaction.emoji != self.emoji:
            return
        count = reaction.count
        if count >= 4:
            description = None
            image = None
            if reaction.message.content:
                description = reaction.message.content
            if len(reaction.message.attachments) > 0:
                image = reaction.message.attachments[0].url
            emb = disnake.Embed(description=description)
            emb.set_image(url=image)
            emb.set_author(
                name=reaction.message.author.display_name,
                icon_url=reaction.message.author.display_avatar.url,
            )
            content = f":star2: {count} <#{reaction.message.channel.id}>"
            view = disnake.ui.View()
            view.add_item(
                disnake.ui.Button(label="Jump", url=reaction.message.jump_url)
            )
            if reaction.message.id in self.cache:
                await self.cache[reaction.message.id].edit(
                    content=content, embed=emb, view=view
                )
            else:
                message = await self.bot.get_channel(self.channel).send(
                    content=content, embed=emb, view=view
                )
                self.cache[reaction.message.id] = message
        elif reaction.message.id in self.cache:
            await self.cache[reaction.message.id].delete()
            self.cache.pop(reaction.message.id)


bot = JaenCat()


@bot.slash_command(description="Отправить реплику от имени персонажа")
@commands.bot_has_permissions(manage_webhooks=True)
async def rp(
    inter,
    character: str = commands.Param(description="Имя персонажа"),
    text: str = commands.Param(description="Текст реплики"),
):
    webhooks = await inter.channel.webhooks()
    if len(webhooks) < 1:
        webhook = await inter.channel.create_webhook(name="Jaen Cat")
        await webhook.send(text, username=character)
    else:
        await webhooks[0].send(text, username=character)
    await inter.response.send_message("Реплика отправлена", ephemeral=True)


allowed_roles = [
    1008009505742782494,
    1008009618187886602,
    1008009905996845078,
    1008010042626293800,
    1008010258767171717,
    1008010366707568740,
    1008010503328645150,
    1008010629757542561,
    1008010761626472599,
    1008010860133892159,
    1008011059614974043,
    1008011282072469605,
    1008011429124788335,
    1008011616173953055,
]


@bot.slash_command(description="Выдача цветной или пинг роли")
@commands.bot_has_permissions(manage_roles=True)
async def claim(
    inter,
    role: disnake.Role = commands.Param(description="Разрешенная роль для выдачи"),
):
    await inter.response.defer()
    if not role.id in allowed_roles:
        return await inter.edit_original_response(
            content="Данной роли нету в списке разрешенных для выдачи"
        )
    ping_roles = [1008011282072469605, 1008011429124788335, 1008011616173953055]
    if not role.id in ping_roles:
        for r in allowed_roles:
            if r in ping_roles:
                continue
            rr = inter.guild.get_role(r)
            if rr in inter.user.roles and rr != role:
                await inter.user.remove_roles(rr)
    if role in inter.user.roles:
        await inter.user.remove_roles(role)
        await inter.edit_original_response(content="Роль успешно убрана")
    else:
        await inter.user.add_roles(role)
        await inter.edit_original_response(content="Роль успешно добавлена")


@bot.slash_command(description="Показать картинки с котиками")
async def cat(inter):
    await inter.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://cataas.com/cat") as resp:
            file = disnake.File(io.BytesIO(await resp.read()), "cat.png")
            emb = disnake.Embed(title="Мяу!")
            emb.set_image(url="attachment://cat.png")
            await inter.edit_original_response(embed=emb, file=file)


@bot.slash_command(
    description="Отправить нарушителей подумать о своем поведении",
    default_member_permissions=disnake.Permissions(moderate_members=True),
)
@commands.bot_has_permissions(moderate_members=True)
async def timeout(
    inter,
    member: disnake.Member = commands.Param(
        description="Участник для выдачи наказания"
    ),
    duration: int = commands.Param(
        description="Время выдачи наказания. По умолчанию 1 час. Установка этого параметра как 0 снимает наказание",
        default=1,
    ),
):
    if duration == 0:
        await member.timeout(until=None)
        emb = disnake.Embed(
            title="Успешно", description="Теперь участник может говорить"
        )
        return await inter.response.send_message(embed=emb)
    until = disnake.utils.utcnow() + timedelta(hours=duration)
    await member.timeout(until=until)
    emb = disnake.Embed(
        title="Успешно",
        description=f"{member.mention} был отправлен подумать о своём поведении до {disnake.utils.format_dt(until)}",
    )
    await inter.response.send_message(embed=emb)


@bot.slash_command(description="Команда для проверки двух пар")
async def ship(
    inter,
    user1: disnake.Member = commands.Param(description="Первый пользователь"),
    user2: disnake.Member = commands.Param(description="Второй пользователь"),
):
    h = hashlib.new("sha256")
    h.update(str.encode(str(user1.id + user2.id)))
    percent = int(h.hexdigest(), 16) % 100
    emb = disnake.Embed(
        title="Совместимость", description=f"{user1} и {user2} совместимы на {percent}%"
    )
    await inter.response.send_message(embed=emb)


@bot.message_command(name="Выполнить")
async def eval_message(i: disnake.Interaction, message: disnake.Message):
    if not await bot.is_owner(i.user):
        return await i.response.send_message(content="Недостаточно прав")
    await i.response.defer()
    regex = r"(?:[\S\s]*?```\w*|^)([\s\S]+?)(?:```[\s\S]*?|$)"
    code = re.search(regex, message.content)
    if code == None or not code.group(1):
        return await i.edit_original_response(content="Код не найден")
    try:
        code = code.group(1)
        env = {
            "bot": bot,
            "i": i,
            "message": message,
        }
        exec(f"async def exec_function():\n{indent(code,'  ')}", env)
        output = await env["exec_function"]()
        await i.edit_original_response(content=f"```py\n{output}\n```")
    except Exception as e:
        await i.edit_original_response(
            content=f"```py\n{''.join(traceback.format_exception(None,e,e.__traceback__))}\n```"
        )


@bot.slash_command(
    description="Закрыть/открыть канал от всех участников",
    default_member_permissions=disnake.Permissions(manage_channels=True),
)
@commands.bot_has_permissions(manage_channels=True)
async def lock(
    inter,
    channel: disnake.TextChannel = commands.Param(
        description="Целевой канал", default=lambda i: i.channel
    ),
):
    role = disnake.utils.get(inter.guild.roles, id=inter.guild.id)
    perms = channel.permissions_for(role)
    await channel.set_permissions(role, send_messages=not perms.send_messages)
    await inter.response.send_message(
        f"Режим блокировки канала <#{channel.id}> был изменен", ephemeral=True
    )


class SurveySelect(disnake.ui.StringSelect):
    def __init__(self, answers):
        options = []
        for i, a in enumerate(answers):
            if not a:
                continue
            options.append(disnake.SelectOption(label=a, value=str(i)))
        super().__init__(
            options=options,
            max_values=1,
            min_values=1,
            placeholder="Выбор за тобой",
            custom_id="survey_select",
        )

    async def callback(self, inter):
        description = inter.message.embeds[0].description
        if str(inter.user.id) in description:
            return await inter.response.defer()
        description += f" {inter.user.mention},"
        label = (
            inter.message.components[0].children[0].options[int(self.values[0])].label
        )
        num = int(label.split("(")[1].split(")")[0]) + 1
        inter.message.components[0].children[0].options[int(self.values[0])].label = (
            label.split("(")[0] + "(" + str(num) + ")"
        )
        emb = disnake.Embed(title="Внимание, опрос", description=description)
        view = PersistentView()
        answers = map(
            lambda p: p.label, inter.message.components[0].children[0].options
        )
        select = SurveySelect(answers)
        view.add_item(select)
        await inter.response.edit_message(embed=emb, view=view)


@bot.slash_command(description="Начать опрос")
async def survey(
    inter,
    content: str = commands.Param(description="Текст опроса"),
    a1: str = commands.Param(description="Первый вариант"),
    a2: str = commands.Param(description="Второй вариант"),
    a3: str = commands.Param(description="Третий вариант", default=None),
    a4: str = commands.Param(description="Первый вариант", default=None),
):
    view = PersistentView()
    answers = [a1, a2, a3, a4]
    for i, a in enumerate(answers):
        if not a:
            continue
        if len(a) > 80:
            return await inter.response.send_message(
                content=f"Вариант ответа {i} слишком длинный. Сократите его"
            )
        answers[i] = f"{a} (0)"
    view.add_item(SurveySelect(answers))
    emb = disnake.Embed(
        title="Внимание, опрос", description=f"{content}\nПроголосовали: "
    )
    await inter.response.send_message(embed=emb, view=view)


@bot.slash_command(
    description="Очистка сообщений",
    default_member_permissions=disnake.Permissions(manage_messages=True),
)
@commands.bot_has_permissions(manage_messages=True)
async def clear(
    inter, count: int = commands.Param(description="Количество сообщений для удаления")
):
    if count > 100 or count < 1:
        return await inter.response.send_message(
            content="Можно только от 1 до 100 сообщений"
        )
    await inter.response.defer()
    await inter.delete_original_response()
    await inter.channel.purge(limit=count)


warn_roles = [1065987290066858034, 1065987408623063070, 1065987500109217843]


def count_warns(member):
    i = len(warn_roles)
    for r in reversed(warn_roles):
        r = disnake.utils.get(member.roles, id=r)
        if not r:
            i -= 1
            continue
        return i
    return 0


@bot.slash_command(
    description="Выдать предупреждение",
    default_member_permissions=disnake.Permissions(manage_roles=True),
)
@commands.bot_has_permissions(manage_roles=True)
async def warn(
    inter,
    member: disnake.Member = commands.Param(
        description="Участник которому необходимо выдать предупреждения"
    ),
    reason: str = commands.Param(
        description="Причина, которая будет видна в журнале аудита"
    ),
):
    count = count_warns(member)
    oneup_role = disnake.utils.get(inter.guild.roles, id=1065990753496596500)
    prev_count = ""
    next_count = ""
    if oneup_role in member.roles:
        prev_count = "Спасалка"
        next_count = count
        await member.remove_roles(
            oneup_role, reason="Выдача предупреждения по причине " + reason
        )
    else:
        prev_count = count
        next_count = count + 1
        if next_count > 3:
            next_count = 3
        give_role = warn_roles[next_count - 1]
        give_role = disnake.utils.get(inter.guild.roles, id=give_role)
        await member.add_roles(
            give_role, reason="Выдача предупреждения по причине " + reason
        )
    await inter.response.send_message(
        content=f"{member.mention} получил предупреждение по причине {reason} ({prev_count} -> {next_count})"
    )


@bot.slash_command(description="Информация о сервере")
async def server(inter):
    emb = disnake.Embed(title=inter.guild.name)
    emb.set_thumbnail(url=inter.guild.icon.url)
    emb.add_field(
        name="Участники",
        value="\n".join(
            [
                f"Всего: {len(inter.guild.members)}",
                f"Людей: {len(list(filter(lambda m: m.bot == False,inter.guild.members)))}",
                f"Ботов: {len(list(filter(lambda m: m.bot == True,inter.guild.members)))}",
            ]
        ),
    )
    emb.add_field(
        name="Статусы",
        value="\n".join(
            [
                f"В сети: {len(list(filter(lambda m: str(m.status) == 'online',inter.guild.members)))}",
                f"Не активен: {len(list(filter(lambda m: str(m.status) == 'idle',inter.guild.members)))}",
                f"Не беспокоить: {len(list(filter(lambda m: str(m.status) == 'dnd',inter.guild.members)))}",
                f"Не в сети: {len(list(filter(lambda m: str(m.status) == 'offline',inter.guild.members)))}",
            ]
        ),
    )
    emb.add_field(
        name="Каналы",
        value="\n".join(
            [
                f"Всего: {len(inter.guild.channels)}",
                f"Текстовых: {len(list(filter(lambda c: c.type == disnake.ChannelType.text,inter.guild.channels)))}",
                f"Голосовых: {len(list(filter(lambda c: c.type == disnake.ChannelType.voice,inter.guild.channels)))}",
            ]
        ),
    )
    emb.add_field(
        name="Владелец",
        value=f"{inter.guild.owner.name}#{inter.guild.owner.discriminator} ({inter.guild.owner.mention})",
    )
    emb.add_field(
        name="Дата создания",
        value=disnake.utils.format_dt(inter.guild.created_at)
        + "\n"
        + disnake.utils.format_dt(inter.guild.created_at, "R"),
    )
    await inter.response.send_message(embed=emb)


@bot.slash_command(description="Топ по сообщениям")
async def leaders(inter, channel: disnake.TextChannel):
    await inter.response.defer()
    top = {}
    async for message in channel.history(limit=100):
        aid = message.author.id
        if message.author.bot or message.is_system():
            continue
        if not aid in top:
            top[aid] = 1
        else:
            top[aid] += 1
    top = dict(sorted(top.items(), key=lambda i: i[1], reverse=True))
    description = ""
    for k, v in top.items():
        description += f"<@{k}>\n{bar(v,100,10)} {v}%\n"
    emb = disnake.Embed(title="Топ по сообщениям", description=description)
    await inter.edit_original_response(embed=emb)


@bot.slash_command(description="Поиграем в сапёр?")
async def minesweeper(inter):
    karta = [["" for _ in range(10)] for _ in range(10)]
    numbers = {
        0: ":zero:",
        1: ":one:",
        2: ":two:",
        3: ":three:",
        4: ":four:",
        5: ":five:",
        6: ":six:",
        7: ":seven:",
        8: ":eight:",
        9: ":nine:",
    }
    def scanaround(cx, cy):
      count = 0
      for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
        x, y = cx + dx, cy + dy
        if x < 0 or x > 9 or y < 0 or y > 9: continue
        if karta[x][y] == ":bomb:": count += 1
      return count

    for i in range(15):
      rx = randint(0,9)
      ry = randint(0,9)
      karta[rx][ry] = ":bomb:"
    description = ""
    for i in range(len(karta)):
      for j in range(len(karta[i])):
        if karta[i][j] == ":bomb:": continue
        count = scanaround(i,j)
        karta[i][j] = numbers[count]
      description += "".join(map(lambda e: f"||{e}||",karta[i])) + "\n"
    emb = disnake.Embed(title="Сапёр", description=description)
    await inter.response.send_message(embed=emb)
 
 
@bot.slash_command(name="aki",description="Игра в Акинатора")
async def akigame(inter):
  await inter.response.defer()
  aki = Akinator()
  question = await aki.start_game(language="ru",child_mode=not inter.channel.nsfw)
  components = [[
    disnake.ui.Button(label="1",custom_id="yes"),
    disnake.ui.Button(label="2",custom_id="no"),
    disnake.ui.Button(label="3",custom_id="idk"),
    disnake.ui.Button(label="4",custom_id="probably"),
    disnake.ui.Button(label="5",custom_id="pn")
    ],
    [
      disnake.ui.Button(label="<-",custom_id="back")
    ]
  ]
  while aki.progression <= 80:
    emb = disnake.Embed(title="Акинатор", description="\n".join([f"Шаг: {aki.step}",f"Шанс угадывания: {bar(aki.progression,100,5)}",f"Вопрос: {question}","Ответы:","1. Да","2. Нет", "3. Не знаю", "4. Вероятно","5. Скорее нет, не совсем"]))
    msg = await inter.edit_original_response(embed=emb,components=components)
    binter = await bot.wait_for("button_click",check=lambda binter: binter.message.id == msg.id and binter.author.id == inter.author.id)
    await binter.response.defer()
    if binter.component.custom_id == "back":
      try:
        question = await aki.back()
      except akinator.CantGoBackAnyFurther: pass
    else:
      question = await aki.answer(binter.component.custom_id)
  await aki.win()
  emb = disnake.Embed(title=aki.first_guess['name'],description=aki.first_guess['description'])
  emb.set_image(url=aki.first_guess["absolute_picture_path"])
  await inter.edit_original_response(embed=emb,components=[])
  await aki.close()
    
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    channel = bot.get_channel(1058288394469380106)
    entry = await message.guild.audit_logs(
        limit=1, action=disnake.AuditLogAction.message_delete
    ).flatten()
    who = None
    if entry[0]:
        entry = entry[0]
    else:
        who = "Автор или бот"
    if entry.target.id == message.author.id:
        who = f"{entry.user.name}#{entry.user.discriminator} ({entry.user.mention})"
    else:
        who = "Автор или бот"
    emb = disnake.Embed(
        title="Сообщение удалено",
        description=f"```{message.content.replace('`','`'+ chr(8302))}```",
    )
    emb.add_field(
        name="Автор",
        value=f"{message.author.name}#{message.author.discriminator} ({message.author.mention})",
    )
    emb.add_field("Кто удалил", who)
    emb.add_field(
        name="Канал", value=f"{message.channel.name} ({message.channel.mention})"
    )
    await channel.send(embed=emb)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.content == after.content:
        return
    channel = bot.get_channel(1058288394469380106)

    emb = disnake.Embed(
        title="Сообщение изменено",
        description=f"Старое сообщение:\n```{before.content.replace('`','`' + chr(8302))}```\nНовое сообщение:\n```{after.content.replace('`','`' + chr(8302))}```",
    )
    emb.add_field(
        name="Автор",
        value=f"{before.author.name}#{before.author.discriminator} ({before.author.mention})",
    )
    emb.add_field(
        name="Канал", value=f"{before.channel.name} ({before.channel.mention})"
    )
    await channel.send(embed=emb)


@bot.event
async def on_invite_create(i):
    await bot.get_channel(1058288394469380106).send(
        embed=disnake.Embed(
            title="Создан новый инвайт",
            description="\n".join(
                [
                    f"Код: {i.code}",
                    f"Создатель: {i.inviter.name}#{i.inviter.discriminator}",
                ]
            ),
        )
    )
    bot.invites.append([i.code, i.uses])


@bot.event
async def on_invite_delete(i):
    for j in bot.invites:
        if i.code == j[0]:
            bot.invites.remove(j)


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.BotMissingPermissions):
        return await inter.response.send_message(
            f"Недостаточно прав у бота.\nНеобходимые права: {''.join(error.missing_permissions)}"
        )
    raise error


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1058288394469380106)
    invites = await member.guild.invites()
    invite = None
    for i in invites:
        for j in bot.invites:
            if i.code == j[0] and i.uses > j[1]:
                invite = i
                break
            if invite:
                break
    bot.invites = []
    for i in invites:
        bot.invites.append([i.code, i.uses])
    emb = disnake.Embed(title="Участник зашёл на сервер")
    emb.add_field(
        name="Кто зашёл",
        value=f"{member.name}#{member.discriminator} ({member.mention})",
    )
    if invite.inviter:
        emb.add_field(
            name="Кто пригласил",
            value=f"{invite.inviter.name}#{invite.inviter.discriminator} ({invite.inviter.mention})",
        )
    else:
        emb.add_field(name="Кто пригласил", value="Неизвестно")
    emb.add_field(
        name="Какой инвайт", value=f"{invite.code} ({invite.uses} использований)"
    )
    await channel.send(embed=emb)


@bot.event
async def on_message(message):
    channels = [
        1007962013080748045,
        1007962768902721616,
        1007963566365737020,
        1060470872609140807,
    ]
    if message.channel.id in channels and len(message.attachments) < 1:
        await message.delete()


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Game("фантик лапкой"))
    bot.add_cog(Starboard(bot))
    if not hasattr(bot, "invites"):
        bot.invites = []
        for i in await bot.guilds[0].invites():
            bot.invites.append([i.code, i.uses])


bot.run(os.getenv("TOKEN"))
