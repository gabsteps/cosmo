from cosmo.core.config.settings_manager import (
    config
)

from cosmo.audio.tts.providers.piper_tts_provider import (
    PiperTTSProvider
)

from cosmo.audio.tts.providers.espeak_tts_provider import (
    EspeakTTSProvider
)


class TTSProviderFactory:

    def create(self):

        engine = (
            config.get(
                "tts",
                "engine"
            )
            or "piper"
        )

        if engine == "piper":
            return PiperTTSProvider()

        if engine == "espeak":
            return EspeakTTSProvider()

        raise RuntimeError(
            f"TTS engine desconhecido: {engine}"
        )


tts_provider_factory = TTSProviderFactory()