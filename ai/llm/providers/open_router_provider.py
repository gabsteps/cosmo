import asyncio
import json
import os
import urllib.request

from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)


class OpenRouterProvider:

    def __init__(self):

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        if not self.api_key:

            raise RuntimeError(
                "OPENROUTER_API_KEY não configurada"
            )

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

        self.timeout = config.get(
            "llm",
            "timeout"
        )

        self.url = (
            "https://openrouter.ai/api/v1/chat/completions"
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

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        history = conversation_manager.get_history()

        if not history or history[-1]["content"] != text:

            history.append(
                {
                    "role": "user",
                    "content": text
                }
            )

        messages.extend(history)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        logger.info(
            f"Mensagens enviadas para LLM: {messages}"
        )

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-OpenRouter-Title": "Zenith Cosmo"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=self.timeout
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        return (
            data["choices"][0]["message"]["content"]
            .strip()
        )


llm_provider = OpenRouterProvider()