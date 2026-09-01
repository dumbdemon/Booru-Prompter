from comfy_api.latest import io
from .get_booru_tags import grabtagsbyurl, grabtagsbycode
import re


BooruPrompter = "Booru Prompter"


def remove_tags(tags: str, to_remove: str) -> str:
    if not to_remove:
        return tags

    remove_list = re.split(r",\s?", to_remove)
    tags_list = tags.split(",")
    final_list = []

    for tag in tags_list:
        if tag not in remove_list:
            final_list.append(tag)
    return ",".join(final_list)


class GetTagsByURL(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="DDGetTagsByURL",
            display_name="Get Tags (URL)",
            category=BooruPrompter,
            inputs=[
                io.String.Input("booru_url", multiline=False),
                io.Boolean.Input("remove_underscores", display_name="Remove Underscores", default=False, label_on="Yes", label_off="No"),
                io.String.Input("exclude_tags", multiline=True),
            ],
            outputs=[
                io.String.Output("all"),
                io.String.Output("tags_only"),
                io.String.Output("artist"),
                io.String.Output("character"),
                io.String.Output("copyright"),
                io.String.Output("meta"),
            ],
        )

    @classmethod
    def execute(cls, booru_url: str, remove_underscores: bool, exclude_tags: str) -> io.NodeOutput:
        tags, artist_tags, character_tags, copyright_tags, meta_tags = grabtagsbyurl(booru_url, remove_underscores)
        tags = remove_tags(tags, exclude_tags)
        all_tags = f"{tags}.{artist_tags}.{character_tags}.{copyright_tags},{meta_tags}"
        return io.NodeOutput(all_tags, tags, artist_tags, character_tags, copyright_tags, meta_tags)


class GetTagsByCode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="DDGetTagsByCode",
            display_name="Get Tags (ID)",
            category=BooruPrompter,
            inputs=[
                io.String.Input("booru_id", multiline=False),
                io.Boolean.Input("remove_underscores", display_name="Remove Underscores", default=False, label_on="Yes", label_off="No"),
                io.String.Input("exclude_tags", multiline=True),
            ],
            outputs=[
                io.String.Output("all"),
                io.String.Output("tags_only"),
                io.String.Output("artist"),
                io.String.Output("character"),
                io.String.Output("copyright"),
                io.String.Output("meta"),
            ],
        )

    @classmethod
    def execute(cls, booru_id: int, remove_underscores: bool, exclude_tags: str) -> io.NodeOutput:
        tags, artist_tags, character_tags, copyright_tags, meta_tags = grabtagsbycode(booru_id, remove_underscores)
        tags = remove_tags(tags, exclude_tags)
        all_tags = f"{tags}.{artist_tags}.{character_tags}.{copyright_tags}.{meta_tags}"
        return io.NodeOutput(all_tags, tags, artist_tags, character_tags, copyright_tags, meta_tags)
