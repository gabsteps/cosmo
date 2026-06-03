import asyncio

from cosmo.audio.tts.tts_provider import (
    tts_provider
)

from cosmo.core.logger.logger_manager import (
    logger
)


class TTSManager:

    async def speak(
        self,
        text: str
    ) -> None:

        await tts_provider.speak(
            text
        )

    def speak_background(
        self,
        text: str
    ) -> asyncio.Task:

        task = asyncio.create_task(
            self._safe_speak(text)
        )

        task.add_done_callback(
            self._handle_task_result
        )

    async def _safe_speak(
        self,
        text: str
    ) -> None:

        try:

            await self.speak(
                text
            )

        except Exception as error:

            logger.exception(
                f"Erro durante TTS: {error}"
            )
    
    def _handle_task_result(
    self,
    task: asyncio.Task
    ) -> None:

        try:

            task.result()

        except Exception as error:

            logger.exception(
                f"Task de TTS falhou: {error}"
            )


tts_manager = TTSManager()