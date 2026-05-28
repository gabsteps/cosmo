from vosk import Model, KaldiRecognizer
import json
from pathlib import Path

from cosmo.core.logger.logger_manager import logger
from cosmo.core.config.settings_manager import config


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "vosk"
    / "vosk-model-small-pt-0.3"
)


class STTEngine:

    def __init__(self):

        logger.info("Carregando modelo STT")

        self.model = Model(str(MODEL_PATH))

        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        self.recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate
        )

        logger.info("STT engine inicializada")

    def process_audio(self, audio_data):

        """
        Processa chunk de áudio
        e retorna texto completo.
        """

        if self.recognizer.AcceptWaveform(audio_data):

            result = json.loads(
                self.recognizer.Result()
            )

            text = result.get(
                "text",
                ""
            ).strip()

            return text

        return None


stt_engine = STTEngine()