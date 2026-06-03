from cosmo.data.database.repositories.user_repository import (
    user_repository
)

from cosmo.data.database.repositories.memory_repository import (
    memory_repository
)

from cosmo.data.database.repositories.conversation_repository import (
    conversation_repository
)

from cosmo.data.database.repositories.event_repository import (
    event_repository
)

from cosmo.data.database.repositories.system_repository import (
    system_repository
)

from cosmo.data.database.repositories.face_repository import (
    face_repository
)


def cleanup_user(
    user_id
):

    conversation_repository.clear_history(
        user_id
    )

    for memory in memory_repository.get_user_memories(
        user_id
    ):
        memory_repository.delete_memory(
            memory["id"]
        )

    for face in face_repository.get_faces_by_user(
        user_id
    ):
        face_repository.delete_face(
            face["id"]
        )

    user_repository.delete_user(
        user_id
    )


def main():

    test_user_name = "test_user_database"

    existing_user = user_repository.get_user_by_name(
        test_user_name
    )

    if existing_user:
        cleanup_user(
            existing_user["id"]
        )

    user = user_repository.get_or_create_user(
        name=test_user_name,
        trust_level=5
    )

    assert user is not None
    assert user["name"] == test_user_name
    assert user["trust_level"] == 5

    user_id = user["id"]

    user_repository.update_last_seen(
        user_id
    )

    user_repository.update_trust_level(
        user_id,
        7
    )

    updated_user = user_repository.get_user_by_id(
        user_id
    )

    assert updated_user["trust_level"] == 7
    assert updated_user["last_seen"] is not None

    added = memory_repository.add_memory_if_new(
        user_id=user_id,
        category="preference",
        content="Preferência do usuário: teste de memória SQLite.",
        importance=3
    )

    assert added is True

    duplicate = memory_repository.add_memory_if_new(
        user_id=user_id,
        category="preference",
        content="Preferência do usuário: teste de memória SQLite.",
        importance=3
    )

    assert duplicate is False

    memories = memory_repository.get_recent_memories(
        user_id=user_id,
        limit=5
    )

    assert len(memories) >= 1
    assert memories[0]["content"] == (
        "Preferência do usuário: teste de memória SQLite."
    )

    conversation_repository.add_message(
        user_id=user_id,
        role="user",
        message="mensagem de teste do usuário"
    )

    conversation_repository.add_message(
        user_id=user_id,
        role="assistant",
        message="mensagem de teste do assistente"
    )

    context = conversation_repository.get_recent_conversation_context(
        user_id=user_id,
        limit=2
    )

    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[1]["role"] == "assistant"

    event_repository.emit_event(
        event_type="database_test",
        payload={
            "ok": True
        }
    )

    events = event_repository.get_recent_events(
        limit=5
    )

    assert len(events) >= 1
    assert events[0]["type"] == "database_test"

    system_repository.set_state(
        "database_test_key",
        "database_test_value"
    )

    state = system_repository.get_state(
        "database_test_key"
    )

    assert state is not None
    assert state["value"] == "database_test_value"

    system_repository.delete_state(
        "database_test_key"
    )

    deleted_state = system_repository.get_state(
        "database_test_key"
    )

    assert deleted_state is None

    cleanup_user(
        user_id
    )

    deleted_user = user_repository.get_user_by_id(
        user_id
    )

    assert deleted_user is None

    print(
        "[TEST] Banco de dados e repositories validados com sucesso."
    )


if __name__ == "__main__":
    main()