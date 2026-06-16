from datetime import datetime, timezone
import time

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

from cosmo.vision.analysis.vision_analyzer import (
    vision_analyzer
)

from cosmo.vision.detection.face_detector import (
    face_detector
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

        if not isinstance(
            self.warmup_frames,
            int
        ) or self.warmup_frames < 0:

            raise RuntimeError(
                "Configuração inválida: vision.warmup_frames deve ser inteiro >= 0"
            )

        if not isinstance(
            self.width,
            int
        ) or self.width <= 0:

            raise RuntimeError(
                "Configuração inválida: vision.width deve ser inteiro > 0"
            )

        if not isinstance(
            self.height,
            int
        ) or self.height <= 0:

            raise RuntimeError(
                "Configuração inválida: vision.height deve ser inteiro > 0"
            )

        if (
            not isinstance(
                self.camera_open_retries,
                int
            )
            or self.camera_open_retries <= 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.camera_open_retries deve ser inteiro > 0"
            )

        if (
            not isinstance(
                self.camera_open_retry_delay,
                int | float
            )
            or self.camera_open_retry_delay < 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.camera_open_retry_delay deve ser número >= 0"
            )

        if (
            not isinstance(
                self.frame_flush_reads,
                int
            )
            or self.frame_flush_reads <= 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.frame_flush_reads deve ser inteiro > 0"
            )

        if (
            not isinstance(
                self.frame_flush_delay,
                int | float
            )
            or self.frame_flush_delay < 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.frame_flush_delay deve ser número >= 0"
            )

        if (
            not isinstance(
                self.camera_buffer_size,
                int
            )
            or self.camera_buffer_size <= 0
        ):

            raise RuntimeError(
                "Configuração inválida: vision.camera_buffer_size deve ser inteiro > 0"
            )

        self.capture = None
        self.active = False
        self.last_error = None
        self.started_at = None
        self.last_brightness = None
        self.image_quality = "unknown"
        self.image_metrics = {}

        self.face_detection = {
            "enabled": False,
            "detection_ready": False,
            "skipped": True,
            "skip_reason": "not_initialized",
            "face_detected": False,
            "face_count": 0,
            "faces": [],
            "largest_face": None,
            "last_error": None,
        }
        
        logger.info(
            f"Vision config carregada: "
            f"camera_index={self.camera_index}, "
            f"width={self.width}, "
            f"height={self.height}, "
            f"grayscale={self.grayscale}, "
            f"snapshot_path={self.snapshot_path}, "
            f"warmup_frames={self.warmup_frames}, "
            f"camera_open_retries={self.camera_open_retries}, "
            f"camera_open_retry_delay={self.camera_open_retry_delay}, "
            f"frame_flush_reads={self.frame_flush_reads}, "
            f"frame_flush_delay={self.frame_flush_delay}, "
            f"camera_buffer_size={self.camera_buffer_size}"
        )

    def start(
        self
    ) -> bool:

        if not self.enabled:

            logger.info(
                "Vision desabilitada por configuração"
            )

            return False

        if (
            self.active
            and self.capture
            and self.capture.isOpened()
        ):

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

            self.capture.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                self.width
            )

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

            analysis = vision_analyzer.analyze(
                frame
            )

            self.image_metrics = analysis

            self.last_brightness = analysis.get(
                "brightness_mean"
            )

            self.image_quality = analysis.get(
                "image_quality",
                "unknown"
            )

            self.face_detection = face_detector.detect(
                frame,
                image_metrics=analysis
            )
            
            logger.info(
                f"Frame capturado: "
                f"brightness={analysis.get('brightness_mean', 0.0):.2f}, "
                f"contrast={analysis.get('brightness_std', 0.0):.2f}, "
                f"dark_ratio={analysis.get('dark_ratio', 0.0):.2f}, "
                f"bright_ratio={analysis.get('bright_ratio', 0.0):.2f}, "
                f"overexposed_ratio={analysis.get('overexposed_ratio', 0.0):.2f}, "
                f"blur_score={analysis.get('blur_score', 0.0):.2f}, "
                f"backlit_score={analysis.get('backlit_score', 0.0):.2f}, "
                f"quality={self.image_quality}, "
                f"face_ready={analysis.get('face_ready', False)}"
                f"face_count={self.face_detection.get('face_count', 0)}"
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
            "face_detection": self.face_detection,
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


camera_manager = CameraManager()