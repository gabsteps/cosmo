from database import db


class SystemRepository:

    def set_state(self, key, value):
        db.execute(
            """
            INSERT INTO system_state(key, value)
            VALUES(?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (key, value)
        )

    def get_state(self, key):
        return db.fetchone(
            """
            SELECT value FROM system_state
            WHERE key = ?
            """,
            (key,)
        )

    def delete_state(self, key):
        db.execute(
            """
            DELETE FROM system_state
            WHERE key = ?
            """,
            (key,)
        )


system_repository = SystemRepository()