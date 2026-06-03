import json

from pathlib import Path

from cosmo.core.logger.logger_manager import (
    logger
)


BASE_DIR = Path(__file__).resolve().parents[3]

STATE_DIR = (
    BASE_DIR
    / "cosmo"
    / "data"
    / "state"
)

STATE_FILE = (
    STATE_DIR
    / "personality_state.json"
)


class PersonalityPersistence:

    def load(
        self,
        active_profile: str
    ) -> dict[str, int] | None:

        if not STATE_FILE.exists():
            return None

        try:
            with STATE_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if data.get("active_profile") != active_profile:
                logger.warning(
                    "Estado de personalidade ignorado: profile diferente"
                )
                return None

            parameters = data.get(
                "parameters"
            )

            if not isinstance(parameters, dict):
                return None

            return {
                key: int(value)
                for key, value in parameters.items()
            }

        except Exception as error:
            logger.exception(
                f"Falha ao carregar estado de personalidade: {error}"
            )

            return None

    def save(
        self,
        active_profile: str,
        parameters: dict[str, int]
    ) -> None:

        try:
            STATE_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            data = {
                "active_profile": active_profile,
                "parameters": parameters
            }

            with STATE_FILE.open(
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            logger.info(
                f"Estado de personalidade salvo: {STATE_FILE}"
            )

        except Exception as error:
            logger.exception(
                f"Falha ao salvar estado de personalidade: {error}"
            )


personality_persistence = PersonalityPersistence()