import time
from threading import Lock

from cosmo.core.logger.logger_manager import logger


class RuntimeState:

    IDLE = "idle"
    WAKE_DETECTED = "wake_detected"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    COOLDOWN = "cooldown"
    ERROR = "error"

    def __init__(self):

        self.mode = self.IDLE
        self.previous_mode = None

        self.ignore_wakeword_until = 0.0

        self.current_transcript = None
        self.current_response = None
        self.last_error = None

        self.tts_active = False
        self.llm_active = False
        self.capture_active = False

        self._lock = Lock()

    def set_mode(
        self,
        mode: str,
        reason: str | None = None
    ) -> None:

        with self._lock:

            if self.mode == mode:
                return

            self.previous_mode = self.mode
            self.mode = mode

            logger.info(
                f"Runtime mode: {self.previous_mode} -> {self.mode}"
                + (f" ({reason})" if reason else "")
            )

    def set_idle(self) -> None:

        with self._lock:
            self.tts_active = False
            self.llm_active = False
            self.capture_active = False
            self.current_transcript = None
            self.current_response = None

        self.set_mode(
            self.IDLE,
            reason="system ready"
        )

    def set_wake_detected(self) -> None:

        self.set_mode(
            self.WAKE_DETECTED,
            reason="wake word detected"
        )

    def set_listening(self) -> None:

        with self._lock:
            self.capture_active = True

        self.set_mode(
            self.LISTENING,
            reason="audio capture started"
        )

    def set_transcribing(self) -> None:

        with self._lock:
            self.capture_active = False

        self.set_mode(
            self.TRANSCRIBING,
            reason="audio captured"
        )

    def set_thinking(
        self,
        transcript: str | None = None
    ) -> None:

        with self._lock:
            self.llm_active = True
            self.current_transcript = transcript

        self.set_mode(
            self.THINKING,
            reason="generating response"
        )

    def set_speaking(
        self,
        response: str | None = None
    ) -> None:

        with self._lock:
            self.llm_active = False
            self.tts_active = True
            self.current_response = response

        self.set_mode(
            self.SPEAKING,
            reason="tts started"
        )

    def set_cooldown(
        self,
        seconds: float = 2.0
    ) -> None:

        with self._lock:
            self.tts_active = False
            self.ignore_wakeword_until = time.time() + seconds

        self.set_mode(
            self.COOLDOWN,
            reason=f"cooldown {seconds:.1f}s"
        )

    def set_error(
        self,
        error: Exception | str
    ) -> None:

        with self._lock:
            self.last_error = str(error)
            self.tts_active = False
            self.llm_active = False
            self.capture_active = False

        self.set_mode(
            self.ERROR,
            reason=str(error)
        )

    def should_ignore_wakeword(self) -> bool:

        with self._lock:

            return (
                self.mode != self.IDLE or
                time.time() < self.ignore_wakeword_until
            )

    def can_accept_wakeword(self) -> bool:

        return not self.should_ignore_wakeword()

    def can_start_capture(self) -> bool:

        with self._lock:
            return self.mode in (
                self.WAKE_DETECTED,
                self.IDLE,
            )

    def can_start_thinking(self) -> bool:

        with self._lock:
            return not self.llm_active

    def can_start_speaking(self) -> bool:

        with self._lock:
            return not self.tts_active

    def snapshot(self) -> dict:

        with self._lock:
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
            }


runtime_state = RuntimeState()