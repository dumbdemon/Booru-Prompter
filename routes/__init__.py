from ..src.booru_prompter.utils.logger import get_logger

logger = get_logger("routes")

_bp_routes_initialized = False
_bp_registered_routes = []


def register_routes(routes_instance):
    global _bp_routes_initialized, _bp_registered_routes  # skipcq:  PYL-W0603

    if _bp_routes_initialized:
        logger.warning("Routes already initialized, skipping re-registration")
        return len(_bp_registered_routes)

    try:
        from . import settings_router
        from . import cache_router

        route_groups = [("Settings", settings_router), ("Cache", cache_router)]

        route_count = 0

        for group_name, route_module in route_groups:
            try:
                if hasattr(route_module, "register_routes"):
                    group_count = route_module.register_routes(routes_instance)
                    route_count += group_count
                    logger.debug(
                        f"Registered {group_count} {group_name} routes successfully"
                    )
                    _bp_registered_routes.extend(
                        route_module.get_route_list()
                        if hasattr(route_module, "get_route_list")
                        else []
                    )
                else:
                    logger.warning(
                        f"Route module {group_name} missing register_routes function"
                    )
            except ImportError as e:
                logger.warning(f"Could not import {group_name} routes: {e}")
            except Exception as e:
                import traceback

                logger.error(f"Error registering {group_name} routes: {e}")
                logger.error(traceback.format_exc())

        _bp_routes_initialized = True
        logger.info(
            "BooruPrompter: Registered %s routes across %s modules",
            route_count,
            len(route_groups),
        )
        return route_count

    except Exception as e:
        logger.error(f"Failed to initialize BooruPrompter routes: {e}")
        return 0


def get_registered_routes():
    return _bp_registered_routes.copy()


def is_initialized():
    return _bp_routes_initialized
