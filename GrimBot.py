import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # подхватывает переменные из файла .env, лежащего в этой же папке

# Токен бери из переменной окружения, никогда не пиши его прямо в код
TOKEN = os.getenv("DISCORD_TOKEN")

VERIFIED_ROLE_NAME = "Verified"  # имя роли, которую получает юзер после верификации

LIBRARY_IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "library_images"
)  # абсолютный путь — не зависит от того, откуда запущен python bot.py
LIBRARY_IMAGES_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
TARIFF_IMAGE_FILENAME = "tarif"  # ищется в LIBRARY_IMAGES_DIR, без учёта регистра/расширения

# Ссылка на скачивание GrimTool с Dropbox
GRIMTOOL_DOWNLOAD_URL = (
    "https://www.dropbox.com/scl/fi/7mol3b9vpvn3j5mrat7dh/GrimTools.exe"
    "?rlkey=2e05wfvzyk8kvlax9cgenprkd&st=t8e0yifc&dl=0"
)

# Домены Steam, которые нужно добавить в исключения антивируса/файрвола,
# если Steam не запускается после установки GrimTool.
STEAM_WHITELIST_DOMAINS = [
    "steampowered.com",
    "steamcommunity.com",
    "steamstatic.com",
    "steamcontent.com",
    "steamusercontent.com",
    "steamserver.net",
    "steam-chat.com",
    "steam-api.com",
    "steamdeck.com",
    "steamgames.com",
    "steam.tv",
    "s.team",
    "playartifact.com",
]

GUIDES_SUBCATEGORIES = {
    "no_connection": {
        "label": "Нет соединения с Steam",
        "emoji": "🌐",
        "url": "https://youtu.be/9Q2qrAZ23_c?si=Y7JwIxdJeY67xFFD",
    },
    "wont_launch": {
        "label": "Steam не запускается после установки GrimTool",
        "emoji": "🚫",
        "url": "https://youtu.be/5mKgEiWDrlo",
        "domains": STEAM_WHITELIST_DOMAINS,
    },
}

LIBRARY_SUBCATEGORIES = {
    "standard": {
        "label": "Стандартная Библиотека IRON",
        "emoji": "🟣",
        "prefix": "standard",  # файлы должны начинаться с этого слова, например Standard1.png
    },
    "unique": {
        "label": "Уникальная Gold/Diamond",
        "emoji": "🟡",
        "prefix": "unique",  # например Unique1.png
    },
    "exclusive": {
        "label": "Эксклюзивная Diamond",
        "emoji": "🔵",
        "prefix": "exclusive",  # например Exclusive.png
    },
}

STAFF_ROLE_NAME = "Поддержка"  # имя роли персонала — поменяй на точное название своей роли
TICKET_CATEGORY_NAME = "Тикеты"  # категория, в которой будут создаваться каналы тикетов

TICKET_CATEGORIES = {
    "tech": {
        "label": "Техническая проблема",
        "description": "Технические проблемы, баги, ошибки",
        "emoji": "🔧",
    },
    "payment": {
        "label": "Проблемы с оплатой",
        "description": "Проблемы с приобретением платных услуг, тарифов",
        "emoji": "💳",
    },
    "staff": {
        "label": "Заявка на персонал",
        "description": "Станьте частью нашего проекта!",
        "emoji": "📋",
    },
    "report": {
        "label": "Жалоба на игрока",
        "description": "Неадекватное поведение и т.д.",
        "emoji": "⚠️",
    },
}

# Контент навигатора — отредактируй текст под себя, структуру не трогай
NAVIGATOR_CATEGORIES = {
    "tariffs": {
        "label": "Тарифы",
        "emoji": "💎",
        "title": "💎 Тарифы",
        "description": (
            "Здесь будет описание тарифов сервера.\n\n"
            "**Базовый** — бесплатно\n"
            "**Премиум** — впиши сюда цену и что входит\n"
            "**VIP** — впиши сюда цену и что входит"
        ),
    },
    "guides": {
        "label": "Гайды",
        "emoji": "📖",
        "title": "📖 Гайды",
        "description": (
            "Здесь будет список гайдов по серверу.\n\n"
            "Например: ссылки на канал #гайды или краткие инструкции прямо тут."
        ),
    },
    "faq": {
        "label": "Часто задаваемые вопросы (FAQ)",
        "emoji": "❓",
        "title": "❓ FAQ",
        "description": (
            "**Вопрос 1?**\nОтвет 1.\n\n"
            "**Вопрос 2?**\nОтвет 2.\n\n"
            "Допиши свои реальные вопросы и ответы."
        ),
    },
    "library": {
        "label": "Библиотека Игр GrimTool",
        "emoji": "🎮",
        "title": "🎮 Библиотека Игр GrimTool",
        # для этого раздела текст не используется — бот шлёт скриншоты из LIBRARY_IMAGES_DIR
        "description": None,
    },
    "download": {
        "label": "Скачать GrimTool",
        "emoji": "⬇️",
        "title": "⬇️ Скачать GrimTool",
        "description": (
            "Нажми на кнопку ниже, чтобы скачать GrimTool с Dropbox."
        ),
    },
}

intents = discord.Intents.default()
intents.members = True  # обязательно включить "Server Members Intent" в Dev Portal
intents.message_content = True  # обязательно включить "Message Content Intent" в Dev Portal

bot = commands.Bot(command_prefix="!", intents=intents)


class VerifyView(discord.ui.View):
    """View с кнопкой. timeout=None + bot.add_view() в on_ready
    делают кнопку рабочей даже после перезапуска бота."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Подтвердить",
        style=discord.ButtonStyle.success,
        custom_id="verify_button",  # custom_id обязателен для persistent view
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        if role is None:
            role = await guild.create_role(
                name=VERIFIED_ROLE_NAME,
                reason="Автосоздание роли верификации",
            )

        member = interaction.user
        if role in member.roles:
            await interaction.response.send_message(
                "Ты уже верифицирован ✅", ephemeral=True
            )
            return

        try:
            await member.add_roles(role, reason="Прошёл верификацию")
        except discord.Forbidden:
            await interaction.response.send_message(
                "Не получилось выдать роль — у бота не хватает прав "
                "или его роль ниже роли Verified в списке ролей сервера.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Готово! Доступ открыт 🔓", ephemeral=True
        )


async def get_or_create_category(guild: discord.Guild) -> discord.CategoryChannel:
    category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
    if category is None:
        category = await guild.create_category(TICKET_CATEGORY_NAME)
    return category


def ticket_channel_name(member: discord.Member) -> str:
    return f"тикет-{member.name}".lower().replace(" ", "-")


class CloseTicketView(discord.ui.View):
    """Кнопка закрытия тикета внутри созданного канала."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Закрыть тикет",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_button",
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Тикет будет закрыт через 5 секунд...", ephemeral=False
        )
        await interaction.channel.send("Канал удаляется...")
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Тикет закрыт")


class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=data["label"],
                description=data["description"],
                emoji=data["emoji"],
                value=key,
            )
            for key, data in TICKET_CATEGORIES.items()
        ]
        super().__init__(
            placeholder="Выберите категорию обращения",
            options=options,
            custom_id="ticket_select",
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        category_key = self.values[0]
        category_data = TICKET_CATEGORIES[category_key]

        existing = discord.utils.get(guild.text_channels, name=ticket_channel_name(member))
        if existing is not None:
            await interaction.response.send_message(
                f"У тебя уже открыт тикет: {existing.mention}", ephemeral=True
            )
            return

        ticket_category = await get_or_create_category(guild)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        if staff_role is not None:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )

        channel = await guild.create_text_channel(
            name=ticket_channel_name(member),
            category=ticket_category,
            overwrites=overwrites,
            reason=f"Тикет от {member}",
        )

        embed = discord.Embed(
            title=f"{category_data['emoji']} {category_data['label']}",
            description=f"Тикет открыл {member.mention}.\n\n"
            f"{category_data['description']}\n\n"
            "Опиши свой вопрос подробнее, персонал ответит как можно скорее.",
            color=discord.Color.blue(),
        )

        await channel.send(
            content=f"{member.mention}" + (f" {staff_role.mention}" if staff_role else ""),
            embed=embed,
            view=CloseTicketView(),
        )

        await interaction.response.send_message(
            f"Тикет создан: {channel.mention}", ephemeral=True
        )


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


def get_library_files(prefix: str | None = None) -> list[discord.File]:
    """Собирает скриншоты из LIBRARY_IMAGES_DIR и возвращает их как discord.File.
    Если указан prefix — берёт только файлы, имя которых начинается с него (без учёта регистра).
    Discord позволяет максимум 10 файлов в одном сообщении."""
    if not os.path.isdir(LIBRARY_IMAGES_DIR):
        return []

    filenames = sorted(
        f for f in os.listdir(LIBRARY_IMAGES_DIR)
        if f.lower().endswith(LIBRARY_IMAGES_EXTENSIONS)
        and (prefix is None or f.lower().startswith(prefix.lower()))
    )
    filenames = filenames[:10]  # лимит Discord — 10 файлов в сообщении

    return [
        discord.File(os.path.join(LIBRARY_IMAGES_DIR, name))
        for name in filenames
    ]


def find_tariff_image_file() -> discord.File | None:
    """Ищет в LIBRARY_IMAGES_DIR файл tarif.* (имя без расширения совпадает с
    TARIFF_IMAGE_FILENAME без учёта регистра)."""
    if not os.path.isdir(LIBRARY_IMAGES_DIR):
        return None

    for f in os.listdir(LIBRARY_IMAGES_DIR):
        name, ext = os.path.splitext(f)
        if ext.lower() in LIBRARY_IMAGES_EXTENSIONS and name.lower() == TARIFF_IMAGE_FILENAME.lower():
            return discord.File(os.path.join(LIBRARY_IMAGES_DIR, f))
    return None


def build_guide_content(sub_data: dict) -> str:
    """Собирает текст сообщения для гайда: эмодзи, название, ссылка и,
    если у гайда есть список доменов (domains), — список доменов Steam,
    которые нужно добавить в исключения антивируса/файрвола."""
    content = f"{sub_data['emoji']} **{sub_data['label']}**\n🔗 {sub_data['url']}"
    domains = sub_data.get("domains")
    if domains:
        domains_list = "\n".join(f"• {d}" for d in domains)
        content += (
            "\n\nЕсли после установки GrimTool Steam не запускается, добавь "
            "следующие домены в исключения антивируса/файрвола:\n"
            f"{domains_list}"
        )
    return content


class GuidesSelect(discord.ui.Select):
    """Под-меню: выбор конкретного видео-гайда."""

    def __init__(self, selected: str | None = None):
        options = [
            discord.SelectOption(
                label=data["label"],
                emoji=data["emoji"],
                value=key,
                default=(key == selected),
            )
            for key, data in GUIDES_SUBCATEGORIES.items()
        ]
        super().__init__(
            placeholder="Выберите гайд",
            options=options,
            custom_id="guides_sub_select",
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        sub_key = self.values[0]
        sub_data = GUIDES_SUBCATEGORIES[sub_key]

        await interaction.response.defer()
        active_navigator_sessions[interaction.user.id] = interaction

        new_view = NavigatorHubView(extra="guides", selected_top="guides", selected_sub=sub_key)

        # edit_original_response вместо send_message — обновляет то же сообщение,
        # а не создаёт новое при каждом переключении гайда
        await interaction.edit_original_response(
            content=build_guide_content(sub_data),
            attachments=[],
            view=new_view,
        )


class DownloadGrimToolButton(discord.ui.Button):
    """Кнопка-ссылка на Dropbox со скачиванием GrimTool.
    У link-кнопок нет custom_id и callback — клик просто открывает url
    в браузере, Discord не отправляет это как interaction боту."""

    def __init__(self):
        super().__init__(
            label="⬇️ Скачать GrimTool",
            style=discord.ButtonStyle.link,
            url=GRIMTOOL_DOWNLOAD_URL,
            row=1,
        )


class LibrarySelect(discord.ui.Select):
    """Под-меню: выбор раздела библиотеки (Standard / Unique / Exclusive)."""

    def __init__(self, selected: str | None = None):
        options = [
            discord.SelectOption(
                label=data["label"],
                emoji=data["emoji"],
                value=key,
                default=(key == selected),
            )
            for key, data in LIBRARY_SUBCATEGORIES.items()
        ]
        super().__init__(
            placeholder="Выберите раздел библиотеки",
            options=options,
            custom_id="library_sub_select",
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        sub_key = self.values[0]
        sub_data = LIBRARY_SUBCATEGORIES[sub_key]

        await interaction.response.defer()
        active_navigator_sessions[interaction.user.id] = interaction

        new_view = NavigatorHubView(extra="library", selected_top="library", selected_sub=sub_key)

        files = get_library_files(prefix=sub_data["prefix"])
        if not files:
            await interaction.edit_original_response(
                content=f"Скриншоты для раздела «{sub_data['label']}» пока не добавлены "
                f"(ожидаются файлы с именем, начинающимся на «{sub_data['prefix']}»).",
                attachments=[],
                view=new_view,
            )
            return

        # edit_original_response вместо send_message — обновляет то же сообщение,
        # а не создаёт новое при каждом переключении раздела
        await interaction.edit_original_response(
            content=f"{sub_data['emoji']} **{sub_data['label']}**",
            attachments=files,
            view=new_view,
        )


# Храним последнее взаимодействие пользователя с навигатором, чтобы при новом
# клике по ПУБЛИЧНОМУ списку можно было удалить предыдущую приватную карточку
# (Discord не позволяет редактировать чужой/старый ephemeral-ответ напрямую).
active_navigator_sessions: dict[int, discord.Interaction] = {}


class NavigatorSelect(discord.ui.Select):
    def __init__(self, selected: str | None = None):
        options = [
            discord.SelectOption(
                label=data["label"],
                emoji=data["emoji"],
                value=key,
                default=(key == selected),
            )
            for key, data in NAVIGATOR_CATEGORIES.items()
        ]
        super().__init__(
            placeholder="Выберите раздел",
            options=options,
            custom_id="navigator_select",
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        category_key = self.values[0]
        # этот select теперь существует только внутри уже открытой приватной
        # карточки навигатора (её открывает кнопка на публичном сообщении) —
        # поэтому всегда просто редактируем то же сообщение
        await interaction.response.defer()
        active_navigator_sessions[interaction.user.id] = interaction

        payload = build_navigator_payload(category_key)
        try:
            await interaction.edit_original_response(**payload)
        except discord.HTTPException as e:
            await interaction.followup.send(
                "Не получилось отправить файл/картинку — скорее всего, размер "
                f"превышает лимит загрузки для этого сервера.\n(Техническая ошибка: {e})",
                ephemeral=True,
            )


def build_navigator_payload(category_key: str) -> dict:
    """Собирает content/embed/attachments/view для конкретного раздела навигатора —
    используется и для первого ответа, и для последующих edit_original_response."""
    data = NAVIGATOR_CATEGORIES[category_key]

    if category_key == "library":
        return {
            "content": "🎮 **Библиотека Игр GrimTool** — выбери раздел:",
            "embed": None,
            "attachments": [],
            "view": NavigatorHubView(extra="library", selected_top="library"),
        }

    if category_key == "guides":
        return {
            "content": "📖 **Гайды** — выбери, что нужно настроить:",
            "embed": None,
            "attachments": [],
            "view": NavigatorHubView(extra="guides", selected_top="guides"),
        }

    if category_key == "download":
        embed = discord.Embed(
            title=data["title"],
            description=data["description"],
            color=discord.Color.gold(),
        )
        return {
            "content": "",
            "embed": embed,
            "attachments": [],
            "view": NavigatorHubView(extra="download", selected_top="download"),
        }

    if category_key == "tariffs":
        image_file = find_tariff_image_file()
        if image_file is None:
            return {
                "content": f"{data['title']}\nКартинка тарифов (`tarif.png`) пока не "
                "добавлена в папку library_images.",
                "embed": None,
                "attachments": [],
                "view": NavigatorHubView(extra=None, selected_top="tariffs"),
            }
        return {
            "content": f"{data['emoji']} **{data['label']}**",
            "embed": None,
            "attachments": [image_file],
            "view": NavigatorHubView(extra=None, selected_top="tariffs"),
        }

    embed = discord.Embed(
        title=data["title"],
        description=data["description"],
        color=discord.Color.gold(),
    )
    return {
        "content": "",
        "embed": embed,
        "attachments": [],
        "view": NavigatorHubView(extra=None, selected_top=category_key),
    }


class NavigatorHubView(discord.ui.View):
    """Единое View для всей навигации: верхний select всегда на месте,
    плюс под-select для тех разделов, где он нужен (библиотека/гайды).
    selected_top/selected_sub — чтобы select показывал реальный текущий выбор,
    а не сбрасывался на placeholder при каждом обновлении сообщения."""

    def __init__(
        self,
        extra: str | None = None,
        selected_top: str | None = None,
        selected_sub: str | None = None,
    ):
        super().__init__(timeout=None)
        self.add_item(NavigatorSelect(selected=selected_top))
        if extra == "library":
            self.add_item(LibrarySelect(selected=selected_sub))
        elif extra == "guides":
            self.add_item(GuidesSelect(selected=selected_sub))
        elif extra == "download":
            self.add_item(DownloadGrimToolButton())


class OpenNavigatorButton(discord.ui.Button):
    """Кнопка на публичном сообщении — открывает приватную карточку с самим
    выпадающим списком разделов. Кнопки не имеют проблемы 'запомненного'
    значения, в отличие от select, поэтому на публичном сообщении только она."""

    def __init__(self):
        super().__init__(
            label="🧭 Открыть навигатор",
            style=discord.ButtonStyle.primary,
            custom_id="open_navigator_button",
        )

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # defer ПЕРВЫМ делом — у нас всего 3 секунды на подтверждение,
        # а удаление старого сообщения может занять больше времени из-за сети
        await interaction.response.defer(ephemeral=True, thinking=True)

        old_interaction = active_navigator_sessions.get(user_id)
        if old_interaction is not None:
            try:
                await old_interaction.delete_original_response()
            except discord.HTTPException:
                pass  # токен уже истёк (>15 мин) или сообщение уже убрано — не страшно

        active_navigator_sessions[user_id] = interaction

        await interaction.edit_original_response(
            content="🧭 **Навигатор** — выбери раздел:",
            embed=None,
            attachments=[],
            view=NavigatorHubView(extra=None),
        )


class NavigatorEntryView(discord.ui.View):
    """View для публичного персистентного сообщения — только кнопка-открывалка."""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OpenNavigatorButton())


NavigatorView = NavigatorEntryView  # алиас для совместимости с !setup_navigator


@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    bot.add_view(NavigatorEntryView())
    bot.add_view(NavigatorHubView(extra=None))
    bot.add_view(NavigatorHubView(extra="library"))
    bot.add_view(NavigatorHubView(extra="guides"))
    bot.add_view(NavigatorHubView(extra="download"))
    print(f"Залогинен как {bot.user}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx: commands.Context):
    """Команда для админа: постит сообщение с кнопкой в текущем канале.
    Использовать один раз в канале #verification."""
    embed = discord.Embed(
        title="Верификация",
        description="Нажми на кнопку ниже, чтобы подтвердить, что ты не бот, "
        "и получить доступ к остальным каналам сервера.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed, view=VerifyView())
    await ctx.message.delete()


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx: commands.Context):
    """Команда для админа: постит сообщение с выпадающим списком категорий тикетов.
    Использовать один раз в канале для создания обращений."""
    embed = discord.Embed(
        title="📨 Обращение к администрации",
        description="Выберите категорию из списка ниже, чтобы создать тикет.\n"
        "Тикеты в неверной категории могут быть закрыты без ответа.",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed, view=TicketView())
    await ctx.message.delete()


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_navigator(ctx: commands.Context):
    """Команда для админа: постит сообщение с навигатором (выпадающий список разделов).
    Ответы на выбор видны только тому, кто выбрал пункт."""
    embed = discord.Embed(
        title="🧭 Навигатор",
        description="Выбери раздел из списка ниже — ответ увидишь только ты.",
        color=discord.Color.gold(),
    )
    await ctx.send(embed=embed, view=NavigatorView())
    await ctx.message.delete()


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(
            "Не найден DISCORD_TOKEN. Установи переменную окружения перед запуском."
        )
    bot.run(TOKEN)
