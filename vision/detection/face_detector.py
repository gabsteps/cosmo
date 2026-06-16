from pathlib import Path

import cv2

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.logger.logger_manager import (
    logger
)


class FaceDetector:

    def __init__(
        self
    ):

        self.enabled = (
            config.get(
                "vision",
                "face_detection_enabled"
            )
            is not False
        )

        self.scale_factor = (
            config.get(
                "vision",
                "face_scale_factor"
            )
            or 1.1
        )

        self.min_neighbors = (
            config.get(
                "vision",
                "face_min_neighbors"
            )
            or 5
        )

        self.min_size = (
            config.get(
                "vision",
                "face_min_size"
            )
            or 60
        )

        self.required_face_ready = (
            config.get(
                "vision",
                "face_required_quality"
            )
            is not False
        )

        self.cascade_path = self._resolve_cascade_path()

        self.classifier = cv2.CascadeClassifier(
            str(
                self.cascade_path
            )
        )

        if self.classifier.empty():

            self.enabled = False

            logger.warning(
                f"FaceDetector desabilitado: cascade inválido em {self.cascade_path}"
            )

        else:

            logger.info(
                f"FaceDetector carregado: "
                f"cascade={self.cascade_path}, "
                f"scale_factor={self.scale_factor}, "
                f"min_neighbors={self.min_neighbors}, "
                f"min_size={self.min_size}, "
                f"required_face_ready={self.required_face_ready}"
            )

    def detect(
        self,
        frame,
        image_metrics: dict | None = None
    ) -> dict:

        if not self.enabled:

            return self._empty_result(
                enabled=False,
                detection_ready=False,
                skipped=True,
                skip_reason="disabled",
                last_error="Face detection desabilitada"
            )

        if frame is None:

            return self._empty_result(
                detection_ready=False,
                skipped=True,
                skip_reason="missing_frame",
                last_error="Frame ausente"
            )

        image_metrics = image_metrics or {}

        if (
            self.required_face_ready
            and image_metrics.get(
                "face_ready"
            )
            is not True
        ):

            return self._empty_result(
                detection_ready=False,
                skipped=True,
                skip_reason="image_not_face_ready"
            )

        try:

            gray = self._to_grayscale(
                frame
            )

            faces_raw = self.classifier.detectMultiScale(
                gray,
                scaleFactor=float(
                    self.scale_factor
                ),
                minNeighbors=int(
                    self.min_neighbors
                ),
                minSize=(
                    int(
                        self.min_size
                    ),
                    int(
                        self.min_size
                    )
                )
            )

            faces = [
                self._normalize_face(
                    face
                )
                for face in faces_raw
            ]

            faces.sort(
                key=lambda face: face.get(
                    "area",
                    0
                ),
                reverse=True
            )

            largest_face = (
                faces[0]
                if faces
                else None
            )

            return {
                "enabled": True,
                "detection_ready": True,
                "skipped": False,
                "skip_reason": None,
                "face_detected": bool(
                    faces
                ),
                "face_count": len(
                    faces
                ),
                "faces": faces,
                "largest_face": largest_face,
                "last_error": None,
            }

        except Exception as error:

            logger.exception(
                f"Erro na detecção facial: {error}"
            )

            return self._empty_result(
                detection_ready=False,
                skipped=False,
                skip_reason=None,
                last_error=str(
                    error
                )
            )

    def _resolve_cascade_path(
        self
    ) -> Path:

        configured_path = config.get(
            "vision",
            "face_cascade_path"
        )

        if configured_path:

            path = Path(
                configured_path
            )

            if path.exists():

                return path

            logger.warning(
                f"face_cascade_path configurado não encontrado: {configured_path}"
            )

        return Path(
            cv2.data.haarcascades
        ) / "haarcascade_frontalface_default.xml"

    def _to_grayscale(
        self,
        frame
    ):

        if len(
            frame.shape
        ) == 3:

            return cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

        return frame

    def _normalize_face(
        self,
        face
    ) -> dict:

        x, y, width, height = [
            int(
                value
            )
            for value in face
        ]

        area = int(
            width * height
        )

        return {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "area": area,
            "center_x": int(
                x + width / 2
            ),
            "center_y": int(
                y + height / 2
            ),
        }

    def _empty_result(
        self,
        enabled: bool = True,
        detection_ready: bool = True,
        skipped: bool = False,
        skip_reason: str | None = None,
        last_error: str | None = None
    ) -> dict:

        return {
            "enabled": enabled,
            "detection_ready": detection_ready,
            "skipped": skipped,
            "skip_reason": skip_reason,
            "face_detected": False,
            "face_count": 0,
            "faces": [],
            "largest_face": None,
            "last_error": last_error,
        }


face_detector = FaceDetector()