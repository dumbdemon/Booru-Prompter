from comfy_api.latest import io, ComfyExtension
from .src.booru_prompter.nodes import GetTagsByCode, GetTagsByURL
from .src.booru_prompter.logger import configure_logging, get_logger

logger = get_logger("BooruPrompter.init")

WEB_DIRECTORY = "./web"
configure_logging()


try:
    from . import server_routes
except Exception as e:
    logger.warning(f"Failed to load SageUtils custom routes: {e}")


class BooruPrompter(ComfyExtension):
    @staticmethod
    async def get_node_list() -> list[type[io.ComfyNode]]:
        return [GetTagsByCode, GetTagsByURL]


async def comfy_entrypoint() -> ComfyExtension:
    return BooruPrompter()


__all__ = ["server_routes"]
