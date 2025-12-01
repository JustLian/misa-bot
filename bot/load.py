from hikari import Color, colors
from hikari import Embed as _Embed
import os
import dotenv
import typing
import random
import datetime


dotenv.load_dotenv()
__all__ = ("settings", "Colors", "Embed")


class Embed(_Embed):
    def __init__(
        self,
        title: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        url: typing.Optional[str] = None,
        color: typing.Optional[colors.Color] = None,
        timestamp: typing.Optional[datetime.datetime] = None
    ):
        super().__init__(
            title=title, description=description, url=url, color=color, timestamp=timestamp
        )
        ms = random.randint(0, 5)
        if ms in (1, 2):
            self.set_footer("made w/ ❤️ by @jxstrian", icon="https://files.catbox.moe/54mi8w.jpg")
        if ms == 3:
            self.set_footer("Ответь боту запросом, чтобы добавить в очередь!")


settings = {
    "discord": {"token": os.environ["discord.token"]},
    "mongo": {
        "password": os.environ.get("mongo.password", None),
        "username": os.environ.get("mongo.username", None),
        "host": os.environ["mongo.host"],
        "port": os.environ["mongo.port"],
        "db": os.environ["mongo.db"],
    },
    "guild": os.environ["guild"],
}


class Colors:
    ERROR = Color.from_hex_code("8884ff")
    WAIT = Color.from_hex_code("fde2ff")
    WARNING = Color.from_hex_code("d7bce8")
    SUCCESS = Color.from_hex_code("f570a5")