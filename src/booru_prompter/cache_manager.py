import shutil
from diskcache import Cache
from typing import Any
from .managers import paths, get_setting, setting
from .logger import get_logger

logger = get_logger("cache.manager")


class CacheManager:
    def __init__(self):
        self.cache_path = paths.get_user_path(".bp_cache")
        self._purge()
        self._new()

    def _purge(self):
        if get_setting(setting.cache_purge_on_startup, False):
            if self.cache_path.exists() and self.cache_path.is_dir():
                shutil.rmtree(self.cache_path)
                logger.info("Cache has been purged")

    def _new(self):
        self.cache = Cache(self.cache_path.resolve().as_posix())
        logger.info("New cache has been created")

    def get(self, key: str, tag=False) -> Any or (Any, None):
        return self.cache.get(key, tag=tag)

    def set(self, key: str, value: {}, tag: str, expire: float = None):
        self.cache.set(key=key, value=value, expire=expire, tag=tag, retry=True)

    def touch(self, key: str, expire: float):
        self.cache.touch(key, expire)

    def hasattr(self, key: str) -> bool:
        return key in self.cache


cache_manager = CacheManager()
