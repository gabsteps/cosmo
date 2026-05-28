from database import db


class UserRepository:

    def create_user(self, name):
        db.execute(
            "INSERT INTO users(name) VALUES(?)",
            (name,)
        )

    def get_user_by_id(self, user_id):
        return db.fetchone(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

    def get_user_by_name(self, name):
        return db.fetchone(
            "SELECT * FROM users WHERE name = ?",
            (name,)
        )

    def get_user_by_face_id(self, face_id):
        return db.fetchone(
            "SELECT * FROM users WHERE face_id = ?",
            (face_id,)
        )

    def list_users(self):
        return db.fetchall(
            "SELECT * FROM users"
        )

    def user_exists(self, name):
        user = db.fetchone(
            "SELECT id FROM users WHERE name = ?",
            (name,)
        )
        return user is not None

    def update_last_seen(self, user_id):
        db.execute(
            """
            UPDATE users
            SET last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (user_id,)
        )

    def update_trust_level(self, user_id, trust_level):
        db.execute(
            """
            UPDATE users
            SET trust_level = ?
            WHERE id = ?
            """,
            (trust_level, user_id)
        )

    def save_face_id(self, user_id, face_id):
        db.execute(
            """
            UPDATE users
            SET face_id = ?
            WHERE id = ?
            """,
            (face_id, user_id)
        )

    def rename_user(self, user_id, new_name):
        db.execute(
            """
            UPDATE users
            SET name = ?
            WHERE id = ?
            """,
            (new_name, user_id)
        )

    def delete_user(self, user_id):
        db.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )


user_repository = UserRepository()