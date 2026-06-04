from pathlib import Path

from cosmo.data.database.database import (
    db
)


class DatabaseMetricsRepository:

    def get_metrics(
        self
    ) -> dict:

        return {
            "database_size_bytes": self._database_size_bytes(),
            "database_size_human": self._format_bytes(
                self._database_size_bytes()
            ),
            "users_count": self._count_table("users"),
            "memories_count": self._count_table("memories"),
            "conversations_count": self._count_table("conversations"),
            "events_count": self._count_table("events"),
            "logs_count": self._count_table("logs"),
            "faces_count": self._count_table("faces"),
            "last_event_type": self._last_value(
                table="events",
                column="type",
                order_column="created_at"
            ),
            "last_log_level": self._last_value(
                table="logs",
                column="level",
                order_column="created_at"
            ),
        }

    def _count_table(
        self,
        table_name: str
    ) -> int:

        row = db.fetchone(
            f"SELECT COUNT(*) AS count FROM {table_name}"
        )

        return (
            row["count"]
            if row
            else 0
        )

    def _last_value(
        self,
        table: str,
        column: str,
        order_column: str
    ):

        row = db.fetchone(
            f"""
            SELECT {column} AS value
            FROM {table}
            ORDER BY {order_column} DESC
            LIMIT 1
            """
        )

        return (
            row["value"]
            if row
            else None
        )

    def _database_size_bytes(
        self
    ) -> int:

        database_path = Path(
            db.path
        )

        if not database_path.exists():
            return 0

        return database_path.stat().st_size

    def _format_bytes(
        self,
        value: float
    ) -> str:

        units = (
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        )

        value = float(
            value
        )

        for unit in units:

            if value < 1024:
                return f"{value:.1f} {unit}"

            value /= 1024

        return f"{value:.1f} PB"


database_metrics_repository = DatabaseMetricsRepository()