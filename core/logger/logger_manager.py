import logging
from pathlib import Path

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.logger.sqlite_log_handler import (
    SQLiteLogHandler
)


class LoggerManager:

    def __init__(self):

        self.logger = logging.getLogger(
            "cosmo"
        )

        self.logger.setLevel(
            self._get_level()
        )

        self.logger.propagate = False

        if not self.logger.handlers:
            self._setup_handlers()

    def _get_level(
        self
    ):

        level_name = (
            config.get(
                "logs",
                "level"
            )
            or "INFO"
        )

        return getattr(
            logging,
            level_name.upper(),
            logging.INFO
        )

    def _setup_handlers(
        self
    ):

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            formatter
        )

        self.logger.addHandler(
            console_handler
        )

        log_path = config.get(
            "logs",
            "path"
        )

        if log_path:

            file_path = Path(
                log_path
            )

            file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            file_handler = logging.FileHandler(
                file_path,
                encoding="utf-8"
            )

            file_handler.setFormatter(
                formatter
            )

            self.logger.addHandler(
                file_handler
            )

        sqlite_enabled = config.get(
            "logs",
            "sqlite_enabled"
        )

        if sqlite_enabled is not False:

            sqlite_handler = SQLiteLogHandler()
            sqlite_handler.setLevel(
                self._get_level()
            )

            self.logger.addHandler(
                sqlite_handler
            )


logger = LoggerManager().logger