from comfy_api.latest import io, ComfyExtension
from .src.booru_prompter.nodes import GetTagsByCode, GetTagsByURL


WEB_DIRECTORY = "./web"


class BooruPrompter(ComfyExtension):
    @staticmethod
    async def get_node_list() -> list[type[io.ComfyNode]]:
        return [GetTagsByCode, GetTagsByURL]


async def comfy_entrypoint() -> ComfyExtension:
    return BooruPrompter()