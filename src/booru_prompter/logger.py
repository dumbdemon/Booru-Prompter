import logging
import os
from typing import Optional

LOGGER_NAME = "BooruPrompter"
DEFAULT_LOG_LEVEL = logging.INFO

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _root_logger():
    return logging.getLogger(LOGGER_NAME)


def _resolve_log_level(level: Optional[int]) -> int:
    """Resolve an explicit level or environment-driven default level."""
    if level is not None:
        return level

    env_level = os.environ.get("BOORUPROMPTER_LOG_LEVEL", "").upper()
    return LOG_LEVELS.get(env_level, DEFAULT_LOG_LEVEL)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name:
        logger_name = f"{LOGGER_NAME}.{name}"
    else:
        logger_name = LOGGER_NAME

    return logging.getLogger(logger_name)


def configure_logging(
    level: Optional[int] = None, handler: Optional[logging.Handler] = None
):  # skipcq: FLK-E501
    logger = _root_logger()
    logger.setLevel(_resolve_log_level(level))

    logger.handlers.clear()

    if handler is None:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
