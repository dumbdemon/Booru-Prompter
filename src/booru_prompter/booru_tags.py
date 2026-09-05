import re
from typing import Dict, Any


class BooruTags:
    def __init__(
        self,
        all_tags: str,
        tags: str,
        artist_tags: str,
        character_tags: str,
        copyright_tags: str,
        meta_tags: str,
    ):
        self._all_tags = all_tags
        self._tags = tags
        self._artist_tags = artist_tags
        self._character_tags = character_tags
        self._copyright_tags = copyright_tags
        self._meta_tags = meta_tags

    @property
    def all_tags(self) -> str:
        return self._all_tags

    @property
    def tags(self) -> str:
        return self._tags

    @property
    def artist_tags(self) -> str:
        return self._artist_tags

    @property
    def character_tags(self) -> str:
        return self._character_tags

    @property
    def copyright_tags(self) -> str:
        return self._copyright_tags

    @property
    def meta_tags(self) -> str:
        return self._meta_tags

    @property
    def tag_counts(self) -> Dict[str, int]:
        return {
            "all_tags": self._check_count(self.all_tags),
            "tags": self._check_count(self.tags),
            "artist_tags": self._check_count(self.artist_tags),
            "character_tags": self._check_count(self.character_tags),
            "copyright_tags": self._check_count(self.copyright_tags),
            "meta_tags": self._check_count(self.meta_tags),
        }

    def _check_count(self, tags) -> int:
        a_list = re.split(r",\s?", tags)
        return len(a_list) if tags else 0

    def _check_empty(self, tags) -> list[Any]:
        a_list = re.split(r",\s?", tags)
        return a_list if tags else []

    def as_dict(self) -> Dict[str, str]:
        return {
            "all_tags": self.all_tags,
            "tags": self.tags,
            "artist_tags": self.artist_tags,
            "character_tags": self.character_tags,
            "copyright_tags": self.copyright_tags,
            "meta_tags": self.meta_tags,
        }

    def as_dict_list(self) -> Dict[str, list[str]]:
        return {
            "all_tags": self._check_empty(self.all_tags),
            "tags": self._check_empty(self.tags),
            "artist_tags": self._check_empty(self.artist_tags),
            "character_tags": self._check_empty(self.character_tags),
            "copyright_tags": self._check_empty(self.copyright_tags),
            "meta_tags": self._check_empty(self.meta_tags),
        }


def create_booru_tags(the_tags: {}) -> BooruTags:
    return BooruTags(
        the_tags.get("all_tags"),
        the_tags.get("tags"),
        the_tags.get("artist_tags"),
        the_tags.get("character_tags"),
        the_tags.get("copyright_tags"),
        the_tags.get("meta_tags"),
    )


def create_error_tags(message: str) -> BooruTags:
    return BooruTags(message, message, message, message, message, message)
