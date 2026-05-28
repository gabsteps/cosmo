from database import db


class MemoryRepository:

    def add_memory(self, user_id, category, content, importance=1):
        db.execute(
            """
            INSERT INTO memories(user_id, category, content, importance)
            VALUES(?, ?, ?, ?)
            """,
            (user_id, category, content, importance)
        )

    def get_user_memories(self, user_id):
        return db.fetchall(
            """
            SELECT * FROM memories
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

    def get_memories_by_category(self, category):
        return db.fetchall(
            """
            SELECT * FROM memories
            WHERE category = ?
            ORDER BY created_at DESC
            """,
            (category,)
        )

    def delete_memory(self, memory_id):
        db.execute(
            "DELETE FROM memories WHERE id = ?",
            (memory_id,)
        )


memory_repository = MemoryRepository()