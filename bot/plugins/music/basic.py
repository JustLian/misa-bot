import crescent.context
import bot
from bot.lavalink_voice import LavalinkVoice

import logging
import typing as t

import hikari
import crescent
from lavalink_rs.model.search import SearchEngines # type: ignore
from lavalink_rs.model.track import TrackData, PlaylistData, TrackLoadType # type: ignore

plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()
# TODO: GUILD ONLY


async def _join(ctx: crescent.Context) -> t.Optional[hikari.Snowflake]:
    if not ctx.guild_id:
        return None

    channel_id = None

    for i in ctx.options.items():
        if i[0] == "channel" and i[1]:
            channel_id = i[1].id
            break

    if not channel_id:
        voice_state = plugin.app.cache.get_voice_state(ctx.guild_id, ctx.user.id)

        if not voice_state or not voice_state.channel_id:
            return None

        channel_id = voice_state.channel_id

    voice = plugin.app.voice.connections.get(ctx.guild_id)

    if not voice:
        await LavalinkVoice.connect(
            ctx.guild_id,
            channel_id,
            ctx.app,
            plugin.model.lavalink,
            (ctx.channel_id, ctx.app.rest),
        )
    else:
        assert isinstance(voice, LavalinkVoice)

        await LavalinkVoice.connect(
            ctx.guild_id,
            channel_id,
            ctx.app,
            plugin.model.lavalink,
            (ctx.channel_id, ctx.app.rest),
            old_voice=voice,
        )

    return channel_id


@plugin.include
@bot.groups.music.child
@crescent.command(
    name="join"
)
class Join:
    channel = crescent.option(
        hikari.GuildVoiceChannel,
        default=None
    )

    async def callback(self, ctx: crescent.Context) -> None:
        """Joins the voice channel you are in"""
        await ctx.defer()
        
        channel_id = await _join(ctx)

        if channel_id:
            await ctx.respond(embed=bot.Embed(
                title="Зашла!",
                description=f"Присоединилась к каналу <#{channel_id}>",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Какой канал?",
                description="Чтобы я зашла в канал, зайди в него, либо укажи в аргументах команды",
                color=bot.Colors.ERROR
            ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    name="leave"
)
async def leave(ctx: crescent.Context) -> None:

    """Leaves the voice channel"""
    if not ctx.guild_id:
        return None

    voice = plugin.app.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(bot.Embed(
            title="Я не в войсе!",
            color=bot.Colors.ERROR
        ))
        return None

    await voice.disconnect()

    await ctx.respond(embed=bot.Embed(
        title="Вышла",
        color=bot.Colors.ERROR
    ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    name="play"
)
class Play:
    query = crescent.option(
        str,
        default=None
    )

    async def callback(self, ctx: crescent.Context) -> None:
        if not ctx.guild_id:
            return None
        
        await ctx.defer()

        await play_cb(ctx, self.query, ctx.user)


@plugin.include
@crescent.event
async def reply_to_play(event: hikari.GuildMessageCreateEvent) -> None:
    
    if event.author.is_bot or event.author.is_system:
        return
    
    if not event.message.referenced_message:
        return
    
    if event.message.referenced_message.author.id != plugin.app.get_me().id:
        return
    
    await play_cb(event.message, event.message.content, event.message.author)


async def play_cb(ctx: crescent.Context, query: str, user) -> None:

    if not query:
        await ctx.respond(embed=bot.Embed(
            title="Что играть?",
            description="Параметр query пустой",
            color=bot.Colors.ERROR
        ))
        return

    voice = plugin.app.voice.connections.get(ctx.guild_id)
    has_joined = False

    if not voice:
        if not hasattr(ctx, "options"):
            await ctx.respond(embed=bot.Embed(
                title="Где я..",
                description="Сначала добавь меня в голосовой канал!",
                color=bot.Colors.ERROR
            ))
            return

        if not await _join(ctx):
            await ctx.respond(embed=bot.Embed(
                title="А куда?",
                description="Сначала зайди в голосовой канал!",
                color=bot.Colors.ERROR
            ))
            return None
        voice = plugin.app.voice.connections.get(ctx.guild_id)
        has_joined = True

    assert isinstance(voice, LavalinkVoice)

    player_ctx = voice.player
    query = query.replace(">", "").replace("<", "")

    if not query:
        player = await player_ctx.get_player()
        queue = player_ctx.get_queue()

        if not player.track and await queue.get_count() > 0:
            player_ctx.skip()
        else:
            if player.track:
                await ctx.respond(embed=bot.Embed(
                    title="Ой-ой",
                    description="Какой-то трек уже играет!",
                    color=bot.Colors.ERROR
                ))
            else:
                await ctx.respond(embed=bot.Embed(
                    title="Ничего нет!",
                    description="Моя очередь пуста :<",
                    color=bot.Colors.ERROR
                ))

        return None

    if not query.startswith("http"):
        query = SearchEngines.spotify(query)

    try:
        tracks = await plugin.model.lavalink.load_tracks(ctx.guild_id, query)
        loaded_tracks = tracks.data

    except Exception as e:
        logging.error(e)
        await ctx.respond(embed=bot.Embed(
            title="Ошибка",
            description="Пишите `@jxstrian` :>",
            color=bot.Colors.ERROR
        ))
        return None

    if tracks.load_type == TrackLoadType.Track:
        assert isinstance(loaded_tracks, TrackData)

        loaded_tracks.user_data = {"requester_id": int(user.id)}

        player_ctx.queue(loaded_tracks)

        if loaded_tracks.info.uri:
            await ctx.respond(embed=bot.Embed(
                title="Добавила!",
                description=f"В очереди трек: [`{loaded_tracks.info.author} - {loaded_tracks.info.title}`](<{loaded_tracks.info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Добавила!",
                description=f"`В очереди трек: {loaded_tracks.info.author} - {loaded_tracks.info.title}`",
                color=bot.Colors.SUCCESS
            ))

    elif tracks.load_type == TrackLoadType.Search:
        assert isinstance(loaded_tracks, list)

        loaded_tracks[0].user_data = {"requester_id": int(user.id)}

        player_ctx.queue(loaded_tracks[0])

        if loaded_tracks[0].info.uri:
            await ctx.respond(embed=bot.Embed(
                title="Добавила!",
                description=f"В очереди трек: [`{loaded_tracks[0].info.author} - {loaded_tracks[0].info.title}`](<{loaded_tracks[0].info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Добавила!",
                description=f"`В очереди трек: {loaded_tracks[0].info.author} - {loaded_tracks[0].info.title}`",
                color=bot.Colors.SUCCESS
            ))

    elif tracks.load_type == TrackLoadType.Playlist:
        assert isinstance(loaded_tracks, PlaylistData)

        if loaded_tracks.info.selected_track:
            track = loaded_tracks.tracks[loaded_tracks.info.selected_track]

            track.user_data = {"requester_id": int(user.id)}

            player_ctx.queue(track)

            if track.info.uri:
                await ctx.respond(embed=bot.Embed(
                    title="Добавила!",
                    description=f"В очереди трек: [`{track.info.author} - {track.info.title}`](<{track.info.uri}>)",
                    color=bot.Colors.SUCCESS
                ))
            else:
                await ctx.respond(embed=bot.Embed(
                    title="Добавила!",
                    description=f"`В очереди трек: {track.info.author} - {track.info.title}`",
                    color=bot.Colors.SUCCESS
                ))
        else:
            tracks = loaded_tracks.tracks

            for i in tracks:
                i.user_data = {"requester_id": int(user.id)}

            queue = player_ctx.get_queue()
            queue.append(tracks)

            await ctx.respond(embed=bot.Embed(
                title="Добавила!",
                description=f"Добавила плейлист: `{loaded_tracks.info.name}`",
                color=bot.Colors.SUCCESS
            ))

    # Error or no search results
    else:
        await ctx.respond(embed=bot.Embed(
            title="Ничего нет!",
            description="Я не нашла ничего по твоему запросу :<",
            color=bot.Colors.ERROR
        ))
        return None

    if has_joined:
        return None

    player_data = await player_ctx.get_player()
    queue = player_ctx.get_queue()

    if player_data:
        if not player_data.track and await queue.get_track(0):
            player_ctx.skip()


@plugin.include
@bot.groups.music.child
@crescent.command()
async def skip(ctx: crescent.Context) -> None:
    """Skip the currently playing song"""
    if not ctx.guild_id:
        return None

    voice = plugin.app.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(bot.Embed(
            title="Я не в войсе!",
            color=bot.Colors.ERROR
        ))
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player.get_player()

    if player.track:
        if player.track.info.uri:
            await ctx.respond(embed=bot.Embed(
                title="Скипнула!",
                description=f"Пропущено: [`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Скипнула!",
                description=f"Пропущено: `{player.track.info.author} - {player.track.info.title}`",
                color=bot.Colors.SUCCESS
            ))

        voice.player.skip()
    else:
        await ctx.respond(embed=bot.Embed(
            title="Что стопать?",
            description="Сейчас ничего не играет.",
            color=bot.Colors.ERROR
        ))


@plugin.include
@bot.groups.music.child
@crescent.command()
async def stop(ctx: crescent.Context) -> None:
    """Stop the currently playing song"""
    if not ctx.guild_id:
        return None

    voice = plugin.app.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(bot.Embed(
            title="Я не в войсе!",
            color=bot.Colors.ERROR
        ))
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player.get_player()

    if player.track:
        if player.track.info.uri:
            await ctx.respond(embed=bot.Embed(
                title="Остановила!",
                description=f"[`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Остановила!",
                description=f"`{player.track.info.author} - {player.track.info.title}`",
                color=bot.Colors.SUCCESS
            ))

        await voice.player.stop_now()
    else:
        await ctx.respond(embed=bot.Embed(
            title="Что стопать?",
            description="Сейчас ничего не играет.",
            color=bot.Colors.ERROR
        ))
