import asyncio
import json
import os
import urllib.request
import urllib.error

from cosmo.core.logger.logger_manager import logger
from cosmo.core.config.settings_manager import config


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
        messages: list[dict[str, str]]
    ) -> str:

        return await asyncio.to_thread(
            self._generate_sync,
            messages
        )

    def _generate_sync(
        self,
        messages: list[dict[str, str]]
    ) -> str:

        if not messages:
            raise ValueError(
                "Lista de mensagens vazia"
            )

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

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8")

            logger.error(
                f"Erro HTTP OpenRouter {error.code}: {body}"
            )

            raise RuntimeError(
                f"Erro HTTP OpenRouter {error.code}: {body}"
            ) from error

        except urllib.error.URLError as error:
            logger.error(
                f"Erro de conexão com OpenRouter: {error}"
            )

            raise RuntimeError(
                f"Erro de conexão com OpenRouter: {error}"
            ) from error

        try:
            return (
                data["choices"][0]["message"]["content"]
                .strip()
            )

        except KeyError as error:
            logger.error(
                f"Resposta inesperada do OpenRouter: {data}"
            )

            raise RuntimeError(
                "Resposta inesperada do OpenRouter"
            ) from error


llm_provider = OpenRouterProvider()