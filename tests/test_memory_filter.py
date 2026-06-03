from cosmo.cognition.memory.memory_filter import (
    memory_filter
)


def main():

    assert memory_filter.is_valid(
        {
            "content": "Preferência do usuário: Eu prefiro respostas curtas."
        }
    ) is True

    assert memory_filter.is_valid(
        {
            "content": "Minha senha é 123456"
        }
    ) is False

    assert memory_filter.is_valid(
        {
            "content": "Meu CPF é 00000000000"
        }
    ) is False

    assert memory_filter.is_valid(
        {
            "content": "hum"
        }
    ) is False

    assert memory_filter.is_valid(
        {
            "content": "não sei"
        }
    ) is False

    print(
        "[TEST] MemoryFilter com banco validado com sucesso."
    )


if __name__ == "__main__":
    main()