let statusEventSource = null;

document.addEventListener(
    "DOMContentLoaded",
    () => {
        bindStatusControls();
        connectStatusStream();
    }
);

function bindStatusControls() {
    const refresh = document.getElementById("status-refresh");
    const live = document.getElementById("status-live");

    if (refresh) {
        refresh.addEventListener(
            "click",
            loadStatusOnce
        );
    }

    if (live) {
        live.addEventListener(
            "change",
            () => {
                if (live.checked) {
                    connectStatusStream();
                } else {
                    disconnectStatusStream();
                    setText("status-state", "Live paused");
                }
            }
        );
    }
}

function connectStatusStream() {
    disconnectStatusStream();

    statusEventSource = new EventSource(
        "/api/status/stream"
    );

    statusEventSource.onopen = () => {
        setText("topbar-status", "Connected");
        setText("status-state", "Live");
    };

    statusEventSource.onerror = () => {
        setText("topbar-status", "Disconnected");
        setText("status-state", "Stream error");
    };

    statusEventSource.onmessage = event => {
        try {
            const snapshot = JSON.parse(
                event.data
            );

            renderStatus(
                snapshot
            );

        } catch (error) {
            setText(
                "status-state",
                `Parse error: ${error.message}`
            );
        }
    };
}

function disconnectStatusStream() {
    if (statusEventSource) {
        statusEventSource.close();
        statusEventSource = null;
    }
}

async function loadStatusOnce() {
    setText(
        "status-state",
        "Loading..."
    );

    try {
        const response = await fetch(
            "/api/status/compact"
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const snapshot = await response.json();

        renderStatus(
            snapshot
        );

        setText(
            "status-state",
            "Loaded"
        );

    } catch (error) {
        setText(
            "status-state",
            "Failed"
        );

        const output = document.getElementById(
            "status-output"
        );

        if (output) {
            output.textContent = `Failed to load status: ${error.message}`;
        }
    }
}

function renderStatus(snapshot) {
    const output = document.getElementById(
        "status-output"
    );

    if (!output) {
        return;
    }

    output.textContent = JSON.stringify(
        snapshot,
        null,
        2
    );
}