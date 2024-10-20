from hikari import Color
import os
import dotenv


dotenv.load_dotenv()
__all__ = ("settings", "Colors")


settings = {
    "discord": {"token": os.environ["discord.token"]},
    "mongo": {
        "password": os.environ["mongo.password"],
        "username": os.environ["mongo.username"],
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
    MODEL_PREVIEW = Color.from_hex_code("db74ca")
