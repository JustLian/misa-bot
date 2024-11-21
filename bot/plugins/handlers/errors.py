from datetime import datetime
import hikari
import crescent
import hikari.errors
import bot
from os import getenv
import traceback


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


CHANNEL_ID = getenv("notifications.channel")


async def global_error_handler(exc: Exception, ctx: crescent.Context, _):

    # Constructing message for the user
    text = "В моём коде произошла какая-то непредвиденная ошибка!"

    if CHANNEL_ID:
        text += f"\nИнформация о ней уже у разработчика, чтобы узнать когда выйдет баг-фикс, рекомендую зайти на наш сервер [Shi no Shinpan]({getenv('guild_invite')})"
    else:
        text += f"\nПожалуйста зайди на наш сервер [Shi no Shinpan]({getenv('guild_invite')}) и сообщи о ней `@jxstrian`"
    
    await ctx.respond(embed=hikari.Embed(
        title="Произошла ошибка :<",
        description=text,
        color=bot.Colors.ERROR
    ))

    if CHANNEL_ID:

        doc = await plugin.model.db.guilds.find_one({'_id': ctx.guild_id})

        # Forming exception.txt
        tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        date = datetime.now().strftime('%d.%m.%Y %H:%M')
        content = f"Date: {date}\nGuild: {ctx.guild_id} | User: {ctx.user.id}\nCommand: {ctx.command}\nArguments: {ctx.options}\nGuild settings dump: {doc}\n\n --- Traceback ---\n\n{tb}"

        file = hikari.Bytes(
            content.encode('utf8'),
            'exception.txt'
        )

        await plugin.app.rest.create_message(
            channel=getenv("notifications.channel"),
            embed=hikari.Embed(
                title="Ошибка!",
                color=bot.Colors.ERROR
            ), attachment=file
        )