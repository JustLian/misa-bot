import datetime
import crescent.plugin
import bot
from bot.lavalink_voice import LavalinkVoice

import crescent
from crescent.ext import tasks
import hikari


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()
no_users = {}


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


@plugin.include
@crescent.event
async def user_left_vc(event: hikari.VoiceStateUpdateEvent) -> None:

    me_id = plugin.app.get_me().id

    if event.state.user_id == me_id:
        return
    
    if not event.old_state:
        return
    
    voice = plugin.app.voice.connections.get(event.guild_id)
    
    if (
        event.old_state.channel_id is not None
        and
        event.state.channel_id is None
    ):
        
        if voice.channel_id != event.old_state.channel_id:
            return
        
        if len([
            x for x in
            plugin.app.cache.get_voice_states_view_for_channel(event.guild_id, voice.channel_id)
            if x != me_id
        ]) == 0:
            
            no_users[voice.channel_id] = (datetime.datetime.now(), event.guild_id)
            print("Marking channel as no_users!")


@plugin.include
@tasks.loop(minutes=2.5)
async def no_users_check():

    me_id = plugin.app.get_me().id
    to_be_deleted = []

    for channel, data in no_users.items():
        date, guild_id = data
        if (datetime.datetime.now() - date) < datetime.timedelta(minutes=5):
            continue

        # Either way it shouldn't be in that list
        to_be_deleted.append(channel)

        # If there are some people, skip over
        if len([
            x for x in
            plugin.app.cache.get_voice_states_view_for_channel(guild_id, channel)
            if x != me_id
        ]) != 0:
            continue
    
        # Disconnecting
        voice = plugin.app.voice.connections.get(guild_id)

        # Already disconnected
        if not voice:
            continue

        await plugin.app.voice.disconnect(guild_id)
    
    [no_users.pop(x) for x in to_be_deleted]