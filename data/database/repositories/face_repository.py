from database import db


class FaceRepository:

    def create_face(self, user_id, encoding_path):
        db.execute(
            """
            INSERT INTO faces(user_id, encoding_path)
            VALUES(?, ?)
            """,
            (user_id, encoding_path)
        )

    def get_faces_by_user(self, user_id):
        return db.fetchall(
            """
            SELECT * FROM faces
            WHERE user_id = ?
            """,
            (user_id,)
        )

    def delete_face(self, face_id):
        db.execute(
            "DELETE FROM faces WHERE id = ?",
            (face_id,)
        )


face_repository = FaceRepository()