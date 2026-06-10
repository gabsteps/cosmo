from datetime import datetime, timezone
import time
import numpy as np
import cv2

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.vision.camera.frame_store import (
    frame_store
)


class CameraManager:

    def __init__(
        self
    ):

        self.enabled = (
            config.get(
                "vision",
                "enabled"
            )
            is not False
        )

        self.camera_index = config.get(
            "vision",
            "camera_index"
        )

        self.width = config.get(
            "vision",
            "width"
        )

        self.height = config.get(
            "vision",
            "height"
        )

        self.grayscale = config.get(
            "vision",
            "grayscale"
        )

        self.snapshot_path = config.get(
            "vision",
            "snapshot_path"
        )

        self.warmup_frames = config.get(
            "vision",
            "warmup_frames"
        )

        self.camera_open_retries = (
            config.get(
                "vision",
                "camera_open_retries"
            )
            or 5
        )

        self.camera_open_retry_delay = (
            config.get(
                "vision",
                "camera_open_retry_delay"
            )
            or 1.0
        )

        self.frame_flush_reads = (
            config.get(
                "vision",
                "frame_flush_reads"
            )
            or 6
        )

        self.frame_flush_delay = (
            config.get(
                "vision",
                "frame_flush_delay"
            )
            or 0.03
        )

        self.camera_buffer_size = (
            config.get(
                "vision",
                "camera_buffer_size"
            )
            or 1
        )
        required_settings = {
            "vision.camera_index": self.camera_index,
            "vision.width": self.width,
            "vision.height": self.height,
            "vision.grayscale": self.grayscale,
            "vision.snapshot_path": self.snapshot_path,
            "vision.warmup_frames": self.warmup_frames,
        }

        missing_settings = [
            key
            for key, value in required_settings.items()
            if value is None
        ]

        if missing_settings:

            raise RuntimeError(
                "Configurações obrigatórias ausentes para Vision: "
                + ", ".join(
                    missing_settings
                )
            )

        if not isinstance(self.warmup_frames, int) or self.warmup_frames < 0:

            raise RuntimeError(
                "Configuração inválida: vision.warmup_frames deve ser inteiro >= 0"
            )

        if not isinstance(self.width, int) or self.width <= 0:

            raise RuntimeError(
                "Configuração inválida: vision.width deve ser inteiro > 0"
            )

        if not isinstance(self.height, int) or self.height <= 0:

            raise RuntimeError(
                "Configuração inválida: vision.height deve ser inteiro > 0"
            )

        if (
            not isinstance(self.camera_open_retries, int)
            or self.camera_open_retries <= 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.camera_open_retries deve ser inteiro > 0"
            )

        if (
            not isinstance(self.camera_open_retry_delay, int | float)
            or self.camera_open_retry_delay < 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.camera_open_retry_delay deve ser número >= 0"
            )

        self.capture = None
        self.active = False
        self.last_error = None
        self.started_at = None
        self.last_brightness = None
        self.image_quality = "unknown"
        self.image_metrics = {}

        logger.info(
            f"Vision config carregada: "
            f"camera_index={self.camera_index}, "
            f"width={self.width}, "
            f"height={self.height}, "
            f"grayscale={self.grayscale}, "
            f"snapshot_path={self.snapshot_path}, "
            f"warmup_frames={self.warmup_frames}, "
            f"camera_open_retries={self.camera_open_retries}, "
            f"camera_open_retry_delay={self.camera_open_retry_delay}"
        )

    def start(
        self
    ) -> bool:

        if not self.enabled:

            logger.info(
                "Vision desabilitada por configuração"
            )

            return False

        if self.active and self.capture and self.capture.isOpened():

            logger.info(
                "CameraManager já está ativo"
            )

            return True

        try:

            logger.info(
                f"Iniciando câmera index={self.camera_index}"
            )

            self.capture = None

            for attempt in range(
                1,
                self.camera_open_retries + 1
            ):

                logger.info(
                    f"Tentando abrir câmera index={self.camera_index} "
                    f"(tentativa {attempt}/{self.camera_open_retries})"
                )

                capture = cv2.VideoCapture(
                    self.camera_index
                )

                if capture.isOpened():

                    self.capture = capture

                    break

                capture.release()

                time.sleep(
                    self.camera_open_retry_delay
                )

            if not self.capture or not self.capture.isOpened():

                self.last_error = (
                    f"Não foi possível abrir câmera index={self.camera_index} "
                    f"após {self.camera_open_retries} tentativas"
                )

                logger.warning(
                    self.last_error
                )

                self.capture = None
                self.active = False

                return False
            
            self.capture.set(
                cv2.CAP_PROP_BUFFERSIZE,
                self.camera_buffer_size
            )

            if self.width:

                self.capture.set(
                    cv2.CAP_PROP_FRAME_WIDTH,
                    self.width
                )

            if self.height:

                self.capture.set(
                    cv2.CAP_PROP_FRAME_HEIGHT,
                    self.height
                )

            self._warmup_camera()

            self.active = True
            self.last_error = None
            self.started_at = datetime.now(
                timezone.utc
            ).isoformat()

            logger.info(
                "CameraManager online"
            )

            return True

        except Exception as error:

            self.last_error = str(
                error
            )

            self.active = False

            if self.capture:

                try:

                    self.capture.release()

                except Exception as release_error:

                    logger.warning(
                        f"Falha ao liberar câmera após erro: {release_error}"
                    )

            self.capture = None

            logger.exception(
                f"Erro ao iniciar câmera: {error}"
            )

            return False

    def stop(
        self
    ) -> None:

        if self.capture:

            try:

                self.capture.release()

            except Exception as error:

                logger.warning(
                    f"Falha ao liberar câmera: {error}"
                )

        self.capture = None
        self.active = False

        logger.info(
            "CameraManager parado"
        )

    def capture_frame(
        self
    ):

        if not self.enabled:

            self.last_error = (
                "Vision desabilitada por configuração"
            )

            return None

        if not self.active or not self.capture:

            started = self.start()

            if not started:
                return None

        try:

            ok, frame = self._read_fresh_frame()
            logger.info(
                f"Frame fresco lido após flush_reads={self.frame_flush_reads}"
            )

            if not ok or frame is None:

                self.last_error = (
                    "Falha ao capturar frame da câmera"
                )

                logger.warning(
                    self.last_error
                )

                return None

            if self.grayscale:

                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

            self.image_metrics = self._calculate_image_metrics(
                frame
            )

            self.last_brightness = self.image_metrics.get(
                "brightness_mean"
            )

            self.image_quality = self._classify_image_quality(
                self.image_metrics
            )

            logger.info(
                f"Frame capturado: "
                f"brightness={self.last_brightness:.2f}, "
                f"contrast={self.image_metrics.get('brightness_std'):.2f}, "
                f"dark_ratio={self.image_metrics.get('dark_ratio'):.2f}, "
                f"bright_ratio={self.image_metrics.get('bright_ratio'):.2f}, "
                f"overexposed_ratio={self.image_metrics.get('overexposed_ratio'):.2f}, "
                f"quality={self.image_quality}"
            )

            frame_store.set_frame(
                frame
            )

            self.last_error = None

            return frame

        except Exception as error:

            self.last_error = str(
                error
            )

            logger.exception(
                f"Erro ao capturar frame: {error}"
            )

            return None

    def save_snapshot(
        self
    ) -> str | None:

        frame = self.capture_frame()

        if frame is None:
            return None

        return frame_store.save_snapshot(
            self.snapshot_path
        )

    def is_available(
        self
    ) -> bool:

        return (
            self.enabled
            and self.active
            and self.capture is not None
            and self.capture.isOpened()
        )

    def snapshot(
        self
    ) -> dict:

        frame_snapshot = frame_store.snapshot()

        return {
            "enabled": self.enabled,
            "camera_active": self.active,
            "camera_available": self.is_available(),
            "camera_index": self.camera_index,
            "width": self.width,
            "height": self.height,
            "grayscale": self.grayscale,
            "started_at": self.started_at,
            "last_error": self.last_error,
            "last_brightness": self.last_brightness,
            "image_quality": self.image_quality,
            "image_metrics": self.image_metrics,
            "last_frame_at": frame_snapshot.get(
                "last_frame_at"
            ),
            "last_snapshot_path": frame_snapshot.get(
                "last_snapshot_path"
            ),
            "has_frame": frame_snapshot.get(
                "has_frame"
            ),
        }

    def _warmup_camera(
        self
    ) -> None:

        if not self.capture:
            return

        failed_reads = 0

        for _ in range(
            self.warmup_frames
        ):

            ok, _ = self.capture.read()

            if not ok:
                failed_reads += 1

        if failed_reads:

            logger.warning(
                f"Warmup da câmera teve {failed_reads} falhas de leitura"
            )

    def _calculate_brightness(
        self,
        frame
    ) -> float:

        if frame is None:
            return 0.0

        return float(
            frame.mean()
        )

    def _classify_image_quality(
        self,
        brightness: float
    ) -> str:

        if brightness < 10:
            return "dark"

        if brightness < 35:
            return "low_light"

        return "ok"

    def _read_fresh_frame(
        self
    ):

        if not self.capture:
            return False, None

        last_ok = False
        last_frame = None

        for _ in range(
            self.frame_flush_reads
        ):

            ok, frame = self.capture.read()

            if ok and frame is not None:

                last_ok = True
                last_frame = frame

            if self.frame_flush_delay > 0:

                time.sleep(
                    self.frame_flush_delay
                )

        return last_ok, last_frame

    def _calculate_image_metrics(
        self,
        frame
    ) -> dict:

        if frame is None:

            return {
                "brightness_mean": 0.0,
                "brightness_std": 0.0,
                "dark_ratio": 1.0,
                "bright_ratio": 0.0,
                "overexposed_ratio": 0.0,
            }

        if len(frame.shape) == 3:

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

        else:

            gray = frame

        gray = gray.astype(
            np.uint8
        )

        brightness_mean = float(
            gray.mean()
        )

        brightness_std = float(
            gray.std()
        )

        dark_ratio = float(
            np.mean(
                gray < 25
            )
        )

        bright_ratio = float(
            np.mean(
                gray > 220
            )
        )

        overexposed_ratio = float(
            np.mean(
                gray > 245
            )
        )

        return {
            "brightness_mean": brightness_mean,
            "brightness_std": brightness_std,
            "dark_ratio": dark_ratio,
            "bright_ratio": bright_ratio,
            "overexposed_ratio": overexposed_ratio,
        }

    def _classify_image_quality(
        self,
        metrics: dict
    ) -> str:

        brightness = metrics.get(
            "brightness_mean",
            0.0
        )

        contrast = metrics.get(
            "brightness_std",
            0.0
        )

        dark_ratio = metrics.get(
            "dark_ratio",
            1.0
        )

        bright_ratio = metrics.get(
            "bright_ratio",
            0.0
        )

        overexposed_ratio = metrics.get(
            "overexposed_ratio",
            0.0
        )

        if overexposed_ratio > 0.02:

            return "overexposed"

        if bright_ratio > 0.08 and dark_ratio > 0.45:

            return "high_contrast"

        if dark_ratio > 0.75:

            return "dark"

        if brightness < 35 or dark_ratio > 0.60:

            return "low_light"

        if contrast < 8:

            return "low_contrast"

        return "ok"

camera_manager = CameraManager()