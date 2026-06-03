from cosmo.data.diagnostics.diagnostics_manager import (
    diagnostics_manager
)


class LocalCommandHandler:

    def handle(
        self,
        command: str
    ) -> str | None:

        if command == "system_status":
            return self._system_status()

        return None

    def _system_status(
        self
    ) -> str:

        snapshot = diagnostics_manager.compact_snapshot()

        mode = snapshot.get(
            "mode"
        )

        queue_size = snapshot.get(
            "queue_size"
        )

        conversation_size = snapshot.get(
            "conversation_size"
        )

        listener_timeouts = snapshot.get(
            "listener_timeouts"
        )

        listener_errors = snapshot.get(
            "listener_errors"
        )

        events_failed = snapshot.get(
            "events_failed"
        )

        last_error = snapshot.get(
            "last_error"
        )

        if last_error:
            error_line = (
                f"Último erro: {last_error}."
            )
        else:
            error_line = (
                "Nenhum erro registrado."
            )

        return (
            "Status operacional: "
            f"modo atual {mode}. "
            f"Fila de eventos: {queue_size}. "
            f"Histórico: {conversation_size} mensagens. "
            f"Timeouts de listener: {listener_timeouts}. "
            f"Erros de listener: {listener_errors}. "
            f"Eventos falhos: {events_failed}. "
            f"{error_line}"
        )


local_command_handler = LocalCommandHandler()