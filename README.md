# Cosmo - Zenith AI Assistant

**A privacy-first, offline-capable AI voice assistant built in Python with modular architecture.**

Cosmo is an intelligent voice assistant designed to run completely locally on your hardware, offering real-time voice interaction, wake-word detection, speech recognition, and persistent memory—all without external API dependencies.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo>
cd cosmo

# Create and activate Python 3.10+ virtual environment
python3 -m venv zenith
source zenith/bin/activate

# Install core dependencies
pip install pyaudio vosk webrtcvad pyyaml

# Run the assistant
python cosmo/main.py
```

## 📋 Features

### ✅ Implemented
- **Voice Interaction Pipeline** — Real-time audio capture and processing
- **Wake Word Detection** — Offline wake-word recognition (default: "cosmo", "zenith")
- **Speech-to-Text (STT)** — Portuguese language support via Vosk
- **Voice Activity Detection (VAD)** — Smart silence detection for command boundaries
- **Event-Driven Architecture** — Pub/Sub pattern for decoupled communication
- **Persistent Storage** — SQLite database for conversations and user memories
- **Dual Event Bus** — Synchronous (critical events) + Asynchronous (background processing)
- **Configuration Management** — YAML-based centralized settings
- **Thread-Safe Operations** — Audio state machine prevents race conditions

### 🟡 In Development
- **Vision System** — Facial detection and recognition
- **Cognitive Intelligence** — Natural language understanding, context, personality
- **API Interfaces** — REST API, CLI, WebSocket support
- **Text-to-Speech (TTS)** — Voice synthesis with Piper (configured but not yet integrated)

### 🔴 Planned
- **LLM Integration** — Local LLM support (Ollama, LM Studio)
- **Advanced Memory** — Semantic and episodic memory systems
- **Task Planning** — Automated task scheduling and execution
- **Distributed Operation** — Multi-instance coordination

## 📂 Project Structure

```
cosmo/
├── core/                           # System core infrastructure
│   ├── bootstrap/                  # Initialization and lifecycle
│   ├── config/                     # Configuration management
│   ├── events/                     # Event bus (sync & async)
│   ├── logger/                     # Logging system
│   ├── runtime/                    # Thread/async runtime management
│   └── scheduler/                  # Task scheduling (planned)
├── audio/                          # Voice processing pipeline
│   ├── wakeword/                   # Wake-word detection
│   ├── stt/                        # Speech-to-text recognition
│   ├── vad/                        # Voice activity detection
│   └── tts/                        # Text-to-speech (planned)
├── vision/                         # Visual processing (in development)
│   ├── camera/                     # Video capture
│   ├── detection/                  # Face/object detection
│   ├── recognition/                # Face recognition
│   └── tracking/                   # Person tracking
├── cognition/                      # AI and intelligence (planned)
│   ├── context/                    # Conversation context
│   ├── memory/                     # Memory management
│   ├── personality/                # Assistant personality
│   └── planner/                    # Task planning
├── data/                           # Data persistence layer
│   ├── database/                   # SQLite database + repositories
│   ├── cache/                      # Audio/data caching
│   ├── embeddings/                 # Face/semantic embeddings
│   └── logs/                       # Application logs
├── interfaces/                     # External interfaces (planned)
│   ├── api/                        # REST API
│   ├── cli/                        # Command-line interface
│   └── websocket/                  # WebSocket server
├── models/                         # ML models and data
│   ├── vosk/                       # Speech recognition model (PT-BR)
│   ├── piper/                      # TTS voice models
│   └── embeddings/                 # Face embedding models
├── tests/                          # Test suite
├── main.py                         # Entry point
├── settings.yaml                   # Configuration file
└── README.md (this file)
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.10+ | Primary implementation |
| **Audio Input** | PyAudio | Microphone stream capture |
| **Speech Recognition** | Vosk (Kaldi) | Offline STT (Portuguese) |
| **Voice Activity Detection** | WebRTC VAD | Silence detection |
| **Text-to-Speech** | Piper | Voice synthesis (not yet integrated) |
| **Computer Vision** | OpenCV | Face detection (Haar Cascades) |
| **Database** | SQLite3 | Persistent data storage |
| **Configuration** | YAML | Settings management |
| **Event Bus** | Custom Python | Pub/Sub event dispatch |
| **Async Runtime** | asyncio | Concurrent task management |

## 📖 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System design, component interactions, data flows
- **[INSTALLATION.md](docs/INSTALLATION.md)** — Setup instructions, dependencies, troubleshooting
- **[CONFIGURATION_REFERENCE.md](docs/CONFIGURATION_REFERENCE.md)** — All configurable parameters
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** — Event types, public APIs, usage examples
- **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** — Development workflow, extending the system
- **[KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)** — Current limitations, bugs, and workarounds
- **[DOCUMENTACAO_SISTEMA.md](DOCUMENTACAO_SISTEMA.md)** — Complete system documentation (Portuguese, detailed)

## 🎯 Core Workflows

### 1. Wake Word Detection → Command Processing

```
User speaks "Cosmo" → Wakeword Engine detects (confidence check)
  ↓
WAKE_WORD_DETECTED event emitted
  ↓
Audio state changes to LISTENING
  ↓
STT Manager listens for command (timeout: 30s, silence: 3s)
  ↓
VAD Engine detects voice activity + silence
  ↓
SPEECH_RECOGNIZED event with text
  ↓
Command saved to database
  ↓
State returns to IDLE (awaiting next wake word)
```

### 2. Event-Driven Communication

```
Event Emitted → Event Bus → Registered Listeners → Callbacks Executed
```

The system uses two parallel event buses:
- **Synchronous** — Critical events (wake word, speech) with immediate dispatch
- **Asynchronous** — Background processing with queue, metrics, and timeout handling

## 🔧 Configuration

Core settings in `cosmo/core/config/settings.yaml`:

```yaml
system:
  name: "Zenith Cosmo 42"
  language: "pt-BR"

audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024

wakeword:
  words: ["cosmo", "zenith"]
  enabled: true

stt:
  silence_threshold_ms: 3000
  max_listening_time_ms: 30000

database:
  path: "data/database/cosmo.db"

logging:
  level: "DEBUG"
  file_path: "data/logs/cosmo.log"
```

See [CONFIGURATION_REFERENCE.md](docs/CONFIGURATION_REFERENCE.md) for all options.

## 🗄️ Data Persistence

SQLite database with repositories for:
- **Users** — Profiles, face IDs, trust levels
- **Conversations** — Message history per user
- **Memories** — User facts, preferences, events
- **Faces** — Face embeddings for recognition
- **Events** — System event log
- **System** — Runtime configuration

## 🔌 APIs & Events

### Key Event Types

**Audio Events:**
```python
WAKE_WORD_DETECTED      # {"word": str, "confidence": float}
SPEECH_RECOGNIZED       # {"text": str, "user_id": int}
VOICE_ACTIVITY_STARTED  # {}
VOICE_ACTIVITY_ENDED    # {}
```

**System Events:**
```python
SYSTEM_STARTED          # {}
SYSTEM_SHUTDOWN         # {"reason": str}
SYSTEM_SLEEP            # {}
SYSTEM_WAKE             # {}
```

See [API_REFERENCE.md](docs/API_REFERENCE.md) for complete event listing.

## 📊 Async Event Bus Metrics

The async event bus automatically collects:
- **Events**: received, emitted, dispatched, dropped, completed, failed, partial_failures
- **Listeners**: successes, timeouts, errors
- **Queue**: peak size, current size
- **Performance**: avg event/listener processing time

Access via: `async_event_bus.get_metrics()`

## ⚙️ Running the System

```bash
# Start the assistant
python cosmo/main.py

# Expected output:
# [2026-05-30 10:30:00] [INFO] Initializing Zenith Cosmo 42
# [2026-05-30 10:30:01] [INFO] Wakeword manager online
# [2026-05-30 10:30:01] [INFO] Zenith Cosmo 42 online ✓
# (Listening for wake word...)
```

Say "Cosmo" to activate, then speak your command. After 3 seconds of silence or 30 seconds total, the command is processed and stored.

## ⚠️ Known Issues

See [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) for current limitations, including:
- Repository import path issues
- STTManager is synchronous only (should be async)
- No database table initialization
- Configuration paths are relative to working directory
- Minimal error handling in I/O operations

## 🚀 Roadmap

**Short Term (1-2 months)**
- [ ] Integrate TTS (Piper)
- [ ] Fix async/sync consistency
- [ ] Implement NLU basics
- [ ] Database migrations

**Medium Term (2-4 months)**
- [ ] Vision system (face detection/recognition)
- [ ] REST API
- [ ] CLI interface
- [ ] Memory system

**Long Term (4+ months)**
- [ ] LLM integration
- [ ] Advanced cognition
- [ ] Distributed operation
- [ ] Docker deployment

## 📝 Development

### Setting Up Development Environment

```bash
python -m venv zenith
source zenith/bin/activate
pip install pyaudio vosk webrtcvad pyyaml

# Optional: development tools
pip install pytest black flake8
```

### Running Tests

```bash
cd cosmo
python tests/critical_event_test.py
python tests/stress_test.py
python tests/priority_test.py
```

See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for contribution guidelines and architecture details.

## 📄 License

Licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 👤 Author

Created as a personal AI exploration project by enthusiast developers.

## 🤝 Contributing

Contributions are welcome! See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for guidelines on:
- Code style
- Commit conventions
- Pull request process
- Architecture principles

---

**Version**: 0.1.1 (ZC-42 with Async Infrastructure)  
**Last Updated**: May 30, 2026  
**Status**: Active Development
