import asyncio

from cosmo.cognition.response.response_generator import (
    response_generator
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)

from cosmo.cognition.personality.personality_state import (
    personality_state
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

        return (
            "Resposta mock do LLM."
        )


async def test_incomplete_command_does_not_call_llm():

    print(
        "\n[TEST] comando incompleto não deve chamar LLM"
    )

    conversation_manager.clear()

    llm_provider = MockLLMProvider()

    response = await response_generator.generate(
        user_text="reduza o nível de honestidade para",
        llm_provider=llm_provider
    )

    print(
        f"[TEST] resposta: {response}"
    )

    assert llm_provider.calls == 0

    assert response == (
        "Preciso de um valor entre 0 e 100 para aplicar esse ajuste."
    )

    history = conversation_manager.get_history()

    assert history[-2]["role"] == "user"
    assert history[-1]["role"] == "assistant"

    print(
        "[TEST] comando incompleto bloqueado corretamente"
    )


async def test_complete_command_changes_runtime_state():

    print(
        "\n[TEST] comando completo deve alterar personality_state"
    )

    conversation_manager.clear()

    llm_provider = MockLLMProvider()

    personality_state.set(
        "honesty",
        95
    )

    response = await response_generator.generate(
        user_text="abaixe honestidade para vinte por cento",
        llm_provider=llm_provider
    )

    print(
        f"[TEST] resposta: {response}"
    )

    assert personality_state.get(
        "honesty"
    ) == 20

    assert llm_provider.calls == 1

    print(
        "[TEST] comando completo alterou runtime corretamente"
    )


async def test_common_text_goes_to_llm():

    print(
        "\n[TEST] texto comum deve ir para LLM"
    )

    conversation_manager.clear()

    llm_provider = MockLLMProvider()

    response = await response_generator.generate(
        user_text="faça uma piada curta",
        llm_provider=llm_provider
    )

    print(
        f"[TEST] resposta: {response}"
    )

    assert llm_provider.calls == 1

    assert response == (
        "Resposta mock do LLM."
    )

    print(
        "[TEST] texto comum encaminhado ao LLM corretamente"
    )


async def main():

    await test_incomplete_command_does_not_call_llm()

    await test_complete_command_changes_runtime_state()

    await test_common_text_goes_to_llm()

    print(
        "\n[TEST] Integração de comandos de personalidade validada com sucesso."
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )