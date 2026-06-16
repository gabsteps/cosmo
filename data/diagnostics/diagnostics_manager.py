from datetime import datetime, timezone

from cosmo.core.runtime.runtime_state import runtime_state

from cosmo.core.events.async_event_bus import async_event_bus

from cosmo.cognition.conversation.conversation_manager import conversation_manager

from cosmo.cognition.personality.personality_state import personality_state

from cosmo.core.system.system_monitor import system_monitor

from cosmo.data.database.repositories.database_metrics_repository import (
    database_metrics_repository
)

from cosmo.vision.vision_manager import (
    vision_manager
)


class DiagnosticsManager:

    def snapshot(
        self
    ) -> dict:

        return {
            "timestamp": self._timestamp(),
            "runtime": runtime_state.snapshot(),
            "event_bus": async_event_bus.get_metrics(),
            "conversation": self._conversation_snapshot(),
            "personality": self._personality_snapshot(),
            "vision": self._vision_snapshot(),
        }

    def compact_snapshot(
        self
    ) -> dict:

        runtime = runtime_state.snapshot()
        event_bus = async_event_bus.get_metrics()
        system = system_monitor.snapshot()
        uptime_seconds = runtime_state.uptime_seconds()
        database = database_metrics_repository.get_metrics()

        return {
            "timestamp": self._timestamp(),
            "system": system,
            "mode": runtime.get(
                "mode"
            ),
            "previous_mode": runtime.get(
                "previous_mode"
            ),
            "tts_active": runtime.get(
                "tts_active"
            ),
            "llm_active": runtime.get(
                "llm_active"
            ),
            "capture_active": runtime.get(
                "capture_active"
            ),
            "conversation_size": conversation_manager.size(),
            "queue_size": event_bus.get(
                "current_queue_size"
            ),
            "events_received": event_bus.get(
                "events_received"
            ),
            "events_completed": event_bus.get(
                "events_completed"
            ),
            "events_no_listeners": event_bus.get(
                "events_no_listeners"
            ),
            "events_failed": event_bus.get(
                "events_failed"
            ),
            "listener_timeouts": event_bus.get(
                "listener_timeouts"
            ),
            "listener_errors": event_bus.get(
                "listener_errors"
            ),
            "last_error": runtime.get(
                "last_error"
            ),
            "uptime_seconds": uptime_seconds,
            "uptime_human": self._format_uptime(
                uptime_seconds
            ),
            "heartbeat_count": runtime_state.heartbeat_count,
            "last_heartbeat_at": runtime_state.last_heartbeat_at,
            "heartbeat_alive": runtime_state.heartbeat_alive(),
            "database": database,
            "vision": self._vision_snapshot(),
        }

    def print_snapshot(
        self
    ) -> None:

        snapshot = self.compact_snapshot()

        print(
            "\n".join(
                f"{key}: {value}"
                for key, value in snapshot.items()
            )
        )

    def _conversation_snapshot(
        self
    ) -> dict:

        history = conversation_manager.get_history()

        return {
            "size": conversation_manager.size(),
            "max_messages": getattr(
                conversation_manager,
                "max_messages",
                None
            ),
            "last_message": (
                history[-1]
                if history
                else None
            ),
        }

    def _personality_snapshot(
        self
    ) -> dict:

        return {
            "parameters": personality_state.all()
        }

    def _vision_snapshot(
        self
    ) -> dict:

        try:

            raw_snapshot = vision_manager.snapshot()

            return self._normalize_vision_snapshot(
                raw_snapshot
            )

        except Exception as error:

            return self._normalize_vision_snapshot(
                {
                    "enabled": False,
                    "camera_active": False,
                    "camera_available": False,
                    "camera_index": None,
                    "width": None,
                    "height": None,
                    "grayscale": None,
                    "started_at": None,
                    "last_error": str(
                        error
                    ),
                    "last_brightness": None,
                    "image_quality": "error",
                    "image_metrics": self._empty_image_metrics(
                        image_quality="error"
                    ),
                    "face_detection": self._empty_face_detection(
                        enabled=False,
                        detection_ready=False,
                        skipped=True,
                        skip_reason="vision_snapshot_error",
                        last_error=str(
                            error
                        )
                    ),
                    "last_frame_at": None,
                    "last_snapshot_path": None,
                    "has_frame": False,
                    "auto_capture": False,
                    "capture_interval": None,
                }
            )

    def _normalize_vision_snapshot(
        self,
        snapshot: dict | None
    ) -> dict:

        snapshot = snapshot or {}

        raw_metrics = (
            snapshot.get(
                "image_metrics"
            )
            or {}
        )

        image_quality = (
            raw_metrics.get(
                "image_quality"
            )
            or snapshot.get(
                "image_quality"
            )
            or "unknown"
        )

        image_metrics = self._normalize_image_metrics(
            raw_metrics,
            image_quality=image_quality
        )

        last_brightness = snapshot.get(
            "last_brightness"
        )

        if last_brightness is None:

            last_brightness = image_metrics.get(
                "brightness_mean"
            )

        face_ready = image_metrics.get(
            "face_ready",
            False
        )

        face_detection = self._normalize_face_detection(
            snapshot.get(
                "face_detection"
            )
        )

        return {
            "enabled": snapshot.get(
                "enabled",
                False
            ),
            "camera_active": snapshot.get(
                "camera_active",
                False
            ),
            "camera_available": snapshot.get(
                "camera_available",
                False
            ),
            "camera_index": snapshot.get(
                "camera_index"
            ),
            "width": snapshot.get(
                "width"
            ),
            "height": snapshot.get(
                "height"
            ),
            "grayscale": snapshot.get(
                "grayscale"
            ),
            "started_at": snapshot.get(
                "started_at"
            ),
            "last_error": snapshot.get(
                "last_error"
            ),
            "last_brightness": last_brightness,
            "image_quality": image_quality,
            "image_metrics": image_metrics,
            "face_ready": face_ready,
            "face_detection": face_detection,
            "last_frame_at": snapshot.get(
                "last_frame_at"
            ),
            "last_snapshot_path": snapshot.get(
                "last_snapshot_path"
            ),
            "has_frame": snapshot.get(
                "has_frame",
                False
            ),
            "auto_capture": snapshot.get(
                "auto_capture",
                False
            ),
            "capture_interval": snapshot.get(
                "capture_interval"
            ),
        }

    def _normalize_image_metrics(
        self,
        metrics: dict | None,
        image_quality: str = "unknown"
    ) -> dict:

        metrics = metrics or {}

        return {
            "brightness_mean": metrics.get(
                "brightness_mean",
                0.0
            ),
            "brightness_std": metrics.get(
                "brightness_std",
                0.0
            ),
            "dark_ratio": metrics.get(
                "dark_ratio",
                0.0
            ),
            "bright_ratio": metrics.get(
                "bright_ratio",
                0.0
            ),
            "overexposed_ratio": metrics.get(
                "overexposed_ratio",
                0.0
            ),
            "blur_score": metrics.get(
                "blur_score",
                0.0
            ),
            "backlit_score": metrics.get(
                "backlit_score",
                0.0
            ),
            "image_quality": metrics.get(
                "image_quality",
                image_quality
            ),
            "face_ready": metrics.get(
                "face_ready",
                False
            ),
        }

    def _normalize_face_detection(
        self,
        face_detection: dict | None
    ) -> dict:

        face_detection = face_detection or {}

        return {
            "enabled": face_detection.get(
                "enabled",
                False
            ),
            "detection_ready": face_detection.get(
                "detection_ready",
                False
            ),
            "skipped": face_detection.get(
                "skipped",
                True
            ),
            "skip_reason": face_detection.get(
                "skip_reason"
            ),
            "face_detected": face_detection.get(
                "face_detected",
                False
            ),
            "face_count": face_detection.get(
                "face_count",
                0
            ),
            "faces": face_detection.get(
                "faces",
                []
            ),
            "largest_face": face_detection.get(
                "largest_face"
            ),
            "last_error": face_detection.get(
                "last_error"
            ),
        }

    def _empty_image_metrics(
        self,
        image_quality: str = "unknown"
    ) -> dict:

        return {
            "brightness_mean": 0.0,
            "brightness_std": 0.0,
            "dark_ratio": 0.0,
            "bright_ratio": 0.0,
            "overexposed_ratio": 0.0,
            "blur_score": 0.0,
            "backlit_score": 0.0,
            "image_quality": image_quality,
            "face_ready": False,
        }

    def _empty_face_detection(
        self,
        enabled: bool = False,
        detection_ready: bool = False,
        skipped: bool = True,
        skip_reason: str | None = "unavailable",
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

    def _format_uptime(
        self,
        total_seconds: int
    ) -> str:

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        seconds = total_seconds % 60

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    def _timestamp(
        self
    ) -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()


diagnostics_manager = DiagnosticsManager()