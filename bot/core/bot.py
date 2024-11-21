import hikari
import crescent
import miru
import bot
import lavalink_rs


# async def hook(ctx: crescent.Context) -> crescent.HookResult:
#     doc = await model.db.users.find_one({"_id": ctx.user.id})
#     if doc is None:
#         doc = {
#             "_id": ctx.user.id,
#             "levels": {"pickaxe": 1, "mine": 1},
#             "coins": 0,
#             "inventory": [],
#             "miners": 0,
#         }
#         await model.db.uers.insert_one(doc)

#     return crescent.HookResult()


gw_bot = hikari.GatewayBot(bot.settings["discord"]["token"], intents=hikari.Intents.ALL)

model = bot.Model(gw_bot)
client = crescent.Client(
    gw_bot,
    model=model,
    # command_hooks=[hook],
    tracked_guilds=[int(bot.settings["guild"])] if bot.settings["guild"] != "None" else None,
)
miru_client = miru.Client(gw_bot)



model.miru = miru_client

client.plugins.load_folder("bot.plugins")


@client.include
@crescent.event
async def add_guild(e: hikari.GuildJoinEvent):
    doc = await model.db.guilds.find_one({"_id": e.guild_id})
    if doc is None:
        doc = {
            "_id": e.guild_id,
            "settings": {
                "welcome": {
                    "title": "Привет :>",
                    "description": "Добро пожаловать на сервер, [user.mention]!",
                    "color": "#fde2ff",
                    "image": None,
                    "thumbnail": None,
                    "channel": None,
                },
                "farewell": {
                    "title": "О нееет",
                    "description": "[user.mention] покинул нас :(",
                    "color": "#6d6d6d",
                    "image": None,
                    "thumbnail": None,
                    "channel": None,
                }
            },
        }
        await model.db.guilds.insert_one(doc)

    return crescent.HookResult()


def run():
    gw_bot.run(
        activity=hikari.Activity(name="Strinova", type=hikari.ActivityType.PLAYING),
        afk=True,
    )
