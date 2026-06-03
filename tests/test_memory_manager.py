from cosmo.cognition.memory.memory_manager import (
    memory_manager
)

from cosmo.data.database.repositories.memory_repository import (
    memory_repository
)

from cosmo.data.database.repositories.conversation_repository import (
    conversation_repository
)


def main():

    user_id = memory_manager.default_user_id

    conversation_repository.clear_history(
        user_id
    )

    memory_manager.clear_user_memory()

    memory_manager.process_interaction(
        user_text="Eu prefiro respostas curtas e diretas.",
        assistant_text="Entendido."
    )

    memories = memory_repository.get_recent_memories(
        user_id=user_id,
        limit=10
    )

    assert len(memories) == 1
    assert memories[0]["category"] == "preference"
    assert "respostas curtas" in memories[0]["content"].lower()

    memory_manager.process_interaction(
        user_text="Eu prefiro respostas curtas e diretas.",
        assistant_text="Já registrado."
    )

    memories = memory_repository.get_recent_memories(
        user_id=user_id,
        limit=10
    )

    assert len(memories) == 1

    memory_manager.process_interaction(
        user_text="hã",
        assistant_text="Não entendi."
    )

    memories = memory_repository.get_recent_memories(
        user_id=user_id,
        limit=10
    )

    assert len(memories) == 1

    memory_manager.process_interaction(
        user_text="De agora em diante, me responda de forma objetiva.",
        assistant_text="Entendido."
    )

    memories = memory_repository.get_recent_memories(
        user_id=user_id,
        limit=10
    )

    assert len(memories) == 2

    context = memory_manager.build_memory_context(
        "qual é o próximo passo?"
    )

    print(
        context
    )

    assert "respostas curtas" in context.lower()
    assert "objetiva" in context.lower()

    history = conversation_repository.get_recent_conversation_context(
        user_id=user_id,
        limit=2
    )

    assert len(history) == 2

    print(
        "[TEST] MemoryManager amadurecido validado com sucesso."
    )


if __name__ == "__main__":
    main()