from database import db


class ConversationRepository:

    def add_message(self, user_id, role, message):
        db.execute(
            """
            INSERT INTO conversations(user_id, role, message)
            VALUES(?, ?, ?)
            """,
            (user_id, role, message)
        )

    def get_conversation_history(self, user_id, limit=20):
        return db.fetchall(
            """
            SELECT * FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit)
        )

    def clear_history(self, user_id):
        db.execute(
            """
            DELETE FROM conversations
            WHERE user_id = ?
            """,
            (user_id,)
        )


conversation_repository = ConversationRepository()