document.addEventListener(
    "DOMContentLoaded",
    () => {
        bindMemoryControls();
        loadMemory();
    }
);

function bindMemoryControls() {
    const refresh = document.getElementById("memory-refresh");
    const category = document.getElementById("memory-category");
    const search = document.getElementById("memory-search");
    const limit = document.getElementById("memory-limit");

    if (refresh) {
        refresh.addEventListener(
            "click",
            loadMemory
        );
    }

    if (limit) {
        limit.addEventListener(
            "change",
            loadMemory
        );
    }

    if (category) {
        category.addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    loadMemory();
                }
            }
        );
    }

    if (search) {
        search.addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    loadMemory();
                }
            }
        );
    }
}

async function loadMemory() {
    const category = document.getElementById("memory-category")?.value ?? "";
    const search = document.getElementById("memory-search")?.value ?? "";
    const limit = document.getElementById("memory-limit")?.value ?? "50";

    const params = new URLSearchParams();

    params.set("limit", limit);

    if (category) {
        params.set("category", category);
    }

    if (search) {
        params.set("search", search);
    }

    setText("memory-status", "Loading...");

    try {
        const response = await fetch(
            `/api/memories?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const rows = await response.json();

        renderTable(
            "memory-output",
            [
                "created_at",
                "category",
                "importance",
                "content"
            ],
            rows
        );

        setText(
            "memory-status",
            `${rows.length} record(s)`
        );

    } catch (error) {
        setText(
            "memory-status",
            "Failed"
        );

        const output = document.getElementById("memory-output");

        if (output) {
            output.innerHTML = `
                <div class="empty-state error-state">
                    Failed to load memories: ${escapeHtml(error.message)}
                </div>
            `;
        }
    }
}