from database import db
import json


class EventRepository:

    def emit_event(self, event_type, payload=None):
        db.execute(
            """
            INSERT INTO events(type, payload)
            VALUES(?, ?)
            """,
            (
                event_type,
                json.dumps(payload) if payload else None
            )
        )

    def get_recent_events(self, limit=50):
        return db.fetchall(
            """
            SELECT * FROM events
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )


event_repository = EventRepository()