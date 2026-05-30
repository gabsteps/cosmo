from cosmo.ai.llm.llm_provider import (
    llm_provider
)


class LLMManager:

    async def generate(
        self,
        text: str
    ) -> str:

        blocked = ["qwen", "alibaba", "ollama", "inteligência artificial"]

        if any(word in text.lower() for word in blocked):
            text = "Eu sou Cosmo, seu companheiro inteligente."

        return await llm_provider.generate(
            text
        )


llm_manager = LLMManager()