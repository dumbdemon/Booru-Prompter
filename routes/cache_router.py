from ..src.booru_prompter.logger import get_logger
from .base_router import route_error_handler, success_response, error_response

logger = get_logger("routes.cache")
_bp_route_list = []


def register_routes(routes_instance):
    _bp_route_list.clear()

    @routes_instance.post("/booru/cache/reset_timer")
    @route_error_handler
    async def reset_all_cache_timer(request):
        try:
            from ..src.booru_prompter.cache_manager import cache_manager
            from datetime import timedelta

            data = await request.json()
            time = timedelta(days=data["value"])
            duration: float = time.total_seconds()
            errors = 0

            for key in cache_manager.cache.iterkeys():
                try:
                    cache_manager.cache.touch(key, duration, True)
                except TimeoutError:
                    errors += 1

            if errors > 0:
                # There were invalid settings, so this is an error
                return error_response(
                    f"Failed to update {errors} cache entries", status=400
                )
            return success_response(
                data={"updated": [], "errors": []}, message="Cache entries updated"
            )
        except Exception as e:
            logger.error("Cache update error: %s", str(e))
            return error_response(f"Failed to cache: {str(e)}", status=500)

    _bp_route_list.extend(
        [
            {
                "method": "POST",
                "path": "/booru/cache/reset_timer",
                "description": "Update cache timers",
            }
        ]
    )

    return len(_bp_route_list)


def get_route_list():
    return _bp_route_list.copy()
