"""Top-level package for booru_prompter."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """Dumb Demon"""
__email__ = "ecchimanga@outlook.com"
__version__ = "0.0.1"

from .src.booru_prompter.nodes import NODE_CLASS_MAPPINGS
from .src.booru_prompter.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
