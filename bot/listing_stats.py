from os import getenv
import aiohttp
from logging import getLogger


log = getLogger("listing_stats")
SDC_URL = 'https://api.server-discord.com/v2/bots/{}/stats'


async def sdc(
    servers: int,
    shards: int,
    me_id: int
) -> None:
    
    token = getenv("listing_token.sdc")
    
    if not token:
        return

    async with aiohttp.request(
        "POST", SDC_URL.format(me_id),
        headers={"Authorization": f"SDC {token}"},
        json={'servers': servers, 'shards': shards}
    ) as req:
        
        if req.status == 200:
            return
        
        log.error(f"Couldn't update SDC: {req.status}")