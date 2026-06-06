function renderTable(targetId, columns, rows) {
    const target = document.getElementById(targetId);

    if (!target) {
        return;
    }

    if (!Array.isArray(rows) || rows.length === 0) {
        target.innerHTML = `
            <div class="empty-state">
                No records found.
            </div>
        `;
        return;
    }

    const tableRows = rows.map(
        row => `
            <tr>
                ${columns.map(
                    column => `
                        <td class="${getCellClass(column)}">
                            ${escapeHtml(formatCell(row[column], column))}
                        </td>
                    `
                ).join("")}
            </tr>
        `
    ).join("");

    target.innerHTML = `
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        ${columns.map(
                            column => `
                                <th class="${getColumnClass(column)}">
                                    ${escapeHtml(column)}
                                </th>
                            `
                        ).join("")}
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        </div>
    `;
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

function getColumnClass(column) {
    const smallColumns = [
        "id",
        "level",
        "role",
        "importance"
    ];

    const mediumColumns = [
        "created_at",
        "timestamp",
        "module",
        "function",
        "type",
        "category"
    ];

    const wideColumns = [
        "message",
        "content",
        "payload"
    ];

    if (smallColumns.includes(column)) {
        return "col-small";
    }

    if (mediumColumns.includes(column)) {
        return "col-medium";
    }

    if (wideColumns.includes(column)) {
        return "col-wide";
    }

    return "col-large";
}

function getCellClass(column) {
    const classes = [];

    if (
        column === "message" ||
        column === "content" ||
        column === "payload"
    ) {
        classes.push("cell-wide");
    }

    if (
        column === "payload" ||
        column === "message" ||
        column === "content"
    ) {
        classes.push("cell-code");
    }

    return classes.join(" ");
}