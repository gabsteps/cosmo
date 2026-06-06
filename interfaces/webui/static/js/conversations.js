document.addEventListener(
    "DOMContentLoaded",
    () => {
        bindConversationControls();
        loadConversations();
    }
);

function bindConversationControls() {
    const refresh = document.getElementById("conversations-refresh");
    const role = document.getElementById("conversations-role");
    const search = document.getElementById("conversations-search");
    const limit = document.getElementById("conversations-limit");

    if (refresh) {
        refresh.addEventListener(
            "click",
            loadConversations
        );
    }

    if (role) {
        role.addEventListener(
            "change",
            loadConversations
        );
    }

    if (limit) {
        limit.addEventListener(
            "change",
            loadConversations
        );
    }

    if (search) {
        search.addEventListener(
            "keydown",
            event => {
                if (event.key === "Enter") {
                    loadConversations();
                }
            }
        );
    }
}

async function loadConversations() {
    const role = document.getElementById("conversations-role")?.value ?? "";
    const search = document.getElementById("conversations-search")?.value ?? "";
    const limit = document.getElementById("conversations-limit")?.value ?? "50";

    const params = new URLSearchParams();

    params.set("limit", limit);

    if (role) {
        params.set("role", role);
    }

    if (search) {
        params.set("search", search);
    }

    setText("conversations-status", "Loading...");

    try {
        const response = await fetch(
            `/api/conversations?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const rows = await response.json();

        renderTable(
            "conversations-output",
            [
                "timestamp",
                "role",
                "message"
            ],
            rows
        );

        setText(
            "conversations-status",
            `${rows.length} record(s)`
        );

    } catch (error) {
        setText(
            "conversations-status",
            "Failed"
        );

        const output = document.getElementById("conversations-output");

        if (output) {
            output.innerHTML = `
                <div class="empty-state error-state">
                    Failed to load conversations: ${escapeHtml(error.message)}
                </div>
            `;
        }
    }
}