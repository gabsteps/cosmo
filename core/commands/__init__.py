import unicodedata


class LocalCommandParser:

    def parse(
        self,
        text: str
    ) -> str | None:

        normalized = self._normalize(
            text
        )

        if self._is_status_command(
            normalized
        ):
            return "system_status"

        return None

    def _is_status_command(
        self,
        text: str
    ) -> bool:

        status_terms = (
            "status",
            "estado",
            "diagnostico",
            "diagnóstico",
            "relatorio",
            "relatório",
        )

        system_terms = (
            "sistema",
            "cosmo",
            "operacional",
            "runtime",
        )

        has_status = any(
            term in text
            for term in status_terms
        )

        has_system = any(
            term in text
            for term in system_terms
        )

        return has_status and has_system

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