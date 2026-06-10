import asyncio

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.vision.vision_manager import (
    vision_manager
)


class VisionAutoCapture:

    def __init__(
        self
    ):

        self.running = False

    async def start(
        self
    ):

        if not vision_manager.auto_capture:

            logger.info(
                "Vision auto_capture desabilitado por configuração"
            )

            return

        if self.running:

            logger.info(
                "Vision auto_capture já está rodando"
            )

            return

        self.running = True

        logger.info(
            f"Vision auto_capture iniciado "
            f"(interval={vision_manager.capture_interval}s)"
        )

        started = await vision_manager.start()

        if not started:

            logger.warning(
                "Vision auto_capture não iniciou: câmera indisponível"
            )

            self.running = False

            return

        try:

            while self.running:

                await vision_manager.save_snapshot()

                await asyncio.sleep(
                    vision_manager.capture_interval
                )

        except asyncio.CancelledError:

            logger.info(
                "Vision auto_capture cancelado"
            )

            raise

        except Exception as error:

            logger.exception(
                f"Erro no Vision auto_capture: {error}"
            )

        finally:

            self.running = False

            await vision_manager.stop()

            logger.info(
                "Vision auto_capture encerrado"
            )

    async def stop(
        self
    ):

        self.running = False


vision_auto_capture = VisionAutoCapture()