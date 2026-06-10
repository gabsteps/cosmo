import sqlite3
from pathlib import Path

from cosmo.core.config.settings_manager import (
    config
)


class LogRepository:

    def __init__(
        self
    ):

        self.repository_file = Path(
            __file__
        ).resolve()

        self.cosmo_root = self.repository_file.parents[3]
        self.project_root = self.repository_file.parents[4]

        self.database_path = self._resolve_database_path()

    def _resolve_database_path(
        self
    ) -> Path:

        configured_path = (
            config.get(
                "database",
                "path"
            )
            or config.get(
                "database",
                "database_path"
            )
            or config.get(
                "database",
                "sqlite_path"
            )
            or "cosmo/data/database/cosmo.db"
        )

        path = Path(
            configured_path
        )

        if path.is_absolute():
            return path

        candidates = [
            self.project_root / path,
            self.cosmo_root / path,
            self.project_root / "cosmo" / path,
            self.cosmo_root / "data/database/cosmo.db",
            self.project_root / "cosmo/data/database/cosmo.db",
        ]

        for candidate in candidates:

            if candidate.exists():
                return candidate

        return candidates[-1]

    def _connect(
        self
    ):

        if not self.database_path.exists():

            raise FileNotFoundError(
                f"Banco de dados não encontrado: {self.database_path}"
            )

        connection = sqlite3.connect(
            str(
                self.database_path
            )
        )

        connection.row_factory = sqlite3.Row

        return connection

    def add_log(
        self,
        level: str,
        message: str,
        logger: str | None = None,
        logger_name: str | None = None,
        module: str | None = None,
        function: str | None = None,
        line: int | None = None,
        exception: str | None = None,
        created_at: str | None = None,
    ) -> None:

        resolved_logger = (
            logger
            or logger_name
            or "cosmo"
        )

        query = """
            INSERT INTO logs (
                level,
                logger,
                message,
                module,
                function,
                line,
                exception,
                created_at
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                COALESCE(?, datetime('now'))
            )
        """

        params = (
            level,
            resolved_logger,
            message,
            module,
            function,
            line,
            exception,
            created_at,
        )

        connection = self._connect()

        try:

            connection.execute(
                query,
                params
            )

            connection.commit()

        finally:

            connection.close()

    def get_recent_logs(
        self,
        limit: int = 200,
        level: str | None = None,
        search: str | None = None,
        logger_name: str | None = None,
        module: str | None = None,
        function: str | None = None,
    ):

        query = """
            SELECT
                id,
                level,
                logger,
                message,
                module,
                function,
                line,
                exception,
                created_at
            FROM logs
            WHERE 1 = 1
        """

        params = []

        if level:

            query += """
                AND level = ?
            """

            params.append(
                level
            )

        if logger_name:

            query += """
                AND logger LIKE ?
            """

            params.append(
                f"%{logger_name}%"
            )

        if module:

            query += """
                AND module LIKE ?
            """

            params.append(
                f"%{module}%"
            )

        if function:

            query += """
                AND function LIKE ?
            """

            params.append(
                f"%{function}%"
            )

        if search:

            query += """
                AND (
                    level LIKE ?
                    OR logger LIKE ?
                    OR message LIKE ?
                    OR module LIKE ?
                    OR function LIKE ?
                    OR CAST(line AS TEXT) LIKE ?
                    OR exception LIKE ?
                    OR created_at LIKE ?
                )
            """

            search_value = f"%{search}%"

            params.extend(
                [
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                    search_value,
                ]
            )

        query += """
            ORDER BY id DESC
            LIMIT ?
        """

        params.append(
            limit
        )

        connection = self._connect()

        try:

            cursor = connection.execute(
                query,
                tuple(
                    params
                )
            )

            return cursor.fetchall()

        finally:

            connection.close()


log_repository = LogRepository()