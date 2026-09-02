import yaml
import folder_paths
from pathlib import Path
from typing import Any, Dict, Optional
from diskcache import Cache
from pydantic import BaseModel, Field, ValidationError
from .logger import get_logger

logging = get_logger("managers")


class BooruSettings(BaseModel):
    booru_site: str = Field("https://danbooru.donmai.us/", description="The booru site for lookup")
    booru_username: str = Field("", description="The user's username for the booru site")
    boory_api_token: str = Field("", description="The user's api token for the booru site")

    cache_purge_on_startup: bool = Field(False)
    cache_use_rolling_delete: bool = Field(True)
    cache_refresh_on_use: bool = Field(True)
    cache_rolling_rate: int = Field(7)

    model_config = {"extra": "ignore"}


class PathManager:
    def __init__(self):
        # Base Paths
        self.ext_path = Path(__file__).resolve().parent.parent.parent
        self.user_path = Path(folder_paths.get_user_directory())

        # Special Paths
        self.user_path = self.user_path / "default" / "BooruPrompter"
        self.defaults_path = self.ext_path / "defaults"

        # Make Directories
        self._mkdir()

    def _mkdir(self) -> None:
        for config in [self.user_path]:
            config.mkdir(parents=True, exist_ok=True)

    def get_user_path(self, filename: str) -> Path:
        return self.user_path / filename

    def get_defaults_path(self, filename: str) -> Path:
        return self.defaults_path / filename


class ConfigManager:
    def __init__(self):
        self.data: Optional[Dict[str, Any]] = {}
        self._model: BooruSettings = BooruSettings()
        config_path = PathManager().get_user_path("settings.yaml")
        with config_path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)
            for key, value in data.items():
                self.data[key] = value
        self.load()

    def load(self) -> None:
        try:
            self._model = BooruSettings.model_validate(self.data)
        except ValidationError:
            self._model = BooruSettings()
            self.save()

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self._model, key, default)

    def set(self, key: str, value: Any) -> bool:
        if not hasattr(self._model, key):
            return False

        try:
            updated = {**self._model.model_dump(), key: value}
            self._model = BooruSettings.model_validate(updated)
            return True
        except ValidationError:
            return False

    def get_setting_info(self, key: str) -> Optional[Dict[str, Any]]:
        field = BooruSettings.model_fields.get(key)
        if field is None:
            return None
        return {
            "description": field.description or "",
            "default": field.default,
            "type": type(field.default).__name__,
            "current_value": self.get(key),
        }

    def list_all_settings(self) -> Dict[str, Dict[str, Any]]:
        return {key: self.get_setting_info(key) for key in BooruSettings.model_fields}

    def save(self) -> None:
        with open(paths.user_path("settings.yaml")) as file:
            yaml.dump(self._model.model_dump(), file, default_flow_style=False, sort_keys=False)

    def reset_all(self) -> None:
        self._model = BooruSettings()
        self.save


class SettingsDefinition:
    def __init__(self):
        self.booru_site = "booru_site"
        self.booru_username = "booru_username"
        self.boory_api_token = "boory_api_token"
        self.cache_purge_on_startup = "cache_purge_on_startup"
        self.cache_use_rolling_delete = "cache_use_rolling_delete"
        self.cache_refresh_on_use = "cache_refresh_on_use"
        self.cache_rolling_rate = "cache_rolling_rate"


paths = PathManager()
cache = Cache(paths.get_user_path(".booruprompter_cache").resolve().as_posix())
setting = SettingsDefinition()


_bp_settings: Optional[BooruSettings] = None


def get_settings() -> ConfigManager:
    global _bp_settings
    if _bp_settings is None:
        _bp_settings = ConfigManager()
    return _bp_settings


def get_setting(key: str, default: Any = None) -> Any:
    return get_settings().get(key, default)


def set_setting(key: str, value: Any) -> bool:
    return get_settings().set()


def save_setting() -> bool:
    return get_settings().save()


def is_known_setting(key: str) -> bool:
    return key in BooruSettings.model_fields
