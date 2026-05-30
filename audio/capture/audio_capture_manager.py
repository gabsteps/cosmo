import asyncio
import wave
import pyaudio
import audioop

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
        self.silence_threshold = config.get(
            "audio",
            "silence_threshold"
        )

        self.silence_timeout = config.get(
            "audio",
            "silence_timeout"
        )

        self.max_record_seconds = config.get(
            "audio",
            "max_record_seconds"
        )

        self.max_silent_chunks = int(
            self.silence_timeout *
            self.sample_rate /
            self.chunk_size
        )

        self.max_chunks = int(
            self.max_record_seconds *
            self.sample_rate /
            self.chunk_size
        )

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

        silent_chunks = 0

        recorded_chunks = 0

        speech_detected = False

        logger.info(
            "Captura iniciada "
            "(aguardando silêncio)"
        )

        while True:

            data = stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )

            frames.append(data)

            volume = audioop.rms(
                data,
                2
            )

            if volume >= self.silence_threshold:

                speech_detected = True
                silent_chunks = 0

            else:

                if speech_detected:

                    silent_chunks += 1


            if (
                speech_detected and
                silent_chunks >= self.max_silent_chunks
            ):
                break

            recorded_chunks += 1

            if recorded_chunks >= self.max_chunks:
                break

            await asyncio.sleep(0)

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