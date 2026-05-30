import asyncio
import wave
import pyaudio

from cosmo.audio.wakeword.wakeword_manager import (
    wakeword_manager
)
from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import config

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    AUDIO_CAPTURE_STARTED,
    AUDIO_CAPTURED
)


class AudioCaptureManager:

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

        self.capture_seconds = 5

        self.output_file = (
            "cosmo/data/cache/audio/input.wav"
        )

    async def capture(self):

        logger.info(
            "Iniciando captura de áudio"
        )

        await async_event_bus.emit(
            AUDIO_CAPTURE_STARTED,
            priority=async_event_bus.PRIORITY_AUDIO
        )

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        frames = []

        total_chunks = int(
            self.sample_rate /
            self.chunk_size *
            self.capture_seconds
        )

        logger.info(
            f"Capturando áudio por "
            f"{self.capture_seconds}s"
        )

        for _ in range(total_chunks):

            data = stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )

            if _ < 5:

                logger.info(
                    f"chunk[{_}]={data[:20]}"
                )

            frames.append(data)

            await asyncio.sleep(0)
            
            logger.info(
                f"frames={len(frames)}"
            )

            logger.info(
                f"wav_bytes={sum(len(f) for f in frames)}"
            )

        stream.stop_stream()
        stream.close()

        sample_width = audio.get_sample_size(
            pyaudio.paInt16
        )

        audio.terminate()

        with wave.open(
            self.output_file,
            "wb"
        ) as wav:

            wav.setnchannels(
                self.channels
            )

            wav.setsampwidth(
                sample_width
            )

            wav.setframerate(
                self.sample_rate
            )

            wav.writeframes(
                b"".join(frames)
            )

        logger.info(
            f"Áudio salvo: "
            f"{self.output_file}"
        )

        await async_event_bus.emit(
            AUDIO_CAPTURED,
            {
                "file_path": self.output_file
            },
            priority=async_event_bus.PRIORITY_AUDIO
        )



audio_capture_manager = AudioCaptureManager()