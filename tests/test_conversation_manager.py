from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)


def main():

    conversation_manager.clear()

    for index in range(20):
        conversation_manager.add_user_message(
            f"user {index}"
        )

        conversation_manager.add_assistant_message(
            f"assistant {index}"
        )

    history = conversation_manager.get_history()

    print(
        f"[TEST] tamanho do histórico: {len(history)}"
    )

    print(
        history
    )

    assert len(history) == 10
    assert history[0]["content"] == "user 15"
    assert history[-1]["content"] == "assistant 19"

    print(
        "[TEST] ConversationManager validado com limite de histórico."
    )


if __name__ == "__main__":
    main()