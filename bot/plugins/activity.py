import random
import hikari
import crescent
from crescent.ext import tasks
import bot


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


@plugin.include
@tasks.loop(minutes=10)
async def activity_update():
    
    server_count = 0
    member_count = 0

    async for guild in plugin.app.rest.fetch_my_guilds(newest_first=True):
        server_count += 1
        member_count += guild.approximate_member_count

    match random.randint(1, 2):
        case 1:
            text = f"{server_count} серверов"
        case 2:
            text = f"{member_count} пользователей"

    
    await plugin.app.update_presence(
        status=hikari.Status.IDLE,
        activity=hikari.Activity(name=text, type=hikari.ActivityType.WATCHING)
    )