from cosmo.core.config.settings_manager import (
    config
)

from cosmo.ai.llm.providers.ollama_provider import (
    OllamaProvider
)


provider = config.get(
    "llm",
    "provider"
)


if provider == "ollama":

    llm_provider = OllamaProvider()

else:

    raise ValueError(
        f"LLM provider inválido: {provider}"
    )