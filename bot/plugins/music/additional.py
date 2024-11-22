import crescent.plugin
import bot
from bot.lavalink_voice import LavalinkVoice

import random

import crescent
import hikari

plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()


@plugin.include
@bot.groups.music.child
@crescent.command(
    description="Поставить музыку на паузу"
)
async def pause(ctx: crescent.Context) -> None:
    """Pause the currently playing song"""
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
                title="На паузе!",
                description=f"[`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="На паузе!",
                description=f"`{player.track.info.author} - {player.track.info.title}`",
                color=bot.Colors.SUCCESS
            ))

        await voice.player.set_pause(True)
    else:
        await ctx.respond(embed=bot.Embed(
            title="Что стопать?",
            description="Сейчас ничего не играет.",
            color=bot.Colors.ERROR
        ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    description="Продолжить вопросизведение музыки"
)
async def resume(ctx: crescent.Context) -> None:
    """Resume the currently playing song"""
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
                title="Включила!",
                description=f"Сейчас играет: [`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Включила!",
                description=f"Сейчас играет: `{player.track.info.author} - {player.track.info.title}`",
                color=bot.Colors.SUCCESS
            ))

        await voice.player.set_pause(False)
    else:
        await ctx.respond(embed=bot.Embed(
            title="Что включать-то?",
            description="В очереди ничего нет",
            color=bot.Colors.ERROR
        ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    description="Показать очередь воспроизведения"
)
async def queue(ctx: crescent.Context) -> None:
    """List the current queue"""
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

    now_playing = "Ничего"

    if player.track:
        time_s = int(player.state.position / 1000 % 60)
        time_m = int(player.state.position / 1000 / 60)
        time_true_s = int(player.state.position / 1000)
        time = f"{time_m:02}:{time_s:02}"

        assert player.track.user_data and isinstance(player.track.user_data, dict)

        if player.track.info.uri:
            now_playing = f"[`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>): {time} (<@!{player.track.user_data['requester_id']}>)"
        else:
            now_playing = f"`{player.track.info.author} - {player.track.info.title}`: {time} (<@!{player.track.user_data['requester_id']}>)"

    queue = await voice.player.get_queue().get_queue()
    queue_text = ""

    for idx, i in enumerate(queue):
        if idx == 9:
            break

        assert i.track.user_data and isinstance(i.track.user_data, dict)

        if i.track.info.uri:
            queue_text += f"**{idx+1}** [`{i.track.info.author} - {i.track.info.title}`](<{i.track.info.uri}>) (<@!{i.track.user_data['requester_id']}>)\n"
        else:
            queue_text += f"**{idx+1}** `{i.track.info.author} - {i.track.info.title}` (<@!{i.track.user_data['requester_id']}>)\n"

    if not queue_text:
        queue_text = "Пусто"

    await ctx.respond(embed=bot.Embed(
        description=f"### Сейчас играет\n{now_playing}\n### Очередь\n{queue_text}",
        color=bot.Colors.WARNING
    ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    name="remove",
    description="Убрать трек из очереди"
)
class Remove:
    index = crescent.option(int)

    async def callback(ctx: crescent.Context) -> None:
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

        queue = voice.player.get_queue()

        if ctx.options.index > await queue.get_count():
            await ctx.respond(bot.Embed(
                title="А где...",
                description="Я не нашла такой трек в очереди!",
                color=bot.Colors.ERROR
            ))
            return None

        assert isinstance(ctx.options.index, int)
        track_in_queue = await queue.get_track(ctx.options.index - 1)
        assert track_in_queue
        track = track_in_queue.track

        if track.info.uri:
            await ctx.respond(embed=bot.Embed(
                title="Включила!",
                description=f"Сейчас играет: [`{track.info.author} - {track.info.title}`](<{track.info.uri}>)",
                color=bot.Colors.SUCCESS
            ))
        else:
            await ctx.respond(embed=bot.Embed(
                title="Включила!",
                description=f"Сейчас играет: `{track.info.author} - {track.info.title}`",
                color=bot.Colors.SUCCESS
            ))

        queue.remove(ctx.options.index - 1)


@plugin.include
@bot.groups.music.child
@crescent.command(
    description="Удалить все треки из очереди"
)
async def clear(ctx: crescent.Context) -> None:
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

    queue = voice.player.get_queue()

    if not await queue.get_count():
        await ctx.respond(bot.Embed(
            title="А что чистить?",
            description="Очередь и так пуста!",
            color=bot.Colors.ERROR
        ))
        return None

    queue.clear()
    await ctx.respond(bot.Embed(
        title="Опа 🧹",
        description="Почистила очередь!",
        color=bot.Colors.SUCCESS
    ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    description="Перемешать треки в очереди"
)
async def shuffle(ctx: crescent.Context) -> None:
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

    queue_ref = voice.player.get_queue()
    queue = await queue_ref.get_queue()

    random.shuffle(queue)

    queue_ref.replace(queue)

    await ctx.respond(bot.Embed(
        title="Перемешала!",
        color=bot.Colors.SUCCESS
    ))


@plugin.include
@bot.groups.music.child
@crescent.command(
    name='volume',
    description="Установить уровень громкости музыки"
)
class Volume:
    volume = crescent.option(int, min_value=1, max_value=200)

    async def callback(self, ctx: crescent.Context) -> None:
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

        voice.player.set_volume(self.volume)
    
        await ctx.respond(bot.Embed(
            title=f"Теперь звук на {self.volume}%!",
            color=bot.Colors.SUCCESS
        ))