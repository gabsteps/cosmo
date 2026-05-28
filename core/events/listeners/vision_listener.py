from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    USER_RECOGNIZED,
    FACE_UNKNOWN
)

from cosmo.core.logger.logger_manager import logger


def on_user_recognized(data):

    user_name = data.get("name")

    logger.info(f"Usuário reconhecido: {user_name}")


def on_unknown_face(data):

    logger.info("Rosto desconhecido detectado")


event_bus.subscribe(
    USER_RECOGNIZED,
    on_user_recognized
)

event_bus.subscribe(
    FACE_UNKNOWN,
    on_unknown_face
)