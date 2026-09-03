import json
import traceback
import tomllib
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from .managers import get_setting, setting, paths
from .logger import get_logger
from datetime import timedelta
from .cache_manager import cache_manager

logging = get_logger("booru_getter")

pyproject = paths.get_pyproject()
with open(pyproject, "rb") as file:
    pyproject_data = tomllib.load(file)
version = pyproject_data.get("project", {}).get("version")

HostURL = get_setting(setting.booru_site)
userid = get_setting(setting.booru_user_id)
headers = {"User-Agent": f"BooruPrompter/{version} (user #{userid})"}

logging.info("User Agent is %s", headers["User-Agent"])


def butify(string: str, replaceunderscores: bool):
    string = string.replace(" ", ", ")
    if replaceunderscores:
        string = string.replace("_", " ")
    string = string.replace("(", "\\(")
    string = string.replace(")", "\\)")
    return string


def get_tags_by_code(code: int, remove_underscores: bool):
    return get_tags_by_url(f"{HostURL}posts/{code}", remove_underscores, code)


def construct_url(url) -> str:
    if not url[-4:] == "json":
        url = url + ".json"

    url += "?"

    username = get_setting(setting.booru_username)
    api_token = get_setting(setting.booru_api_token)

    if username:
        url += f"login={username}&"

    if api_token:
        url += f"api_key={api_token}"

    logging.debug(url)
    return url


def set_duration() -> float or None:
    duration: float = None
    time = timedelta(days=get_setting(setting.cache_rolling_rate, 7))
    if get_setting(setting.cache_refresh_on_use, True):
        duration = time.total_seconds()
    return duration


def get_tags_by_url(url: str, remove_underscores: bool, ref_code=None) -> {}:
    duration = set_duration()

    index = url.find("?")
    if index > -1:
        url = url[:index]

    if "posts/" not in url:
        raise ValueError(f"URL is not a post: {url}")

    if not ref_code:
        ref_code = url.split("/")[-1]

    if cache_manager.hasattr(ref_code):
        if get_setting(setting.cache_refresh_on_use, True):
            cache_manager.touch(ref_code, duration)

        old_tags, tag = cache_manager.get(ref_code, True)
        if old_tags is not None and tag is HostURL:
            return cache_manager.get(ref_code)

    url = construct_url(url)

    if url.lower().startswith("http"):
        req = Request(url, headers=headers)
    else:
        raise ValueError from None
    message = None

    try:
        with urlopen(req) as response:  # skipcq: BAN-B310
            data = json.load(response)

            all_tags = {
                "all_tags": butify(data["tag_string"], remove_underscores),
                "tags": butify(data["tag_string_general"], remove_underscores),
                "artist_tags": butify(data["tag_string_artist"], remove_underscores),
                "character_tags": butify(
                    data["tag_string_character"], remove_underscores
                ),
                "copyright_tags": butify(
                    data["tag_string_copyright"], remove_underscores
                ),
                "meta_tags": butify(data["tag_string_meta"], remove_underscores),
            }

            cache_manager.set(
                key=ref_code, value=all_tags, expire=duration, tag=HostURL
            )

            return all_tags
    except HTTPError as e:
        message = f"HTTP Error Status Code {e.code}"
    except URLError as e:
        message = f"Failed to reach the server. Reason: {e.reason}"
    except Exception as e:
        message = f"Something went wrong: {str(e)}"
        logging.error(traceback.format_exc())

    all_tags = {
        "all_tags": message,
        "tags": message,
        "artist_tags": message,
        "character_tags": message,
        "copyright_tags": message,
        "meta_tags": message,
    }

    return all_tags
