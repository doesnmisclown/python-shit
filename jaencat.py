from disnake.ext import commands
import disnake, traceback, aiohttp, hashlib, re, string, io
from datetime import timedelta, date
from textwrap import indent
from tortoise import Tortoise, fields
from tortoise.models import Model


def bar(n, m, l):
    return "[" + ("#" * round(n / m * l)).ljust(l, " ") + "]"


class Role(Model):
    role_id = fields.BigIntField(pk=True)
    guild_id = fields.BigIntField()
    alone = fields.BooleanField()

    class Meta:
        table = "roles"


class Guild(Model):
    guild_id = fields.BigIntField(pk=True)
    starboard_channel = fields.BigIntField()

    class Meta:
        table = "guilds"


class PersistentView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class JaenCat(commands.InteractionBot):
    def __init__(self):
        intents = disnake.Intents.default()
        intents.message_content = True
        super().__init__(
            intents=intents,
        )
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
        guild = await Guild.get_or_none(guild_id=reaction.message.guild.id)
        if not guild:
            return
        if guild.starboard_channel == 0:
            return
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
            emb.set_user(
                name=reaction.message.user.display_name,
                icon_url=reaction.message.user.display_avatar.url,
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
                message = await self.bot.get_channel(guild.starboard_channel).send(
                    content=content, embed=emb, view=view
                )
                self.cache[reaction.message.id] = message
        elif reaction.message.id in self.cache:
            await self.cache[reaction.message.id].delete()
            self.cache.pop(reaction.message.id)


if __name__ != "__main__":
    exit()
bot = JaenCat()


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Game("фантик"))
    await Tortoise.init(
        db_url="mysql://root:6UT4Ki85%5EPwH@localhost:3306/jaencat",
        modules={"models": ["__main__"]},
    )
    bot.add_cog(Starboard(bot))


@bot.slash_command(description="Выдача цветной или пинг роли")
@commands.bot_has_permissions(manage_roles=True)
async def claim(
    inter,
    role: disnake.Role = commands.Param(description="Разрешенная роль для выдачи"),
):
    await inter.response.defer()
    r = await Role.get_or_none(guild_id=inter.guild.id, role_id=role.id)
    if not r:
        return await inter.edit_original_response(
            content="Данной роли нету в списке разрешенных для выдачи"
        )
    if r.alone:
        alone_roles = await Role.filter(guild_id=inter.guild.id, alone=True)
        for ar in alone_roles:
            ar = disnake.utils.get(inter.guild.roles, id=ar.role_id)
            await inter.user.remove_roles(ar)
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


@bot.slash_command(description="Отправить реплику от имени персонажа")
@commands.bot_has_permissions(manage_webhooks=True)
async def rp(
    inter,
    character: str = commands.Param(description="Имя персонажа"),
    text: str = commands.Param(description="Текст реплики"),
):
    if len(bot.rp_names) > 24:
        bot.rp_names = bot.rp_names[1:]
    if not character in bot.rp_names:
        bot.rp_names.append(character)
    webhooks = await inter.channel.webhooks()
    if len(webhooks) < 1:
        webhook = await inter.channel.create_webhook(name="Jaen Cat")
        await webhook.send(text, username=character)
    else:
        await webhooks[0].send(text, username=character)
    await inter.response.send_message("Реплика отправлена", ephemeral=True)


@rp.autocomplete("character")
async def character_autocomplete(i: disnake.Interaction, current: str):
    return [
        ch
        for ch in bot.rp_names
        if current.lower() in ch.lower()
    ]


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
            "Role": Role,
            "Guild": Guild,
            "Tortoise": Tortoise,
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
        answers[i] = f"{a} (0)"
    view.add_item(SurveySelect(answers))
    emb = disnake.Embed(
        title="Внимание, опрос", description=f"{content}\nПроголосовали: "
    )
    await inter.response.send_message(embed=emb, view=view)

@bot.event
async def on_slash_command_error(inter,error):
  if isinstance(error,commands.BotMissingPermissions): return await inter.response.send_message(f"Недостаточно прав у бота.\nНеобходимые права: {''.join(error.missing_permissions)}")
  raise error
bot.run("")
