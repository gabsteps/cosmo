from cosmo.data.database.database import (
    db
)

import json


class EventRepository:

    def emit_event(
        self,
        event_type,
        payload=None
    ):

        db.execute(
            """
            INSERT INTO events(type, payload)
            VALUES(?, ?)
            """,
            (
                event_type,
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    default=str
                )
                if payload
                else None
            )
        )

    def get_recent_events(
        self,
        limit=50,
        event_type=None
    ):

        if event_type:

            return db.fetchall(
                """
                SELECT *
                FROM events
                WHERE type = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (
                    event_type,
                    limit
                )
            )

        return db.fetchall(
            """
            SELECT *
            FROM events
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                limit,
            )
        )


event_repository = EventRepository()