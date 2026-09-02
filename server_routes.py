import logging


try:
    from server import PromptServer
    from aiohttp import web
    from .src.booru_prompter.managers import get_settings, is_known_setting

    try:
        from .routes import register_routes

        _modular_routes_available = True
    except ImportError as e:
        logging.warning(f"BooruPrompter: Modular routes not available ({e}), using legacy routes only")
        _modular_routes_available = False

    if hasattr(PromptServer, "instance") and PromptServer.instance is not None:
        routes = PromptServer.instance.routes

        if _modular_routes_available:
            try:
                route_count = register_routes(routes)
                if route_count > 0:
                    logging.info(f"BooruPrompter: {route_count} module loaded")
                else:
                    logging.warning("Routes not loaded.")
            except Exception as modular_error:
                logging.error(f"BooruPrompter: Error with modular routes ({modular_error}), continuing with legacy routes")

        @routes.get("/booru/settings")
        async def get_boooru_settings(request):
            """
            Returns all SageUtils settings with their current values and schema information.
            """
            try:
                import json

                settings = get_settings()
                settings_info = settings.list_all_settings()

                # Double-check that the result is JSON serializable
                json.dumps(settings_info)  # This will raise an exception if not serializable

                return web.json_response({"success": True, "settings": settings_info})
            except (TypeError, ValueError) as e:
                return web.json_response({"success": False, "error": f"JSON serialization error: {str(e)}"}, status=500)
            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                logging.error(f"SageUtils settings error: {error_details}")
                return web.json_response(
                    {"success": False, "error": f"Failed to retrieve settings: {str(e)}", "details": error_details}, status=500
                )

        @routes.post("/booru/settings")
        async def update_boooru_settings(request):
            """
            Updates SageUtils settings. Expects JSON body with setting key-value pairs.
            """
            try:
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

                # Save if any settings were updated
                if updated_settings:
                    if settings.save():
                        return web.json_response(
                            {
                                "success": True,
                                "updated": updated_settings,
                                "errors": errors,
                                "message": f"Updated {len(updated_settings)} setting(s)",
                            }
                        )
                    return web.json_response(
                        {"success": False, "error": "Failed to save settings", "updated": updated_settings, "errors": errors},
                        status=500,
                    )
                else:
                    # No settings needed updating - this could be success or error
                    if errors:
                        # There were invalid settings, so this is an error
                        return web.json_response({"success": False, "error": "No valid settings to update", "errors": errors}, status=400)
                    # All settings were already at correct values - this is success
                    return web.json_response(
                        {"success": True, "updated": [], "errors": [], "message": "All settings already at requested values"}
                    )

            except Exception as e:
                return web.json_response({"success": False, "error": f"Failed to update settings: {str(e)}"}, status=500)

        @routes.post("/booru/settings/reset")
        async def reset_boooru_settings(request):
            """
            Resets all SageUtils settings to their default values.
            """
            try:
                settings = get_settings()
                settings.reset_to_defaults()
                return web.json_response({"success": True, "message": "All settings reset to defaults"})
            except Exception as e:
                return web.json_response({"success": False, "error": f"Failed to reset settings: {str(e)}"}, status=500)
    else:
        logging.warning("Warning: PromptServer instance not available, skipping route registration")

except ImportError as e:
    logging.warning(f"Warning: Could not import required modules for SageUtils routes: {e}")
except Exception as e:
    logging.error(f"Warning: Error setting up SageUtils routes: {e}")
