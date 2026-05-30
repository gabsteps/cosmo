from cosmo.audio.capture.audio_capture_manager import (
    audio_capture_manager
)
from cosmo.core.events.async_event_bus import async_event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED

from cosmo.core.logger.logger_manager import logger

from cosmo.core.runtime.runtime_state import(
    runtime_state
)

from cosmo.audio.tts.tts_manager import (
    tts_manager
)


async def on_wake_word_detected(data):

    word = data.get("word")

    logger.info(
        f"Wake word detectada: {word}"
    )

    if runtime_state.should_ignore_wakeword():
        return

    runtime_state.mode = runtime_state.LISTENING

    await tts_manager.speak(
        "ooopa"
    )

    await audio_capture_manager.capture()


async_event_bus.subscribe(
    WAKE_WORD_DETECTED,
    on_wake_word_detected
)