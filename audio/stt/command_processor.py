from cosmo.core.logger.logger_manager import logger

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    USER_SPEECH_RECEIVED
)


class CommandProcessor:

    def __init__(self):

        event_bus.subscribe(
            USER_SPEECH_RECEIVED,
            self.process_command
        )

    def process_command(self, data):

        text = data["text"]

        logger.info(
            f"Processando comando: {text}"
        )

        # Comandos iniciais simples
        if "horas" in text:

            logger.info(
                "Usuário perguntou horário"
            )

        elif "nome" in text:

            logger.info(
                "Usuário perguntou nome"
            )

        else:

            logger.info(
                "Comando desconhecido"
            )


command_processor = CommandProcessor()