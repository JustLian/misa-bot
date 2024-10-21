import hikari
from bot.db import connect
import bot
import miru
import lavalink_rs


class Model:
    def __init__(self, client: hikari.GatewayBot):
        self.client = client
        self.miru: miru.Client = None
        self.lavalink: lavalink_rs.LavalinkClient
        self.db = connect()[bot.settings["mongo"]["db"]]

        client.event_manager.subscribe(hikari.ShardReadyEvent, self._ready)
        client.event_manager.subscribe(hikari.StoppingEvent, self._stop)

    async def _ready(self, _):
        pass

    async def _stop(self, _):
        pass
