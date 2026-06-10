document.addEventListener(
    "DOMContentLoaded",
    () => {
        bindLogsControls();
        loadLogs();
    }
);

function bindLogsControls() {
    const refresh = document.getElementById("logs-refresh");

    const controls = [
        "logs-level",
        "logs-limit"
    ];

    const textControls = [
        "logs-search",
        "logs-module",
        "logs-function"
    ];

    if (refresh) {
        refresh.addEventListener(
            "click",
            loadLogs
        );
    }

    controls.forEach(
        id => {
            const element = document.getElementById(id);

            if (element) {
                element.addEventListener(
                    "change",
                    loadLogs
                );
            }
        }
    );

    textControls.forEach(
        id => {
            const element = document.getElementById(id);

            if (element) {
                element.addEventListener(
                    "keydown",
                    event => {
                        if (event.key === "Enter") {
                            loadLogs();
                        }
                    }
                );
            }
        }
    );
}

async function loadLogs() {
    const level = document.getElementById("logs-level")?.value ?? "";
    const search = document.getElementById("logs-search")?.value ?? "";
    const module = document.getElementById("logs-module")?.value ?? "";
    const functionName = document.getElementById("logs-function")?.value ?? "";
    const limit = document.getElementById("logs-limit")?.value ?? "200";

    const params = new URLSearchParams();

    params.set(
        "limit",
        limit
    );

    if (level) {
        params.set(
            "level",
            level
        );
    }

    if (search) {
        params.set(
            "search",
            search
        );
    }

    if (module) {
        params.set(
            "module",
            module
        );
    }

    if (functionName) {
        params.set(
            "function",
            functionName
        );
    }

    setText(
        "logs-status",
        "Loading..."
    );

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
                "logger",
                "module",
                "function",
                "message",
                "exception"
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