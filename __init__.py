from comfy_api.latest import io, ComfyExtension
from .src.booru_prompter.nodes import GetTagsByCode, GetTagsByURL, ReadCache
from .src.booru_prompter.utils.logger import configure_logging, get_logger

logger = get_logger("BooruPrompter.init")

WEB_DIRECTORY = "./web"
configure_logging()


try:
    from . import server_routes
except Exception as e:
    logger.warning("Failed to load BooruPrompter custom routes: %s", e)


class BooruPrompter(ComfyExtension):
    @staticmethod
    async def get_node_list() -> list[type[io.ComfyNode]]:
        return [GetTagsByCode, GetTagsByURL, ReadCache]


async def comfy_entrypoint() -> ComfyExtension:
    return BooruPrompter()


__all__ = ["server_routes"]
