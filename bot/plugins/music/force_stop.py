import crescent.plugin
import bot
from bot.lavalink_voice import LavalinkVoice

import crescent
import hikari


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


@plugin.include
@crescent.event
async def kicked_from_vc(event: hikari.VoiceStateUpdateEvent) -> None:

    if event.state.user_id != plugin.app.get_me().id:
        return
    
    if not event.old_state:
        return

    if (
        event.old_state.channel_id is not None
        and
        event.state.channel_id is None
    ):
        voice = plugin.app.voice.connections.get(event.guild_id)

        assert isinstance(voice, LavalinkVoice)

        await voice.player.stop_now()
        await plugin.app.voice.disconnect(event.guild_id)
