from comfy_api.latest import io
from .managers import get_setting, setting, cache_manager
from .tags.get_booru_tags import get_tags_by_code, get_tags_by_url
from .tags.booru_tags import BooruTags, create_booru_tags
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
    a_space = " " if add_space else ""

    return f",{a_space}".join(tags_list)


def handle_artists(artists_tags: str, remove_underscores: bool) -> str:
    a_tags = re.split(r",\s?", artists_tags)
    artist_prefix = get_setting(setting.tags_artist_prefix).replace(" ", "_")
    final_list = []
    for artist in a_tags:
        if artist[len(artist_prefix) :] == artist_prefix:
            continue
        the_string = f"{artist_prefix}_{artist}"
        if remove_underscores:
            the_string = the_string.replace("_", " ")
        final_list.append(the_string)

    return ", ".join(final_list)


def handle_all_tags_artist(booru_tags: BooruTags, remove_underscores: bool) -> str:
    all_tags = booru_tags.all_tags
    artist_tags = booru_tags.artist_tags
    artist_prefix = get_setting(setting.tags_artist_prefix).replace(" ", "_")
    final_list = []

    for tag in re.split(r",\s?", all_tags):
        if tag in re.split(r",\s?", artist_tags):
            string = f"{artist_prefix}_{tag}"
            if remove_underscores:
                string = string.replace("_", " ")
            final_list.append(string)
        else:
            final_list.append(tag)
    return ", ".join(final_list)


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
    def validate_inputs(cls, **kwargs) -> bool | str:
        if kwargs.get("booru_url", ""):
            return "Input cannot be empty"
        return True

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput:
        booru_url = kwargs.get("booru_url", "")
        remove_underscores = kwargs.get("remove_underscores", False)
        add_space = kwargs.get("add_space", True)
        exclude_tags = kwargs.get("exclude_tags", "")

        the_tags: BooruTags = get_tags_by_url(booru_url, remove_underscores)

        all_tags = remove_tags(
            handle_all_tags_artist(the_tags, remove_underscores),
            exclude_tags,
            add_space,
        )

        tags = remove_tags(the_tags.tags, exclude_tags, add_space)
        artist_tags = remove_tags(
            handle_artists(the_tags.artist_tags, remove_underscores),
            add_space=add_space,
        )
        character_tags = remove_tags(the_tags.character_tags, add_space=add_space)
        copyright_tags = remove_tags(the_tags.copyright_tags, add_space=add_space)
        meta_tags = remove_tags(the_tags.meta_tags, add_space=add_space)

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
                io.Int.Input("booru_id", default=1, min=1, max=0xFFFFFFFFFFFFF),
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
    def validate_inputs(cls, **kwargs) -> bool | str:
        if kwargs.get("booru_id", 0) == 0:
            return "Input cannot be '0'"
        return True

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput:
        booru_id = kwargs.get("booru_id", 0)
        remove_underscores = kwargs.get("remove_underscores", False)
        add_space = kwargs.get("add_space", True)
        exclude_tags = kwargs.get("exclude_tags", "")

        the_tags = get_tags_by_code(booru_id, remove_underscores)
        all_tags = remove_tags(
            handle_all_tags_artist(the_tags, remove_underscores),
            exclude_tags,
            add_space,
        )
        tags = remove_tags(the_tags.tags, exclude_tags, add_space)
        artist_tags = remove_tags(
            handle_artists(the_tags.artist_tags, remove_underscores),
            add_space=add_space,
        )
        character_tags = remove_tags(the_tags.character_tags, add_space=add_space)
        copyright_tags = remove_tags(the_tags.copyright_tags, add_space=add_space)
        meta_tags = remove_tags(the_tags.meta_tags, add_space=add_space)

        return io.NodeOutput(
            all_tags, tags, artist_tags, character_tags, copyright_tags, meta_tags
        )  # skipcq: FLK-E501


class ReadCache(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="DDExportCache",
            display_name="Export Cache",
            category=BooruPrompter,
            inputs=[],
            outputs=[io.String.Output("cache_json")],
        )

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput:
        import json

        disk_cache = {}
        for key in cache_manager.cache.iterkeys():
            t_cache: BooruTags = create_booru_tags(cache_manager.cache.get(key))
            dict_cache = t_cache.as_dict_list()
            dict_cache["tag_counts"] = t_cache.tag_counts
            disk_cache[key] = dict_cache
        try:
            return io.NodeOutput(json.dumps(disk_cache, indent=4))
        except Exception as e:
            return io.NodeOutput(f"Unable to load data: {str(e)}")
