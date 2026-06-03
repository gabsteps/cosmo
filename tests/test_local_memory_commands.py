import asyncio

from cosmo.cognition.response.response_generator import (
    response_generator
)

from cosmo.cognition.memory.memory_manager import (
    memory_manager
)

from cosmo.data.database.repositories.memory_repository import (
    memory_repository
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)


class MockLLMProvider:

    def __init__(self):
        self.calls = 0

    async def generate(
        self,
        messages
    ):
        self.calls += 1
        return "Resposta do LLM. Não deveria aparecer."


async def main():

    user_id = memory_manager.default_user_id

    conversation_manager.clear()

    memory_manager.clear_user_memory()

    memory_repository.add_memory_if_new(
        user_id=user_id,
        category="preference",
        content="Preferência do usuário: Eu prefiro respostas curtas.",
        importance=3
    )

    llm_provider = MockLLMProvider()

    response = await response_generator.generate(
        user_text="o que você lembra sobre mim?",
        llm_provider=llm_provider
    )

    print(
        response
    )

    assert llm_provider.calls == 0
    assert "Memórias persistentes registradas" in response
    assert "respostas curtas" in response.lower()

    response = await response_generator.generate(
        user_text="limpar minhas memórias",
        llm_provider=llm_provider
    )

    print(
        response
    )

    assert llm_provider.calls == 0
    assert "apagadas" in response or "apagada" in response

    memories = memory_repository.get_user_memories(
        user_id
    )

    assert len(memories) == 0

    response = await response_generator.generate(
        user_text="o que você lembra sobre mim?",
        llm_provider=llm_provider
    )

    print(
        response
    )

    assert "Não tenho memórias persistentes" in response

    print(
        "[TEST] Comandos locais de memória validados com sucesso."
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )