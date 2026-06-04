import logging
import traceback

from cosmo.data.database.repositories.log_repository import (
    log_repository
)


class SQLiteLogHandler(logging.Handler):

    def emit(
        self,
        record
    ):

        try:

            exception_text = None

            if record.exc_info:
                exception_text = "".join(
                    traceback.format_exception(
                        *record.exc_info
                    )
                )

            log_repository.add_log(
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line=record.lineno,
                exception=exception_text
            )

        except Exception:
            # Nunca deixe o logger quebrar a aplicação.
            self.handleError(
                record
            )