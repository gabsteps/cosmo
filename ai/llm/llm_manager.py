from cosmo.ai.llm.llm_provider import (
    llm_provider
)


class LLMManager:

    async def generate(
        self,
        text: str
    ) -> str:

        return await llm_provider.generate(
            text
        )


llm_manager = LLMManager()