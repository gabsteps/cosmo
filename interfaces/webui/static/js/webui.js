let lastHeartbeatCount = null;
let currentInspector = "status";

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}

function formatBoolean(value) {
    return value ? "true" : "false";
}

async function fetchJson(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
}

function updateHeartbeat(status) {
    const heart = document.getElementById("heartbeat-heart");
    const main = document.getElementById("heartbeat-main");
    const sub = document.getElementById("heartbeat-sub");

    if (!heart || !main || !sub) {
        return;
    }

    const alive = !!status.heartbeat_alive;
    const currentCount = status.heartbeat_count ?? 0;

    if (alive) {
        heart.classList.remove("dead");
        heart.classList.add("alive");

        main.textContent = "Heartbeat Status";
        sub.textContent = `Last beat registered. Count: ${currentCount}`;

        setText("heartbeat-status", "alive");

        if (
            lastHeartbeatCount !== null
            && currentCount > lastHeartbeatCount
        ) {
            heart.classList.remove("beat");

            void heart.offsetWidth;

            heart.classList.add("beat");

            window.setTimeout(
                () => {
                    heart.classList.remove("beat");
                },
                650
            );
        }

        lastHeartbeatCount = currentCount;
        return;
    }

    heart.classList.remove("alive");
    heart.classList.remove("beat");
    heart.classList.add("dead");

    main.textContent = "Heartbeat stalled or unavailable";
    sub.textContent = "No recent heartbeat detected";

    setText("heartbeat-status", "stale");

    lastHeartbeatCount = currentCount;
}

function updateRuntimeCards(status) {
    const modeElement = document.getElementById("runtime-mode");
    const mode = status.mode ?? "-";

    if (modeElement) {
        modeElement.textContent = mode;
        modeElement.className = "runtime-mode";
        modeElement.classList.add(`mode-${mode}`);
    }

    setText("previous-mode", status.previous_mode ?? "-");
    setText("uptime-human", status.uptime_human ?? "00:00:00");
    setText("tts-active", formatBoolean(status.tts_active));
    setText("llm-active", formatBoolean(status.llm_active));
    setText("capture-active", formatBoolean(status.capture_active));

    setText("queue-size", status.queue_size ?? 0);
    setText("events-received", status.events_received ?? 0);
    setText("events-completed", status.events_completed ?? 0);
    setText("events-failed", status.events_failed ?? 0);
    setText("listener-timeouts", status.listener_timeouts ?? 0);
    setText("listener-errors", status.listener_errors ?? 0);
    setText("heartbeat-count", status.heartbeat_count ?? 0);

    const system = status.system ?? {};

    setText("cpu-percent", `${system.cpu_percent ?? 0}%`);
    setText("memory-percent", `${system.memory_percent ?? 0}%`);
    setText("disk-percent", `${system.disk_percent ?? 0}%`);

    setText(
        "temperature",
        system.temperature_celsius === null ||
        system.temperature_celsius === undefined
            ? "unavailable"
            : `${system.temperature_celsius} °C`
    );

    setText("network-download", system.network_download_human ?? "0 B/s");
    setText("network-upload", system.network_upload_human ?? "0 B/s");

    const process = system.process ?? {};

    setText("process-pid", process.pid ?? "-");
    setText("process-status", process.status ?? "-");
    setText("process-cpu", `${process.cpu_percent ?? 0}%`);
    setText("process-memory-rss", process.memory_rss_human ?? "0 MB");
    setText("process-memory-percent", `${process.memory_percent ?? 0}%`);
    setText("process-threads", process.threads ?? 0);
    setText("process-open-files", process.open_files ?? 0);

    const database = status.database ?? {};

    setText("database-size", database.database_size_human ?? "0 B");
    setText("database-users", database.users_count ?? 0);
    setText("database-memories", database.memories_count ?? 0);
    setText("database-conversations", database.conversations_count ?? 0);
    setText("database-events", database.events_count ?? 0);
    setText("database-logs", database.logs_count ?? 0);
    setText("database-last-event", database.last_event_type ?? "-");
    
    const vision = status.vision ?? {};

    setText("vision-enabled", formatBoolean(vision.enabled));
    setText("vision-camera-active", formatBoolean(vision.camera_active));
    setText("vision-camera-available", formatBoolean(vision.camera_available));
    setText("vision-camera-index", vision.camera_index ?? "-");

    setText(
        "vision-resolution",
        (
            vision.width && vision.height
                ? `${vision.width}x${vision.height}`
                : "-"
        )
    );

    setText("vision-grayscale", formatBoolean(vision.grayscale));

    setText(
        "vision-brightness",
        (
            vision.last_brightness === null ||
            vision.last_brightness === undefined
                ? "-"
                : Number(vision.last_brightness).toFixed(2)
        )
    );

    const visionQualityElement = document.getElementById("vision-quality");

    if (visionQualityElement) {
        const quality = vision.image_quality ?? "unknown";

        visionQualityElement.textContent = quality;
        visionQualityElement.className = "stat-value";
        visionQualityElement.classList.add(`vision-quality-${quality}`);
    }

    setText(
        "vision-last-frame",
        vision.last_frame_at ?? "-"
    );

    const visionErrorElement = document.getElementById("vision-error");

    if (visionErrorElement) {
        if (vision.last_error) {
            visionErrorElement.textContent = vision.last_error;
            visionErrorElement.classList.add("has-error");
        } else {
            visionErrorElement.textContent = "No vision errors.";
            visionErrorElement.classList.remove("has-error");
        }
    }

    updateHeartbeat(status);
    updateAlerts(status);
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

    if (process.error) {
        alerts.push({
            level: "warning",
            text: `Process monitor error: ${process.error}`
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

    if (!alerts.length) {
        card.classList.add("alerts-hidden");
        count.textContent = "0";

        container.innerHTML = `
            <div class="alert-item alert-ok">
                No alerts detected.
            </div>
        `;

        return;
    }

    card.classList.remove("alerts-hidden");
    count.textContent = alerts.length;

    container.innerHTML = alerts.map(
        alert => `
            <div class="alert-item alert-${alert.level}">
                ${escapeHtml(alert.text)}
            </div>
        `
    ).join("");
}

function startStatusStream() {
    const source = new EventSource("/api/status/stream");

    source.onmessage = function(event) {
        const status = JSON.parse(event.data);
        updateRuntimeCards(status);
    };

    source.onerror = function(error) {
        console.error("Status stream error:", error);

        setText("heartbeat-status", "stream error");

        const heart = document.getElementById("heartbeat-heart");

        if (heart) {
            heart.classList.remove("alive");
            heart.classList.remove("beat");
            heart.classList.add("dead");
        }
    };
}

async function loadStatusOutput() {
    try {
        const status = await fetchJson("/api/status/compact");

        updateRuntimeCards(status);

        document.getElementById("output").textContent =
            JSON.stringify(status, null, 2);

    } catch (error) {
        document.getElementById("output").textContent =
            `Failed to load status: ${error.message}`;
    }
}

function selectInspector(type) {
    currentInspector = type;

    renderInspectorToolbar(type);
    loadCurrentInspector();
}

function renderInspectorToolbar(type) {
    const toolbar = document.getElementById("inspector-toolbar");

    if (!toolbar) {
        return;
    }

    if (type === "status") {
        toolbar.innerHTML = `
            <span class="footer-note">
                No filters available for status.
            </span>
        `;
        return;
    }

    if (type === "logs") {
        toolbar.innerHTML = `
            <select id="filter-level">
                <option value="">All levels</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
            </select>

            <input id="filter-search" type="text" placeholder="Search logs..." />

            <select id="filter-limit">
                <option value="50">50 logs</option>
                <option value="100">100 logs</option>
                <option value="200" selected>200 logs</option>
                <option value="500">500 logs</option>
            </select>
        `;
    }

    if (type === "events") {
        toolbar.innerHTML = `
            <input id="filter-type" type="text" placeholder="Event type..." />
            <input id="filter-search" type="text" placeholder="Search events..." />

            <select id="filter-limit">
                <option value="50">50 events</option>
                <option value="100">100 events</option>
                <option value="200" selected>200 events</option>
                <option value="500">500 events</option>
            </select>
        `;
    }

    if (type === "memories") {
        toolbar.innerHTML = `
            <input id="filter-category" type="text" placeholder="Category..." />
            <input id="filter-search" type="text" placeholder="Search memories..." />

            <select id="filter-limit">
                <option value="20">20 memories</option>
                <option value="50" selected>50 memories</option>
                <option value="100">100 memories</option>
            </select>
        `;
    }

    if (type === "conversations") {
        toolbar.innerHTML = `
            <select id="filter-role">
                <option value="">All roles</option>
                <option value="user">user</option>
                <option value="assistant">assistant</option>
            </select>

            <input id="filter-search" type="text" placeholder="Search conversations..." />

            <select id="filter-limit">
                <option value="20">20 messages</option>
                <option value="50" selected>50 messages</option>
                <option value="100">100 messages</option>
            </select>
        `;
    }

    toolbar
        .querySelectorAll("input, select")
        .forEach(
            element => {
                element.addEventListener(
                    "input",
                    loadCurrentInspector
                );

                element.addEventListener(
                    "change",
                    loadCurrentInspector
                );
            }
        );
}

async function loadCurrentInspector() {
    if (currentInspector === "status") {
        return loadStatusOutput();
    }

    const params = new URLSearchParams();

    const limit = document.getElementById("filter-limit")?.value;
    const search = document.getElementById("filter-search")?.value;
    const level = document.getElementById("filter-level")?.value;
    const eventType = document.getElementById("filter-type")?.value;
    const category = document.getElementById("filter-category")?.value;
    const role = document.getElementById("filter-role")?.value;

    if (limit) {
        params.set("limit", limit);
    }

    if (search) {
        params.set("search", search);
    }

    if (level) {
        params.set("level", level);
    }

    if (eventType) {
        params.set("event_type", eventType);
    }

    if (category) {
        params.set("category", category);
    }

    if (role) {
        params.set("role", role);
    }

    const url = `/api/${currentInspector}?${params.toString()}`;

    try {
        const data = await fetchJson(url);
        renderInspectorTable(currentInspector, data);

    } catch (error) {
        document.getElementById("output").textContent =
            `Failed to load ${url}: ${error.message}`;
    }
}

function renderInspectorTable(type, data) {
    if (!Array.isArray(data)) {
        document.getElementById("output").textContent =
            JSON.stringify(data, null, 2);
        return;
    }

    if (type === "logs") {
        return renderTable(
            ["created_at", "level", "module", "function", "message"],
            data
        );
    }

    if (type === "events") {
        return renderTable(
            ["created_at", "type", "payload"],
            data
        );
    }

    if (type === "memories") {
        return renderTable(
            ["created_at", "category", "importance", "content"],
            data
        );
    }

    if (type === "conversations") {
        return renderTable(
            ["timestamp", "role", "message"],
            data
        );
    }

    document.getElementById("output").textContent =
        JSON.stringify(data, null, 2);
}

function renderTable(columns, rows) {
    const tableRows = rows.map(
        row => `
            <tr>
                ${columns.map(
                    column => `
                        <td class="${isWideColumn(column) ? "cell-wide" : ""}">
                            ${escapeHtml(formatCell(row[column], column))}
                        </td>
                    `
                ).join("")}
            </tr>
        `
    ).join("");

    document.getElementById("output").innerHTML = `
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        ${columns.map(
                            column => `<th>${escapeHtml(column)}</th>`
                        ).join("")}
                    </tr>
                </thead>
                <tbody>
                    ${
                        tableRows
                        || `<tr><td colspan="${columns.length}">No records found.</td></tr>`
                    }
                </tbody>
            </table>
        </div>
    `;
}

function isWideColumn(column) {
    return [
        "message",
        "content",
        "payload"
    ].includes(column);
}

function formatCell(value, column = null) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    if (
        column === "created_at" ||
        column === "timestamp"
    ) {
        return formatTimestamp(value);
    }

    if (typeof value === "object") {
        return JSON.stringify(
            value,
            null,
            2
        );
    }

    return value;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

document.addEventListener(
    "DOMContentLoaded",
    () => {
        document
            .querySelectorAll("[data-inspector]")
            .forEach(
                button => {
                    button.addEventListener(
                        "click",
                        () => {
                            selectInspector(
                                button.dataset.inspector
                            );
                        }
                    );
                }
            );

        renderInspectorToolbar("status");
        loadStatusOutput();
        startStatusStream();
    }
);

function formatTimestamp(value) {
    if (!value) {
        return "";
    }

    const normalized = String(value)
        .replace(" ", "T");

    const date = new Date(`${normalized}Z`);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString(
        "pt-BR",
        {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }
    );
}

function updateVisionPreview(vision) {
    const preview = document.getElementById("vision-preview");
    const empty = document.getElementById("vision-preview-empty");

    if (!preview || !empty) {
        return;
    }

    if (!vision || !vision.has_frame || !vision.last_snapshot_path) {
        preview.classList.remove("visible");
        empty.classList.remove("hidden");
        return;
    }

    const cacheBust = encodeURIComponent(
        vision.last_frame_at ?? Date.now()
    );

    preview.src = `/api/vision/snapshot?t=${cacheBust}`;
    preview.classList.add("visible");
    empty.classList.add("hidden");
}