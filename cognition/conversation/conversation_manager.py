from collections import deque


class ConversationManager:

    def __init__(
        self,
        max_messages: int = 10
    ):

        self.max_messages = max_messages

        self.history = deque(
            maxlen=max_messages
        )

    def add_user_message(
        self,
        text: str
    ) -> None:

        text = text.strip()

        if not text:
            return

        self.history.append(
            {
                "role": "user",
                "content": text
            }
        )

    def add_assistant_message(
        self,
        text: str
    ) -> None:

        text = text.strip()

        if not text:
            return

        self.history.append(
            {
                "role": "assistant",
                "content": text
            }
        )

    def get_history(
        self
    ) -> list[dict[str, str]]:

        return list(
            self.history
        )

    def clear(
        self
    ) -> None:

        self.history.clear()

    def size(
        self
    ) -> int:

        return len(
            self.history
        )


conversation_manager = ConversationManager(
    max_messages=10
)