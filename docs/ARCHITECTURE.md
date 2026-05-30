# Cosmo Architecture & System Design

## Overview

Cosmo is built on a **layered, event-driven architecture** with clear separation of concerns. The system emphasizes offline-first processing, modular design, and real-time responsiveness.

### Architectural Principles

1. **Vertical Decoupling** — Upper layers don't depend on lower layer implementations (via abstractions and repositories)
2. **Horizontal Decoupling** — Components at the same layer communicate via events, not direct calls
3. **Inversion of Control** — Event bus manages control flow rather than components calling each other
4. **Offline-First** — All critical operations work without external APIs
5. **Thread/Task Safety** — State machines and explicit transitions prevent race conditions

## Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Level 5: External Interfaces (Planned)                 │
│  REST API | CLI | WebSocket                             │
├─────────────────────────────────────────────────────────┤
│  Level 4: Cognitive Intelligence (In Development)       │
│  Context | Memory | Personality | Planner               │
├─────────────────────────────────────────────────────────┤
│  Level 3: Sensory Processing (Partial)                  │
│  Audio (STT, TTS, VAD, Wakeword) | Vision (In dev)      │
├─────────────────────────────────────────────────────────┤
│  Level 2: System Core (Implemented)                     │
│  Event Bus | Config | Logger | Runtime | Scheduler      │
├─────────────────────────────────────────────────────────┤
│  Level 1: Persistence (Partial)                         │
│  Database | Repositories                                │
├─────────────────────────────────────────────────────────┤
│  Level 0: External Resources                            │
│  Vosk Model | Piper Voices | Haar Cascades | Config    │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Bootstrap & Lifecycle (`core/bootstrap/`)

**Responsibility**: System initialization, startup/shutdown sequencing

**Components**:
- `bootstrap.py` — Main entry point, orchestrates startup
- `lifecycle.py` — State machine (running/sleeping)
- `task_manager.py` — Wrapper for async task creation

**Key Methods**:
```python
bootstrap.start()           # Initialize system
bootstrap.shutdown()        # Graceful shutdown
lifecycle.is_running()      # Check if system is active
lifecycle.sleep()/wake()    # Suspend/resume operations
```

**Startup Sequence**:
1. `main.py` calls `bootstrap.start()`
2. `lifecycle.start()` — Sets running=True
3. `event_bus.emit(SYSTEM_STARTED)` — Triggers listeners
4. Thread creation for audio pipeline
5. `runtime_manager.wait_forever()` — Main process blocks

### 2. Event System (`core/events/`)

**Responsibility**: Pub/Sub event dispatch and coordination

**Pattern**: Observer pattern with singleton event buses

#### Synchronous Event Bus (`event_bus.py`)

- **Implementation**: Simple dict of lists
- **Dispatch**: Immediate, blocking
- **Use**: Critical events requiring low latency
- **No Metrics**: Performance-first

**API**:
```python
event_bus.subscribe(event_type: str, callback: Callable)
event_bus.emit(event_type: str, data: dict)
```

**Example**:
```python
def on_wake_word(data):
    logger.info(f"Detected: {data['word']}")

event_bus.subscribe(WAKE_WORD_DETECTED, on_wake_word)
event_bus.emit(WAKE_WORD_DETECTED, {"word": "cosmo"})
```

#### Asynchronous Event Bus (`async_event_bus.py`)

- **Implementation**: Queue-based with asyncio
- **Queue Size**: Bounded (max 100 events)
- **Dispatch**: Deferred via event loop
- **Timeout**: 10 seconds per listener
- **Metrics**: 19 real-time performance metrics
- **Tracing**: UUID per event for debugging

**API**:
```python
await async_event_bus.emit(event_type: str, data: dict, priority: int)
async_event_bus.subscribe(event_type: str, async_callback: AsyncCallable)
metrics = async_event_bus.get_metrics()
```

**Dual Bus Pattern**:
```
┌─────────────────────────────────────┐
│  Event Emission                     │
│  (from wakeword_manager, etc)       │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
  ┌──────────┐   ┌────────────┐
  │ Sync Bus │   │ Async Bus  │
  │ (fast)   │   │ (durable)  │
  └────┬─────┘   └──────┬─────┘
       │                │
       └────┬───────────┘
            │
     ┌──────▼──────┐
     │ Listeners   │
     │ (callbacks) │
     └─────────────┘
```

**Event Types** (`event_types.py`):

| Category | Events |
|----------|--------|
| **Audio** | `WAKE_WORD_DETECTED`, `SPEECH_RECOGNIZED`, `VOICE_ACTIVITY_STARTED/ENDED` |
| **Vision** | `FACE_DETECTED`, `USER_RECOGNIZED`, `FACE_UNKNOWN`, `TRACKING_STARTED/STOPPED` |
| **Memory** | `MEMORY_CREATED`, `MEMORY_UPDATED`, `MEMORY_DELETED` |
| **Conversation** | `COMMAND_RECEIVED`, `CONVERSATION_STARTED/FINISHED` |
| **System** | `SYSTEM_STARTED`, `SYSTEM_SHUTDOWN`, `SYSTEM_SLEEP/WAKE` |
| **Network** | `NETWORK_CONNECTED`, `NETWORK_DISCONNECTED` |
| **Cognition** | `THOUGHT_CREATED`, `INTENT_DETECTED`, `PLANNER_TASK_CREATED` |

### 3. Configuration (`core/config/`)

**Responsibility**: Centralized settings management

**Component**: `settings_manager.py`
- Loads YAML configuration
- Provides nested key access
- Single source of truth

**Usage**:
```python
sample_rate = config.get("audio", "sample_rate")  # 16000
wake_words = config.get("wakeword", "words")       # ["cosmo", "zenith", ...]
```

**File**: `cosmo/core/config/settings.yaml`

See [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md) for all options.

### 4. Logging (`core/logger/`)

**Responsibility**: Structured application logging

**Component**: `logger_manager.py`
- File and console output
- Configurable levels (DEBUG, INFO, WARNING, ERROR)
- Format: `[TIMESTAMP] [LEVEL] [NAME] message`

**Output**:
- Console: INFO level only
- File (`data/logs/cosmo.log`): DEBUG level

**Usage**:
```python
from cosmo.core.logger import logger
logger.info("System started")
logger.error("Audio device error", exc_info=True)
```

### 5. Runtime Management (`core/runtime/`)

**Responsibility**: Thread and async task orchestration

**Components**:
- `runtime_manager.py` — Thread-based (synchronous approach)
- `async_runtime.py` — Async-based (modern approach)

**RuntimeManager API** (legacy):
```python
runtime_manager.start_thread(target, name)   # Create thread daemon
runtime_manager.wait_forever()               # Block until threads end
```

**AsyncRuntime API** (preferred):
```python
task = async_runtime.create_task(coroutine, name)
await async_runtime.start()      # Start event loop
await async_runtime.shutdown()   # Cancel all tasks
```

### 6. Scheduler (`core/scheduler/`)

**Status**: Not yet implemented

**Future**: Periodic task scheduling, cron-like functionality

---

## Audio Pipeline

### Architecture

```
┌──────────────────────────────────────────────────────┐
│  IDLE STATE: Wakeword Detection Active               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  WakewordManager (daemon thread)                    │
│  ├─ PyAudio stream open (16000 Hz, mono)           │
│  ├─ Continuous loop: read chunk → process          │
│  │                                                  │
│  └─ WakewordEngine (Vosk)                          │
│     ├─ KaldiRecognizer.AcceptWaveform()            │
│     └─ Match result against config.wakeword.words  │
│                                                      │
│  IF DETECTED:                                        │
│  ├─ Emit WAKE_WORD_DETECTED event                  │
│  ├─ audio_state.state = LISTENING                  │
│  └─ Start STTManager thread                        │
└──────────────────────────────────────────────────────┘

         ▼ LISTENING STATE (Active)

┌──────────────────────────────────────────────────────┐
│  LISTENING STATE: Command Processing Active          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  STTManager (worker thread)                         │
│  ├─ New PyAudio stream for STT                      │
│  ├─ Loop until timeout or silence                  │
│  │                                                  │
│  ├─ VADEngine (WebRTC)                             │
│  │  ├─ Check each frame for voice activity        │
│  │  └─ Track silence duration                      │
│  │                                                  │
│  └─ STTEngine (Vosk)                               │
│     ├─ Accumulate partial results                  │
│     └─ Extract final text when done               │
│                                                      │
│  WHEN DONE (silence > 3s or timeout):              │
│  ├─ Close stream                                    │
│  ├─ Emit SPEECH_RECOGNIZED with text               │
│  ├─ audio_state.state = IDLE                       │
│  └─ Thread exits                                    │
└──────────────────────────────────────────────────────┘
```

### Audio State Machine

```
                    IDLE
                     │
    User says "Cosmo" (detected)
                     │
                     ▼
    ┌─────────────────────────────┐
    │ LISTENING                   │
    │ - User speaks command       │
    │ - VAD active                │
    │ - STT processing            │
    └─────────────────────────────┘
                     │
    Silence > 3s or timeout
                     │
                     ▼
    ┌─────────────────────────────┐
    │ Command stored              │
    │ Listeners invoked           │
    └─────────────────────────────┘
                     │
                     ▼
                    IDLE
```

### Components

#### WakewordManager & Engine

**Responsibility**: Continuous microphone listening for wake phrases

**Files**: `audio/wakeword/wakeword_manager.py`, `wakeword_engine.py`

**Status**: ✅ Implemented (async)

**Key Features**:
- Real-time audio capture (1024 samples/chunk ≈ 64ms)
- Vosk model (PT-BR): `vosk-model-small-pt-0.3`
- Configurable wake words from settings.yaml
- Priority event emission (async_event_bus.PRIORITY_AUDIO)

**Flow**:
1. Open PyAudio stream (16000 Hz, mono)
2. Loop: read chunk → WakewordEngine.process_audio()
3. If match: emit WAKE_WORD_DETECTED, set audio_state to LISTENING
4. Otherwise: continue looping

#### STTManager & Engine

**Responsibility**: Capture and convert spoken command to text

**Files**: `audio/stt/stt_manager.py`, `stt_engine.py`

**Status**: ⚠️ Implemented (synchronous, needs async conversion)

**Key Features**:
- Vosk speech recognition (PT-BR)
- Timeout: 30 seconds total
- Silence threshold: 3 seconds
- Partial results available

**Flow**:
1. Started by audio_listener on WAKE_WORD_DETECTED
2. Open new PyAudio stream
3. Process chunks through VADEngine and STTEngine
4. Accumulate text until silence > 3s detected
5. Emit SPEECH_RECOGNIZED with final text

**Issue**: Uses synchronous `stream.read()` (blocking I/O). Should be converted to async with `asyncio.to_thread()`.

#### VADEngine

**Responsibility**: Detect presence/absence of speech

**File**: `audio/vad/vad_engine.py`

**Status**: ✅ Implemented

**Technology**: WebRTC VAD (webrtcvad library)

**Key Features**:
- Aggressiveness level: 0-3 (configured: 2)
- Frame size: 30ms (WebRTC requirement)
- Returns boolean: is_speech(frame) → True/False

**Usage**:
```python
vad = VADEngine()
is_speech = vad.is_speech(audio_chunk)  # True if voice detected
```

#### STTEngine

**Responsibility**: Vosk-based speech-to-text conversion

**File**: `audio/stt/stt_engine.py`

**Status**: ✅ Implemented

**Key Features**:
- Model loading: `cosmo/models/vosk/vosk-model-small-pt-0.3`
- Returns text as recognized
- Handles partial and final results

#### CommandProcessor

**Responsibility**: Parse and handle recognized commands

**File**: `audio/stt/command_processor.py`

**Status**: ⚠️ Stub (basic example only)

**Current**: Simple keyword matching ("horas", "nome", etc.)

**Future**: NLU integration for intent detection

---

## Data Persistence Layer

### Database Schema

**File**: `data/database/database.py`

**Technology**: SQLite3 with WAL mode

**Configuration**:
- Foreign Keys: Enabled
- Journal Mode: WAL (for concurrent read/write)
- Synchronous: NORMAL (balanced safety/performance)
- Location: `data/database/cosmo.db`

**Status**: ⚠️ Connection & pragmas implemented, but NO table creation

### Repository Pattern

**Location**: `data/database/repositories/`

**Purpose**: Abstraction layer for data access

**Current Status**:
- ✅ UserRepository — ~90% complete
- ✅ ConversationRepository — Complete
- ⚠️ FaceRepository — Stub
- ⚠️ MemoryRepository — Not implemented
- ⚠️ EventRepository — Stub
- ⚠️ SystemRepository — Not implemented

**Critical Issue**: Import statements use `from database import db` instead of `from cosmo.data.database.database import db` — this will fail at runtime.

### Tables (Planned Schema)

```sql
users (id, name, face_id, trust_level, last_seen, created_at)
conversations (id, user_id, role, message, timestamp)
memories (id, user_id, category, content, importance, created_at)
faces (id, user_id, face_data, embedding_vector, confidence, created_at)
events (id, event_type, data, timestamp)
system (key, value, updated_at)
```

---

## Vision System

**Status**: 🔴 Not implemented (directories exist, empty)

**Architecture**:
```
Camera
  ↓
FaceDetector (Haar Cascades or YOLO)
  ↓
FaceRecognizer (embeddings comparison)
  ↓
FaceRepository (match against known users)
  ↓
Events: FACE_DETECTED → USER_RECOGNIZED or UNKNOWN_FACE
```

**Planned Components**:
- `camera/camera.py` — Video stream capture
- `detection/detector.py` — Face detection
- `recognition/recognizer.py` — Face embedding & matching
- `tracking/tracker.py` — Person tracking across frames

---

## Cognition System

**Status**: 🔴 Not implemented (directories exist, empty)

**Planned Components**:
- `context/` — Conversation context tracking
- `memory/` — Semantic & episodic memory
- `personality/` — Assistant personality traits
- `planner/` — Task planning & scheduling

---

## Event Flow Example

### Wake Word → Command → Storage

```
Timeline:

[T=0ms]     User says "Cosmo"
            │
            ▼ (WakewordManager processing)

[T=100ms]   WakewordEngine detects "cosmo"
            │ Confidence: 0.94
            │
            ▼ event_bus.emit(WAKE_WORD_DETECTED, {...})

[T=101ms]   Event dispatched to audio_listener
            │ Starts STTManager thread
            │
            ▼ audio_state.state = LISTENING

[T=150ms]   User says "what time is it?"
            │ STTManager listening via VAD + STT
            │
            ▼ (STTEngine accumulating text)

[T=600ms]   VADEngine detects voice activity

[T=3600ms]  Silence detected (3+ seconds)
            │ Final text: "what time is it"
            │
            ▼ event_bus.emit(SPEECH_RECOGNIZED, {
                "text": "what time is it",
                "user_id": 1,
                "confidence": 0.89
              })

[T=3601ms]  Event dispatched to conversation_listener
            │
            ├─ conversation_repository.add_message(
            │   1, "user", "what time is it"
            │ )
            │
            ├─ command_processor.process_command(...)
            │
            └─ audio_state.state = IDLE

[T=3602ms]  WakewordManager resumes listening
            │
            ▼ (back to IDLE state)
```

---

## Thread/Async Model

**Current Status**: Mixed paradigm (hybrid sync + async)

### Synchronous (Threading)

- WakewordManager: Thread daemon
- STTManager: Thread daemon
- RuntimeManager: Thread coordination

### Asynchronous (asyncio)

- AsyncEventBus: Queue dispatcher
- AsyncRuntime: Task manager
- WakewordManager: Uses `asyncio.to_thread()` for I/O

**Issue**: System uses both threading and asyncio. Should consolidate on asyncio for consistency.

---

## Design Patterns Used

### 1. Pub/Sub (Observer)

Events are published by components and received by registered subscribers.

```python
# Publisher
event_bus.emit(WAKE_WORD_DETECTED, data)

# Subscriber
event_bus.subscribe(WAKE_WORD_DETECTED, callback)
```

### 2. Singleton

Core components instantiated once and imported globally:
- event_bus
- logger
- config
- database
- async_event_bus

### 3. Repository

Data access abstracted through repository classes:
```python
user = user_repository.get_user_by_name("João")
```

### 4. State Machine

Audio state (IDLE ↔ LISTENING) controlled with explicit transitions:
```python
audio_state.state = AudioState.LISTENING
```

### 5. Manager

Components orchestrate multiple sub-components:
- WakewordManager — audio + events + state
- STTManager — audio + VAD + STT + events
- RuntimeManager — threads + event loop coordination

---

## Startup & Shutdown

### Startup Sequence

```
1. main.py
   └─ bootstrap.start()
      ├─ lifecycle.start() → lifecycle.running = True
      ├─ event_bus.emit(SYSTEM_STARTED)
      │  └─ system_listener.on_system_started()
      │
      ├─ runtime_manager.start_event_pipeline()
      │  ├─ Register audio_listener
      │  ├─ Register vision_listener
      │  ├─ Register conversation_listener
      │  └─ Register system_listener
      │
      ├─ runtime_manager.start_thread(
      │   target=wakeword_manager.start,
      │   name="WakewordManager"
      │ )
      │
      └─ runtime_manager.wait_forever()
         └─ Blocks until thread.join() completes
```

### Shutdown Sequence

```
1. Signal received (Ctrl+C or SIGTERM)
   │
   ├─ bootstrap.shutdown()
   │  ├─ lifecycle.stop()
   │  ├─ event_bus.emit(SYSTEM_SHUTDOWN)
   │  ├─ wakeword_manager.stop()
   │  └─ cleanup
   │
   └─ Process exits
```

---

## Extensibility Points

### Adding a New Component

1. Create module in appropriate layer
2. Define event types it publishes/subscribes to
3. Register listeners in bootstrap
4. Update configuration if needed

### Example: Adding Vision

```python
# 1. Create vision/detector.py
class FaceDetector:
    def process_frame(self, frame):
        # Detect faces
        faces = ...
        event_bus.emit(FACE_DETECTED, {"count": len(faces)})

# 2. Create vision/listener.py
def on_face_detected(data):
    logger.info(f"Detected {data['count']} faces")

event_bus.subscribe(FACE_DETECTED, on_face_detected)

# 3. Register in bootstrap.py
from cosmo.vision.listener import *

# 4. Start in bootstrap.start()
runtime_manager.start_thread(
    target=face_detector.start,
    name="FaceDetector"
)
```

---

## Performance Considerations

### Latency

- **Wake Word Detection**: ~100-500ms (Vosk processing)
- **STT Processing**: Real-time (streaming)
- **Event Dispatch**: <1ms (synchronous bus)

### Resource Usage

- **Memory**: ~200-300 MB (Vosk model in RAM)
- **CPU**: 5-10% idle (wakeword detection)
- **CPU**: 20-30% active (STT processing)

### Optimization Opportunities

- Profile CPU/memory usage
- Cache Vosk model
- Implement frame dropping on high load
- Use async I/O exclusively

---

## Known Limitations

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for complete list. Key points:

1. **No async/await unified model** — Mix of threading and asyncio
2. **No error recovery** — Failed listeners aren't retried
3. **No persistence** — No automatic database migrations
4. **No authentication** — No user verification for commands
5. **No LLM integration** — No language model for responses

---

## Future Enhancements

### Short Term

- Async STTManager conversion
- Database migrations
- Error handling & recovery
- Configuration validation

### Medium Term

- Vision system implementation
- REST API
- WebSocket server
- Context/memory system

### Long Term

- LLM integration
- Task planning
- Distributed operation
- Mobile client support

---

**Document Version**: 1.0  
**Last Updated**: May 30, 2026  
**Scope**: Comprehensive system architecture and component interaction
