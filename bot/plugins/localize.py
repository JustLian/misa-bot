import inspect
import crescent
import miru

from pyi18n import PyI18n
from pyi18n.loaders import PyI18nYamlLoader

from cachetools import TTLCache


plugin = crescent.Plugin()

loader = PyI18nYamlLoader('locale/', namespaced=True)
i18n = PyI18n(('en', 'ru'), loader=loader)

lang_cache = TTLCache(
    maxsize=1_000,
    ttl=900
)


async def _(key: str, obj: dict | str | int = None, params: dict = {}):

    guild_id = None
    lang = None

    # Trying to extract guild id from passed obj
    if obj:
        
        # Guild document from mongoDB
        if isinstance(obj, dict):
            lang = obj['settings']['general']['language']
        
        # Guild id as str/int
        elif isinstance(obj, int):
            guild_id = obj

        elif isinstance(obj, str):
            guild_id = int(obj)

    if not guild_id:
        frame = inspect.currentframe()
        parent_frame = frame.f_back

        args, _, _, values = inspect.getargvalues(parent_frame)
        arguments = {arg: values[arg] for arg in args}

        if (
            'ctx' in arguments and
            isinstance(arguments['ctx'], (crescent.Context, miru.ViewContext))
        ):
            guild_id = arguments['ctx'].guild_id
        
        elif (
            'event' in arguments and
            hasattr(arguments['event'], 'guild_id')
        ):

            guild_id = arguments['event'].guild_id

    if not lang:

        if not guild_id:
            return "COULDN'T EXTRACT GUILD_ID"
        
        if guild_id in lang_cache:
            lang = lang_cache[guild_id]

        else:
            doc = await plugin.model.db.guilds.find_one({"_id": guild_id}, {"settings.general.language": 1})

            if not doc:
                return F"COULDN'T FIND GUILD DOCUMENT ({guild_id})"
            
            lang = doc['settings']['general']['language']

    return i18n.gettext(lang, key, *params)