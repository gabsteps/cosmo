import asyncio

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    TRANSCRIPT_READY,
)

from cosmo.cognition.pipeline.conversation_pipeline import (
    conversation_pipeline
)

from cosmo.cognition.pipeline.conversation_pipeline import (
    conversation_pipeline
)
from cosmo.core.runtime.runtime_state import (
    runtime_state
)


async def on_transcript_ready(payload):

    text = payload.get("text", "").strip()

    if not text:
        logger.warning(
            "transcript_ready ignorado: texto vazio"
        )
        return

    if not runtime_state.can_start_thinking():
        logger.info(
            "Transcript ignorado: geração de resposta já em andamento"
        )
        return

    logger.info(
        f"Processando transcript em background: {text}"
    )

    runtime_state.set_thinking(text)

    asyncio.create_task(
        conversation_pipeline.process_text(text)
    )

async_event_bus.subscribe(
    TRANSCRIPT_READY,
    on_transcript_ready
)
