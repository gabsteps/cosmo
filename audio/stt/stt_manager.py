import pyaudio

from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import config

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    SPEECH_RECEIVED
)

from cosmo.audio.stt.stt_engine import (
    stt_engine
)


class STTManager:

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

    def listen_once(self):

        """
        Escuta uma frase única.
        """

        logger.info("Escuta ativa iniciada")

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        while True:

            audio_data = stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )

            text = stt_engine.process_audio(
                audio_data
            )

            if text:

                logger.info(
                    f"Texto reconhecido: {text}"
                )

                event_bus.emit(
                    SPEECH_RECEIVED,
                    {
                        "text": text
                    }
                )

                break

        stream.stop_stream()
        stream.close()

        logger.info("Escuta finalizada")


stt_manager = STTManager()