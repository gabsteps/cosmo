import asyncio

from cosmo.audio.tts.tts_manager import (
    tts_manager
)

from cosmo.core.logger.logger_manager import (
    logger
)


class TTSFallback:

    def __init__(self):
        self._lock = asyncio.Lock()

    async def speak_timeout_message(self) -> None:
        async with self._lock:
            try:
                await tts_manager.speak(
                    "Não entendi o que disse."
                )

            except Exception as error:
                logger.exception(
                    f"Falha ao executar TTS de timeout: {error}"
                )


tts_fallback = TTSFallback()