import json
from urllib.request import urlopen, Request
from .managers import get_setting, cache, setting

HostURL = get_setting(setting.booru_site)


def getauth() -> tuple:
    username = get_setting(setting.booru_username)
    api_token = get_setting(setting.boory_api_token)
    return username, api_token


def butify(string: str, replaceunderscores: bool):
    string = string.replace(" ", ", ")
    if replaceunderscores:
        string = string.replace("_", " ")
    return string


def get_tags_by_code(code: int, remove_underscores: bool):
    return get_tags_by_url(f"{HostURL}posts/{code}", remove_underscores, code)


def get_tags_by_url(url: str, remove_underscores: bool, ref_code=None) -> {}:
    index = url.find("?")
    if index > -1:
        url = url[:index]

    if "posts/" not in url:
        raise ValueError(f"URL is not a post: {url}")

    if not ref_code:
        ref_code = url.split("/")[-1]

    if ref_code in cache:
        return cache[ref_code]

    if not url[-4:] == "json":
        url = url + ".json"

    url += "?"

    username, api_token = getauth()

    if username:
        url += f"login={username}&"

    if api_token:
        url += f"api_key={api_token}&"

    print(url)

    if url.lower().startswith("http"):
        req = Request(url)
    else:
        raise ValueError from None

    with urlopen(req) as response:  # skipcq: BAN-B310
        data = json.load(response.read())

        all_tags = {
            "all_tags": butify(data["tag_string"], remove_underscores),
            "tags": butify(data["tag_string_general"], remove_underscores),
            "artist_tags": data["tag_string_artist"],
            "character_tags": data["tag_string_character"],
            "copyright_tags": data["tag_string_copyright"],
            "meta_tags": data["tag_string_meta"],
        }

        # cache.set(ref_code, all_tags)

        return all_tags
