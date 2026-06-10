function setText(id, value) {
    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent = value ?? "-";
}

function formatBoolean(value) {
    return value ? "true" : "false";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function formatTimestamp(value) {
    if (!value) {
        return "-";
    }

    let normalized = String(value);

    if (
        normalized.includes("T") &&
        (
            normalized.endsWith("Z") ||
            normalized.includes("+00:00")
        )
    ) {
        const date = new Date(normalized);

        if (!Number.isNaN(date.getTime())) {
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
    }

    normalized = normalized.replace(" ", "T");

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
