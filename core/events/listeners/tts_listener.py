import asyncio

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    RESPONSE_GENERATED
)

from cosmo.audio.tts.tts_pipeline import (
    tts_pipeline
)

from cosmo.core.logger.logger_manager import (
    logger
)


async def on_response_generated(payload):

    text = payload.get(
        "text",
        ""
    ).strip()

    if not text:
        logger.warning(
            "response_generated ignorado: texto vazio"
        )
        return

    logger.info(
        "TTS será executado em background"
    )

    task = asyncio.create_task(
        tts_pipeline.speak_response(text)
    )

    task.add_done_callback(
        _handle_tts_task_result
    )


def _handle_tts_task_result(task):

    try:
        task.result()

    except Exception as error:
        logger.exception(
            f"Task de TTS falhou: {error}"
        )


async_event_bus.subscribe(
    RESPONSE_GENERATED,
    on_response_generated
)