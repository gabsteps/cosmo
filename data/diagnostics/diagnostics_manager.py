# cosmo/core/data/diagnostics/diagnostics_manager.py

from datetime import datetime, timezone

from cosmo.core.runtime.runtime_state import (
    runtime_state
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)

from cosmo.cognition.personality.personality_state import (
    personality_state
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
        }

    def compact_snapshot(
        self
    ) -> dict:

        runtime = runtime_state.snapshot()
        event_bus = async_event_bus.get_metrics()

        return {
            "timestamp": self._timestamp(),
            "mode": runtime.get("mode"),
            "previous_mode": runtime.get("previous_mode"),
            "tts_active": runtime.get("tts_active"),
            "llm_active": runtime.get("llm_active"),
            "capture_active": runtime.get("capture_active"),
            "conversation_size": conversation_manager.size(),
            "queue_size": event_bus.get("current_queue_size"),
            "events_received": event_bus.get("events_received"),
            "events_completed": event_bus.get("events_completed"),
            "events_failed": event_bus.get("events_failed"),
            "listener_timeouts": event_bus.get("listener_timeouts"),
            "listener_errors": event_bus.get("listener_errors"),
            "last_error": runtime.get("last_error"),
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
            )
        }

    def _personality_snapshot(
        self
    ) -> dict:

        return {
            "parameters": personality_state.all()
        }

    def _timestamp(
        self
    ) -> str:

        return (
            datetime
            .now(timezone.utc)
            .isoformat()
        )


diagnostics_manager = DiagnosticsManager()