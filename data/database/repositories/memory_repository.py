from cosmo.data.database.database import (
    db
)


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
    
    def memory_exists(
        self,
        user_id,
        content
    ):

        return db.fetchone(
            """
            SELECT id
            FROM memories
            WHERE user_id = ?
            AND lower(content) = lower(?)
            LIMIT 1
            """,
            (
                user_id,
                content.strip()
            )
        ) is not None

    def add_memory_if_new(
        self,
        user_id,
        category,
        content,
        importance=1
    ):

        content = content.strip()

        if not content:
            return False

        if self.memory_exists(
            user_id,
            content
        ):
            return False

        self.add_memory(
            user_id=user_id,
            category=category,
            content=content,
            importance=importance
        )

        return True

    def get_recent_memories(
        self,
        user_id,
        limit=5
    ):

        return db.fetchall(
            """
            SELECT *
            FROM memories
            WHERE user_id = ?
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        )    


memory_repository = MemoryRepository()