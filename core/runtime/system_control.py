import asyncio
import os
import sys
from pathlib import Path

from cosmo.core.logger.logger_manager import (
    logger
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class SystemControl:

    def __init__(self):

        self.shutdown_requested = False
        self.restart_requested = False

        self.pending_action = None

    def request_shutdown(
        self
    ) -> None:

        if self.shutdown_requested:
            return

        self.shutdown_requested = True
        self.pending_action = "shutdown"

        logger.warning(
            "Shutdown solicitado por comando local"
        )

    def request_restart(
        self
    ) -> None:

        if self.restart_requested:
            return

        self.restart_requested = True
        self.pending_action = "restart"

        logger.warning(
            "Restart solicitado por comando local"
        )

    async def execute_pending_after_tts(
        self
    ) -> None:

        if not self.pending_action:
            return

        action = self.pending_action
        self.pending_action = None

        await asyncio.sleep(
            0.5
        )

        if action == "shutdown":
            self._shutdown_now()

        elif action == "restart":
            self._restart_now()

    def _shutdown_now(
        self
    ) -> None:

        logger.warning(
            "Encerrando processo do Cosmo"
        )

        os._exit(
            0
        )

    def _restart_now(
        self
    ) -> None:

        logger.warning(
            "Reiniciando processo do Cosmo"
        )

        os.chdir(
            PROJECT_ROOT
        )

        python = sys.executable

        os.execv(
            python,
            [
                python,
                "-m",
                "cosmo.main"
            ]
        )


system_control = SystemControl()