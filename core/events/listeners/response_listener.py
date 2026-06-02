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


async def on_response_generated(
    payload
):

    text = payload["text"]

    await async_event_bus.emit(
        TTS_STARTED
    )

    tts_manager.speak_background(text)

    await async_event_bus.emit(
        TTS_FINISHED
    )


async_event_bus.subscribe(
    RESPONSE_GENERATED,
    on_response_generated
)