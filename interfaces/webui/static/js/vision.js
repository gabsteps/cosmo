let lastVisionSnapshotKey = null;
let latestVisionFaceDetection = null;

document.addEventListener(
    "DOMContentLoaded",
    () => {
        connectVisionStream();
    }
);

window.addEventListener(
    "resize",
    () => {
        renderVisionFaceOverlay();
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

    updateFaceDetection(
        vision.face_detection ?? {}
    );

    latestVisionFaceDetection = vision.face_detection ?? {};

    renderVisionFaceOverlay();
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

        renderVisionFaceOverlay();
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

function updateFaceDetection(
    faceDetection
) {
    const normalized = normalizeFaceDetection(
        faceDetection
    );

    setText(
        "vision-face-detection-enabled",
        formatBoolean(
            normalized.enabled
        )
    );

    setText(
        "vision-face-detection-ready",
        formatBoolean(
            normalized.detection_ready
        )
    );

    setText(
        "vision-face-detection-skipped",
        formatBoolean(
            normalized.skipped
        )
    );

    setText(
        "vision-face-detection-skip-reason",
        normalized.skip_reason ?? "-"
    );

    setText(
        "vision-face-detected",
        formatBoolean(
            normalized.face_detected
        )
    );

    setText(
        "vision-face-count",
        normalized.face_count ?? 0
    );

    setText(
        "vision-largest-face",
        formatLargestFace(
            normalized.largest_face
        )
    );

    updateFaceDetectedPill(
        normalized
    );

    updateFaceDetectionError(
        normalized
    );
}

function normalizeFaceDetection(
    faceDetection
) {
    faceDetection = faceDetection ?? {};

    return {
        enabled: faceDetection.enabled === true,
        detection_ready: faceDetection.detection_ready === true,
        skipped: faceDetection.skipped === true,
        skip_reason: faceDetection.skip_reason ?? null,
        face_detected: faceDetection.face_detected === true,
        face_count: Number(
            faceDetection.face_count ?? 0
        ),
        faces: Array.isArray(
            faceDetection.faces
        )
            ? faceDetection.faces
            : [],
        largest_face: faceDetection.largest_face ?? null,
        last_error: faceDetection.last_error ?? null,
    };
}

function formatLargestFace(
    face
) {
    if (!face) {
        return "-";
    }

    const x = face.x ?? "-";
    const y = face.y ?? "-";
    const width = face.width ?? "-";
    const height = face.height ?? "-";
    const area = face.area ?? "-";

    return `${x},${y} ${width}x${height} area=${area}`;
}

function updateFaceDetectedPill(
    faceDetection
) {
    const pill = document.getElementById(
        "vision-face-detected-pill"
    );

    if (!pill) {
        return;
    }

    pill.className = "vision-face-detected-pill";

    if (faceDetection.last_error) {
        pill.textContent = "Detection error";
        pill.classList.add(
            "error"
        );
        return;
    }

    if (faceDetection.skipped) {
        pill.textContent = "Skipped";
        pill.classList.add(
            "skipped"
        );
        return;
    }

    if (faceDetection.face_detected) {
        pill.textContent = `${faceDetection.face_count} face(s)`;
        pill.classList.add(
            "detected"
        );
        return;
    }

    if (faceDetection.detection_ready) {
        pill.textContent = "No face";
        pill.classList.add(
            "not-detected"
        );
        return;
    }

    pill.textContent = "Not ready";
    pill.classList.add(
        "not-ready"
    );
}

function updateFaceDetectionError(
    faceDetection
) {
    const element = document.getElementById(
        "vision-face-detection-error"
    );

    if (!element) {
        return;
    }

    if (faceDetection.last_error) {
        element.textContent = faceDetection.last_error;
        element.classList.add(
            "has-error"
        );
        return;
    }

    element.textContent = "No face detection errors.";
    element.classList.remove(
        "has-error"
    );
}

function renderVisionFaceOverlay() {
    const overlay = document.getElementById(
        "vision-face-overlay"
    );

    const preview = document.getElementById(
        "vision-large-preview"
    );

    if (!overlay || !preview) {
        return;
    }

    overlay.innerHTML = "";

    if (
        !latestVisionFaceDetection ||
        latestVisionFaceDetection.face_detected !== true
    ) {
        return;
    }

    const faces = Array.isArray(
        latestVisionFaceDetection.faces
    )
        ? latestVisionFaceDetection.faces
        : [];

    if (!faces.length) {
        return;
    }

    if (
        !preview.classList.contains(
            "visible"
        ) ||
        !preview.naturalWidth ||
        !preview.naturalHeight
    ) {
        return;
    }

    const geometry = calculateContainedImageGeometry(
        preview
    );

    if (!geometry) {
        return;
    }

    faces.forEach(
        (face, index) => {
            const box = createVisionFaceBox(
                face,
                geometry,
                index,
                isLargestFace(
                    face,
                    latestVisionFaceDetection.largest_face
                )
            );

            if (box) {
                overlay.appendChild(
                    box
                );
            }
        }
    );
}

function calculateContainedImageGeometry(
    image
) {
    const containerWidth = image.clientWidth;
    const containerHeight = image.clientHeight;
    const naturalWidth = image.naturalWidth;
    const naturalHeight = image.naturalHeight;

    if (
        !containerWidth ||
        !containerHeight ||
        !naturalWidth ||
        !naturalHeight
    ) {
        return null;
    }

    const scale = Math.min(
        containerWidth / naturalWidth,
        containerHeight / naturalHeight
    );

    const renderedWidth = naturalWidth * scale;
    const renderedHeight = naturalHeight * scale;

    const offsetX = (
        containerWidth - renderedWidth
    ) / 2;

    const offsetY = (
        containerHeight - renderedHeight
    ) / 2;

    return {
        scale,
        offsetX,
        offsetY,
        renderedWidth,
        renderedHeight,
        naturalWidth,
        naturalHeight
    };
}

function createVisionFaceBox(
    face,
    geometry,
    index,
    largest
) {
    const x = Number(
        face.x
    );

    const y = Number(
        face.y
    );

    const width = Number(
        face.width
    );

    const height = Number(
        face.height
    );

    if (
        Number.isNaN(x) ||
        Number.isNaN(y) ||
        Number.isNaN(width) ||
        Number.isNaN(height)
    ) {
        return null;
    }

    const box = document.createElement(
        "div"
    );

    box.className = "vision-face-box";

    if (largest) {
        box.classList.add(
            "largest"
        );
    }

    box.style.left = `${geometry.offsetX + x * geometry.scale}px`;
    box.style.top = `${geometry.offsetY + y * geometry.scale}px`;
    box.style.width = `${width * geometry.scale}px`;
    box.style.height = `${height * geometry.scale}px`;

    const label = document.createElement(
        "div"
    );

    label.className = "vision-face-label";

    label.textContent = largest
        ? "largest face"
        : `face ${index + 1}`;

    box.appendChild(
        label
    );

    return box;
}

function isLargestFace(
    face,
    largestFace
) {
    if (!face || !largestFace) {
        return false;
    }

    return (
        Number(face.x) === Number(largestFace.x) &&
        Number(face.y) === Number(largestFace.y) &&
        Number(face.width) === Number(largestFace.width) &&
        Number(face.height) === Number(largestFace.height)
    );
}