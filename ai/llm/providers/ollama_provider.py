import asyncio
import json
import urllib.request

from cosmo.core.config.settings_manager import (
    config
)


class OllamaProvider:

    def __init__(self):

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

        self.system_prompt = config.get(
            "llm",
            "system_prompt"
        )

        self.url = (
            "http://localhost:11434/api/generate"
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

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Usuário: {text}\n"
            f"Cosmo:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        return data.get(
            "response",
            ""
        ).strip()