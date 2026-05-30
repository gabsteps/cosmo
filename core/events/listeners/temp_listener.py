from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    TRANSCRIPT_READY
)


async def on_transcript_ready(data):

    logger.info(
        f'Transcript: {data["text"]}'
    )


async_event_bus.subscribe(
    TRANSCRIPT_READY,
    on_transcript_ready
)