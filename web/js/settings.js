import { app } from "../../../../scripts/app.js";
import { api } from "../../../../scripts/api.js";

async function loadBooruSettings() {
    try {
        const response = await api.fetchApi("/booru/settings");
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                return data.settings || data.data?.settings;
            } else {
                console.error("Server returned error:", data.error);
                if (data.details) {
                    console.error("Error details:", data.details); // skipcq: JS-0002
                }
            }
        } else {
            console.error("HTTP error:", response.status, response.statusText); // skipcq: JS-0002
        }
        throw new Error("Failed to load settings from server");
    } catch (error) {
        console.error("Error loading BooruPrompter settings:", error); // skipcq: JS-0002
        // Return fallback settings structure
        return {
            booru_site: { current_value: "https://danbooru.donmai.us/" },
            booru_username: { current_value: "" },
            booru_api_token: { current_value: "" },
            booru_user_id: { current_value: "0000000" },

            cache_purge_on_startup: { current_value: false },
            cache_use_rolling_delete: { current_value: true },
            cache_refresh_on_use: { current_value: true },
            cache_rolling_rate: { current_value: 7 }
        };
    }
}

async function saveBooruSetting(key, value) {
    try {
        const response = await api.fetchApi("/booru/settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ [key]: value })
        });

        const data = await response.json();
        if (data.success) {
            console.log(`Successfully saved setting ${key}: ${value}`); // skipcq: JS-0002
            if (data.errors && data.errors.length > 0) {
                console.warn("Warnings during setting save:", data.errors); // skipcq: JS-0002
            }
        } else {
            console.error(`Failed to save setting ${key}:`, data.error); // skipcq: JS-0002
        }
        return data.success;
    } catch (error) {
        console.error(`Error saving BooruPrompter setting ${key}:`, error); // skipcq: JS-0002
        return false;
    }
}

async function resetCacheEntries(time) {
    try {
        const response = await api.fetchApi("/booru/cache/reset_timer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ ["value"]: time })
        });
    } catch (error) {
        console.error("Unable to reset cache:", error); // skipcq: JS-0002
        return false;
    }
}

app.registerExtension({
    name: "BooruPrompter.Core",

    async setup() {
        console.log("Setting up BooruPrompter settings integration..."); // skipcq: JS-0002

        // Load current settings from server
        const serverSettings = await loadSageSettings();
        if (!serverSettings) {
            console.warn("Could not load BooruPrompter settings from server - settings will use defaults"); // skipcq: JS-0002
            return;
        }

        console.log("Loaded BooruPrompter settings from server:", serverSettings); // skipcq: JS-0002

        // Set current values for all settings from server
        // Map backend keys to the new frontend setting IDs
        const keyToIdMap = {
            "booru_site": "BooruPrompter.Boorus.select_booru",
            "booru_username": "BooruPrompter.Boorus.username",
            "booru_api_token": "BooruPrompter.Boorus.api_token",
            "booru_user_id": "BooruPrompter.Boorus.booruUserId",
            "cache_purge_on_startup": "BooruPrompter.CacheSettings.purgeOnStarUp",
            "cache_use_rolling_delete": "BooruPrompter.CacheSettings.useRollingDelete",
            "cache_refresh_on_use": "BooruPrompter.CacheSettings.refreshOnUse",
            "cache_rolling_rate": "BooruPrompter.CacheSettings.rollingRate"
        };

        for (const [key, settingInfo] of Object.entries(serverSettings)) {
            const settingId = keyToIdMap[key];
            if (settingId && settingInfo.current_value !== undefined) {
                try {
                    await app.extensionManager.setting.set(settingId, settingInfo.current_value);
                    console.log(`Set initial value for ${settingId}:`, settingInfo.current_value); // skipcq: JS-0002
                } catch (error) {
                    console.warn(`Could not set initial value for ${settingId}:`, error); // skipcq: JS-0002
                }
            }
        }

        console.log("BooruPrompter settings integration completed"); // skipcq: JS-0002
    },

    settings: [
        {
            id: "BooruPrompter.Boorus.select_booru",
            name: "Select Booru",
            type: "combo",
            defaultValue: "https://danbooru.donmai.us/",
            options: [
                { text: "Danbooru", value: "https://danbooru.donmai.us/" },
                { text: "E621", value: "https://e621.net/" }
            ],
            tooltip: "Choose which booru site to use.",
            onChange: async (newVal, oldVal) => {
                console.log(`Booru Site was changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("booru_site", newVal);
            }
        },
        {
            id: "BooruPrompter.Boorus.username",
            name: "Booru Username",
            type: "text",
            tooltip: "Your username for the selected booru",
            onChange: async (newVal, oldVal) => {
                console.log(`Booru Username changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("booru_username", newVal);
            }
        }, //booru_user_id
        {
            id: "BooruPrompter.Boorus.booruUserId",
            name: "Booru User ID",
            type: "text",
            tooltip: "Your user ID for the selected booru (you can get this from your profile)",
            onChange: async (newVal, oldVal) => {
                console.log(`Booru User ID changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("booru_user_id", newVal);
            }
        },
        {
            id: "BooruPrompter.Boorus.api_token",
            name: "API Token",
            defaultValue: "",
            attrs: {
                type: "password",
                autocomplete: "off"
            },
            tooltip: "Your API token for the selected booru",
            onChange: async (newVal) => {
                console.log("Booru API token changed"); // skipcq: JS-0002
                await saveBooruSetting("booru_api_token", newVal);
            }
        },
        {
            id: "BooruPrompter.CacheSettings.purgeOnStarUp",
            name: "Purge on Startup",
            type: "boolean",
            defaultValue: false,
            tooltip: "No rolling deletion. Instead to purge on startup.",
            onChange: async (newVal, oldVal) => {
                console.log(`Cache Purge on Startup was changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("cache_purge_on_startup", newVal);
            }
        },
        {
            id: "BooruPrompter.CacheSettings.useRollingDelete",
            name: "Use Rolling Delete",
            type: "boolean",
            defaultValue: true,
            tooltip: "Whether to enable rolling deletion. If you enable Purge on Start Up, this toggle means nothing.",
            onChange: async (newVal, oldVal) => {
                console.log(`Cache Use Rolling Delete was changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("cache_use_rolling_delete", newVal);
            }
        },
        {
            id: "BooruPrompter.CacheSettings.refreshOnUse",
            name: "Refresh Cache Entry Timer",
            type: "boolean",
            defaultValue: true,
            tooltip: "refresh cache entry if used",
            onChange: async (newVal, oldVal) => {
                console.log(`Cache Refresh on Use changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("cache_refresh_on_use", newVal);
            }
        },
        {
            id: "BooruPrompter.CacheSettings.rollingRate",
            name: "Rolling Deletion Rate",
            type: "number",
            defaultValue: 7,
            tooltip: "How long to keep a cache entry on creation/use",
            onChange: async (newVal, oldVal) => {
                console.log(`Cache Rolling Rate was changed from "${oldVal}" to "${newVal}"`); // skipcq: JS-0002
                await saveBooruSetting("cache_rolling_rate", newVal);
                await resetCacheEntries(newVal);
            }
        }
    ]
})
