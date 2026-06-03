# cosmo/cognition/memory/memory_filter.py

import unicodedata

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.data.database.repositories.memory_filter_repository import (
    memory_filter_repository
)


class MemoryFilter:

    FALLBACK_BLOCKED_TERMS = (
        "senha",
        "password",
        "cartao",
        "cpf",
        "rg",
        "documento",
        "endereco",
        "rua",
        "numero da casa",
        "diagnostico medico",
        "doenca",
        "religiao",
        "partido politico",
    )

    FALLBACK_NOISE_MARKERS = (
        "ha",
        "hum",
        "e e",
        "nao sei",
        "sei la",
        "deixa",
        "esquece",
        "cancelar",
    )

    FALLBACK_MIN_CONTENT_LENGTH = 12

    def is_valid(
        self,
        memory: dict
    ) -> bool:

        content = memory.get(
            "content",
            ""
        ).strip()

        min_content_length = self._get_min_content_length()

        if len(content) < min_content_length:
            return False

        normalized = self._normalize(
            content
        )

        if any(
            blocked in normalized
            for blocked in self._get_blocked_terms()
        ):
            return False

        if self._looks_like_stt_noise(
            normalized
        ):
            return False

        return True

    def _looks_like_stt_noise(
        self,
        text: str
    ) -> bool:

        return text in self._get_noise_markers()

    def _get_blocked_terms(
        self
    ) -> tuple[str, ...]:

        try:
            rows = memory_filter_repository.get_blocked_terms()

            terms = tuple(
                self._normalize(row["term"])
                for row in rows
            )

            if terms:
                return terms

        except Exception as error:
            logger.exception(
                f"Falha ao carregar termos bloqueados de memória: {error}"
            )

        return self.FALLBACK_BLOCKED_TERMS

    def _get_noise_markers(
        self
    ) -> tuple[str, ...]:

        try:
            rows = memory_filter_repository.get_noise_markers()

            markers = tuple(
                self._normalize(row["marker"])
                for row in rows
            )

            if markers:
                return markers

        except Exception as error:
            logger.exception(
                f"Falha ao carregar marcadores de ruído de memória: {error}"
            )

        return self.FALLBACK_NOISE_MARKERS

    def _get_min_content_length(
        self
    ) -> int:

        try:
            value = memory_filter_repository.get_setting(
                "min_content_length",
                default=self.FALLBACK_MIN_CONTENT_LENGTH
            )

            return int(
                value
            )

        except Exception as error:
            logger.exception(
                f"Falha ao carregar min_content_length: {error}"
            )

            return self.FALLBACK_MIN_CONTENT_LENGTH

    def _normalize(
        self,
        text: str
    ) -> str:

        text = text.lower().strip()

        text = unicodedata.normalize(
            "NFD",
            text
        )

        text = "".join(
            char
            for char in text
            if unicodedata.category(char) != "Mn"
        )

        return text


memory_filter = MemoryFilter()