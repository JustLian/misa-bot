import hikari
import crescent
import bot
from os import getenv


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


CHANNEL_ID = getenv("notifications.channel")


if CHANNEL_ID:
    
    @plugin.include
    @crescent.event
    async def guild_created(event: hikari.GuildJoinEvent) -> None:
        await plugin.app.rest.create_message(
            channel=getenv("notifications.channel"),
            embed=hikari.Embed(
                title="Новый сервер",
                description=f"Название: `{event.guild.name}`\nКоличество пользователей: `{event.guild.member_count}`",
                color=bot.Colors.SUCCESS
            )
        )

    @plugin.include
    @crescent.event
    async def guild_created(event: hikari.GuildLeaveEvent) -> None:
        await plugin.app.rest.create_message(
            channel=getenv("notifications.channel"),
            embed=hikari.Embed(
                title="Сервер убран",
                description=f"Название: `{event.old_guild.name}`",
                color=bot.Colors.WARNING
            )
        )

    @plugin.include
    @crescent.event
    async def guild_created(_: hikari.ShardReadyEvent) -> None:
        await plugin.app.rest.create_message(
            channel=getenv("notifications.channel"),
            embed=hikari.Embed(
                title="Бот запущен!",
                color=bot.Colors.WAIT
            )
        )