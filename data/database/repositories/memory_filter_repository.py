from cosmo.data.database.database import (
    db
)


class MemoryFilterRepository:

    def get_blocked_terms(
        self
    ):

        return db.fetchall(
            """
            SELECT term
            FROM memory_blocked_terms
            WHERE active = 1
            ORDER BY length(term) DESC
            """
        )

    def get_noise_markers(
        self
    ):

        return db.fetchall(
            """
            SELECT marker
            FROM memory_noise_markers
            WHERE active = 1
            ORDER BY length(marker) DESC
            """
        )

    def get_setting(
        self,
        key,
        default=None
    ):

        row = db.fetchone(
            """
            SELECT value
            FROM memory_filter_settings
            WHERE key = ?
            """,
            (key,)
        )

        if not row:
            return default

        return row["value"]

    def set_setting(
        self,
        key,
        value
    ):

        db.execute(
            """
            INSERT INTO memory_filter_settings(key, value)
            VALUES(?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (
                key,
                str(value)
            )
        )


memory_filter_repository = MemoryFilterRepository()