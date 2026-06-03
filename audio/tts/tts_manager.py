# cosmo/audio/tts/tts_manager.py

from cosmo.audio.tts.providers.tts_provider_factory import (
    tts_provider_factory
)


class TTSManager:

    def __init__(self):

        self.provider = (
            tts_provider_factory.create()
        )

    async def speak(
        self,
        text: str
    ) -> None:

        await self.provider.speak(
            text
        )


tts_manager = TTSManager()