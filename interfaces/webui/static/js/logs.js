document.addEventListener(
    "DOMContentLoaded",
    () => {
        bindLogsControls();
        loadLogs();
    }
);

function bindLogsControls() {
    const refresh = document.getElementById("logs-refresh");
    const level = document.getElementById("logs-level");
    const search = document.getElementById("logs-search");
    const limit = document.getElementById("logs-limit");

    if (refresh) {
        refresh.addEventListener(
            "click",
            loadLogs
        );
    }

    if (level) {
        level.addEventListener(
            "change",
            loadLogs
        );
    }

    if (limit) {
        limit.addEventListener(
            "change",
            loadLogs
        );
    }

    if (search) {
        search.addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    loadLogs();
                }
            }
        );
    }
}

async function loadLogs() {
    const level = document.getElementById("logs-level")?.value ?? "";
    const search = document.getElementById("logs-search")?.value ?? "";
    const limit = document.getElementById("logs-limit")?.value ?? "200";

    const params = new URLSearchParams();

    params.set("limit", limit);

    if (level) {
        params.set("level", level);
    }

    if (search) {
        params.set("search", search);
    }

    setText("logs-status", "Loading...");

    try {
        const response = await fetch(
            `/api/logs?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const rows = await response.json();

        renderTable(
            "logs-output",
            [
                "created_at",
                "level",
                "module",
                "function",
                "message"
            ],
            rows
        );

        setText(
            "logs-status",
            `${rows.length} record(s)`
        );

    } catch (error) {
        setText(
            "logs-status",
            "Failed"
        );

        const output = document.getElementById("logs-output");

        if (output) {
            output.innerHTML = `
                <div class="empty-state error-state">
                    Failed to load logs: ${escapeHtml(error.message)}
                </div>
            `;
        }
    }
}