from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    VISION_STARTED,
    VISION_STOPPED,
    VISION_FRAME_CAPTURED,
    VISION_ERROR
)

from cosmo.vision.camera.camera_manager import (
    camera_manager
)


class VisionManager:

    def __init__(
        self
    ):

        self.camera_manager = camera_manager

        self.auto_capture = (
            config.get(
                "vision",
                "auto_capture"
            )
            is True
        )

        self.capture_interval = (
            config.get(
                "vision",
                "capture_interval"
            )
            or 10
        )

    async def start(
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

            await async_event_bus.emit(
                VISION_STARTED,
                {
                    "camera_index": self.camera_manager.camera_index
                },
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

        else:

            logger.warning(
                "VisionManager não conseguiu iniciar câmera"
            )

            await async_event_bus.emit(
                VISION_ERROR,
                {
                    "error": self.camera_manager.last_error
                },
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

        return started

    async def stop(
        self
    ) -> None:

        logger.info(
            "Parando VisionManager"
        )

        self.camera_manager.stop()

        await async_event_bus.emit(
            VISION_STOPPED,
            {},
            priority=async_event_bus.PRIORITY_BACKGROUND
        )

        logger.info(
            "VisionManager parado"
        )

    def capture_frame(
        self
    ):

        return self.camera_manager.capture_frame()

    async def save_snapshot(
        self
    ) -> str | None:

        snapshot_path = self.camera_manager.save_snapshot()

        if snapshot_path:

            await async_event_bus.emit(
                VISION_FRAME_CAPTURED,
                {
                    "snapshot_path": snapshot_path,
                    "brightness": self.camera_manager.last_brightness,
                    "image_quality": self.camera_manager.image_quality,
                },
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

        else:

            await async_event_bus.emit(
                VISION_ERROR,
                {
                    "error": self.camera_manager.last_error
                },
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

        return snapshot_path

    def get_snapshot_path(
        self
    ) -> str | None:

        return self.camera_manager.snapshot_path

    def snapshot(
        self
    ) -> dict:

        camera_snapshot = self.camera_manager.snapshot()

        return {
            **camera_snapshot,
            "auto_capture": self.auto_capture,
            "capture_interval": self.capture_interval,
        }


vision_manager = VisionManager()