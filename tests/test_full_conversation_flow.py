import asyncio
import time

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    RESPONSE_GENERATED,
    TTS_STARTED,
    TTS_FINISHED
)

from cosmo.core.events.listeners.transcript_listener import (
    on_transcript_ready
)

# Import necessário para registrar o listener real:
# RESPONSE_GENERATED -> on_response_generated
from cosmo.core.events.listeners.tts_listener import (  # noqa: F401
    on_response_generated
)

from cosmo.cognition.pipeline.conversation_pipeline import (
    conversation_pipeline
)


class MockLLMProvider:

    async def generate(
        self,
        messages
    ):
        await asyncio.sleep(2)

        return (
            "Resposta mock gerada. "
            "Se você ouviu isso, o fluxo completo funcionou."
        )


events_seen = []


async def on_test_response_generated(
    payload
):
    events_seen.append(
        RESPONSE_GENERATED
    )

    print(
        f"[TEST] response_generated recebido: {payload}"
    )


async def on_test_tts_started(
    payload
):
    events_seen.append(
        TTS_STARTED
    )

    print(
        f"[TEST] tts_started recebido: {payload}"
    )


async def on_test_tts_finished(
    payload
):
    events_seen.append(
        TTS_FINISHED
    )

    print(
        f"[TEST] tts_finished recebido: {payload}"
    )


async def wait_until(
    condition,
    timeout: float = 25.0,
    interval: float = 0.1
) -> bool:

    started_at = time.time()

    while time.time() - started_at < timeout:

        if condition():
            return True

        await asyncio.sleep(
            interval
        )

    return False


async def main():

    conversation_pipeline.set_llm_provider(
        MockLLMProvider()
    )

    async_event_bus.subscribe(
        RESPONSE_GENERATED,
        on_test_response_generated
    )

    async_event_bus.subscribe(
        TTS_STARTED,
        on_test_tts_started
    )

    async_event_bus.subscribe(
        TTS_FINISHED,
        on_test_tts_finished
    )

    bus_task = asyncio.create_task(
        async_event_bus.start()
    )

    try:

        started_at = time.time()

        await on_transcript_ready(
            {
                "text": "faça uma piada curta"
            }
        )

        listener_elapsed = time.time() - started_at

        print(
            f"[TEST] on_transcript_ready retornou em {listener_elapsed:.3f}s"
        )

        if listener_elapsed > 0.2:
            raise AssertionError(
                "on_transcript_ready bloqueou. Era esperado retornar rápido."
            )

        completed = await wait_until(
            lambda: TTS_FINISHED in events_seen,
            timeout=30.0
        )

        print(
            f"[TEST] eventos vistos: {events_seen}"
        )

        if not completed:
            raise AssertionError(
                "tts_finished não foi recebido dentro do tempo esperado."
            )

        if RESPONSE_GENERATED not in events_seen:
            raise AssertionError(
                "response_generated não foi despachado."
            )

        if TTS_STARTED not in events_seen:
            raise AssertionError(
                "tts_started não foi despachado."
            )

        if TTS_FINISHED not in events_seen:
            raise AssertionError(
                "tts_finished não foi despachado."
            )

        response_index = events_seen.index(
            RESPONSE_GENERATED
        )

        tts_started_index = events_seen.index(
            TTS_STARTED
        )

        tts_finished_index = events_seen.index(
            TTS_FINISHED
        )

        if not (
            response_index < tts_started_index < tts_finished_index
        ):
            raise AssertionError(
                "Ordem incorreta. Esperado: response_generated -> tts_started -> tts_finished."
            )

        print(
            "[TEST] Fluxo completo validado com sucesso."
        )

    finally:

        await async_event_bus.shutdown()

        bus_task.cancel()

        try:
            await bus_task

        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(
        main()
    )