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
            or 1.05
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
            or 55
        )

        self.required_detection_quality = (
            config.get(
                "vision",
                "face_required_quality"
            )
            is not False
        )

        self.min_area_ratio = (
            config.get(
                "vision",
                "face_min_area_ratio"
            )
            or 0.012
        )

        self.max_center_y_ratio = (
            config.get(
                "vision",
                "face_max_center_y_ratio"
            )
            or 0.88
        )

        self.min_aspect_ratio = (
            config.get(
                "vision",
                "face_min_aspect_ratio"
            )
            or 0.70
        )

        self.max_aspect_ratio = (
            config.get(
                "vision",
                "face_max_aspect_ratio"
            )
            or 1.45
        )

        self.max_results = (
            config.get(
                "vision",
                "face_max_results"
            )
            or 3
        )

        self.eye_validation_enabled = (
            config.get(
                "vision",
                "face_eye_validation_enabled"
            )
            is True
        )

        self.required_eyes = (
            config.get(
                "vision",
                "face_required_eyes"
            )
            or 1
        )

        self.eye_scale_factor = (
            config.get(
                "vision",
                "face_eye_scale_factor"
            )
            or 1.08
        )

        self.eye_min_neighbors = (
            config.get(
                "vision",
                "face_eye_min_neighbors"
            )
            or 3
        )

        self.eye_min_size = (
            config.get(
                "vision",
                "face_eye_min_size"
            )
            or 10
        )

        self.eye_required_min_area_ratio = (
            config.get(
                "vision",
                "face_eye_required_min_area_ratio"
            )
            or 0.035
        )

        self.preprocess_enabled = (
            config.get(
                "vision",
                "face_preprocess_enabled"
            )
            is not False
        )

        self.clahe_clip_limit = (
            config.get(
                "vision",
                "face_clahe_clip_limit"
            )
            or 2.0
        )

        self.clahe_tile_grid_size = (
            config.get(
                "vision",
                "face_clahe_tile_grid_size"
            )
            or 8
        )

        self.clahe = cv2.createCLAHE(
            clipLimit=float(
                self.clahe_clip_limit
            ),
            tileGridSize=(
                int(
                    self.clahe_tile_grid_size
                ),
                int(
                    self.clahe_tile_grid_size
                )
            )
        )

        self.cascade_path = self._resolve_cascade_path()

        self.classifier = cv2.CascadeClassifier(
            str(
                self.cascade_path
            )
        )

        self.eye_cascade_path = self._resolve_eye_cascade_path()

        self.eye_classifier = cv2.CascadeClassifier(
            str(
                self.eye_cascade_path
            )
        )

        if self.classifier.empty():

            self.enabled = False

            logger.warning(
                f"FaceDetector desabilitado: cascade inválido em {self.cascade_path}"
            )

        if self.eye_validation_enabled and self.eye_classifier.empty():

            logger.warning(
                f"Validação por olhos desabilitada: eye cascade inválido em {self.eye_cascade_path}"
            )

            self.eye_validation_enabled = False

        if self.enabled:

            logger.info(
                f"FaceDetector carregado: "
                f"cascade={self.cascade_path}, "
                f"scale_factor={self.scale_factor}, "
                f"min_neighbors={self.min_neighbors}, "
                f"min_size={self.min_size}, "
                f"required_detection_quality={self.required_detection_quality}, "
                f"min_area_ratio={self.min_area_ratio}, "
                f"max_center_y_ratio={self.max_center_y_ratio}, "
                f"aspect_ratio={self.min_aspect_ratio}-{self.max_aspect_ratio}, "
                f"max_results={self.max_results}, "
                f"eye_validation_enabled={self.eye_validation_enabled}, "
                f"required_eyes={self.required_eyes}, "
                f"eye_required_min_area_ratio={self.eye_required_min_area_ratio}, "
                f"preprocess_enabled={self.preprocess_enabled}, "
                f"clahe_clip_limit={self.clahe_clip_limit}, "
                f"clahe_tile_grid_size={self.clahe_tile_grid_size}"
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

        if self.required_detection_quality:

            detection_allowed, skip_reason = self._is_detection_allowed(
                image_metrics
            )

            if not detection_allowed:

                return self._empty_result(
                    detection_ready=False,
                    skipped=True,
                    skip_reason=skip_reason
                )

        try:

            gray = self._prepare_detection_frame(
                frame
            )

            frame_height, frame_width = gray.shape[:2]
            frame_area = frame_width * frame_height

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

            raw_faces = [
                self._normalize_face(
                    face
                )
                for face in faces_raw
            ]

            accepted_faces, rejected_faces = self._filter_faces(
                raw_faces,
                gray=gray,
                frame_width=frame_width,
                frame_height=frame_height,
                frame_area=frame_area
            )

            accepted_faces.sort(
                key=lambda face: face.get(
                    "score",
                    0.0
                ),
                reverse=True
            )

            if self.max_results and self.max_results > 0:

                accepted_faces = accepted_faces[
                    : int(
                        self.max_results
                    )
                ]

            largest_face = (
                accepted_faces[0]
                if accepted_faces
                else None
            )

            logger.info(
                f"Face detection: "
                f"raw={len(raw_faces)}, "
                f"accepted={len(accepted_faces)}, "
                f"rejected={len(rejected_faces)}, "
                f"largest={largest_face}"
            )

            return {
                "enabled": True,
                "detection_ready": True,
                "skipped": False,
                "skip_reason": None,
                "face_detected": bool(
                    accepted_faces
                ),
                "face_count": len(
                    accepted_faces
                ),
                "raw_face_count": len(
                    raw_faces
                ),
                "filtered_out_count": len(
                    rejected_faces
                ),
                "faces": accepted_faces,
                "raw_faces": raw_faces,
                "rejected_faces": rejected_faces,
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

    def _is_detection_allowed(
        self,
        image_metrics: dict
    ) -> tuple[bool, str | None]:

        image_quality = image_metrics.get(
            "image_quality",
            "unknown"
        )

        blocked_qualities = {
            "unusable_dark",
            "dark",
            "overexposed",
            "blurred",
            "unavailable",
            "error",
        }

        if image_quality in blocked_qualities:

            return (
                False,
                f"blocked_quality:{image_quality}"
            )

        brightness = float(
            image_metrics.get(
                "brightness_mean",
                0.0
            )
            or 0.0
        )

        dark_ratio = float(
            image_metrics.get(
                "dark_ratio",
                1.0
            )
            or 0.0
        )

        blur_score = float(
            image_metrics.get(
                "blur_score",
                0.0
            )
            or 0.0
        )

        if brightness < 25:

            return (
                False,
                "brightness_too_low"
            )

        if dark_ratio > 0.80:

            return (
                False,
                "too_dark"
            )

        if blur_score < 45:

            return (
                False,
                "too_blurred_for_detection"
            )

        return (
            True,
            None
        )

    def _filter_faces(
        self,
        faces: list[dict],
        gray,
        frame_width: int,
        frame_height: int,
        frame_area: int
    ) -> tuple[list[dict], list[dict]]:

        if not faces:

            return (
                [],
                []
            )

        accepted_faces = []
        rejected_faces = []

        for face in faces:

            filter_reason = self._get_filter_reason(
                face,
                frame_width=frame_width,
                frame_height=frame_height,
                frame_area=frame_area
            )

            if filter_reason:

                self._reject_face(
                    face,
                    filter_reason
                )

                logger.info(
                    f"Face rejeitada: reason={filter_reason}, "
                    f"x={face.get('x')}, "
                    f"y={face.get('y')}, "
                    f"width={face.get('width')}, "
                    f"height={face.get('height')}, "
                    f"area={face.get('area')}"
                ) 

                rejected_faces.append(
                    face
                )

                continue

            eyes_valid, eye_count, eye_reason = self._validate_face_eyes(
                gray,
                face,
                frame_area=frame_area
            )

            face["eye_count"] = eye_count
            face["eye_detected"] = eye_count > 0
            face["eye_validation_reason"] = eye_reason

            if not eyes_valid:

                self._reject_face(
                    face,
                    eye_reason or "eye_validation_failed"
                )

                logger.info(
                    f"Face rejeitada: reason={eye_reason}, "
                    f"eye_count={eye_count}, "
                    f"x={face.get('x')}, "
                    f"y={face.get('y')}, "
                    f"width={face.get('width')}, "
                    f"height={face.get('height')}, "
                    f"area={face.get('area')}"
                )


                rejected_faces.append(
                    face
                )

                continue

            face["filtered"] = False
            face["filter_reason"] = None
            face["score"] = self._score_face(
                face,
                frame_width=frame_width,
                frame_height=frame_height
            )

            accepted_faces.append(
                face
            )

        return (
            accepted_faces,
            rejected_faces
        )

    def _get_filter_reason(
        self,
        face: dict,
        frame_width: int,
        frame_height: int,
        frame_area: int
    ) -> str | None:

        area_ratio = face.get(
            "area",
            0
        ) / max(
            frame_area,
            1
        )

        center_y_ratio = face.get(
            "center_y",
            0
        ) / max(
            frame_height,
            1
        )

        aspect_ratio = face.get(
            "width",
            0
        ) / max(
            face.get(
                "height",
                1
            ),
            1
        )

        if area_ratio < self.min_area_ratio:

            return "area_too_small"

        if center_y_ratio > self.max_center_y_ratio:

            return "too_low_in_frame"

        if aspect_ratio < self.min_aspect_ratio:

            return "too_narrow"

        if aspect_ratio > self.max_aspect_ratio:

            return "too_wide"

        return None

    def _validate_face_eyes(
        self,
        gray,
        face: dict,
        frame_area: int
    ) -> tuple[bool, int, str | None]:

        if not self.eye_validation_enabled:

            return (
                True,
                0,
                None
            )

        if self.eye_classifier.empty():

            return (
                True,
                0,
                "eye_validation_unavailable"
            )

        x = int(
            face.get(
                "x",
                0
            )
        )

        y = int(
            face.get(
                "y",
                0
            )
        )

        width = int(
            face.get(
                "width",
                0
            )
        )

        height = int(
            face.get(
                "height",
                0
            )
        )

        if width <= 0 or height <= 0:

            return (
                False,
                0,
                "invalid_face_roi"
            )

        face_area_ratio = face.get(
            "area",
            0
        ) / max(
            frame_area,
            1
        )

        if face_area_ratio < self.eye_required_min_area_ratio:

            return (
                True,
                0,
                "eye_validation_skipped_small_face"
            )

        roi = gray[
            y:y + height,
            x:x + width
        ]

        if roi.size == 0:

            return (
                False,
                0,
                "empty_face_roi"
            )

        upper_roi = roi[
            : max(
                int(
                    height * 0.62
                ),
                1
            ),
            :
        ]

        eyes = self.eye_classifier.detectMultiScale(
            upper_roi,
            scaleFactor=float(
                self.eye_scale_factor
            ),
            minNeighbors=int(
                self.eye_min_neighbors
            ),
            minSize=(
                int(
                    self.eye_min_size
                ),
                int(
                    self.eye_min_size
                )
            )
        )

        eye_count = len(
            eyes
        )

        if eye_count >= int(
            self.required_eyes
        ):

            return (
                True,
                eye_count,
                None
            )

        return (
            False,
            eye_count,
            "no_eyes_detected"
        )

    def _score_face(
        self,
        face: dict,
        frame_width: int,
        frame_height: int
    ) -> float:

        area_ratio = face.get(
            "area",
            0
        ) / max(
            frame_width * frame_height,
            1
        )

        center_x_ratio = face.get(
            "center_x",
            0
        ) / max(
            frame_width,
            1
        )

        center_y_ratio = face.get(
            "center_y",
            0
        ) / max(
            frame_height,
            1
        )

        horizontal_center_bonus = 1.0 - abs(
            center_x_ratio - 0.5
        )

        vertical_center_bonus = 1.0 - abs(
            center_y_ratio - 0.38
        )

        eye_bonus = 0.0

        if face.get(
            "eye_count",
            0
        ) >= 1:

            eye_bonus = 2.0

        score = (
            area_ratio * 100.0
            + horizontal_center_bonus * 2.0
            + vertical_center_bonus * 2.0
            + eye_bonus
        )

        face["area_ratio"] = area_ratio
        face["center_x_ratio"] = center_x_ratio
        face["center_y_ratio"] = center_y_ratio

        return float(
            score
        )

    def _reject_face(
        self,
        face: dict,
        reason: str
    ) -> None:

        face["filtered"] = True
        face["filter_reason"] = reason
        face["score"] = 0.0

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

    def _resolve_eye_cascade_path(
        self
    ) -> Path:

        configured_path = config.get(
            "vision",
            "face_eye_cascade_path"
        )

        if configured_path:

            path = Path(
                configured_path
            )

            if path.exists():

                return path

            logger.warning(
                f"face_eye_cascade_path configurado não encontrado: {configured_path}"
            )

        return Path(
            cv2.data.haarcascades
        ) / "haarcascade_eye.xml"

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

    def _prepare_detection_frame(
        self,
        frame
    ):

        gray = self._to_grayscale(
            frame
        )

        if not self.preprocess_enabled:

            return gray

        try:

            return self.clahe.apply(
                gray
            )

        except Exception as error:

            logger.warning(
                f"Falha ao aplicar CLAHE na detecção facial: {error}"
            )

            return gray

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
            "score": 0.0,
            "area_ratio": 0.0,
            "center_x_ratio": 0.0,
            "center_y_ratio": 0.0,
            "eye_count": 0,
            "eye_detected": False,
            "eye_validation_reason": None,
            "filtered": False,
            "filter_reason": None,
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
            "raw_face_count": 0,
            "filtered_out_count": 0,
            "faces": [],
            "raw_faces": [],
            "rejected_faces": [],
            "largest_face": None,
            "last_error": last_error,
        }


face_detector = FaceDetector()