import asyncio
import pyaudio

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    WAKE_WORD_DETECTED
)

from cosmo.audio.wakeword.wakeword_engine import (
    wakeword_engine
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)


class WakewordManager:

    def __init__(
        self
    ):

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

        self.idle_sleep = (
            config.get(
                "wakeword",
                "idle_sleep"
            )
            or 0.03
        )

        self.audio = pyaudio.PyAudio()

        self.stream = None

        self.running = False

        self._lock = asyncio.Lock()

    async def start(
        self
    ):

        async with self._lock:

            if self.running:

                logger.info(
                    "Wakeword manager já está rodando"
                )

                return

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

            if runtime_state.should_ignore_wakeword():

                await asyncio.sleep(
                    0.1
                )

                continue

            if not self.stream:

                logger.warning(
                    "Wakeword sem stream ativo"
                )

                break

            try:

                audio_data = await asyncio.to_thread(
                    self.stream.read,
                    self.chunk_size,
                    exception_on_overflow=False
                )

            except OSError as error:

                logger.warning(
                    f"Wakeword stream interrompido: {error}"
                )

                break

            except Exception as error:

                logger.exception(
                    f"Erro inesperado no wakeword: {error}"
                )

                break

            detected_word = wakeword_engine.process_audio(
                audio_data
            )

            if not detected_word:

                await asyncio.sleep(
                    self.idle_sleep
                )

                continue

            logger.info(
                f"Wakeword detectada pelo engine: {detected_word}"
            )

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

            await asyncio.sleep(
                0.3
            )

        await self._cleanup_stream()

    async def stop(
        self
    ):

        async with self._lock:

            if not self.running and not self.stream:

                logger.info(
                    "Wakeword manager já está pausado"
                )

                return

            logger.info(
                "Parando wakeword manager"
            )

            self.running = False

        await asyncio.sleep(
            0.1
        )

        await self._cleanup_stream()

        logger.info(
            "Wakeword manager pausado"
        )

    async def _cleanup_stream(
        self
    ):

        async with self._lock:

            if not self.stream:

                return

            try:

                self.stream.stop_stream()

            except Exception as error:

                logger.warning(
                    f"Falha ao parar stream wakeword: {error}"
                )

            try:

                self.stream.close()

            except Exception as error:

                logger.warning(
                    f"Falha ao fechar stream wakeword: {error}"
                )

            self.stream = None

    async def shutdown(
        self
    ):

        await self.stop()

        self.audio.terminate()

        logger.info(
            "Wakeword manager encerrado"
        )


wakeword_manager = WakewordManager()