from collections import deque


class ConversationManager:

    def __init__(self):

        self.history = deque(
            maxlen=10
        )

    def add_user_message(
        self,
        text: str
    ):

        self.history.append(
            {
                "role": "user",
                "content": text
            }
        )

    def add_assistant_message(
        self,
        text: str
    ):

        self.history.append(
            {
                "role": "assistant",
                "content": text
            }
        )

    def get_history(self):

        return list(
            self.history
        )


conversation_manager = (
    ConversationManager()
)