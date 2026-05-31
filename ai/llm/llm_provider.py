from cosmo.core.config.settings_manager import (
    config
)


provider = config.get(
    "llm",
    "provider"
)


if provider == "openrouter":

    from cosmo.ai.llm.providers.open_router_provider import (
        llm_provider
    )

elif provider == "ollama":

    from cosmo.ai.llm.providers.ollama_provider import (
        llm_provider
    )

else:

    raise ValueError(
        f"LLM provider inválido: {provider}"
    )