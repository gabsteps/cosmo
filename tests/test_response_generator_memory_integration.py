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

from cosmo.data.database.repositories.conversation_repository import (
    conversation_repository
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)


class MockLLMProvider:

    def __init__(self):

        self.calls = 0
        self.last_messages = None

    async def generate(
        self,
        messages
    ):

        self.calls += 1
        self.last_messages = messages

        return "Resposta mock do LLM."


async def main():

    user_id = memory_manager.default_user_id

    conversation_manager.clear()

    conversation_repository.clear_history(
        user_id
    )

    memory_manager.clear_user_memory()

    llm_provider = MockLLMProvider()

    response = await response_generator.generate(
        user_text="Eu prefiro respostas curtas e diretas.",
        llm_provider=llm_provider
    )

    assert response == "Resposta mock do LLM."
    assert llm_provider.calls == 1

    memories = memory_repository.get_recent_memories(
        user_id=user_id,
        limit=10
    )

    assert len(memories) == 1
    assert memories[0]["category"] == "preference"
    assert "respostas curtas" in memories[0]["content"].lower()

    llm_provider_2 = MockLLMProvider()

    await response_generator.generate(
        user_text="qual é o próximo passo?",
        llm_provider=llm_provider_2
    )

    messages = llm_provider_2.last_messages

    memory_system_messages = [
        message
        for message in messages
        if (
            message["role"] == "system"
            and "MEMÓRIAS RELEVANTES" in message["content"]
        )
    ]

    assert len(memory_system_messages) == 1
    assert "respostas curtas" in memory_system_messages[0]["content"].lower()

    print(
        "[TEST] Integração de memória no ResponseGenerator validada com sucesso."
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )