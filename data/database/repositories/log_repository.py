from cosmo.data.database.database import (
    db
)


class LogRepository:

    def add_log(
        self,
        level,
        logger_name,
        message,
        module=None,
        function=None,
        line=None,
        exception=None
    ):

        db.execute(
            """
            INSERT INTO logs(
                level,
                logger,
                message,
                module,
                function,
                line,
                exception
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                level,
                logger_name,
                message,
                module,
                function,
                line,
                exception
            )
        )

    def get_recent_logs(
        self,
        limit=200,
        level=None
    ):

        if level:

            return db.fetchall(
                """
                SELECT *
                FROM logs
                WHERE level = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (
                    level,
                    limit
                )
            )

        return db.fetchall(
            """
            SELECT *
            FROM logs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                limit,
            )
        )

    def clear_logs(
        self
    ):

        db.execute(
            "DELETE FROM logs"
        )


log_repository = LogRepository()