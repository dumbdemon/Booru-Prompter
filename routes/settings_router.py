import json
from ..src.booru_prompter.logger import get_logger
from aiohttp import web
from .base_router import route_error_handler, success_response, error_response

logging = get_logger("routes.settings")
_bp_route__list = []


def register_routes(routes_instance):
    global _bp_route__list
    _bp_route__list.clear()

    @routes_instance.get("/booru/settings")
    @route_error_handler
    async def get_boooru_settings(request):
        try:
            from ..src.booru_prompter.managers import get_settings

            settings = get_settings()
            settings_info = settings.list_all_settings()

            json.dumps(settings_info)  # This will raise an exception if not serializable

            return web.json_response({"success": True, "settings": settings_info})

        except (TypeError, ValueError) as e:
            logging.error(f"Settings JSON serialization error: {str(e)}")
            return error_response(f"JSON serialization error: {str(e)}", status=500)
        except Exception as e:
            logging.error(f"Settings retrieval error: {str(e)}")
            return error_response(f"Failed to retrieve settings: {str(e)}", status=500)

    @routes_instance.post("/booru/settings")
    @route_error_handler
    async def update_boooru_settings(request):
        try:
            from ..src.booru_prompter.managers import get_settings, is_known_setting

            data = await request.json()
            settings = get_settings()

            updated_settings = []
            errors = []

            for key, value in data.items():
                if is_known_setting(key):
                    try:
                        if settings.set(key, value):
                            updated_settings.append(key)
                    except Exception as e:
                        errors.append(f"Failed to set '{key}': {str(e)}")
                else:
                    errors.append(f"Unknown setting: '{key}'")

            if updated_settings:
                if settings.save():
                    return success_response(
                        data={"updated": updated_settings, "errors": errors}, message=f"Updated {len(updated_settings)} setting(s)"
                    )
                else:
                    return error_response("Failed to save settings", status=500, updated=updated_settings, errors=errors)
            else:
                # No settings needed updating - this is actually a success case
                # All settings were either already at correct values or invalid
                if errors:
                    # There were invalid settings, so this is an error
                    return error_response("No valid settings to update", status=400, errors=errors)
                else:
                    # All settings were already at correct values - this is success
                    return success_response(data={"updated": [], "errors": []}, message="All settings already at requested values")

        except Exception as e:
            logging.error(f"Settings update error: {str(e)}")
            return error_response(f"Failed to update settings: {str(e)}", status=500)

    @routes_instance.post("/booru/settings/reset")
    @route_error_handler
    async def reset_boooru_settings(request):
        try:
            from ..src.booru_prompter.managers import get_settings

            settings = get_settings()
            settings.reset_all()

            return success_response(message="All settings reset to defaults")

        except Exception as e:
            logging.error(f"Settings reset error: {str(e)}")
            return error_response(f"Failed to reset settings: {str(e)}", status=500)

    # Track registered routes
    _bp_route__list.extend(
        [
            {"method": "GET", "path": "/booru/settings", "description": "Get all settings"},
            {"method": "POST", "path": "/booru/settings", "description": "Update settings"},
            {"method": "POST", "path": "/booru/settings/reset", "description": "Reset settings to defaults"},
        ]
    )

    return len(_bp_route__list)


def get_route_list():
    return _bp_route__list.copy()
