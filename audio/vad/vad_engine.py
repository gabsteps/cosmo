import webrtcvad

from cosmo.core.config.settings_manager import config


class VADEngine:

    def __init__(self):

        # agressividade: 0 (leve) a 3 (rigoroso)
        self.vad = webrtcvad.Vad(2)

        self.sample_rate = config.get("audio", "sample_rate")

        # WebRTC só aceita: 10, 20 ou 30ms
        self.frame_ms = 30

        self.frame_size = int(self.sample_rate * self.frame_ms / 1000)

    def is_speech(self, audio_chunk: bytes) -> bool:

        """
        Retorna True se o frame contém voz.
        """

        try:
            return self.vad.is_speech(audio_chunk, self.sample_rate)

        except Exception:
            return False


vad_engine = VADEngine()