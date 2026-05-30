from cosmo.audio.tts.tts_provider import (
    tts_provider
)


class TTSManager:

    async def speak(
        self,
        text: str
    ) -> None:

        await tts_provider.speak(
            text
        )


tts_manager = TTSManager()