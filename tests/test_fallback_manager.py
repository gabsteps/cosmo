# cosmo/tests/test_fallback_manager.py

from cosmo.core.fallback.fallback_manager import (
    fallback_manager
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)


def main():

    assert fallback_manager.stt_empty()
    assert fallback_manager.stt_error()
    assert fallback_manager.llm_timeout()
    assert fallback_manager.llm_error()
    assert fallback_manager.tts_error()
    assert fallback_manager.command_incomplete()
    assert fallback_manager.unknown_error()

    runtime_state.set_idle()

    runtime_state.set_thinking(
        "teste"
    )
    assert fallback_manager.busy_message()

    runtime_state.set_speaking(
        "resposta"
    )
    assert fallback_manager.busy_message()

    runtime_state.set_cooldown(
        seconds=1.0
    )
    assert fallback_manager.busy_message()

    runtime_state.set_idle()

    print(
        "[TEST] FallbackManager validado com sucesso."
    )


if __name__ == "__main__":
    main()