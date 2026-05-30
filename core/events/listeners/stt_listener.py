from cosmo.audio.stt.stt_manager import (
    stt_manager
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    AUDIO_CAPTURED
)


async def on_audio_captured(data):

    file_path = data["file_path"]

    await stt_manager.transcribe(
        file_path
    )


async_event_bus.subscribe(
    AUDIO_CAPTURED,
    on_audio_captured
)