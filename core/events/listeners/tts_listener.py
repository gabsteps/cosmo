import asyncio
from cosmo.audio.tts.tts_manager import (
    tts_manager
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    RESPONSE_GENERATED,
    TTS_STARTED,
    TTS_FINISHED
)

from cosmo.audio.wakeword.wakeword_manager import (
    wakeword_manager
)


async def on_response_generated(payload):

    text = payload.get(
        "text",
        ""
    )

    await async_event_bus.emit(
        TTS_STARTED,
        {
            "text": text
        },
        priority=async_event_bus.PRIORITY_AUDIO
    )

    await wakeword_manager.stop()

    try:
        await tts_manager.speak(text)

    finally:
        await asyncio.sleep(2.0)

        asyncio.create_task(
            wakeword_manager.start()
        )

    await async_event_bus.emit(
        TTS_FINISHED,
        {
            "text": text
        },
        priority=async_event_bus.PRIORITY_AUDIO
    )


async_event_bus.subscribe(
    RESPONSE_GENERATED,
    on_response_generated
)