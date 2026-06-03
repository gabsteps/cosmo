import asyncio

from cosmo.core.runtime.runtime_state import (
    runtime_state
)

from cosmo.core.events.listeners.transcript_listener import (
    on_transcript_ready
)

from cosmo.cognition.conversation.conversation_pipeline import (
    conversation_pipeline
)


class MockLLMProvider:

    async def generate(self, messages):
        await asyncio.sleep(1)
        return "Resposta mock para validar estado."


async def main():

    conversation_pipeline.set_llm_provider(
        MockLLMProvider()
    )

    runtime_state.set_idle()

    assert runtime_state.mode == runtime_state.IDLE

    runtime_state.set_wake_detected()
    assert runtime_state.mode == runtime_state.WAKE_DETECTED

    runtime_state.set_listening()
    assert runtime_state.mode == runtime_state.LISTENING

    runtime_state.set_transcribing()
    assert runtime_state.mode == runtime_state.TRANSCRIBING

    await on_transcript_ready(
        {
            "text": "teste de estado"
        }
    )

    assert runtime_state.mode == runtime_state.THINKING

    print(
        "[TEST] runtime_state chegou em THINKING corretamente."
    )


if __name__ == "__main__":
    asyncio.run(main())