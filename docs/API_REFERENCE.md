# API Reference

## Event Types & Data Structures

Cosmo uses an event-driven architecture. All inter-component communication flows through the event bus.

### Audio Events

#### `WAKE_WORD_DETECTED`

Emitted when a configured wake word is recognized.

**Emitter**: `WakewordEngine` → `WakewordManager`

**Data Structure**:
```python
{
    "word": str,           # Detected wake word (e.g., "cosmo")
    "confidence": float,   # Confidence score (0.0-1.0)
}
```

**Example Listener**:
```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED

def on_wake_word_detected(data):
    word = data.get("word")
    confidence = data.get("confidence")
    logger.info(f"Wake word '{word}' detected (confidence: {confidence:.2f})")

event_bus.subscribe(WAKE_WORD_DETECTED, on_wake_word_detected)
```

---

#### `SPEECH_RECOGNIZED`

Emitted when a voice command is fully captured and converted to text.

**Emitter**: `STTManager`

**Data Structure**:
```python
{
    "text": str,          # Recognized text (e.g., "what time is it")
    "user_id": int,       # ID of speaking user (default: 1)
    "confidence": float,  # Confidence score (0.0-1.0)
    "duration_ms": int,   # Duration of speech in milliseconds
}
```

**Example**:
```python
from cosmo.core.events.event_types import SPEECH_RECOGNIZED

def on_speech_recognized(data):
    text = data.get("text")
    confidence = data.get("confidence")
    logger.info(f"Recognized: '{text}' (confidence: {confidence:.2f})")

event_bus.subscribe(SPEECH_RECOGNIZED, on_speech_recognized)
```

---

#### `VOICE_ACTIVITY_STARTED`

Emitted when speech activity is detected.

**Emitter**: `VADEngine` → `STTManager`

**Data Structure**:
```python
{
    "timestamp": float,    # Unix timestamp
}
```

---

#### `VOICE_ACTIVITY_ENDED`

Emitted when speech activity ceases.

**Emitter**: `VADEngine` → `STTManager`

**Data Structure**:
```python
{
    "timestamp": float,    # Unix timestamp
    "silence_duration_ms": int,
}
```

---

### Vision Events (Planned)

#### `FACE_DETECTED`

Emitted when face(s) are detected in the camera frame.

**Data Structure** (planned):
```python
{
    "count": int,         # Number of faces detected
    "faces": [
        {
            "id": str,
            "bbox": [x, y, w, h],  # Bounding box
            "confidence": float,
        }
    ]
}
```

---

#### `USER_RECOGNIZED`

Emitted when a detected face is matched to a known user.

**Data Structure** (planned):
```python
{
    "user_id": int,       # ID of recognized user
    "confidence": float,  # Face match confidence
    "face_id": str,       # Face identifier
}
```

---

#### `FACE_UNKNOWN`

Emitted when a face is detected but not recognized.

**Data Structure** (planned):
```python
{
    "face_id": str,       # Unknown face identifier
    "bbox": [x, y, w, h], # Bounding box
}
```

---

### Conversation Events

#### `COMMAND_RECEIVED`

Emitted when a text command is ready for processing.

**Emitter**: Application (after SPEECH_RECOGNIZED processing)

**Data Structure**:
```python
{
    "command": str,       # Parsed command text
    "user_id": int,       # User ID
    "source": str,        # "voice" or "text"
}
```

---

#### `CONVERSATION_STARTED`

Emitted when a conversation with a user begins.

**Data Structure**:
```python
{
    "user_id": int,
    "timestamp": float,
}
```

---

#### `CONVERSATION_FINISHED`

Emitted when a conversation ends.

**Data Structure**:
```python
{
    "user_id": int,
    "duration_seconds": float,
    "message_count": int,
}
```

---

### Memory Events

#### `MEMORY_CREATED`

Emitted when new user memory is created.

**Data Structure**:
```python
{
    "user_id": int,
    "category": str,      # e.g., "preference", "fact", "event"
    "content": str,       # Memory text
    "importance": int,    # 0-100
}
```

---

#### `MEMORY_UPDATED`

Emitted when existing memory is modified.

**Data Structure**:
```python
{
    "memory_id": int,
    "user_id": int,
    "category": str,
    "content": str,
    "importance": int,
}
```

---

#### `MEMORY_DELETED`

Emitted when memory is removed.

**Data Structure**:
```python
{
    "memory_id": int,
    "user_id": int,
}
```

---

### System Events

#### `SYSTEM_STARTED`

Emitted when the system completes initialization.

**Emitter**: `Bootstrap`

**Data Structure**:
```python
{
    "system": str,        # System name (e.g., "Zenith Cosmo 42")
    "version": str,       # Version number
    "timestamp": float,   # Unix timestamp
}
```

---

#### `SYSTEM_SHUTDOWN`

Emitted when the system is shutting down.

**Data Structure**:
```python
{
    "reason": str,        # Reason for shutdown (e.g., "user_requested")
    "timestamp": float,
}
```

---

#### `SYSTEM_SLEEP`

Emitted when system enters sleep mode.

**Data Structure**:
```python
{
    "timestamp": float,
}
```

---

#### `SYSTEM_WAKE`

Emitted when system wakes from sleep.

**Data Structure**:
```python
{
    "timestamp": float,
}
```

---

### Cognition Events (Planned)

#### `INTENT_DETECTED`

Emitted when NLU detects user intent.

**Data Structure** (planned):
```python
{
    "intent": str,        # e.g., "get_time", "set_reminder"
    "confidence": float,
    "parameters": {},     # Intent-specific parameters
}
```

---

#### `THOUGHT_CREATED`

Emitted when system generates an internal thought.

**Data Structure** (planned):
```python
{
    "content": str,
    "context": dict,
}
```

---

## Core APIs

### Event Bus API

#### Synchronous Event Bus

```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED

# Subscribe to event
def my_callback(data):
    print(f"Event data: {data}")

event_bus.subscribe(WAKE_WORD_DETECTED, my_callback)

# Emit event
event_bus.emit(WAKE_WORD_DETECTED, {
    "word": "cosmo",
    "confidence": 0.95
})

# Unsubscribe
event_bus.unsubscribe(WAKE_WORD_DETECTED, my_callback)
```

**API Methods**:
- `subscribe(event_type: str, callback: Callable) → None`
- `unsubscribe(event_type: str, callback: Callable) → None`
- `emit(event_type: str, data: dict = None) → None`

---

#### Asynchronous Event Bus

```python
from cosmo.core.events.async_event_bus import async_event_bus, AsyncEventBus

# Subscribe to async event
async def my_async_callback(data):
    logger.info(f"Processing: {data}")
    await asyncio.sleep(1)  # Non-blocking I/O

async_event_bus.subscribe(WAKE_WORD_DETECTED, my_async_callback)

# Emit with priority
await async_event_bus.emit(
    WAKE_WORD_DETECTED,
    {"word": "cosmo"},
    priority=AsyncEventBus.PRIORITY_AUDIO  # High priority
)

# Get metrics
metrics = async_event_bus.get_metrics()
print(f"Events processed: {metrics['events_completed']}")
print(f"Listener errors: {metrics['listener_errors']}")
```

**API Methods**:
- `subscribe(event_type: str, callback: AsyncCallable) → None`
- `emit(event_type: str, data: dict = None, priority: int = None) → Awaitable`
- `get_metrics() → dict`
- `start() → Awaitable` (starts event processing loop)
- `shutdown() → Awaitable`

**Priority Levels**:
- `PRIORITY_CRITICAL` — 0 (highest)
- `PRIORITY_AUDIO` — 1
- `PRIORITY_BACKGROUND` — 2 (lowest)

---

### Configuration API

```python
from cosmo.core.config.settings_manager import config

# Get configuration value
sample_rate = config.get("audio", "sample_rate")  # 16000

# Get nested value
wake_words = config.get("wakeword", "words")  # ["cosmo", "zenith", ...]

# Get with default
debug = config.get("system", "debug", default=False)

# Get entire section
audio_config = config.get("audio")  # Returns dict
```

**API Methods**:
- `get(*keys, default=None) → Any` — Get value by nested keys

---

### Logger API

```python
from cosmo.core.logger.logger_manager import logger

# Log at different levels
logger.debug("Detailed debug info")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system error")

# Log with exception info
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")

# Logger outputs to:
# - Console: INFO and above
# - File (data/logs/cosmo.log): DEBUG and above
```

**API Methods**:
- `debug(msg, *args, **kwargs) → None`
- `info(msg, *args, **kwargs) → None`
- `warning(msg, *args, **kwargs) → None`
- `error(msg, *args, **kwargs) → None`
- `critical(msg, *args, **kwargs) → None`
- `exception(msg, *args, **kwargs) → None`

---

### Repository APIs

#### UserRepository

```python
from cosmo.data.database.repositories.user_repository import user_repository

# Create user
user_id = user_repository.create_user("João Silva")

# Get user
user = user_repository.get_user_by_id(1)
user = user_repository.get_user_by_name("João Silva")

# Check existence
exists = user_repository.user_exists("João Silva")

# Update user info
user_repository.update_trust_level(1, 85)
user_repository.save_face_id(1, "face_embedding_id")
user_repository.update_last_seen(1)

# List all users
users = user_repository.list_users()

# Delete user
user_repository.delete_user(1)
```

**Note**: ⚠️ Import issue — uses `from database import db` instead of full path

---

#### ConversationRepository

```python
from cosmo.data.database.repositories.conversation_repository import conversation_repository

# Add message to conversation
msg_id = conversation_repository.add_message(
    user_id=1,
    role="user",           # "user" or "assistant"
    message="Hello Cosmo"
)

# Get conversation history
history = conversation_repository.get_conversation_history(
    user_id=1,
    limit=20               # Most recent N messages
)

# Clear conversation
conversation_repository.clear_history(user_id=1)
```

---

#### MemoryRepository (Not Implemented)

Expected API (when implemented):

```python
from cosmo.data.database.repositories.memory_repository import memory_repository

memory_id = memory_repository.add_memory(
    user_id=1,
    category="preference",
    content="Likes classical music",
    importance=75
)

memories = memory_repository.get_user_memories(user_id=1)
preferences = memory_repository.get_memories_by_category("preference")

memory_repository.delete_memory(memory_id)
```

---

### Audio Manager APIs

#### WakewordManager

```python
from cosmo.audio.wakeword.wakeword_manager import wakeword_manager

# Start listening for wake words (blocking)
async def start_listening():
    await wakeword_manager.start()

# Stop listening
await wakeword_manager.stop()
```

---

#### STTManager

```python
from cosmo.audio.stt.stt_manager import stt_manager

# Listen for a single command (currently synchronous)
text = stt_manager.listen_once()  # Blocks until done

# Returns final recognized text
print(f"Recognized: {text}")
```

⚠️ **Note**: Should be converted to async: `await stt_manager.listen_once()`

---

#### VADEngine

```python
from cosmo.audio.vad.vad_engine import vad_engine

# Check if audio chunk contains speech
is_speech = vad_engine.is_speech(audio_chunk)

if is_speech:
    print("Voice detected")
else:
    print("Silence detected")
```

---

## Usage Examples

### Example 1: Custom Event Listener

```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED
from cosmo.core.logger.logger_manager import logger

def log_wake_word(data):
    word = data.get("word")
    confidence = data.get("confidence", 0)
    logger.info(f"Detected '{word}' with {confidence:.1%} confidence")

# Register listener
event_bus.subscribe(WAKE_WORD_DETECTED, log_wake_word)
```

---

### Example 2: Async Event Listener with Timeout

```python
import asyncio
from cosmo.core.events.async_event_bus import async_event_bus
from cosmo.core.events.event_types import SPEECH_RECOGNIZED
from cosmo.core.logger.logger_manager import logger

async def process_command(data):
    text = data.get("text", "")
    logger.info(f"Processing: {text}")
    
    # Do some async processing
    await asyncio.sleep(2)
    
    logger.info("Processing complete")

async_event_bus.subscribe(SPEECH_RECOGNIZED, process_command)

# If this listener takes > 10 seconds, it will timeout
# and async_event_bus will log a listener_timeout metric
```

---

### Example 3: React to Multiple Events

```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import (
    WAKE_WORD_DETECTED,
    SPEECH_RECOGNIZED,
    SYSTEM_SHUTDOWN
)

def on_wake_word(data):
    logger.info("Woken up")

def on_speech(data):
    logger.info(f"You said: {data['text']}")

def on_shutdown(data):
    logger.info("Goodbye!")

# Register all listeners
event_bus.subscribe(WAKE_WORD_DETECTED, on_wake_word)
event_bus.subscribe(SPEECH_RECOGNIZED, on_speech)
event_bus.subscribe(SYSTEM_SHUTDOWN, on_shutdown)
```

---

### Example 4: Get AsyncEventBus Metrics

```python
from cosmo.core.events.async_event_bus import async_event_bus

metrics = async_event_bus.get_metrics()

print(f"Events received: {metrics['events_received']}")
print(f"Events completed: {metrics['events_completed']}")
print(f"Events failed: {metrics['events_failed']}")
print(f"Listener timeouts: {metrics['listener_timeouts']}")
print(f"Queue peak size: {metrics['queue_peak']}")
print(f"Avg processing time: {metrics['avg_event_processing_time']:.3f}s")
```

---

### Example 5: Configuration Access

```python
from cosmo.core.config.settings_manager import config

# Audio configuration
sample_rate = config.get("audio", "sample_rate")
chunk_size = config.get("audio", "chunk_size")

# Wake word configuration
wake_words = config.get("wakeword", "words")
confidence_threshold = config.get("wakeword", "confidence_threshold")

# System configuration
system_name = config.get("system", "name")
debug_mode = config.get("system", "debug")

# Database configuration
db_path = config.get("database", "path")

print(f"System: {system_name}")
print(f"Sample Rate: {sample_rate} Hz")
print(f"Wake Words: {wake_words}")
```

---

## Error Handling

### Event Listener Errors

If a synchronous event listener raises an exception, it will propagate:

```python
def bad_listener(data):
    raise ValueError("Something went wrong")

event_bus.subscribe(WAKE_WORD_DETECTED, bad_listener)
event_bus.emit(WAKE_WORD_DETECTED, {})  # Raises ValueError
```

**Recommendation**: Wrap listeners in try/except:

```python
def safe_listener(data):
    try:
        process(data)
    except Exception as e:
        logger.error(f"Listener error: {e}", exc_info=True)
```

### Async Listener Timeouts

Async listeners have a 10-second timeout. If exceeded:

```python
async def slow_listener(data):
    await asyncio.sleep(15)  # Exceeds 10s timeout

async_event_bus.subscribe(WAKE_WORD_DETECTED, slow_listener)

# Timeout tracked in metrics:
# metrics["listener_timeouts"] += 1
```

---

## Performance Considerations

### Event Bus Performance

- **Sync Bus**: <1ms dispatch time per event
- **Async Bus**: 1-5ms including queue overhead
- **Max queue size**: 100 events (configured)
- **Listener timeout**: 10 seconds (configurable)

### Metrics Collection Overhead

AsyncEventBus metrics collection adds <1% CPU overhead.

---

## Versioning

This API reference documents **Cosmo 0.1.1**.

---

**Last Updated**: May 30, 2026
