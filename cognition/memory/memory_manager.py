# cosmo/cognition/memory/memory_manager.py

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.data.database.repositories.user_repository import (
    user_repository
)

from cosmo.data.database.repositories.memory_repository import (
    memory_repository
)

from cosmo.data.database.repositories.conversation_repository import (
    conversation_repository
)

from cosmo.cognition.memory.memory_extractor import (
    memory_extractor
)

from cosmo.cognition.memory.memory_filter import (
    memory_filter
)


class MemoryManager:

    def __init__(
        self
    ):

        self.default_user_name = "Gabriel"

        self.default_user = user_repository.get_or_create_user(
            name=self.default_user_name,
            trust_level=10
        )

        self.default_user_id = self.default_user["id"]

    def process_interaction(
        self,
        user_text: str,
        assistant_text: str,
        save_conversation: bool = True,
        extract_memories: bool = True
    ) -> None:

        user_text = user_text.strip()
        assistant_text = assistant_text.strip()

        if not user_text or not assistant_text:
            return

        if save_conversation:
            self.save_conversation(
                user_text=user_text,
                assistant_text=assistant_text
            )

        if extract_memories:
            self.extract_and_save_memories(
                user_text=user_text,
                assistant_text=assistant_text
            )

    def save_conversation(
        self,
        user_text: str,
        assistant_text: str
    ) -> None:

        conversation_repository.add_message(
            user_id=self.default_user_id,
            role="user",
            message=user_text
        )

        conversation_repository.add_message(
            user_id=self.default_user_id,
            role="assistant",
            message=assistant_text
        )

    def extract_and_save_memories(
        self,
        user_text: str,
        assistant_text: str
    ) -> None:

        candidates = memory_extractor.extract(
            user_text=user_text,
            assistant_text=assistant_text
        )

        for candidate in candidates:

            if not memory_filter.is_valid(
                candidate
            ):
                logger.info(
                    f"Memória descartada pelo filtro: {candidate}"
                )
                continue

            saved = memory_repository.add_memory_if_new(
                user_id=self.default_user_id,
                category=candidate["category"],
                content=candidate["content"],
                importance=candidate["importance"]
            )

            if saved:
                logger.info(
                    f"Memória persistente salva: {candidate['content']}"
                )

    def build_memory_context(
        self,
        user_text: str,
        limit: int = 5
    ) -> str:

        memories = memory_repository.get_recent_memories(
            user_id=self.default_user_id,
            limit=limit
        )

        if not memories:
            return ""

        lines = []

        for memory in memories:
            lines.append(
                f"- [{memory['category']}] {memory['content']}"
            )

        return "\n".join(
            lines
        )

    def get_recent_memories(
        self,
        limit: int = 10
    ) -> list:

        return memory_repository.get_recent_memories(
            user_id=self.default_user_id,
            limit=limit
        )

    def clear_user_memory(
        self
    ) -> None:

        memories = memory_repository.get_user_memories(
            self.default_user_id
        )

        for memory in memories:
            memory_repository.delete_memory(
                memory["id"]
            )

    def list_memory_context(
        self,
        limit: int = 10
    ) -> str:

        memories = self.get_recent_memories(
            limit=limit
        )

        if not memories:
            return (
                "Não tenho memórias persistentes registradas sobre você."
            )

        lines = []

        for memory in memories:
            lines.append(
                f"- [{memory['category']}] {memory['content']}"
            )

        return "\n".join(
            lines
        )


    def clear_all_memories(
        self
    ) -> int:

        memories = memory_repository.get_user_memories(
            self.default_user_id
        )

        count = len(
            memories
        )

        for memory in memories:
            memory_repository.delete_memory(
                memory["id"]
            )

        return count

memory_manager = MemoryManager()