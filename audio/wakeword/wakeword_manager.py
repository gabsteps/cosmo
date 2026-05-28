import pyaudio

from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import config

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    WAKE_WORD_DETECTED
)

from cosmo.audio.wakeword.wakeword_engine import (
    wakeword_engine
)


class WakewordManager:

    def __init__(self):

        # Configurações de áudio vindas do YAML
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

        # Inicializa PyAudio
        self.audio = pyaudio.PyAudio()

        # Stream principal do microfone
        self.stream = None

        # Estado do loop
        self.running = False

    def start(self):

        """
        Inicia captura contínua do microfone.
        """

        logger.info("Iniciando wakeword manager")

        # Abre stream de captura
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        self.running = True

        logger.info("Wakeword manager online")

        # Loop principal
        while self.running:

            # Captura chunk do microfone
            audio_data = self.stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )

            # Processa áudio
            detected_word = (
                wakeword_engine.process_audio(
                    audio_data
                )
            )

            # Wake word detectada
            if detected_word:
                
                # Emite evento global
                event_bus.emit(
                    WAKE_WORD_DETECTED,
                    {
                        "word": detected_word
                    }
                )

    def stop(self):

        """
        Finaliza captura de áudio.
        """

        logger.info("Parando wakeword manager")

        self.running = False

        # Fecha stream se existir
        if self.stream:

            self.stream.stop_stream()
            self.stream.close()

        # Finaliza PyAudio
        self.audio.terminate()

        logger.info("Wakeword manager encerrado")


wakeword_manager = WakewordManager()