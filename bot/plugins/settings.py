import hikari
import crescent
import bot
import miru


class InputValue(miru.Modal):
    value = miru.TextInput(
        label="Значение",
        placeholder="Введите значение параметра",
        required=True
    )

    def __init__(self, category, setting):
        if setting in ['description',]:
            print("hai")
            self.value.style = hikari.TextInputStyle.PARAGRAPH

        super().__init__(
            title=f"{category}: {setting}",
        )
        self.category = category
        self.setting = setting

    async def callback(self, ctx: miru.ModalContext) -> None:

        await plugin.model.db.guilds.update_one(
            {"_id": ctx.guild_id},
            {"$set": {
                f"settings.{self.category}.{self.setting}": self.value.value
            }}
        )

        await ctx.respond(
            embed=hikari.Embed(
                title="Сохранено!",
                description=f"Установлено значение `{self.value.value}`",
                color=bot.Colors.SUCCESS,
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )


class EditProperty(miru.View):

    def __init__(self, category, setting):
        super().__init__(timeout=200)
        self.category = category
        self.setting = setting

        if SETTINGS[self.category][self.setting]['type'] in ["str", "url", "hex"]:
            self.input_btn = miru.Button(
                label="Ввести", style=hikari.ButtonStyle.SUCCESS, emoji="✒️"
            )
            self.input_btn.callback = self.input_btn_callback

            self.add_item(self.input_btn)

        elif SETTINGS[self.category][self.setting]['type'] in ["text-channel", "voice-channel"]:
            self.channel_select = miru.ChannelSelect(
                channel_types=[hikari.ChannelType.GUILD_TEXT],
                placeholder="Выберите канал",
            )
            self.channel_select.callback = self.channel_select_callback

            self.add_item(self.channel_select)

    async def channel_select_callback(
        self, ctx: miru.ViewContext
    ) -> None:
        await plugin.model.db.guilds.update_one(
            {"_id": ctx.guild_id},
            {"$set": {f"settings.{self.category}.{self.setting}": self.channel_select.values[0].id}},
        )

        self.stop()

        await ctx.respond(
            embed=hikari.Embed(
                title="Сохранено!",
                description=f"Установлен канал {self.channel_select.values[0].mention}",
                color=bot.Colors.SUCCESS,
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    async def input_btn_callback(self, ctx: miru.ViewContext) -> None:
        
        modal = InputValue(self.category, self.setting)
        await ctx.respond_with_modal(modal)

    @miru.button(label="Очистить", style=hikari.ButtonStyle.DANGER, emoji="🧹")
    async def clear_button(self, ctx: miru.ViewContext, _) -> None:
        await plugin.model.db.guilds.update_one(
            {"_id": ctx.guild_id},
            {
                "$set": {
                    f"settings.{self.category}.{self.setting}": SETTINGS[self.category][
                        self.setting
                    ]["empty"]
                }
            },
        )

        self.stop()

        await ctx.respond(
            embed=hikari.Embed(title="Сохранено!", color=bot.Colors.SUCCESS),
            flags=hikari.MessageFlag.EPHEMERAL,
        )


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


SETTINGS = {
    "welcome": {
        "title": {"type": "str", "empty": ""},
        "description": {"type": "str", "empty": ""},
        "color": {"type": "hex", "empty": "#ffffff"},
        "image": {"type": "url", "empty": None},
        "thumbnail": {"type": "url", "empty": None},
        "channel": {"type": "text-channel", "empty": None},
    },
    "farewell": {
        "title": {"type": "str", "empty": ""},
        "description": {"type": "str", "empty": ""},
        "color": {"type": "hex", "empty": "#ffffff"},
        "image": {"type": "url", "empty": None},
        "thumbnail": {"type": "url", "empty": None},
        "channel": {"type": "text-channel", "empty": None},
    },
}


async def ac_option(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
):
    category = ctx.options.get("category", "")
    return [(x, x) for x in SETTINGS.get(category, {"wrongCategory"}).keys()]


@plugin.include
@crescent.command(name="config", description="Настройки бота")
class Settings:
    category = crescent.option(
        str, "Категория параметров", choices=[(x, x) for x in SETTINGS.keys()]
    )
    setting = crescent.option(str, "Параметр", autocomplete=ac_option)

    async def callback(self, ctx: crescent.Context):
        await ctx.defer(ephemeral=True)

        if self.category not in SETTINGS:
            await ctx.respond(embed=hikari.Embed(
                title="Такой категории нет",
                color=bot.Colors.ERROR
            ), ephemeral=True)
            return
        
        if self.setting not in SETTINGS[self.category]:
            await ctx.respond(embed=hikari.Embed(
                title="Такой настройки нет",
                color=bot.Colors.ERROR
            ), ephemeral=True)
            return
        
        doc = await plugin.model.db.guilds.find_one({"_id": ctx.guild_id})
        
        view = EditProperty(self.category, self.setting)
        msg = await ctx.respond(embed=hikari.Embed(
            title="Настройки",
            color=bot.Colors.WAIT
        ).add_field(
            "Параметр", f"`{self.category}: {self.setting}`"
        ).add_field(
            "Значение", f"`{doc['settings'][self.category][self.setting]}`"
        ).add_field(
            "Типа значения", "`" + SETTINGS[self.category][self.setting]["type"] + "`"
        ), ephemeral=True, components=view)

        plugin.model.miru.start_view(view, bind_to=msg)