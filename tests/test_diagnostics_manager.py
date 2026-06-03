from cosmo.data.diagnostics.diagnostics_manager import (
    diagnostics_manager
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)


def main():

    runtime_state.set_idle()

    conversation_manager.clear()

    conversation_manager.add_user_message(
        "teste"
    )

    conversation_manager.add_assistant_message(
        "resposta"
    )

    snapshot = diagnostics_manager.snapshot()

    compact = diagnostics_manager.compact_snapshot()

    print(
        snapshot
    )

    print(
        compact
    )

    assert "runtime" in snapshot
    assert "event_bus" in snapshot
    assert "conversation" in snapshot
    assert "personality" in snapshot

    assert compact["mode"] == runtime_state.IDLE
    assert compact["conversation_size"] == 2

    print(
        "[TEST] DiagnosticsManager validado com sucesso."
    )


if __name__ == "__main__":
    main()