document.addEventListener(
    "DOMContentLoaded",
    () => {
        bindEventsControls();
        loadEvents();
    }
);

function bindEventsControls() {
    const refresh = document.getElementById("events-refresh");
    const type = document.getElementById("events-type");
    const search = document.getElementById("events-search");
    const limit = document.getElementById("events-limit");

    if (refresh) {
        refresh.addEventListener(
            "click",
            loadEvents
        );
    }

    if (limit) {
        limit.addEventListener(
            "change",
            loadEvents
        );
    }

    if (type) {
        type.addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    loadEvents();
                }
            }
        );
    }

    if (search) {
        search.addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    loadEvents();
                }
            }
        );
    }
}

async function loadEvents() {
    const eventType = document.getElementById("events-type")?.value ?? "";
    const search = document.getElementById("events-search")?.value ?? "";
    const limit = document.getElementById("events-limit")?.value ?? "50";

    const params = new URLSearchParams();

    params.set("limit", limit);

    if (eventType) {
        params.set("event_type", eventType);
    }

    if (search) {
        params.set("search", search);
    }

    setText("events-status", "Loading...");

    try {
        const response = await fetch(
            `/api/events?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const rows = await response.json();

        renderTable(
            "events-output",
            [
                "created_at",
                "type",
                "payload"
            ],
            rows
        );

        setText(
            "events-status",
            `${rows.length} record(s)`
        );

    } catch (error) {
        setText(
            "events-status",
            "Failed"
        );

        const output = document.getElementById("events-output");

        if (output) {
            output.innerHTML = `
                <div class="empty-state error-state">
                    Failed to load events: ${escapeHtml(error.message)}
                </div>
            `;
        }
    }
}