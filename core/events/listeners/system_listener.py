from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import SYSTEM_STARTED

from cosmo.core.logger.logger_manager import logger


def on_system_started(data):

    logger.info("Sistema iniciado")


event_bus.subscribe(
    SYSTEM_STARTED,
    on_system_started
)