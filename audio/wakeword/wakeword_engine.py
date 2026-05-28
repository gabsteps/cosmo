from vosk import Model
from vosk import KaldiRecognizer

import json

from cosmo.core.config.settings_manager import config


class WakewordEngine:

    def __init__(self):

        # Caminho do modelo Vosk
        self.model_path = "cosmo/models/vosk/vosk-model-small-pt-0.3"

        # Carrega modelo de reconhecimento offline
        self.model = Model(self.model_path)

        # Configuração do sample rate vinda do YAML
        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        # Inicializa reconhecedor
        self.recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate
        )

        # Lista de wake words válidas
        self.wake_words = config.get(
            "wakeword",
            "words"
        )

    def process_audio(self, audio_data):

        """
        Processa chunk de áudio.

        Retorna:
        - palavra detectada
        - None se nada encontrado
        """

        # Vosk retorna resultado completo apenas
        # quando identifica frase válida
        if self.recognizer.AcceptWaveform(audio_data):

            result = self.recognizer.Result()

            data = json.loads(result)

            text = data.get(
                "text",
                ""
            ).lower()

            # Verifica wake words
            for word in self.wake_words:

                if word in text:

                    return word

        return None


wakeword_engine = WakewordEngine()