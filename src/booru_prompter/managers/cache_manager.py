import shutil
from diskcache import Cache
from .config_manager import SettingsDefinition as setting, get_setting
from .paths_manager import PathManager as paths
from ..utils.logger import get_logger

logger = get_logger("cache.manager")


class CacheManager:
    def __init__(self):
        self.cache_path = paths().get_user_path(".bp_cache")
        self._purge()
        self._new()

    def _purge(self):
        if get_setting(setting().cache_purge_on_startup, False):
            # Check if user wants to purge before checking directory status
            if self.cache_path.exists() and self.cache_path.is_dir():
                shutil.rmtree(self.cache_path)
                logger.info("Cache has been purged")

    def _new(self):
        self._cache = Cache(self.cache_path.resolve().as_posix())
        logger.info("Cache Populated")

    def hasattr(self, key: str) -> bool:
        return key in self._cache

    @property
    def cache(self):
        return self._cache
