# cosmo/cognition/memory/memory_extractor.py


class MemoryExtractor:

    def extract(
        self,
        user_text: str,
        assistant_text: str | None = None
    ) -> list[dict]:

        original = user_text.strip()
        text = original.lower()

        memories = []

        if not text:
            return memories

        if self._is_preference(text):
            memories.append(
                {
                    "category": "preference",
                    "content": f"Preferência do usuário: {original}",
                    "importance": 3,
                }
            )

        if self._is_persistent_instruction(text):
            memories.append(
                {
                    "category": "instruction",
                    "content": f"Instrução persistente do usuário: {original}",
                    "importance": 4,
                }
            )

        if self._is_project_fact(text):
            memories.append(
                {
                    "category": "project_fact",
                    "content": f"Fato sobre o projeto Cosmo: {original}",
                    "importance": 3,
                }
            )

        if self._is_explicit_memory(text):
            memories.append(
                {
                    "category": "explicit",
                    "content": self._clean_explicit_memory(original),
                    "importance": 5,
                }
            )

        return memories

    def _is_preference(
        self,
        text: str
    ) -> bool:

        markers = (
            "eu prefiro",
            "prefiro",
            "gosto que você",
            "gosto quando você",
            "não gosto que você",
            "não gosto quando você",
            "me responda sempre",
            "responda sempre",
        )

        return any(
            marker in text
            for marker in markers
        )

    def _is_persistent_instruction(
        self,
        text: str
    ) -> bool:

        markers = (
            "de agora em diante",
            "a partir de agora",
            "daqui pra frente",
            "sempre que",
            "quando eu pedir",
            "nas próximas conversas",
        )

        return any(
            marker in text
            for marker in markers
        )

    def _is_project_fact(
        self,
        text: str
    ) -> bool:

        markers = (
            "no projeto cosmo",
            "o cosmo deve",
            "o cosmo vai",
            "o cosmo precisa",
            "o objetivo do cosmo",
            "a arquitetura do cosmo",
            "o fluxo do cosmo",
        )

        return any(
            marker in text
            for marker in markers
        )

    def _is_explicit_memory(
        self,
        text: str
    ) -> bool:

        markers = (
            "lembre que",
            "lembre-se que",
            "guarde que",
            "salve que",
            "registre que",
        )

        return any(
            marker in text
            for marker in markers
        )

    def _clean_explicit_memory(
        self,
        text: str
    ) -> str:

        replacements = (
            "lembre-se que",
            "lembre que",
            "guarde que",
            "salve que",
            "registre que",
        )

        cleaned = text.strip()

        lowered = cleaned.lower()

        for marker in replacements:
            if lowered.startswith(marker):
                return cleaned[len(marker):].strip().capitalize()

        return cleaned


memory_extractor = MemoryExtractor()