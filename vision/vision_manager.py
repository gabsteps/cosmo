from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.vision.camera.camera_manager import (
    camera_manager
)


class VisionManager:

    def __init__(
        self
    ):

        self.camera_manager = camera_manager

    def start(
        self
    ) -> bool:

        logger.info(
            "Iniciando VisionManager"
        )

        started = self.camera_manager.start()

        if started:

            logger.info(
                "VisionManager online"
            )

        else:

            logger.warning(
                "VisionManager não conseguiu iniciar câmera"
            )

        return started

    def stop(
        self
    ) -> None:

        logger.info(
            "Parando VisionManager"
        )

        self.camera_manager.stop()

        logger.info(
            "VisionManager parado"
        )

    def capture_frame(
        self
    ):

        return self.camera_manager.capture_frame()

    def save_snapshot(
        self
    ) -> str | None:

        return self.camera_manager.save_snapshot()

    def snapshot(
        self
    ) -> dict:

        return self.camera_manager.snapshot()

    def get_snapshot_path(
        self
    ) -> str | None:

        return self.camera_manager.snapshot_path

vision_manager = VisionManager()