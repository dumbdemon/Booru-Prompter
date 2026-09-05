import asyncio
import traceback
from functools import wraps

from aiohttp import web

from ..src.booru_prompter.utils.logger import get_logger

logger = get_logger("routes.settings")


def route_error_handler(func):
    @wraps(func)
    async def wrapper(request):
        try:
            return await func(request)
        except asyncio.CancelledError:
            raise asyncio.CancelledError
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error("Route error in %s: %s", {func.__name__, error_details})
            return web.json_response(
                {"success": False, "error": f"Internal server error: {str(e)}"},
                status=500,
            )

    return wrapper


def validate_json_body(*required_fields):
    def decorator(func):
        @wraps(func)
        async def wrapper(request):
            try:
                data = await request.json()
            except Exception:
                return web.json_response(
                    {"success": False, "error": "Invalid JSON body"}, status=400
                )
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                message = ", ".join(missing_fields)
                return web.json_response(
                    {
                        "success": False,
                        "error": f"Missing required fields: {message}",
                    },
                    status=400,
                )
            request.json_data = data
            return await func(request)

        return wrapper

    return decorator


def validate_query_params(*required_params):
    def decorator(func):
        @wraps(func)
        async def wrapper(request):
            missing_params = [p for p in required_params if not request.query.get(p)]
            if missing_params:
                message = ", ".join(missing_params)
                return web.json_response(
                    {
                        "success": False,
                        "error": f"Missing required query parameters: {message}",
                    },
                    status=400,
                )
            return await func(request)

        return wrapper

    return decorator


def success_response(data=None, message=None):
    body = {"success": True}
    if data is not None:
        body["data"] = data
    if message:
        body["message"] = message
    return web.json_response(body)


def error_response(message, status=400, errors=None, updated=None):
    if errors is None:
        errors = []

    if updated is None:
        updated = []

    return web.json_response(
        {
            "success": False,
            "error": message,
            "err_messages": errors,
            "updaetd": updated,
        },
        status=status,
    )


__all__ = [
    "route_error_handler",
    "validate_json_body",
    "validate_query_params",
    "success_response",
    "error_response",
]
