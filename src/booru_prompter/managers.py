import yaml
import folder_paths
import pathlib
import traceback
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from .logger import get_logger
from .crytography import decrypt, encrypt

logging = get_logger("managers")


class SettingsDefinition:
    def __init__(self):
        self.booru_site = "booru_site"
        self.booru_username = "booru_username"
        self.booru_api_token = "booru_api_token"
        self.booru_user_id = "booru_user_id"
        self.cache_purge_on_startup = "cache_purge_on_startup"
        self.cache_use_rolling_delete = "cache_use_rolling_delete"
        self.cache_refresh_on_use = "cache_refresh_on_use"
        self.cache_rolling_rate = "cache_rolling_rate"


class BooruSettings(BaseModel):
    booru_site: str = Field(
        "https://danbooru.donmai.us/", description="The booru site for lookup"
    )
    booru_username: str = Field(
        "", description="The user's username for the booru site"
    )
    booru_api_token: str = Field(
        "", description="The user's api token for the booru site"
    )
    booru_user_id: str = Field(
        "0000000", description="The user's User ID used for the User Agent"
    )

    cache_purge_on_startup: bool = Field(
        False, description="Whether to delete all cache entries on start up"
    )
    cache_use_rolling_delete: bool = Field(
        True, description="Whether or not to set a cache timer"
    )
    cache_refresh_on_use: bool = Field(
        True, description="Whether to reset the cache timer (if exists) on use"
    )
    cache_rolling_rate: int = Field(
        7, description="The time in days to delete cache entry"
    )

    model_config = {"extra": "ignore"}


class PathManager:
    def __init__(self):
        # Base Paths
        self.ext_path = pathlib.Path(__file__).resolve().parent.parent.parent
        self.user_path = pathlib.Path(folder_paths.get_user_directory())

        # Special Paths
        self.user_path = self.user_path / "default" / "BooruPrompter"
        self.defaults_path = self.ext_path / "defaults"

        # Make Directories
        self._mkdir()

    def _mkdir(self) -> None:
        for config in [self.user_path]:
            config.mkdir(parents=True, exist_ok=True)

    def get_user_path(self, filename: str) -> pathlib.Path:
        return self.user_path / filename

    def get_defaults_path(self, filename: str) -> pathlib.Path:
        return self.defaults_path / filename

    def get_pyproject(self) -> pathlib.Path:
        return self.ext_path / "pyproject.toml"


class ConfigManager:
    def __init__(self):
        self.config_name = "settings.yaml"
        self.data: Optional[Dict[str, Any]] = {}
        self._model: BooruSettings = BooruSettings()
        settings = PathManager().get_user_path(self.config_name)
        with settings.open(mode="r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            for key, value in data.items():
                e_value = decrypt(key, value, PathManager())
                self.data[key] = e_value
            logging.info("%s keys registered", len(self.data))
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

        if key == setting.booru_user_id:
            import re

            patttern = re.compile(r"^\d+$")
            matches = patttern.findall(value)

            if len(matches) == 0:
                logging.error("Failed to validate: Not A Number")
                return False

        try:
            updated = {**self._model.model_dump(), key: value}
            self._model = BooruSettings.model_validate(updated)
            return True
        except ValidationError:
            logging.error("Failed to validate: \n%s", traceback.format_exc())
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

    def save(self) -> bool:
        settings = PathManager().get_user_path(self.config_name)
        try:
            with settings.open(mode="w", encoding="utf-8") as file:
                data = self._model.model_dump()
                safe_data = {k: encrypt(k, v, PathManager()) for k, v in data.items()}
                yaml.dump(safe_data, file, default_flow_style=False, sort_keys=False)
                return True
        except Exception as e:
            logging.error(
                "Errors occurred while saving: %s\n%s", e, traceback.format_exc()
            )
            return False

    def reset_all(self) -> None:
        self._model = BooruSettings()
        self.save()


paths = PathManager()
setting = SettingsDefinition()


_bp_settings: Optional[BooruSettings] = None


def get_settings() -> ConfigManager:
    global _bp_settings  # skipcq: PYL-W0603
    if _bp_settings is None:
        _bp_settings = ConfigManager()
    return _bp_settings


def get_setting(key: str, default: Any = None) -> Any:
    return get_settings().get(key, default)


def set_setting(key: str, value: Any) -> bool:
    return get_settings().set(key, value)


def save_setting() -> bool:
    return get_settings().save()


def is_known_setting(key: str) -> bool:
    return key in BooruSettings.model_fields
