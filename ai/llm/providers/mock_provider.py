class MockLLMProvider:

    async def generate(
        self,
        text: str
    ) -> str:

        normalized = text.lower().strip()

        if (
            "nome" in normalized
            and (
                "qual" in normalized
                or "quem" in normalized
            )
        ):
            return "Meu nome é Cosmo."

        return f"Você disse: {text}"


llm_provider = MockLLMProvider()

