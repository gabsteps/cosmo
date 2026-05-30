# Developer Guide

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo> cosmo
cd cosmo

# Create virtual environment
python3 -m venv zenith
source zenith/bin/activate

# Install dependencies
pip install pyaudio vosk webrtcvad pyyaml

# Install development tools
pip install pytest pytest-cov black flake8 mypy
```

### Project Structure for Developers

```
cosmo/
├── cosmo/                        # Main package
│   ├── core/                     # Core infrastructure (stable)
│   ├── audio/                    # Audio pipeline (stable)
│   ├── vision/                   # Vision system (in dev)
│   ├── cognition/                # Cognition system (planned)
│   ├── data/                     # Data access layer (in dev)
│   └── interfaces/               # APIs (planned)
├── tests/                        # Test suite
├── docs/                         # Documentation
├── models/                       # ML models (Vosk, Piper, etc.)
├── data/                         # Runtime data (logs, database, cache)
└── main.py                       # Entry point
```

### Code Style

#### Python Code Style

- **Format**: Use `black` for automatic formatting
- **Linting**: Use `flake8` to catch issues
- **Type hints**: Use `mypy` for type checking

```bash
# Format code
black cosmo/

# Check style
flake8 cosmo/ --max-line-length=100

# Type checking
mypy cosmo/ --ignore-missing-imports
```

#### Naming Conventions

- **Modules**: `lowercase_with_underscores` (e.g., `audio_state.py`)
- **Classes**: `PascalCase` (e.g., `WakewordManager`)
- **Functions/Methods**: `lowercase_with_underscores` (e.g., `process_audio()`)
- **Constants**: `UPPERCASE_WITH_UNDERSCORES` (e.g., `WAKE_WORD_DETECTED`)
- **Singletons**: `lowercase` (e.g., `event_bus`, `logger`, `config`)

#### Documentation

- Use docstrings for public functions/classes (PEP 257)
- Use type hints for function signatures
- Keep comments concise and explain "why", not "what"

```python
def process_audio(audio_chunk: bytes) -> Optional[str]:
    """
    Process audio chunk and extract recognized text.
    
    Args:
        audio_chunk: Raw PCM audio data (16-bit, 16kHz)
    
    Returns:
        Recognized text or None if not ready
    """
    # Implementation
```

---

## Architecture Decisions

### Event-Driven Design

**Decision**: Use Pub/Sub pattern for inter-component communication

**Rationale**:
- Loose coupling between modules
- Easy to add new features without modifying existing code
- Event history traceable for debugging

**Implementation**:
- Synchronous event bus for critical events (low latency)
- Asynchronous event bus for background processing (durable)

**When to use each**:
- **Sync**: Wake word detection, system state changes
- **Async**: Database writes, heavy processing, logging

### Singleton Pattern for Core Components

**Decision**: Use singleton instances for: event_bus, logger, config, database, runtime

**Rationale**:
- Single source of truth
- Easy access from any module
- Prevents multiple instances causing conflicts

**Import pattern**:
```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.logger.logger_manager import logger
from cosmo.core.config.settings_manager import config
```

### State Machine for Audio

**Decision**: Use explicit state transitions (IDLE ↔ LISTENING)

**Rationale**:
- Prevents race conditions
- Clear state semantics
- Easy to debug state issues

**Implementation**:
```python
class AudioState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
```

---

## Adding New Features

### Example: Add a Custom Command Handler

1. **Create listener module**:

```python
# cosmo/interfaces/custom_listener.py
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import COMMAND_RECEIVED
from cosmo.core.logger.logger_manager import logger

def on_command_received(data):
    command = data.get("command")
    
    if "weather" in command.lower():
        logger.info("Handling weather command")
        # Add your logic
    
    elif "time" in command.lower():
        logger.info("Handling time command")
        # Add your logic

event_bus.subscribe(COMMAND_RECEIVED, on_command_received)
```

2. **Register listener in bootstrap**:

```python
# cosmo/core/bootstrap/bootstrap.py
from cosmo.interfaces import custom_listener  # Add import

class Bootstrap:
    def start(self):
        logger.info("Initializing Zenith Cosmo 42")
        lifecycle.start()
        
        event_bus.emit(SYSTEM_STARTED, {...})
        
        # Register custom listener
        custom_listener  # Import ensures subscription
        
        runtime_manager.start_thread(...)
```

3. **Test your listener**:

```python
# Test it
python3 << 'EOF'
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import COMMAND_RECEIVED
from cosmo.interfaces.custom_listener import *

# Emit test event
event_bus.emit(COMMAND_RECEIVED, {
    "command": "what is the weather?"
})
EOF
```

### Example: Add an Async Event Handler

```python
# cosmo/interfaces/async_handler.py
import asyncio
from cosmo.core.events.async_event_bus import async_event_bus
from cosmo.core.events.event_types import SPEECH_RECOGNIZED
from cosmo.core.logger.logger_manager import logger

async def handle_speech_async(data):
    text = data.get("text")
    logger.info(f"Async handling: {text}")
    
    # Do async work (network, database, etc)
    await asyncio.sleep(1)
    
    logger.info("Async handling complete")

# Register async listener
async_event_bus.subscribe(SPEECH_RECOGNIZED, handle_speech_async)
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest cosmo/tests/

# Run specific test
pytest cosmo/tests/critical_event_test.py

# Run with verbose output
pytest -v cosmo/tests/

# Generate coverage report
pytest --cov=cosmo --cov-report=html cosmo/tests/
```

### Writing Tests

Example test:

```python
# cosmo/tests/test_audio_state.py
import pytest
from cosmo.audio.audio_state import AudioState, audio_state

def test_audio_state_initial():
    """Audio state should start in IDLE"""
    assert audio_state.state == AudioState.IDLE

def test_audio_state_transition():
    """Audio state should transition to LISTENING"""
    audio_state.state = AudioState.LISTENING
    assert audio_state.state == AudioState.LISTENING
    
    # Reset
    audio_state.state = AudioState.IDLE
```

### Testing Event Bus

```python
# Test event emission
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED

def test_event_emission():
    called = {"flag": False}
    
    def listener(data):
        called["flag"] = True
    
    event_bus.subscribe(WAKE_WORD_DETECTED, listener)
    event_bus.emit(WAKE_WORD_DETECTED, {"word": "test"})
    
    assert called["flag"] is True
```

### Testing Configuration

```python
from cosmo.core.config.settings_manager import config

def test_config_access():
    sample_rate = config.get("audio", "sample_rate")
    assert sample_rate == 16000
    
    wake_words = config.get("wakeword", "words")
    assert "cosmo" in wake_words
```

---

## Debugging

### Enable Debug Logging

```bash
# Edit settings.yaml
logging:
  level: DEBUG

# Or run with:
COSMO_DEBUG=1 python cosmo/main.py
```

### View Real-time Logs

```bash
tail -f data/logs/cosmo.log
```

### Print Debug Info

```python
from cosmo.core.logger.logger_manager import logger
from cosmo.core.events.async_event_bus import async_event_bus

logger.debug(f"Variable value: {variable}")

# Print event bus metrics
metrics = async_event_bus.get_metrics()
logger.info(f"Events processed: {metrics['events_completed']}")
```

### Common Issues

**Issue**: Wake word not detected
- Check microphone device
- Check wake word configuration
- Enable debug logging
- Check Vosk model is present

**Issue**: Commands not recognized
- Check audio levels (microphone volume)
- Check silence threshold
- Try speaking louder/clearer
- Check language setting

**Issue**: High CPU usage
- Reduce audio.chunk_size
- Reduce logging level
- Check for infinite loops in listeners
- Profile code

---

## Code Organization

### Module Responsibilities

Each module should have a single, clear responsibility:

| Module | Responsibility |
|--------|-----------------|
| `wakeword_manager.py` | Audio capture loop + wake-word emission |
| `stt_manager.py` | Speech recognition loop + text emission |
| `vad_engine.py` | Voice activity detection logic |
| `event_bus.py` | Event dispatch mechanism |
| `logger_manager.py` | Logging infrastructure |
| `config.py` | Configuration loading |
| `database.py` | Database connection |
| `repositories/*` | Data access for specific entities |

### Avoid Cross-Module Coupling

**Bad**: One module imports and calls directly from another
```python
# ❌ DON'T
from cosmo.audio.stt_manager import stt_manager
stt_manager.listen_once()  # Direct call
```

**Good**: Use events to communicate
```python
# ✅ DO
event_bus.subscribe(WAKE_WORD_DETECTED, on_wake_word)
# STTManager is started by the listener, not directly called
```

---

## Performance Optimization

### Profiling

```bash
# Profile code execution
python -m cProfile -s cumulative cosmo/main.py | head -20
```

### Memory Usage

```bash
# Monitor memory
watch -n 1 'ps aux | grep python'

# Profile memory
pip install memory_profiler
python -m memory_profiler cosmo/main.py
```

### CPU Optimization

- Use `asyncio.to_thread()` for blocking I/O
- Avoid tight loops without sleep
- Cache expensive computations
- Profile before optimizing

---

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Type**: feat, fix, docs, test, refactor, perf, chore

**Example**:
```
feat: add async STT manager

- Convert STTManager to use asyncio.to_thread()
- Add timeout handling for speech recognition
- Improve responsiveness to long audio streams

Fixes #123
```

### Commit Best Practices

- Commit frequently with small, focused changes
- Write descriptive messages
- Reference issues in commits
- Test before committing

---

## Pull Request Process

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and commit
4. Push to your fork: `git push origin feature/my-feature`
5. Create pull request
6. Wait for review and CI checks

### PR Requirements

- ✅ Code passes linting (flake8, mypy)
- ✅ New tests added for new features
- ✅ Existing tests pass
- ✅ Documentation updated
- ✅ Commit messages are clear

---

## Future Development

### Async/Sync Unification

**Current**: Mixed paradigm (threading + asyncio)

**Goal**: Full asyncio-based system

**Steps**:
1. Convert STTManager to async
2. Remove RuntimeManager (use AsyncRuntime only)
3. Convert all I/O to async
4. Unify on asyncio.run()

### Error Handling

**Current**: Minimal error handling

**Goal**: Comprehensive recovery

**Implementation**:
- Add try/except to all I/O
- Implement retry logic
- Add circuit breakers
- Log all errors

### Database Migrations

**Current**: No migrations

**Goal**: Automated schema management

**Implementation**:
- Create migration framework
- Define schema versions
- Auto-migrate on startup

### Vision System

**Current**: Empty directories

**Goal**: Functional face detection/recognition

**Implementation**:
- Implement camera capture
- Add face detection (Haar Cascades)
- Add face recognition (embeddings)
- Integrate with user repository

---

## Architecture Principles

### Layered Architecture

```
Interface Layer (REST API, WebSocket, CLI)
  ↓
Business Logic Layer (Command processing, NLU)
  ↓
Data Layer (Database, repositories)
  ↓
Core Infrastructure (Event bus, Config, Logger)
  ↓
External Services (Vosk, PyAudio, SQLite)
```

### Separation of Concerns

Each module should do ONE thing well:
- Audio capture is separate from processing
- Event dispatch is separate from listeners
- Database connection is separate from queries
- Configuration loading is separate from usage

### Interface Segregation

Components interact via clear interfaces:
- Event bus for async communication
- Repository pattern for data access
- Configuration manager for settings
- Logger for logging

---

## Resources

- **Python**: https://docs.python.org/3.10/
- **asyncio**: https://docs.python.org/3/library/asyncio.html
- **Vosk**: https://github.com/alphacep/vosk-api
- **PyAudio**: https://people.csail.mit.edu/hubert/pyaudio/
- **WebRTC VAD**: https://github.com/wiseman/py-webrtcvad
- **YAML**: https://yaml.org/

---

**Last Updated**: May 30, 2026
