from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED

from cosmo.core.logger.logger_manager import logger


def on_wake_word_detected(data):

    word = data.get("word")

    logger.info(f"Wake word detectada: {word}")


event_bus.subscribe(
    WAKE_WORD_DETECTED,
    on_wake_word_detected
)