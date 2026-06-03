class BaseTTSProvider:

    async def speak(
        self,
        text: str
    ) -> None:

        raise NotImplementedError(
            "TTS provider precisa implementar speak(text)"
        )