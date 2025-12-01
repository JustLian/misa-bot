import motor.motor_asyncio
import bot


client = None
_host = bot.settings["mongo"]["host"]
_port = bot.settings["mongo"]["port"]
_username = bot.settings["mongo"]["username"]
_password = bot.settings["mongo"]["password"]


def connect():
    global client
    if not client:
        if _username:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                "mongodb://{}:{}@{}:{}/?authMechanism=DEFAULT".format(
                    _username, _password, _host, _port
                )
            )
        else:
            client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{_host}:{_port}")
    return client
