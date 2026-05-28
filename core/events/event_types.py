# =========================
# AUDIO
# =========================

WAKE_WORD_DETECTED = "wake_word_detected"

VOICE_ACTIVITY_STARTED = "voice_activity_started"
VOICE_ACTIVITY_ENDED = "voice_activity_ended"

SPEECH_RECOGNIZED = "speech_recognized"
SPEECH_RECEIVED = "speech_received"

TTS_STARTED = "tts_started"
TTS_FINISHED = "tts_finished"


# =========================
# VISION
# =========================

FACE_DETECTED = "face_detected"

FACE_UNKNOWN = "face_unknown"

USER_RECOGNIZED = "user_recognized"

USER_LOST = "user_lost"

TRACKING_STARTED = "tracking_started"
TRACKING_STOPPED = "tracking_stopped"


# =========================
# MEMORY
# =========================

MEMORY_CREATED = "memory_created"

MEMORY_UPDATED = "memory_updated"

MEMORY_DELETED = "memory_deleted"


# =========================
# CONVERSATION
# =========================

COMMAND_RECEIVED = "command_received"

CONVERSATION_STARTED = "conversation_started"

CONVERSATION_FINISHED = "conversation_finished"


# =========================
# SYSTEM
# =========================

SYSTEM_STARTED = "system_started"

SYSTEM_SHUTDOWN = "system_shutdown"

SYSTEM_SLEEP = "system_sleep"

SYSTEM_WAKE = "system_wake"

ERROR_OCCURRED = "error_occurred"


# =========================
# NETWORK
# =========================

NETWORK_CONNECTED = "network_connected"

NETWORK_DISCONNECTED = "network_disconnected"


# =========================
# MOTION
# =========================

MOTION_STARTED = "motion_started"

MOTION_STOPPED = "motion_stopped"

OBSTACLE_DETECTED = "obstacle_detected"


# =========================
# COGNITION
# =========================

THOUGHT_CREATED = "thought_created"

INTENT_DETECTED = "intent_detected"

PLANNER_TASK_CREATED = "planner_task_created"



# No futuro:
# adicione async.

# Exemplo:

# async def emit(...)

# Porque:

# áudio
# câmera
# IA
# TTS

# vão rodar simultaneamente.