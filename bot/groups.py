import crescent
import hikari
import toolbox


__all__ = ["music", "admin"]


# async def _admin_hook(ctx: crescent.Context) -> crescent.HookResult:
#     if (
#         toolbox.calculate_permissions(ctx.member)
#         .intersection(hikari.Permissions.MANAGE_GUILD)
#     ) == hikari.Permissions.NONE:
#         await ctx.respond(embed=hikari.Embed(
#             title='Недостаточно прав',
#             description='Эту команду могут использовать только администраторы сервера',
#             color="#000000"
#         ), flags=hikari.MessageFlag.EPHEMERAL)
#         return crescent.HookResult(exit=True)

#     return crescent.HookResult()


music = crescent.Group(
    "music",
    dm_enabled=False,
    default_member_permissions=hikari.Permissions.CONNECT
)

admin = crescent.Group(
    "admin",
    dm_enabled=False,
    default_member_permissions=hikari.Permissions.MANAGE_GUILD
)
