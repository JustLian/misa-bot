import hikari
import crescent
import bot


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


@plugin.include
@crescent.command
async def info(ctx: crescent.Context) -> None:

    await ctx.respond(embed=hikari.Embed(
        description="## Misa Amane ❤️\n* Привет :] Я - очередной general-purpose бот, находящийся в разработке.\n* Пока что я умею только играть музыку и приветствовать новых людей на твоём сервере!\n* Используй `/admin config` для настройки приветствий\n* `/music play` запустит трек с практически любого сервиса\n* Бот полностью бесплатный, если есть предложения или баг-репорт, заходи на [Shi no Shimpan]()"
    ))