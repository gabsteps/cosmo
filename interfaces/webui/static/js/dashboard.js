let lastHeartbeatCount = null;

document.addEventListener(
    "DOMContentLoaded",
    () => {
        connectStatusStream();
    }
);

function connectStatusStream() {
    const source = new EventSource("/api/status/stream");

    source.onopen = () => {
        setText("topbar-status", "Connected");
    };

    source.onerror = () => {
        setText("topbar-status", "Disconnected");
    };

    source.onmessage = event => {
        const status = JSON.parse(event.data);

        updateDashboard(status);
    };
}

function updateDashboard(status) {
    updateRuntime(status);
    updateEventBus(status);
    updateSystem(status);
    updateProcess(status);
    updateVision(status);
    updateDatabase(status);
    updateAlerts(status);
}

function updateRuntime(status) {
    const mode = status.mode ?? "unknown";
    const runtimeMode = document.getElementById("runtime-mode");

    if (runtimeMode) {
        runtimeMode.textContent = mode;
        runtimeMode.className = `runtime-mode mode-${mode}`;
    }

    setText("previous-mode", status.previous_mode ?? "-");
    setText("system-uptime", status.uptime_human ?? "00:00:00");
    setText("tts-active", formatBoolean(status.tts_active));
    setText("llm-active", formatBoolean(status.llm_active));
    setText("capture-active", formatBoolean(status.capture_active));

    updateHeartbeat(status);
}

function updateHeartbeat(status) {
    const heart = document.getElementById("heartbeat-heart");
    const sub = document.getElementById("heartbeat-sub");

    if (!heart || !sub) {
        return;
    }

    const alive = Boolean(status.heartbeat_alive);
    const count = status.heartbeat_count ?? 0;

    heart.classList.toggle("alive", alive);
    heart.classList.toggle("dead", !alive);

    sub.textContent = alive
        ? `Last beat registered. Count: ${count}`
        : "Heartbeat unavailable.";

    if (
        lastHeartbeatCount !== null &&
        count !== lastHeartbeatCount
    ) {
        heart.classList.remove("beat");

        void heart.offsetWidth;

        heart.classList.add("beat");
    }

    lastHeartbeatCount = count;
}

function updateEventBus(status) {
    setText("queue-size", status.queue_size ?? 0);
    setText("events-received", status.events_received ?? 0);
    setText("events-completed", status.events_completed ?? 0);
    setText("events-failed", status.events_failed ?? 0);
    setText("listener-timeouts", status.listener_timeouts ?? 0);
    setText("listener-errors", status.listener_errors ?? 0);
    setText("heartbeat-count", status.heartbeat_count ?? 0);
    setText("heartbeat-alive", status.heartbeat_alive ? "alive" : "stale");
}

function updateSystem(status) {
    const system = status.system ?? {};

    setText("system-cpu", `${system.cpu_percent ?? 0}%`);
    setText("system-ram", `${system.memory_percent ?? 0}%`);
    setText("system-disk", `${system.disk_percent ?? 0}%`);

    setText(
        "system-temperature",
        system.temperature_celsius === null ||
        system.temperature_celsius === undefined
            ? "-"
            : `${system.temperature_celsius} °C`
    );

    setText("system-download", system.network_download_human ?? "0 B/s");
    setText("system-upload", system.network_upload_human ?? "0 B/s");
}

function updateProcess(status) {
    const process = status.system?.process ?? {};

    setText("process-pid", process.pid ?? "-");
    setText("process-status", process.status ?? "-");
    setText("process-cpu", `${process.cpu_percent ?? 0}%`);
    setText("process-memory-rss", process.memory_rss_human ?? "0 MB");
    setText("process-memory-percent", `${process.memory_percent ?? 0}%`);
    setText("process-threads", process.threads ?? 0);
    setText("process-open-files", process.open_files ?? 0);
}

function updateVision(status) {
    const vision = status.vision ?? {};

    const cameraStatus = vision.camera_active
        ? (
            vision.camera_available
                ? "active"
                : "unavailable"
        )
        : "inactive";

    setText("vision-camera-status", cameraStatus);

    setText(
        "vision-resolution",
        vision.width && vision.height
            ? `${vision.width}x${vision.height}`
            : "-"
    );

    setText(
        "vision-brightness",
        vision.last_brightness === null ||
        vision.last_brightness === undefined
            ? "-"
            : Number(vision.last_brightness).toFixed(2)
    );

    const quality = vision.image_quality ?? "unknown";
    const qualityElement = document.getElementById("vision-quality");

    if (qualityElement) {
        qualityElement.textContent = quality;
        qualityElement.className = "mini-value";
        qualityElement.classList.add(`vision-quality-${quality}`);
    }

    const errorElement = document.getElementById("vision-error");

    if (errorElement) {
        if (vision.last_error) {
            errorElement.textContent = vision.last_error;
            errorElement.classList.add("has-error");
        } else {
            errorElement.textContent = "No vision errors.";
            errorElement.classList.remove("has-error");
        }
    }
}

function updateDatabase(status) {
    const database = status.database ?? {};

    setText("database-size", database.database_size_human ?? "0 B");
    setText("database-users", database.users_count ?? 0);
    setText("database-memories", database.memories_count ?? 0);
    setText("database-conversations", database.conversations_count ?? 0);
    setText("database-events", database.events_count ?? 0);
    setText("database-logs", database.logs_count ?? 0);
    setText("database-last-event", database.last_event_type ?? "-");
}

function updateAlerts(status) {
    const alerts = [];
    const system = status.system ?? {};
    const process = system.process ?? {};
    const vision = status.vision ?? {};

    if (!status.heartbeat_alive) {
        alerts.push({
            level: "error",
            text: "Heartbeat stalled or unavailable."
        });
    }

    if ((status.events_failed ?? 0) > 0) {
        alerts.push({
            level: "warning",
            text: `Event bus has ${status.events_failed} failed event(s).`
        });
    }

    if ((status.listener_errors ?? 0) > 0) {
        alerts.push({
            level: "warning",
            text: `Detected ${status.listener_errors} listener error(s).`
        });
    }

    if ((status.listener_timeouts ?? 0) > 0) {
        alerts.push({
            level: "warning",
            text: `Detected ${status.listener_timeouts} listener timeout(s).`
        });
    }

    if (status.last_error) {
        alerts.push({
            level: "error",
            text: `Runtime error: ${status.last_error}`
        });
    }

    if ((system.memory_percent ?? 0) >= 85) {
        alerts.push({
            level: "warning",
            text: `High RAM usage: ${system.memory_percent}%.`
        });
    }

    if ((system.disk_percent ?? 0) >= 90) {
        alerts.push({
            level: "warning",
            text: `High disk usage: ${system.disk_percent}%.`
        });
    }

    if (
        system.temperature_celsius !== null &&
        system.temperature_celsius !== undefined &&
        system.temperature_celsius >= 80
    ) {
        alerts.push({
            level: "warning",
            text: `High temperature: ${system.temperature_celsius} °C.`
        });
    }

    if ((process.cpu_percent ?? 0) >= 40) {
        alerts.push({
            level: "warning",
            text: `High Cosmo CPU usage: ${process.cpu_percent}%.`
        });
    }

    if (
        vision.enabled &&
        vision.camera_active &&
        vision.image_quality === "dark"
    ) {
        alerts.push({
            level: "warning",
            text: "Vision image is too dark."
        });
    }

    if (
        vision.enabled &&
        vision.camera_active &&
        vision.image_quality === "low_light"
    ) {
        alerts.push({
            level: "warning",
            text: "Vision image has low light."
        });
    }

    if (vision.last_error) {
        alerts.push({
            level: "warning",
            text: `Vision error: ${vision.last_error}`
        });
    }

    const card = document.getElementById("alerts-card");
    const container = document.getElementById("alerts-list");
    const count = document.getElementById("alerts-count");

    if (!card || !container || !count) {
        return;
    }

    count.textContent = alerts.length;

    if (!alerts.length) {
        container.innerHTML = `
            <div class="alert-item alert-ok">
                No alerts detected.
            </div>
        `;

        return;
    }

    container.innerHTML = alerts.map(
        alert => `
            <div class="alert-item alert-${alert.level}">
                ${escapeHtml(alert.text)}
            </div>
        `
    ).join("");
}