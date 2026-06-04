import asyncio

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    TTS_FINISHED
)

from cosmo.core.runtime.system_control import (
    system_control
)


async def on_tts_finished(
    payload
):

    asyncio.create_task(
        system_control.execute_pending_after_tts()
    )


async_event_bus.subscribe(
    TTS_FINISHED,
    on_tts_finished
)