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

        self.detection_cooldown = (
            config.get(
                "wakeword",
                "detection_cooldown"
            )
            or 2.0
        )

        self.audio = pyaudio.PyAudio()

        self.stream = None

        self.running = False

        self._lock = asyncio.Lock()

        required_settings = {
            "audio.sample_rate": self.sample_rate,
            "audio.chunk_size": self.chunk_size,
            "audio.channels": self.channels,
        }

        missing_settings = [
            key
            for key, value in required_settings.items()
            if value is None
        ]

        if missing_settings:

            raise RuntimeError(
                "Configurações obrigatórias ausentes para WakewordManager: "
                + ", ".join(
                    missing_settings
                )
            )

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

        try:

            while self.running:

                if runtime_state.mode != "idle":

                    await self._close_stream_if_open()

                    await asyncio.sleep(
                        self.idle_sleep
                    )

                    continue

                if not self.stream:

                    opened = await self._open_stream_if_needed()

                    if not opened:

                        await asyncio.sleep(
                            0.5
                        )

                        continue

                    wakeword_engine.reset()

                audio_data = await self._read_chunk()

                if audio_data is None:

                    await self._close_stream_if_open()

                    await asyncio.sleep(
                        0.5
                    )

                    continue

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
                    priority=async_event_bus.PRIORITY_AUDIO
                )

                wakeword_engine.reset()

                await self._close_stream_if_open()

                await asyncio.sleep(
                    self.detection_cooldown
                )

        finally:

            await self._cleanup_stream()

            logger.info(
                "Wakeword manager offline"
            )

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

    async def _read_chunk(self) -> bytes | None:

        if not self.stream:
            return None

        try:
            return await asyncio.to_thread(
                self.stream.read,
                self.chunk_size,
                exception_on_overflow=False
            )

        except OSError as error:
            logger.warning(f"Falha transitória ao ler wakeword stream: {error}")
            return None

        except Exception as error:
            logger.exception(f"Erro inesperado ao ler wakeword stream: {error}")
            return None

    async def _drain_for(
        self,
        seconds: float
    ) -> None:

        if seconds <= 0:

            return

        end_time = (
            asyncio.get_running_loop().time()
            + seconds
        )

        drained_chunks = 0

        while (
            self.running
            and asyncio.get_running_loop().time() < end_time
        ):

            audio_data = await self._read_chunk()

            if audio_data is None:

                break

            drained_chunks += 1

            await asyncio.sleep(
                self.idle_sleep
            )

        logger.debug(
            f"Wakeword drain concluído: {drained_chunks} chunk(s)"
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

    async def _open_stream_if_needed(
        self
    ) -> bool:

        async with self._lock:

            if self.stream:

                return True

            try:

                logger.info(
                    "Abrindo stream wakeword"
                )

                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size
                )

                logger.info(
                    "Stream wakeword aberto"
                )

                return True

            except Exception as error:

                logger.warning(
                    f"Falha ao abrir stream wakeword: {error}"
                )

                self.stream = None

                return False

    async def _close_stream_if_open(
        self
    ) -> None:

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

            logger.info(
                "Stream wakeword fechado"
            )

wakeword_manager = WakewordManager()