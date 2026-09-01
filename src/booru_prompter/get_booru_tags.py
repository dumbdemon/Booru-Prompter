import json
from urllib.request import urlopen
from .configmanager import config


HostURL = config["booru"]["site"]


def getauth() -> tuple:
    return config["booru"]["username"], config["booru"]["api_token"]


def butify(string: str, replaceunderscores: bool):
    string = string.replace(" ", ", ")
    if replaceunderscores:
        string = string.replace("_", " ")
    return string


def grabtagsbycode(code: int, remove_underscores: bool):
    return grabtagsbyurl(f"{HostURL}posts/{code}", remove_underscores)


def grabtagsbyurl(url: str, remove_underscores: bool) -> dict():
    index = url.find("?")
    if index > -1:
        url = url[:index]

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
        response = urlopen(url)
    else:
        raise ValueError from None
    data = json.load(response.read())

    all_tags = {
        "tags": butify(data["tag_string_general"], remove_underscores),
        "artist_tags": data["tag_string_artist"],
        "character_tags": data["tag_string_character"],
        "copyright_tags": data["tag_string_copyright"],
        "meta_tags": data["tag_string_meta"],
    }

    # todo: Create cache if not erxist and add to it

    return all_tags
