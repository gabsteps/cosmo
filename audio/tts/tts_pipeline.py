import asyncio

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.audio.tts.tts_manager import (
    tts_manager
)

from cosmo.audio.wakeword.wakeword_engine import (
    wakeword_engine
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    TTS_STARTED,
    TTS_FINISHED
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)

from cosmo.core.config.settings_manager import (
    config
)


class TTSPipeline:

    def __init__(
        self
    ):

        self.post_tts_cooldown = (
            config.get(
                "tts",
                "post_tts_cooldown"
            )
            or 2.0
        )

    async def speak_response(
        self,
        text: str
    ) -> None:

        if not text or not text.strip():

            logger.warning(
                "TTS ignorado: texto vazio"
            )

            return

        text = text.strip()

        try:

            runtime_state.set_speaking(
                text
            )

            await async_event_bus.emit(
                TTS_STARTED,
                {
                    "text": text
                },
                priority=async_event_bus.PRIORITY_AUDIO
            )

            await tts_manager.speak(
                text
            )

        except Exception as error:

            logger.exception(
                f"Erro no TTSPipeline: {error}"
            )

        finally:

            runtime_state.set_cooldown(
                seconds=self.post_tts_cooldown
            )

            wakeword_engine.reset()

            try:

                await async_event_bus.emit(
                    TTS_FINISHED,
                    {
                        "text": text
                    },
                    priority=async_event_bus.PRIORITY_AUDIO
                )

            except Exception as error:

                logger.warning(
                    f"Falha ao emitir TTS_FINISHED: {error}"
                )

            await asyncio.sleep(
                self.post_tts_cooldown
            )

            runtime_state.set_idle()


tts_pipeline = TTSPipeline()