import time


class RuntimeState:

    IDLE = "idle"
    WAKE_DETECTED = "wake_detected"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    COOLDOWN = "cooldown"

    def __init__(self):

        self.started_at = time.time()

        self.mode = self.IDLE
        self.previous_mode = None

        self.ignore_wakeword_until = 0.0

        self.tts_active = False
        self.llm_active = False
        self.capture_active = False

        self.current_transcript = None
        self.current_response = None
        self.last_error = None

        self.heartbeat_count = 0
        self.last_heartbeat_at = None

    def _set_mode(
        self,
        new_mode: str,
        reason: str = ""
    ) -> None:

        old_mode = self.mode
        self.previous_mode = old_mode
        self.mode = new_mode

        if reason:
            from cosmo.core.logger.logger_manager import logger
            logger.info(
                f"Runtime mode: {old_mode} -> {new_mode} ({reason})"
            )

    def set_idle(self) -> None:
        self.tts_active = False
        self.llm_active = False
        self.capture_active = False
        self.current_transcript = None
        self.current_response = None
        self._set_mode(
            self.IDLE,
            "system ready"
        )

    def set_wake_detected(self) -> None:
        self._set_mode(
            self.WAKE_DETECTED,
            "wake word detected"
        )

    def set_listening(self) -> None:
        self.capture_active = True
        self._set_mode(
            self.LISTENING,
            "audio capture started"
        )

    def set_transcribing(self) -> None:
        self.capture_active = False
        self._set_mode(
            self.TRANSCRIBING,
            "audio captured"
        )

    def set_thinking(
        self,
        text: str | None = None
    ) -> None:
        self.llm_active = True
        self.current_transcript = text
        self._set_mode(
            self.THINKING,
            "generating response"
        )

    def set_speaking(
        self,
        text: str | None = None
    ) -> None:
        self.tts_active = True
        self.llm_active = False
        self.current_response = text
        self._set_mode(
            self.SPEAKING,
            "tts started"
        )

    def set_cooldown(
        self,
        seconds: float = 2.0
    ) -> None:
        self.tts_active = False
        self.capture_active = False
        self.llm_active = False
        self.ignore_wakeword_until = (
            time.time() + seconds
        )
        self._set_mode(
            self.COOLDOWN,
            f"cooldown {seconds}s"
        )

    def should_ignore_wakeword(self) -> bool:
        return (
            self.mode != self.IDLE
            or time.time() < self.ignore_wakeword_until
        )

    def can_start_thinking(self) -> bool:
        return self.mode in (
            self.IDLE,
            self.TRANSCRIBING
        )

    def mark_heartbeat(self) -> None:
        self.heartbeat_count += 1
        self.last_heartbeat_at = time.time()

    def uptime_seconds(self) -> int:
        return int(
            time.time() - self.started_at
        )

    def heartbeat_alive(self) -> bool:
        if self.last_heartbeat_at is None:
            return False

        return (
            time.time() - self.last_heartbeat_at
        ) <= 10.0

    def snapshot(
        self
    ) -> dict:

        return {
            "mode": self.mode,
            "previous_mode": self.previous_mode,
            "ignore_wakeword_until": self.ignore_wakeword_until,

            "tts_active": self.tts_active,
            "llm_active": self.llm_active,
            "capture_active": self.capture_active,

            "current_transcript": self.current_transcript,
            "current_response": self.current_response,
            "last_error": self.last_error,

            "started_at": self.started_at,
            "uptime_seconds": self.uptime_seconds(),

            "heartbeat_count": self.heartbeat_count,
            "last_heartbeat_at": self.last_heartbeat_at,
            "heartbeat_alive": self.heartbeat_alive(),
        }
runtime_state = RuntimeState()