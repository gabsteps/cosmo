from enum import Enum


class AudioState(Enum):
    IDLE = "idle"
    LISTENING = "listening"


class AudioStateManager:

    def __init__(self):
        self.state = AudioState.IDLE


audio_state = AudioStateManager()