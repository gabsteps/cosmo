import cv2
import numpy as np


class VisionAnalyzer:

    def __init__(
        self
    ):

        self.dark_threshold = 25
        self.bright_threshold = 220
        self.overexposed_threshold = 245

        self.blur_threshold = 80.0
        self.low_contrast_threshold = 8.0

    def analyze(
        self,
        frame
    ) -> dict:

        if frame is None:

            return self._empty_analysis()

        gray = self._to_grayscale(
            frame
        )

        metrics = self._calculate_metrics(
            gray
        )

        metrics["image_quality"] = self._classify_image_quality(
            metrics
        )

        metrics["face_ready"] = self._is_face_ready(
            metrics
        )

        return metrics

    def _empty_analysis(
        self
    ) -> dict:

        return {
            "brightness_mean": 0.0,
            "brightness_std": 0.0,
            "dark_ratio": 1.0,
            "bright_ratio": 0.0,
            "overexposed_ratio": 0.0,
            "blur_score": 0.0,
            "backlit_score": 0.0,
            "image_quality": "unavailable",
            "face_ready": False,
        }

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

    def _calculate_metrics(
        self,
        gray
    ) -> dict:

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
                gray < self.dark_threshold
            )
        )

        bright_ratio = float(
            np.mean(
                gray > self.bright_threshold
            )
        )

        overexposed_ratio = float(
            np.mean(
                gray > self.overexposed_threshold
            )
        )

        blur_score = self._calculate_blur_score(
            gray
        )

        backlit_score = self._calculate_backlit_score(
            gray
        )

        return {
            "brightness_mean": brightness_mean,
            "brightness_std": brightness_std,
            "dark_ratio": dark_ratio,
            "bright_ratio": bright_ratio,
            "overexposed_ratio": overexposed_ratio,
            "blur_score": blur_score,
            "backlit_score": backlit_score,
        }

    def _calculate_blur_score(
        self,
        gray
    ) -> float:

        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F
        )

        return float(
            laplacian.var()
        )

    def _calculate_backlit_score(
        self,
        gray
    ) -> float:

        height, width = gray.shape[:2]

        if height <= 0 or width <= 0:

            return 0.0

        center_y_start = int(
            height * 0.25
        )

        center_y_end = int(
            height * 0.75
        )

        center_x_start = int(
            width * 0.25
        )

        center_x_end = int(
            width * 0.75
        )

        center = gray[
            center_y_start:center_y_end,
            center_x_start:center_x_end
        ]

        border_top = gray[
            :center_y_start,
            :
        ]

        border_bottom = gray[
            center_y_end:,
            :
        ]

        border_left = gray[
            center_y_start:center_y_end,
            :center_x_start
        ]

        border_right = gray[
            center_y_start:center_y_end,
            center_x_end:
        ]

        border_parts = [
            part.flatten()
            for part in [
                border_top,
                border_bottom,
                border_left,
                border_right,
            ]
            if part.size > 0
        ]

        if not border_parts or center.size <= 0:

            return 0.0

        border = np.concatenate(
            border_parts
        )

        center_mean = float(
            center.mean()
        )

        border_mean = float(
            border.mean()
        )

        return max(
            border_mean - center_mean,
            0.0
        )

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

        blur_score = metrics.get(
            "blur_score",
            0.0
        )

        backlit_score = metrics.get(
            "backlit_score",
            0.0
        )

        if dark_ratio >= 0.98 or brightness <= 3:

            return "unusable_dark"

        if dark_ratio > 0.75:

            return "dark"

        if brightness < 35 or dark_ratio > 0.60:

            return "low_light"

        if overexposed_ratio > 0.08:

            return "overexposed"

        if backlit_score > 45 and bright_ratio > 0.04:

            return "backlit"

        if bright_ratio > 0.08 and dark_ratio > 0.45:

            return "high_contrast"

        if overexposed_ratio > 0.02:

            return "partially_overexposed"

        if contrast < self.low_contrast_threshold:

            return "low_contrast"

        if blur_score < self.blur_threshold:

            return "blurred"

        return "ok"

    def _is_face_ready(
        self,
        metrics: dict
    ) -> bool:

        image_quality = metrics.get(
            "image_quality",
            "unknown"
        )

        if image_quality not in {
            "ok",
            "partially_overexposed",
        }:

            return False

        brightness = metrics.get(
            "brightness_mean",
            0.0
        )

        contrast = metrics.get(
            "brightness_std",
            0.0
        )

        blur_score = metrics.get(
            "blur_score",
            0.0
        )

        dark_ratio = metrics.get(
            "dark_ratio",
            1.0
        )

        overexposed_ratio = metrics.get(
            "overexposed_ratio",
            0.0
        )

        return (
            brightness >= 35
            and contrast >= self.low_contrast_threshold
            and blur_score >= self.blur_threshold
            and dark_ratio <= 0.60
            and overexposed_ratio <= 0.04
        )


vision_analyzer = VisionAnalyzer()