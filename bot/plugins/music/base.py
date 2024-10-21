import bot

import os
import logging
import typing as t

import hikari
import crescent
import lavalink_rs
from lavalink_rs.model import events # type: ignore


plugin = crescent.Plugin[hikari.GatewayBot, bot.Model]()
# TODO: Make commands guild-only


class Events(lavalink_rs.EventHandler):
    async def ready(
        self,
        client: lavalink_rs.LavalinkClient,
        session_id: str,
        event: events.Ready,
    ) -> None:
        del client, session_id, event
        logging.info("HOLY READY")

    async def track_start(
        self,
        client: lavalink_rs.LavalinkClient,
        session_id: str,
        event: events.TrackStart,
    ) -> None:
        del session_id

        logging.info(
            f"Started track {event.track.info.author} - {event.track.info.title} in {event.guild_id.inner}"
        )

        player_ctx = client.get_player_context(event.guild_id.inner)

        assert player_ctx
        assert player_ctx.data

        data = t.cast(t.Tuple[hikari.Snowflake, hikari.api.RESTClient], player_ctx.data)

        assert event.track.user_data and isinstance(event.track.user_data, dict)

        if event.track.info.uri:
            await data[1].create_message(
                data[0],
                embed=bot.Embed(
                    description=f"Сейчас играет: [`{event.track.info.author} - {event.track.info.title}`](<{event.track.info.uri}>)\nЗапросил: <@{event.track.user_data['requester_id']}>",
                    color=bot.Colors.SUCCESS
                )
            )
        else:
            await data[1].create_message(
                data[0],
                embed=bot.Embed(
                    description=f"Сейчас играет: `{event.track.info.author} - {event.track.info.title}`\nЗапросил: <@{event.track.user_data['requester_id']}>",
                    color=bot.Colors.SUCCESS
                )
            )


# async def custom_node(
#    client: lavalink_rs.LavalinkClient, guild_id: lavalink_rs.GuildId | int
# ) -> lavalink_rs.Node:
#    node = client.get_node_by_index(0)
#    assert node
#    return node

@plugin.include
@crescent.event
async def start_lavalink(event: hikari.ShardReadyEvent) -> None:
    """Event that triggers when the hikari gateway is ready."""

    node = lavalink_rs.NodeBuilder(
        os.environ["lavalink.host"],
        os.environ["lavalink.ssl"] == "True",
        os.environ["lavalink.password"],
        event.my_user.id,
    )

    lavalink_client = await lavalink_rs.LavalinkClient.new(
        Events(),
        [node],
        lavalink_rs.NodeDistributionStrategy.sharded(),
        # lavalink_rs.NodeDistributionStrategy.custom(custom_node),
    )

    plugin.model.lavalink = lavalink_client