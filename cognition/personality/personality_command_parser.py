import re
import unicodedata

from dataclasses import dataclass

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.data.database.repositories.personality_command_repository import (
    personality_command_repository
)


@dataclass(frozen=True)
class PersonalityCommand:

    spoken_param: str
    param: str
    value: int


@dataclass(frozen=True)
class PersonalityCommandParseResult:

    is_personality_command: bool
    is_complete: bool
    command: PersonalityCommand | None = None
    missing_value: bool = False
    spoken_param: str | None = None
    param: str | None = None


class PersonalityCommandParser:

    FALLBACK_PARAMETER_ALIASES = {
        "humor": "humor",
        "sarcasmo": "sarcasm",
        "honestidade": "honesty",
        "empatia": "empathy",
        "disciplina": "discipline",
        "pragmatismo": "pragmatism",
    }

    FALLBACK_NUMBER_WORDS = {
        "zero": 0,
        "dez": 10,
        "vinte": 20,
        "trinta": 30,
        "quarenta": 40,
        "cinquenta": 50,
        "sessenta": 60,
        "setenta": 70,
        "oitenta": 80,
        "noventa": 90,
        "cem": 100,
    }

    FALLBACK_COMMAND_WORDS = (
        "ajuste",
        "defina",
        "coloque",
        "configure",
        "mude",
        "altere",
        "reduza",
        "abaixe",
        "aumente",
        "suba",
        "nivel",
        "parametro",
    )

    def parse(
        self,
        text: str
    ) -> PersonalityCommandParseResult:

        normalized = self._normalize(
            text
        )

        parameter_match = self._find_parameter(
            normalized
        )

        if not parameter_match:
            return PersonalityCommandParseResult(
                is_personality_command=False,
                is_complete=False
            )

        spoken_param = parameter_match

        parameter_aliases = self._load_parameter_aliases()

        param = parameter_aliases.get(
            spoken_param
        )

        if not param:
            return PersonalityCommandParseResult(
                is_personality_command=False,
                is_complete=False
            )

        if not self._looks_like_parameter_command(
            normalized
        ):
            return PersonalityCommandParseResult(
                is_personality_command=False,
                is_complete=False
            )

        raw_value = self._find_value(
            normalized
        )

        if raw_value is None:
            return PersonalityCommandParseResult(
                is_personality_command=True,
                is_complete=False,
                missing_value=True,
                spoken_param=spoken_param,
                param=param
            )

        value = self._parse_value(
            raw_value
        )

        if value is None:
            return PersonalityCommandParseResult(
                is_personality_command=True,
                is_complete=False,
                missing_value=True,
                spoken_param=spoken_param,
                param=param
            )

        return PersonalityCommandParseResult(
            is_personality_command=True,
            is_complete=True,
            command=PersonalityCommand(
                spoken_param=spoken_param,
                param=param,
                value=value
            )
        )

    def _load_parameter_aliases(
        self
    ) -> dict[str, str]:

        try:
            rows = (
                personality_command_repository
                .get_active_parameter_aliases()
            )

            aliases = {}

            for row in rows:
                aliases[
                    self._normalize(row["alias"])
                ] = row["parameter"]

            if aliases:
                return aliases

        except Exception as error:
            logger.exception(
                f"Falha ao carregar aliases de personalidade: {error}"
            )

        return {
            self._normalize(alias): parameter
            for alias, parameter in self.FALLBACK_PARAMETER_ALIASES.items()
        }

    def _load_number_words(
        self
    ) -> dict[str, int]:

        try:
            rows = (
                personality_command_repository
                .get_active_number_words()
            )

            number_words = {}

            for row in rows:
                number_words[
                    self._normalize(row["word"])
                ] = int(row["value"])

            if number_words:
                return number_words

        except Exception as error:
            logger.exception(
                f"Falha ao carregar números por extenso: {error}"
            )

        return {
            self._normalize(word): value
            for word, value in self.FALLBACK_NUMBER_WORDS.items()
        }

    def _load_command_words(
        self
    ) -> tuple[str, ...]:

        try:
            rows = (
                personality_command_repository
                .get_active_command_words()
            )

            words = tuple(
                self._normalize(row["word"])
                for row in rows
            )

            if words:
                return words

        except Exception as error:
            logger.exception(
                f"Falha ao carregar palavras de comando: {error}"
            )

        return tuple(
            self._normalize(word)
            for word in self.FALLBACK_COMMAND_WORDS
        )

    def _looks_like_parameter_command(
        self,
        text: str
    ) -> bool:

        command_words = self._load_command_words()

        return any(
            re.search(
                rf"\b{re.escape(word)}\b",
                text
            )
            for word in command_words
        )

    def _find_parameter(
        self,
        text: str
    ) -> str | None:

        parameter_aliases = self._load_parameter_aliases()

        normalized_aliases = sorted(
            parameter_aliases.keys(),
            key=len,
            reverse=True
        )

        for alias in normalized_aliases:

            if re.search(
                rf"\b{re.escape(alias)}\b",
                text
            ):
                return alias

        return None

    def _find_value(
        self,
        text: str
    ) -> str | None:

        number_words = self._load_number_words()

        number_patterns = sorted(
            (
                re.escape(word)
                for word in number_words.keys()
            ),
            key=len,
            reverse=True
        )

        word_pattern = "|".join(
            number_patterns
        )

        value_pattern = (
            r"\b("
            r"\d{1,3}"
            r"|"
            r"(?:"
            f"{word_pattern}"
            r")(?: e (?:"
            f"{word_pattern}"
            r"))?"
            r")\b"
            r"(?:\s*por\s*cento|\s*%)?"
        )

        matches = re.findall(
            value_pattern,
            text
        )

        if not matches:
            return None

        return matches[-1]

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

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    def _clamp(
        self,
        value: int
    ) -> int:

        return max(
            0,
            min(100, value)
        )

    def _parse_value(
        self,
        raw_value: str
    ) -> int | None:

        raw_value = self._normalize(
            raw_value
        )

        if raw_value.isdigit():
            return self._clamp(
                int(raw_value)
            )

        number_words = self._load_number_words()

        if raw_value in number_words:
            return self._clamp(
                number_words[raw_value]
            )

        if " e " in raw_value:

            parts = raw_value.split(
                " e "
            )

            if len(parts) != 2:
                return None

            ten = number_words.get(
                parts[0]
            )

            unit = number_words.get(
                parts[1]
            )

            if ten is None or unit is None:
                return None

            return self._clamp(
                ten + unit
            )

        return None
    
personality_command_parser = PersonalityCommandParser()