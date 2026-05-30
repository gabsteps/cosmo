import time

class RuntimeState:

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    COOLDOWN = "cooldown"

    def __init__(self):

        self.mode = self.IDLE
        self.ignore_wakeword_until = 0.0

    def should_ignore_wakeword(self):

        return (
            self.mode != self.IDLE or
            time.time() < self.ignore_wakeword_until
        )

runtime_state = RuntimeState()