import asyncio
import pyaudio

from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import config

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    WAKE_WORD_DETECTED
)

from cosmo.audio.wakeword.wakeword_engine import (
    wakeword_engine
)


class WakewordManager:

    def __init__(self):

        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        self.chunk_size = config.get(
            "audio",
            "chunk_size"
        )

        self.channels = config.get(
            "audio",
            "channels"
        )

        self.audio = pyaudio.PyAudio()

        self.stream = None

        self.running = False

    async def start(self):

        """
        Inicia captura contínua do microfone.
        """

        logger.info(
            "Iniciando wakeword manager"
        )

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        self.running = True

        logger.info(
            "Wakeword manager online"
        )

        while self.running:

            audio_data = (
                await asyncio.to_thread(
                    self.stream.read,
                    self.chunk_size,
                    exception_on_overflow=False
                )
            )

            detected_word = (
                wakeword_engine.process_audio(
                    audio_data
                )
            )

            if detected_word:

                await async_event_bus.emit(
                    WAKE_WORD_DETECTED,
                    {
                        "word": detected_word
                    },
                    priority=(
                        async_event_bus
                        .PRIORITY_AUDIO
                    )
                )

    async def stop(self):

        """
        Finaliza captura de áudio.
        """


        logger.info(
            "Parando wakeword manager"
        )

        self.running = False

        if self.stream:

            self.stream.stop_stream()
            self.stream.close()

            self.stream = None

        logger.info(
            "Wakeword manager pausado"
        )
        
    async def shutdown(self):

        await self.stop()

        self.audio.terminate()

        logger.info(
            "Wakeword manager encerrado"
        )


wakeword_manager = WakewordManager()