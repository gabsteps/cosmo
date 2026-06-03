import asyncio

from cosmo.cognition.response.response_generator import (
    response_generator
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)

from cosmo.core.runtime.runtime_state import (
    runtime_state
)


class MockLLMProvider:

    def __init__(self):
        self.calls = 0

    async def generate(
        self,
        messages
    ):
        self.calls += 1
        return "Resposta do LLM. Isso não deveria aparecer."


async def main():

    conversation_manager.clear()

    runtime_state.set_idle()

    llm_provider = MockLLMProvider()

    response = await response_generator.generate(
        user_text="cosmo status do sistema",
        llm_provider=llm_provider
    )

    print(
        response
    )

    assert llm_provider.calls == 0

    assert "Status operacional" in response
    assert "modo atual" in response
    assert "Fila de eventos" in response
    assert "Histórico" in response

    print(
        "[TEST] Comando local de status validado com sucesso."
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )