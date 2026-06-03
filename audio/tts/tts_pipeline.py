from cosmo.core.logger.logger_manager import logger
import asyncio

from cosmo.audio.tts.tts_manager import (
    tts_manager
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)


class TTSPipeline:

    async def speak_response(
        self,
        text: str
    ) -> None:

        text = text.strip()

        if not text:
            logger.warning(
                "TTS ignorado: texto vazio"
            )
            return

        try:
            runtime_state.set_speaking(
                text
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
                seconds=2.0
            )

            await asyncio.sleep(
                2.0
            )

            runtime_state.set_idle()


tts_pipeline = TTSPipeline()