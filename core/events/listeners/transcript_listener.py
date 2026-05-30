from cosmo.ai.llm.llm_manager import (
    llm_manager
)

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    RESPONSE_GENERATED,
    TRANSCRIPT_READY,
)


async def on_transcript_ready(
    payload
):

    text = payload.get("text", "").strip()
    
    if not text:
        return

    
    logger.info(
        f"Processando transcript: {text}"
    )

    response = await llm_manager.generate(
        text
    )

    logger.info(
        f"Resposta gerada: {response}"
    )

    await async_event_bus.emit(
    RESPONSE_GENERATED,
    {
        "text": response,
        "source_text": text
    },
    priority=async_event_bus.PRIORITY_COGNITION
)

async_event_bus.subscribe(
    TRANSCRIPT_READY,
    on_transcript_ready
)