import bot
import hikari
import crescent


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


@plugin.include
@crescent.event
async def join(e: hikari.MemberCreateEvent):
    doc = await plugin.model.db.guilds.find_one({"_id": e.guild_id})

    if doc["settings"]["welcome"]["channel"] == None:
        return

    embed = hikari.Embed(
        title=doc["settings"]["welcome"]["title"],
        description=doc["settings"]["welcome"]["description"].replace(
            "[user.mention]", e.member.mention
        ),
        color=doc["settings"]["welcome"]["color"],
    )

    if doc["settings"]["welcome"]["image"] != None:
        embed.set_image(doc["settings"]["welcome"]["image"])

    if doc["settings"]["welcome"]["thumbnail"] != None:
        embed.set_thumbnail(doc["settings"]["welcome"]["thumbnail"])

    await plugin.app.rest.create_message(
        doc["settings"]["welcome"]["channel"], embed=embed, user_mentions=True
    )


@plugin.include
@crescent.event
async def leave(e: hikari.MemberDeleteEvent):
    doc = await plugin.model.db.guilds.find_one({"_id": e.guild_id})

    if doc["settings"]["farewell"]["channel"] == None:
        return

    embed = hikari.Embed(
        title=doc["settings"]["farewell"]["title"],
        description=doc["settings"]["farewell"]["description"].replace(
            "[user.mention]", e.member.mention
        ),
        color=doc["settings"]["farewell"]["color"],
    )

    if doc["settings"]["farewell"]["image"] != None:
        embed.set_image(doc["settings"]["farewell"]["image"])

    if doc["settings"]["farewell"]["thumbnail"] != None:
        embed.set_thumbnail(doc["settings"]["farewell"]["thumbnail"])

    await plugin.app.rest.create_message(
        doc["settings"]["farewell"]["channel"], embed=embed, user_mentions=True
    )
