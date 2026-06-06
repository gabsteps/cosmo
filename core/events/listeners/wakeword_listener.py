import asyncio

from cosmo.audio.capture.audio_capture_manager import (
    audio_capture_manager
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    WAKE_WORD_DETECTED
)

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)

from cosmo.audio.tts.tts_manager import (
    tts_manager
)


_wakeword_flow_task = None


async def on_wake_word_detected(
    data
):

    global _wakeword_flow_task

    word = data.get(
        "word"
    )

    logger.info(
        f"Wake word detectada: {word}"
    )

    if runtime_state.should_ignore_wakeword():

        logger.info(
            "Wakeword ignorada pelo runtime_state"
        )

        return

    if (
        _wakeword_flow_task
        and not _wakeword_flow_task.done()
    ):

        logger.info(
            "Wakeword ignorada: fluxo de wakeword já em execução"
        )

        return

    _wakeword_flow_task = asyncio.create_task(
        _handle_wakeword_flow(
            word
        )
    )


async def _handle_wakeword_flow(
    word: str
):

    try:

        runtime_state.set_wake_detected()

        runtime_state.set_listening()

        await tts_manager.speak(
            "sim?"
        )

        await asyncio.wait_for(
            audio_capture_manager.capture(),
            timeout=35
        )

        runtime_state.set_transcribing()

    except asyncio.TimeoutError:

        logger.warning(
            "Timeout durante captura após wakeword"
        )

        runtime_state.set_idle()

    except Exception as error:

        logger.exception(
            f"Erro no fluxo de wakeword: {error}"
        )

        runtime_state.set_idle()


async_event_bus.subscribe(
    WAKE_WORD_DETECTED,
    on_wake_word_detected
)