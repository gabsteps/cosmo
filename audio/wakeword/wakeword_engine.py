import json
import math
import struct
import unicodedata

from vosk import Model
from vosk import KaldiRecognizer

from cosmo.core.config.settings_manager import (
    config
)


class WakewordEngine:

    def __init__(self):

        self.model_path = (
            "cosmo/models/vosk/vosk-model-small-pt-0.3"
        )

        self.model = Model(
            self.model_path
        )

        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        self.recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate
        )

        self.wake_words = tuple(
            self._normalize(word)
            for word in config.get(
                "wakeword",
                "words"
            )
        )

        self.energy_threshold = (
            config.get(
                "wakeword",
                "energy_threshold"
            )
            or 250
        )

        self.silence_grace_chunks = (
            config.get(
                "wakeword",
                "silence_grace_chunks"
            )
            or 8
        )

        self._silence_grace_remaining = 0

    def process_audio(
        self,
        audio_data: bytes
    ) -> str | None:

        if not audio_data:
            return None

        rms = self._calculate_rms(
            audio_data
        )

        if rms >= self.energy_threshold:

            self._silence_grace_remaining = (
                self.silence_grace_chunks
            )

        elif self._silence_grace_remaining > 0:

            self._silence_grace_remaining -= 1

        else:

            return None

        if self.recognizer.AcceptWaveform(
            audio_data
        ):

            result = json.loads(
                self.recognizer.Result()
            )

            return self._detect_word_from_text(
                result.get(
                    "text",
                    ""
                )
            )

        partial = json.loads(
            self.recognizer.PartialResult()
        )

        return self._detect_word_from_text(
            partial.get(
                "partial",
                ""
            )
        )

    def _detect_word_from_text(
        self,
        text: str
    ) -> str | None:

        normalized_text = self._normalize(
            text
        )

        if not normalized_text:
            return None

        for wake_word in self.wake_words:

            if wake_word in normalized_text:
                return wake_word

        return None

    def _calculate_rms(
        self,
        audio_data: bytes
    ) -> float:

        sample_count = len(
            audio_data
        ) // 2

        if sample_count <= 0:
            return 0.0

        samples = struct.unpack(
            f"<{sample_count}h",
            audio_data
        )

        square_sum = sum(
            sample * sample
            for sample in samples
        )

        return math.sqrt(
            square_sum / sample_count
        )

    def _normalize(
        self,
        text: str
    ) -> str:

        text = text.lower().strip()

        text = unicodedata.normalize(
            "NFD",
            text
        )

        return "".join(
            char
            for char in text
            if unicodedata.category(char) != "Mn"
        )


wakeword_engine = WakewordEngine()