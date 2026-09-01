import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "BooruPrompter.Core",
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
            tooltip: "Choose which booru site to use."
        },
        {
            id: "BooruPrompter.Boorus.username",
            name: "Booru Username",
            type: "text",
            tooltip: "Your username for the selected booru"
        },
        {
            id: "BooruPrompter.Boorus.api_token",
            name: "API Token",
            attrs: {
                type: "password",
                autocomplete: "off"
            },
            tooltip: "Your API token for the selected booru"
        },
        {
            id: "BooruPrompter.CacheSettings.purgeOnStarUp",
            name: "Purge on Startup",
            type: "boolean",
            defaultValue: false,
            tooltip: "No rolling deletion. Instead to purge on startup."
        },
        {
            id: "BooruPrompter.CacheSettings.oldestDeletion",
            name: "Oldest to Keep (days)",
            type: "number",
            defaultValue: 7,
            tooltip: "How long to keep in cache to be considered stale"
        },
        {
            id: "BooruPrompter.CacheSettings.lastUsedTime",
            name: "Ignore if Last Used Within (days)",
            type: "number",
            defaultValue: 2,
            tooltip: "Keep in cache if last used within a specified time"
        }
    ]
})
