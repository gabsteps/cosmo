import asyncio
import time

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    RESPONSE_GENERATED
)

from cosmo.core.events.listeners.transcript_listener import (
    on_transcript_ready
)

from cosmo.core.events.listeners.tts_listener import (
    on_response_generated
)

from cosmo.cognition.conversation.conversation_pipeline import (
    conversation_pipeline
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)


class SlowMockLLMProvider:

    async def generate(
        self,
        messages
    ):
        await asyncio.sleep(5)
        return "Resposta lenta mock."


events_seen = []


async def on_test_response_generated(
    payload
):
    events_seen.append(
        {
            "event": RESPONSE_GENERATED,
            "payload": payload
        }
    )

    print(
        f"[TEST] response_generated recebido: {payload}"
    )


async def test_double_transcript_during_thinking():

    print(
        "\n[TEST] Validando bloqueio de transcript durante THINKING"
    )

    runtime_state.set_idle()

    conversation_pipeline.set_llm_provider(
        SlowMockLLMProvider()
    )

    started_at = time.time()

    await on_transcript_ready(
        {
            "text": "primeira pergunta"
        }
    )

    first_elapsed = time.time() - started_at

    print(
        f"[TEST] primeiro transcript retornou em {first_elapsed:.3f}s"
    )

    if runtime_state.mode != runtime_state.THINKING:
        raise AssertionError(
            f"Esperado THINKING, recebido: {runtime_state.mode}"
        )

    await on_transcript_ready(
        {
            "text": "segunda pergunta enquanto ainda está pensando"
        }
    )

    await asyncio.sleep(0.5)

    if runtime_state.current_transcript != "primeira pergunta":
        raise AssertionError(
            "Segundo transcript sobrescreveu o primeiro. Bloqueio falhou."
        )

    print(
        "[TEST] segundo transcript foi ignorado corretamente durante THINKING"
    )


async def test_double_tts_during_speaking():

    print(
        "\n[TEST] Validando bloqueio de TTS durante SPEAKING"
    )

    if runtime_state.mode != runtime_state.IDLE:
        raise AssertionError(
            f"Teste de TTS precisa começar em IDLE. Estado atual: {runtime_state.mode}"
        )
    first_task = asyncio.create_task(
        on_response_generated(
            {
                "text": (
                    "Primeira fala de teste. "
                    "Ela deve ocupar o estado de fala por alguns segundos."
                )
            }
        )
    )

    await asyncio.sleep(0.2)

    if runtime_state.mode != runtime_state.SPEAKING:
        raise AssertionError(
            f"Esperado SPEAKING, recebido: {runtime_state.mode}"
        )

    await on_response_generated(
        {
            "text": "Segunda fala que deve ser ignorada."
        }
    )

    await first_task

    await asyncio.sleep(12)

    if runtime_state.mode != runtime_state.IDLE:
        raise AssertionError(
            f"Esperado IDLE após TTS, recebido: {runtime_state.mode}"
        )

    print(
        "[TEST] segunda fala não bloqueou o listener; valide no log se foi ignorada pelo TTSPipeline"
    )


async def main():

    async_event_bus.subscribe(
        RESPONSE_GENERATED,
        on_test_response_generated
    )

    bus_task = asyncio.create_task(
        async_event_bus.start()
    )

    try:
        await test_double_transcript_during_thinking()

        await wait_until_idle()

        await test_double_tts_during_speaking()

        await wait_until_idle()

        print(
            "\n[TEST] Validação de concorrência concluída."
        )

    finally:
        await async_event_bus.shutdown()

        bus_task.cancel()

        try:
            await bus_task

        except asyncio.CancelledError:
            pass

async def wait_until_idle(
    timeout: float = 20.0
) -> None:

    started_at = time.time()

    while time.time() - started_at < timeout:

        if runtime_state.mode == runtime_state.IDLE:
            return

        await asyncio.sleep(0.1)

    raise AssertionError(
        f"Runtime não voltou para IDLE. Estado atual: {runtime_state.mode}"
    )

if __name__ == "__main__":
    asyncio.run(
        main()
    )