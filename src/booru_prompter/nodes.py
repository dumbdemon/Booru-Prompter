from comfy_api.latest import io
from .get_booru_tags import get_tags_by_code, get_tags_by_url
import re


BooruPrompter = "Booru Prompter"


def remove_tags(tags: str, to_remove: str = "", add_space: bool = True) -> str:
    tags_list = re.split(r",\s?", tags)

    if to_remove:
        remove_list = re.split(r",\s?", to_remove)
        final_list = []

        for tag in tags_list:
            if tag not in remove_list:
                final_list.append(tag)
        tags_list = final_list

    return f",{" " if add_space else ""}".join(tags_list)


class GetTagsByURL(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="DDGetTagsByURL",
            display_name="Get Tags (URL)",
            category=BooruPrompter,
            inputs=[
                io.String.Input("booru_url", multiline=False),
                io.Boolean.Input(
                    "remove_underscores",
                    display_name="Remove Underscores",
                    default=False,
                    label_on="Yes",
                    label_off="No",
                ),
                io.Boolean.Input(
                    "add_space",
                    display_name="Add Space after Comma",
                    default=True,
                    label_on="Yes",
                    label_off="No",
                ),
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
    def execute(cls, **kwargs) -> io.NodeOutput:
        booru_url = kwargs.get("booru_url", "")
        remove_underscores = kwargs.get("remove_underscores", False)
        add_space = kwargs.get("add_space", True)
        exclude_tags = kwargs.get("exclude_tags", "")

        the_tags = get_tags_by_url(booru_url, remove_underscores)
        all_tags = remove_tags(the_tags.get("all_tags"), exclude_tags, add_space)
        tags = remove_tags(the_tags.get("tags"), exclude_tags, add_space)
        artist_tags = remove_tags(the_tags.get("artist_tags"), add_space=add_space)
        character_tags = remove_tags(
            the_tags.get("character_tags"), add_space=add_space
        )
        copyright_tags = remove_tags(
            the_tags.get("copyright_tags"), add_space=add_space
        )
        meta_tags = remove_tags(the_tags.get("meta_tags"), add_space=add_space)

        return io.NodeOutput(
            all_tags, tags, artist_tags, character_tags, copyright_tags, meta_tags
        )  # skipcq: FLK-E501


class GetTagsByCode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="DDGetTagsByCode",
            display_name="Get Tags (ID)",
            category=BooruPrompter,
            inputs=[
                io.String.Input("booru_id", multiline=False),
                io.Boolean.Input(
                    "remove_underscores",
                    display_name="Remove Underscores",
                    default=False,
                    label_on="Yes",
                    label_off="No",
                ),
                io.Boolean.Input(
                    "add_space",
                    display_name="Add Space after Comma",
                    default=True,
                    label_on="Yes",
                    label_off="No",
                ),
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
    def execute(cls, **kwargs) -> io.NodeOutput:
        booru_id = kwargs.get("booru_id", 0)
        remove_underscores = kwargs.get("remove_underscores", False)
        add_space = kwargs.get("add_space", True)
        exclude_tags = kwargs.get("exclude_tags", "")

        the_tags = get_tags_by_code(booru_id, remove_underscores)
        all_tags = remove_tags(the_tags.get("all_tags"), exclude_tags, add_space)
        tags = remove_tags(the_tags.get("tags"), exclude_tags, add_space)
        artist_tags = remove_tags(the_tags.get("artist_tags"), add_space=add_space)
        character_tags = remove_tags(
            the_tags.get("character_tags"), add_space=add_space
        )
        copyright_tags = remove_tags(
            the_tags.get("copyright_tags"), add_space=add_space
        )
        meta_tags = remove_tags(the_tags.get("meta_tags"), add_space=add_space)

        return io.NodeOutput(
            all_tags, tags, artist_tags, character_tags, copyright_tags, meta_tags
        )  # skipcq: FLK-E501
