from .config_manager import (
    SettingsDefinition,
    get_setting,
    get_settings,
    set_setting,
    save_setting,
    is_known_setting,
)
from .cache_manager import CacheManager
from .paths_manager import PathManager


cache_manager = CacheManager()
setting = SettingsDefinition()
paths = PathManager()


__all__ = [
    "get_setting",
    "get_settings",
    "get_settings",
    "set_setting",
    "save_setting",
    "is_known_setting",
    "cache_manager",
    "setting",
    "paths",
]
