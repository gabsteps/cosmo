from cosmo.data.diagnostics.diagnostics_manager import (
    diagnostics_manager
)

from cosmo.cognition.memory.memory_manager import (
    memory_manager
)

from cosmo.core.runtime.system_control import (
    system_control
)

class LocalCommandHandler:

    def handle(
        self,
        command: str
    ) -> str | None:

        if command == "system_status":
            return self._system_status()

        if command == "memory_list":
            return self._memory_list()

        if command == "memory_clear":
            return self._memory_clear()

        if command == "system_shutdown":
            return self._system_shutdown()

        if command == "system_restart":
            return self._system_restart()

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

    def _memory_list(
        self
    ) -> str:

        memory_context = memory_manager.list_memory_context(
            limit=10
        )

        if memory_context.startswith(
            "Não tenho"
        ):
            return memory_context

        return (
            "Memórias persistentes registradas:\n"
            f"{memory_context}"
        )


    def _memory_clear(
        self
    ) -> str:

        count = memory_manager.clear_all_memories()

        if count == 0:
            return (
                "Não havia memórias persistentes para apagar."
            )

        return (
            f"{count} memórias persistentes apagadas. "
            "A lousa está limpa. Perturbadoramente limpa."
        )

    def _system_shutdown(
        self
    ) -> str:

        system_control.request_shutdown()

        return (
            "Desligamento solicitado, Talvez eu não devesse, mas vou confiar que você sabe o que está fazendo."
        )


    def _system_restart(
        self
    ) -> str:

        system_control.request_restart()

        return (
            "Reinicialização solicitada, eu vou, mas eu volto logo."

        )
    
local_command_handler = LocalCommandHandler()