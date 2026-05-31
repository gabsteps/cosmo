import asyncio
from openai import OpenAI

from cosmo.core.config.settings_manager import (
    config
)


class OpenAIProvider:

    def __init__(self):

        self.client = OpenAI()

        self.model = config.get(
            "llm",
            "model"
        )

        self.system_prompt = config.get(
            "llm",
            "system_prompt"
        )

        self.temperature = config.get(
            "llm",
            "temperature"
        )

        self.max_tokens = config.get(
            "llm",
            "max_tokens"
        )

    async def generate(
        self,
        text: str
    ) -> str:

        return await asyncio.to_thread(
            self._generate_sync,
            text
        )

    def _generate_sync(
        self,
        text: str
    ) -> str:

        response = self.client.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=text,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens
        )

        return response.output_text.strip()


llm_provider = OpenAIProvider()