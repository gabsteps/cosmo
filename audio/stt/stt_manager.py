from cosmo.core.logger.logger_manager import logger

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    TRANSCRIPT_READY
)

from cosmo.audio.stt.stt_engine import (
    stt_engine
)


class STTManager:

    async def transcribe(
        self,
        file_path: str
    ):

        logger.info(
            f"Transcrevendo áudio: {file_path}"
        )

        text = await stt_engine.transcribe(
            file_path
        )

        logger.info(
            f"Texto reconhecido: {text}"
        )

        await async_event_bus.emit(
            TRANSCRIPT_READY,
            {
                "text": text,
                "file_path": file_path
            },
            priority=(
                async_event_bus
                .PRIORITY_AUDIO
            )
        )


stt_manager = STTManager()