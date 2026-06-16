let lastVisionSnapshotKey = null;

document.addEventListener(
    "DOMContentLoaded",
    () => {
        connectVisionStream();
    }
);

function connectVisionStream() {
    const source = new EventSource(
        "/api/status/stream"
    );

    source.onopen = () => {
        setText(
            "topbar-status",
            "Connected"
        );
    };

    source.onerror = () => {
        setText(
            "topbar-status",
            "Disconnected"
        );
    };

    source.onmessage = event => {
        const status = JSON.parse(
            event.data
        );

        updateVisionPage(
            status.vision ?? {}
        );
    };
}

function updateVisionPage(
    vision
) {
    const metrics = vision.image_metrics ?? {};

    setText(
        "vision-enabled",
        formatBoolean(
            vision.enabled
        )
    );

    setText(
        "vision-camera-active",
        formatBoolean(
            vision.camera_active
        )
    );

    setText(
        "vision-camera-available",
        formatBoolean(
            vision.camera_available
        )
    );

    setText(
        "vision-camera-index",
        vision.camera_index ?? "-"
    );

    setText(
        "vision-resolution",
        vision.width && vision.height
            ? `${vision.width}x${vision.height}`
            : "-"
    );

    setText(
        "vision-grayscale",
        formatBoolean(
            vision.grayscale
        )
    );

    setText(
        "vision-started-at",
        formatTimestamp(
            vision.started_at
        )
    );

    setText(
        "vision-auto-capture",
        formatBoolean(
            vision.auto_capture
        )
    );

    setText(
        "vision-capture-interval",
        vision.capture_interval
            ? `${vision.capture_interval}s`
            : "-"
    );

    setText(
        "vision-has-frame",
        formatBoolean(
            vision.has_frame
        )
    );

    setText(
        "vision-last-frame",
        formatTimestamp(
            vision.last_frame_at
        )
    );

    setText(
        "vision-snapshot-path",
        vision.last_snapshot_path ?? "-"
    );

    updateVisionMetrics(
        vision,
        metrics
    );

    updateVisionQuality(
        metrics.image_quality
        ?? vision.image_quality
        ?? "unknown"
    );

    updateVisionFaceReady(
        metrics.face_ready
    );

    updateVisionGuidance(
        metrics,
        vision
    );

    updateVisionError(
        vision
    );

    updateVisionPreviewStatus(
        vision
    );

    updateVisionPreview(
        vision
    );
}

function updateVisionMetrics(
    vision,
    metrics
) {
    setText(
        "vision-brightness",
        formatMetric(
            metrics.brightness_mean
            ?? vision.last_brightness
        )
    );

    setText(
        "vision-contrast",
        formatMetric(
            metrics.brightness_std
        )
    );

    setText(
        "vision-dark-ratio",
        formatPercentRatio(
            metrics.dark_ratio
        )
    );

    setText(
        "vision-bright-ratio",
        formatPercentRatio(
            metrics.bright_ratio
        )
    );

    setText(
        "vision-overexposed-ratio",
        formatPercentRatio(
            metrics.overexposed_ratio
        )
    );

    setText(
        "vision-blur-score",
        formatMetric(
            metrics.blur_score
        )
    );

    setText(
        "vision-backlit-score",
        formatMetric(
            metrics.backlit_score
        )
    );
}

function updateVisionQuality(
    quality
) {
    const element = document.getElementById(
        "vision-quality"
    );

    if (!element) {
        return;
    }

    const normalizedQuality = normalizeQuality(
        quality
    );

    element.textContent = normalizedQuality;
    element.className = "vision-quality-badge";
    element.classList.add(
        `vision-quality-${normalizedQuality}`
    );
}

function updateVisionFaceReady(
    faceReady
) {
    const ready = faceReady === true;

    setText(
        "vision-face-ready",
        formatBoolean(
            ready
        )
    );

    const pill = document.getElementById(
        "vision-face-ready-pill"
    );

    if (!pill) {
        return;
    }

    pill.textContent = ready
        ? "Face ready"
        : "Face not ready";

    pill.className = "vision-face-ready-pill";

    if (ready) {
        pill.classList.add(
            "ready"
        );
    } else {
        pill.classList.add(
            "not-ready"
        );
    }
}

function updateVisionGuidance(
    metrics,
    vision
) {
    const element = document.getElementById(
        "vision-guidance"
    );

    if (!element) {
        return;
    }

    const quality = normalizeQuality(
        metrics.image_quality
        ?? vision.image_quality
        ?? "unknown"
    );

    const guidance = getVisionGuidance(
        quality,
        metrics,
        vision
    );

    element.innerHTML = `
        <div class="vision-guidance-title">${escapeHtml(guidance.title)}</div>
        <div class="vision-guidance-body">${escapeHtml(guidance.body)}</div>
    `;

    element.className = "vision-guidance";
    element.classList.add(
        `vision-guidance-${guidance.level}`
    );
}

function getVisionGuidance(
    quality,
    metrics,
    vision
) {
    if (vision.last_error) {
        return {
            level: "error",
            title: "Vision error",
            body: vision.last_error
        };
    }

    if (!vision.has_frame) {
        return {
            level: "warning",
            title: "No frame available",
            body: "The camera is active, but no frame has been received yet."
        };
    }

    switch (quality) {
        case "ok":
            return {
                level: "ok",
                title: "Image looks usable",
                body: "Lighting and sharpness are acceptable for the next vision stage."
            };

        case "partially_overexposed":
            return {
                level: "warning",
                title: "Partial overexposure",
                body: "There are bright clipped areas. Avoid strong light sources in the frame."
            };

        case "overexposed":
            return {
                level: "error",
                title: "Overexposed image",
                body: "Too much of the image is saturated. Reduce direct light or camera exposure."
            };

        case "backlit":
            return {
                level: "warning",
                title: "Backlit frame",
                body: "The background appears brighter than the subject area. Move the light source in front of the subject."
            };

        case "high_contrast":
            return {
                level: "warning",
                title: "High contrast",
                body: "The image has strong bright and dark regions. Use more even lighting."
            };

        case "low_contrast":
            return {
                level: "warning",
                title: "Low contrast",
                body: "The frame lacks contrast. Add more directional or ambient light."
            };

        case "low_light":
            return {
                level: "warning",
                title: "Low light",
                body: "The image is too dim for reliable face analysis. Add more light."
            };

        case "dark":
            return {
                level: "error",
                title: "Dark image",
                body: "Most of the frame is dark. The camera needs more light."
            };

        case "unusable_dark":
            return {
                level: "error",
                title: "Unusable dark frame",
                body: "The frame is effectively black. Vision and face detection should remain disabled."
            };

        case "blurred":
            return {
                level: "error",
                title: "Blurred frame",
                body: "The frame lacks sharpness. Hold still, improve focus, or increase lighting."
            };

        case "unavailable":
            return {
                level: "error",
                title: "Image unavailable",
                body: "No valid image metrics are available."
            };

        default:
            return {
                level: "warning",
                title: "Unknown image quality",
                body: "Vision metrics are present, but the quality class is not recognized."
            };
    }
}

function updateVisionError(
    vision
) {
    const element = document.getElementById(
        "vision-error"
    );

    if (!element) {
        return;
    }

    if (vision.last_error) {
        element.textContent = vision.last_error;
        element.classList.add(
            "has-error"
        );
        return;
    }

    element.textContent = "No vision errors.";
    element.classList.remove(
        "has-error"
    );
}

function updateVisionPreviewStatus(
    vision
) {
    const element = document.getElementById(
        "vision-preview-status"
    );

    if (!element) {
        return;
    }

    if (vision.last_error) {
        element.textContent = "Error";
        element.className = "inline-status status-error";
        return;
    }

    if (!vision.has_frame) {
        element.textContent = "No frame";
        element.className = "inline-status status-warning";
        return;
    }

    element.textContent = "Frame available";
    element.className = "inline-status status-ok";
}

function updateVisionPreview(
    vision
) {
    const preview = document.getElementById(
        "vision-large-preview"
    );

    const empty = document.getElementById(
        "vision-large-empty"
    );

    if (!preview || !empty) {
        return;
    }

    const snapshotKey = [
        vision.last_snapshot_path ?? "configured_snapshot",
        vision.last_frame_at ?? "static"
    ].join(
        "|"
    );

    if (snapshotKey === lastVisionSnapshotKey) {
        return;
    }

    lastVisionSnapshotKey = snapshotKey;

    const cacheBust = encodeURIComponent(
        vision.last_frame_at ?? "static"
    );

    preview.onload = () => {
        preview.classList.add(
            "visible"
        );

        empty.classList.add(
            "hidden"
        );
    };

    preview.onerror = () => {
        preview.classList.remove(
            "visible"
        );

        empty.classList.remove(
            "hidden"
        );
    };

    preview.src = `/api/vision/snapshot?t=${cacheBust}`;
}

function normalizeQuality(
    quality
) {
    if (!quality) {
        return "unknown";
    }

    return String(
        quality
    )
        .trim()
        .toLowerCase()
        .replaceAll(
            " ",
            "_"
        );
}

function formatMetric(
    value
) {
    if (
        value === null ||
        value === undefined ||
        Number.isNaN(
            Number(
                value
            )
        )
    ) {
        return "-";
    }

    return Number(
        value
    ).toFixed(
        2
    );
}

function formatPercentRatio(
    value
) {
    if (
        value === null ||
        value === undefined ||
        Number.isNaN(
            Number(
                value
            )
        )
    ) {
        return "-";
    }

    return `${(
        Number(
            value
        ) * 100
    ).toFixed(
        1
    )}%`;
}