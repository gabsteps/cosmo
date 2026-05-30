import json
import wave

from vosk import (
    Model,
    KaldiRecognizer
)

from pathlib import Path

from cosmo.core.logger.logger_manager import (
    logger
)


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "vosk"
    / "vosk-model-small-pt-0.3"
)


class STTEngine:

    def __init__(self):

        logger.info(
            "Carregando modelo STT"
        )

        self.model = Model(
            str(MODEL_PATH)
        )

        logger.info(
            "STT engine inicializada"
        )

    async def transcribe(
        self,
        file_path: str
    ) -> str:

        with wave.open(
            file_path,
            "rb"
        ) as wav:

            recognizer = (
                KaldiRecognizer(
                    self.model,
                    wav.getframerate()
                )
            )

            while True:

                data = wav.readframes(
                    4000
                )

                if not data:
                    break

                recognizer.AcceptWaveform(
                    data
                )

            result = json.loads(
                recognizer.FinalResult()
            )

            return (
                result
                .get("text", "")
                .strip()
            )


stt_engine = STTEngine()