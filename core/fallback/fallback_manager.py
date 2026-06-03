from cosmo.core.fallback.fallback_messages import (
    FallbackMessages
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)


class FallbackManager:

    def stt_empty(self) -> str:
        return FallbackMessages.STT_EMPTY

    def stt_error(self) -> str:
        return FallbackMessages.STT_ERROR

    def llm_timeout(self) -> str:
        return FallbackMessages.LLM_TIMEOUT

    def llm_error(self) -> str:
        return FallbackMessages.LLM_ERROR

    def tts_error(self) -> str:
        return FallbackMessages.TTS_ERROR

    def command_incomplete(self) -> str:
        return FallbackMessages.COMMAND_INCOMPLETE

    def unknown_error(self) -> str:
        return FallbackMessages.UNKNOWN_ERROR

    def busy_message(self) -> str:

        mode = runtime_state.mode

        if mode == runtime_state.THINKING:
            return FallbackMessages.SYSTEM_BUSY_THINKING

        if mode == runtime_state.SPEAKING:
            return FallbackMessages.SYSTEM_BUSY_SPEAKING

        if mode == runtime_state.COOLDOWN:
            return FallbackMessages.SYSTEM_BUSY_COOLDOWN

        return FallbackMessages.UNKNOWN_ERROR


fallback_manager = FallbackManager()