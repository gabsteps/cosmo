from cosmo.data.database.database import (
    db
)


class LocalCommandRepository:

    def get_active_commands(self):

        return db.fetchall(
            """
            SELECT intent, phrase
            FROM local_commands
            WHERE active = 1
            ORDER BY intent, phrase
            """
        )

    def add_command_phrase(
        self,
        intent,
        phrase,
        language="pt-BR"
    ):

        db.execute(
            """
            INSERT OR IGNORE INTO local_commands(
                intent,
                phrase,
                language,
                active
            )
            VALUES(?, ?, ?, 1)
            """,
            (
                intent,
                phrase,
                language
            )
        )

    def disable_command_phrase(
        self,
        intent,
        phrase
    ):

        db.execute(
            """
            UPDATE local_commands
            SET active = 0
            WHERE intent = ?
            AND phrase = ?
            """,
            (
                intent,
                phrase
            )
        )


local_command_repository = LocalCommandRepository()