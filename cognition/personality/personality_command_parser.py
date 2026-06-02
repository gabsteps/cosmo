import re
import unicodedata

from dataclasses import dataclass


@dataclass(frozen=True)
class PersonalityCommand:
    spoken_param: str
    param: str
    value: int


PARAMETER_ALIASES = {
    "verbosidade": "verbosity",
    "humor": "humor",
    "sarcasmo": "sarcasm",
    "honestidade": "honesty",
    "empatia": "empathy",
    "curiosidade": "curiosity",
    "confianca": "confidence",
    "confiança": "confidence",
    "formalidade": "formality",
    "adaptabilidade": "adaptability",
    "disciplina": "discipline",
    "imaginacao": "imagination",
    "imaginação": "imagination",
    "estabilidade emocional": "emotional_stability",
    "pragmatismo": "pragmatism",
    "otimismo": "optimism",
    "engenhosidade": "resourcefulness",
    "recursos": "resourcefulness",
    "alegria": "cheerfulness",
    "animacao": "cheerfulness",
    "animação": "cheerfulness",
    "engajamento": "engagement",
    "respeito": "respectfulness",
}


NUMBER_WORDS = {
    "zero": 0,
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "três": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "quatorze": 14,
    "catorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
    "cem": 100,
    "cento": 100,
}


TENS = {
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
}


UNITS = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "três": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
}


class PersonalityCommandParser:

    def parse(
        self,
        text: str
    ) -> PersonalityCommand | None:

        normalized = self._normalize(
            text
        )

        action_pattern = (
            r"(ajuste|ajustar|defina|definir|coloque|configure|configurar|mude|mudar|altere|alterar)"
        )

        parameter_pattern = "|".join(
            sorted(
                (
                    re.escape(self._normalize(key))
                    for key in PARAMETER_ALIASES.keys()
                ),
                key=len,
                reverse=True
            )
        )

        value_pattern = (
            r"(\d{1,3}"
            r"|zero|um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove"
            r"|dez|onze|doze|treze|quatorze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove"
            r"|vinte(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|trinta(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|quarenta(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|cinquenta(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|sessenta(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|setenta(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|oitenta(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|noventa(?: e (?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove))?"
            r"|cem|cento)"
        )

        pattern = (
            rf"{action_pattern}"
            rf".*?\b({parameter_pattern})\b"
            rf".*?\b{value_pattern}\b"
            rf"(?:\s*por\s*cento|\s*%)?"
        )

        match = re.search(
            pattern,
            normalized
        )

        if not match:
            return None

        spoken_param = match.group(2)
        raw_value = match.group(3)

        value = self._parse_value(
            raw_value
        )

        if value is None:
            return None

        param = PARAMETER_ALIASES.get(
            spoken_param
        )

        if not param:
            return None

        return PersonalityCommand(
            spoken_param=spoken_param,
            param=param,
            value=value
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

        if raw_value in NUMBER_WORDS:
            return self._clamp(
                NUMBER_WORDS[raw_value]
            )

        if " e " in raw_value:

            parts = raw_value.split(" e ")

            if len(parts) != 2:
                return None

            ten = TENS.get(
                parts[0]
            )

            unit = UNITS.get(
                parts[1]
            )

            if ten is None or unit is None:
                return None

            return self._clamp(
                ten + unit
            )

        return None

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


personality_command_parser = PersonalityCommandParser()