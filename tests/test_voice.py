from cosmo.core.config.settings_manager import (
    config
)

from cosmo.audio.tts.providers.tts_provider_factory import (
    tts_provider_factory
)

from cosmo.audio.tts.providers.piper_tts_provider import (
    PiperTTSProvider
)

from cosmo.audio.tts.providers.espeak_tts_provider import (
    EspeakTTSProvider
)


def main():

    provider = tts_provider_factory.create()

    engine = config.get(
        "tts",
        "engine"
    )

    if engine == "piper":

        assert isinstance(
            provider,
            PiperTTSProvider
        )

    elif engine == "espeak":

        assert isinstance(
            provider,
            EspeakTTSProvider
        )

    else:

        raise AssertionError(
            f"Engine inesperado no teste: {engine}"
        )

    print(
        f"[TEST] TTSProviderFactory validada com engine {engine}."
    )


if __name__ == "__main__":
    main()