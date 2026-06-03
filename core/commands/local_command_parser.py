import unicodedata

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.data.database.repositories.local_command_repository import (
    local_command_repository
)


class LocalCommandParser:

    def __init__(self):

        self.fallback_commands = {
            "diagnostico": "system_status",
            "diagnóstico": "system_status",
            "status": "system_status",
            "estado": "system_status",
            "relatorio": "system_status",
            "relatório": "system_status",
            "o que voce lembra sobre mim": "memory_list",
            "o que você lembra sobre mim": "memory_list",
            "listar memorias": "memory_list",
            "listar memórias": "memory_list",
            "limpar memorias": "memory_clear",
            "limpar memórias": "memory_clear",
            "esqueca tudo sobre mim": "memory_clear",
            "esqueça tudo sobre mim": "memory_clear",
        }

    def parse(
        self,
        text: str
    ) -> str | None:

        normalized = self._normalize(
            text
        )

        command = self._parse_from_database(
            normalized
        )

        if command:
            return command

        return self._parse_from_fallback(
            normalized
        )

    def _parse_from_database(
        self,
        normalized_text: str
    ) -> str | None:

        try:
            commands = (
                local_command_repository
                .get_active_commands()
            )

            for command in commands:

                phrase = self._normalize(
                    command["phrase"]
                )

                if normalized_text == phrase:
                    return command["intent"]

            return None

        except Exception as error:

            logger.exception(
                f"Falha ao consultar comandos locais no banco: {error}"
            )

            return None

    def _parse_from_fallback(
        self,
        normalized_text: str
    ) -> str | None:

        for phrase, intent in self.fallback_commands.items():

            if normalized_text == self._normalize(
                phrase
            ):
                return intent

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

        return text


local_command_parser = LocalCommandParser()