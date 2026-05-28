from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import COMMAND_RECEIVED

from cosmo.core.logger.logger_manager import logger


def on_command_received(data):

    command = data.get("command")

    logger.info(f"Comando recebido: {command}")


event_bus.subscribe(
    COMMAND_RECEIVED,
    on_command_received
)