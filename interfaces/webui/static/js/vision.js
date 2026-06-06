let lastVisionSnapshotKey = null;

document.addEventListener(
    "DOMContentLoaded",
    () => {
        connectVisionStream();
    }
);

function connectVisionStream() {
    const source = new EventSource("/api/status/stream");

    source.onopen = () => {
        setText("topbar-status", "Connected");
    };

    source.onerror = () => {
        setText("topbar-status", "Disconnected");
    };

    source.onmessage = event => {
        const status = JSON.parse(event.data);

        updateVisionPage(status.vision ?? {});
    };
}

function updateVisionPage(vision) {
    setText("vision-enabled", formatBoolean(vision.enabled));
    setText("vision-camera-active", formatBoolean(vision.camera_active));
    setText("vision-camera-available", formatBoolean(vision.camera_available));
    setText("vision-camera-index", vision.camera_index ?? "-");

    setText(
        "vision-resolution",
        vision.width && vision.height
            ? `${vision.width}x${vision.height}`
            : "-"
    );

    setText("vision-grayscale", formatBoolean(vision.grayscale));

    setText(
        "vision-started-at",
        formatTimestamp(vision.started_at)
    );

    setText(
        "vision-brightness",
        vision.last_brightness === null ||
        vision.last_brightness === undefined
            ? "-"
            : Number(vision.last_brightness).toFixed(2)
    );

    updateVisionQuality(
        vision.image_quality ?? "unknown"
    );

    setText("vision-has-frame", formatBoolean(vision.has_frame));
    setText("vision-last-frame", formatTimestamp(vision.last_frame_at));
    setText("vision-snapshot-path", vision.last_snapshot_path ?? "-");

    updateVisionError(vision);
    updateVisionPreview(vision);
}

function updateVisionQuality(quality) {
    const element = document.getElementById("vision-quality");

    if (!element) {
        return;
    }

    element.textContent = quality;
    element.className = "stat-value";
    element.classList.add(`vision-quality-${quality}`);
}

function updateVisionError(vision) {
    const element = document.getElementById("vision-error");

    if (!element) {
        return;
    }

    if (vision.last_error) {
        element.textContent = vision.last_error;
        element.classList.add("has-error");
        return;
    }

    element.textContent = "No vision errors.";
    element.classList.remove("has-error");
}

function updateVisionPreview(vision) {
    const preview = document.getElementById("vision-large-preview");
    const empty = document.getElementById("vision-large-empty");

    if (!preview || !empty) {
        return;
    }

    const snapshotKey = [
        vision.last_snapshot_path ?? "configured_snapshot",
        vision.last_frame_at ?? "static"
    ].join("|");

    if (snapshotKey === lastVisionSnapshotKey) {
        return;
    }

    lastVisionSnapshotKey = snapshotKey;

    const cacheBust = encodeURIComponent(
        vision.last_frame_at ?? "static"
    );

    preview.onload = () => {
        preview.classList.add("visible");
        empty.classList.add("hidden");
    };

    preview.onerror = () => {
        preview.classList.remove("visible");
        empty.classList.remove("hidden");
    };

    preview.src = `/api/vision/snapshot?t=${cacheBust}`;
}