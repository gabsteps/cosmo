# Configuration Reference

## Overview

Cosmo uses a centralized YAML configuration file at `cosmo/core/config/settings.yaml`. All system parameters can be configured without modifying code.

## Full Configuration File

```yaml
# System Identity & Behavior
system:
  name: "Zenith Cosmo 42"
  codename: "ZC-42"
  version: "0.1.1"
  language: "pt-BR"
  timezone: "America/Sao_Paulo"
  debug: true

# Audio Input Configuration
audio:
  sample_rate: 16000              # Hz - Standard for speech processing
  channels: 1                     # Mono input
  chunk_size: 1024                # Samples per chunk (~64ms at 16kHz)
  dtype: "int16"                  # Audio data type
  device_index: null              # null = default device, or integer device ID

# Wake Word Detection Settings
wakeword:
  enabled: true
  words:
    - "cosmo"
    - "cosmos"
    - "cosme"
    - "zenith"
    - "zênite"
  confidence_threshold: 0.7       # Min confidence (0.0-1.0) to accept detection

# Speech-to-Text (STT) Configuration
stt:
  engine: "vosk"
  silence_threshold_ms: 3000      # Silence duration to end listening
  max_listening_time_ms: 30000    # Max time to listen for command
  confidence_threshold: 0.5       # Min confidence for final result

# Voice Activity Detection
vad:
  engine: "webrtcvad"
  aggressiveness: 2               # 0 (low) to 3 (high) sensitivity
  frame_ms: 30                    # MUST BE 30 for WebRTC (fixed)

# Text-to-Speech (Not Yet Integrated)
tts:
  engine: "piper"
  language: "pt-BR"
  voice_model: "pt_BR-faber-medium"
  speed: 1.0                      # 0.5-2.0
  volume: 1.0                     # 0.0-2.0

# Vision System (In Development)
vision:
  enabled: false
  camera_index: 0
  resolution:
    width: 640
    height: 480
  grayscale: true
  face_detector: "haar"           # haar, yolo, mediapipe (future)
  face_recognition_model: "facenet"

# Face Recognition Settings
face_recognition:
  confidence_threshold: 70        # 0-100 (percentage)

# Memory Configuration
memory:
  max_conversation_history: 20    # Sliding window size
  max_memories_per_user: 100

# Database Configuration
database:
  type: "sqlite"
  path: "data/database/cosmo.db"
  enable_wal: true                # Write-Ahead Logging
  foreign_keys: true              # Enforce referential integrity
  synchronous: "NORMAL"           # NORMAL, FULL, OFF

# Logging Configuration
logging:
  level: "DEBUG"                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  console: true                   # Output to console
  file: true                      # Output to file
  file_path: "data/logs/cosmo.log"
  max_file_size_mb: 10
  backup_count: 5

# Task Scheduler (Not Yet Implemented)
scheduler:
  enabled: false
  timezone: "America/Sao_Paulo"
  max_workers: 4
```

## Configuration Parameters

### System Section

```yaml
system:
  name: "Zenith Cosmo 42"          # Display name of the system
  codename: "ZC-42"                # Internal identifier
  version: "0.1.1"                 # Current version
  language: "pt-BR"                # Language code (pt-BR, en-US, etc.)
  timezone: "America/Sao_Paulo"    # IANA timezone for timestamps
  debug: true                      # Enable debug mode
```

| Parameter | Type | Valid Values | Purpose |
|-----------|------|--------------|---------|
| `name` | string | Any | Display name |
| `language` | string | `pt-BR`, `en-US`, etc. | UI/NLP language |
| `debug` | boolean | `true`, `false` | Debug logging |
| `timezone` | string | IANA timezone | For timestamps |

### Audio Section

```yaml
audio:
  sample_rate: 16000              # Sample rate in Hz
  channels: 1                     # Number of channels (1=mono, 2=stereo)
  chunk_size: 1024                # Samples per read operation
  dtype: "int16"                  # Audio format (int16, float32, etc.)
  device_index: null              # Microphone device (-1=default, 0=first, etc.)
```

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `sample_rate` | 8000-48000 | 16000 | Vosk requires 16000 |
| `channels` | 1-2 | 1 | Mono recommended |
| `chunk_size` | 512-4096 | 1024 | Larger = less responsive |
| `device_index` | null or 0-N | null | Use `null` for default |

**Finding your device index**:

```bash
python3 << 'EOF'
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"[{i}] {info['name']}")
p.terminate()
EOF
```

### Wakeword Section

```yaml
wakeword:
  enabled: true
  words:
    - "cosmo"
    - "zenith"
  confidence_threshold: 0.7
```

| Parameter | Type | Range | Notes |
|-----------|------|-------|-------|
| `enabled` | boolean | - | Enable/disable wake-word detection |
| `words` | list | - | Portuguese words only (Vosk PT-BR) |
| `confidence_threshold` | float | 0.0-1.0 | Higher = stricter matching |

**Changing Wake Words**:

```yaml
wakeword:
  words:
    - "assistente"
    - "ai"
    - "comando"
```

### STT Section

```yaml
stt:
  engine: "vosk"
  silence_threshold_ms: 3000      # Time of silence to end listening
  max_listening_time_ms: 30000    # Maximum listening duration
  confidence_threshold: 0.5       # Minimum confidence score
```

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `silence_threshold_ms` | 1000-10000 | 3000 | Milliseconds |
| `max_listening_time_ms` | 5000-60000 | 30000 | Milliseconds |
| `confidence_threshold` | 0.0-1.0 | 0.5 | Vosk confidence |

### VAD Section

```yaml
vad:
  engine: "webrtcvad"
  aggressiveness: 2               # 0=low, 1=medium-low, 2=medium, 3=high
  frame_ms: 30                    # MUST be 30 (WebRTC requirement)
```

| Parameter | Range | Notes |
|-----------|-------|-------|
| `aggressiveness` | 0-3 | 2 is recommended for speech recognition |
| `frame_ms` | Fixed | Must be 30ms (WebRTC requirement) |

### TTS Section

```yaml
tts:
  engine: "piper"
  language: "pt-BR"
  voice_model: "pt_BR-faber-medium"
  speed: 1.0                      # 0.5-2.0x
  volume: 1.0                     # 0.0-2.0
```

| Parameter | Values | Notes |
|-----------|--------|-------|
| `engine` | `piper` | Only option supported |
| `voice_model` | Model name | From Piper voice list |
| `speed` | 0.5-2.0 | 1.0 = normal speed |
| `volume` | 0.0-2.0 | 1.0 = normal volume |

**⚠️ Note**: TTS is configured but not yet integrated into the system.

### Vision Section

```yaml
vision:
  enabled: false
  camera_index: 0
  resolution:
    width: 640
    height: 480
  grayscale: true
  face_detector: "haar"
  face_recognition_model: "facenet"
```

| Parameter | Notes |
|-----------|-------|
| `enabled` | Set to `true` when vision module is ready |
| `camera_index` | 0 = default camera, 1 = second camera, etc. |
| `grayscale` | `true` = faster processing, `false` = color |

### Face Recognition Section

```yaml
face_recognition:
  confidence_threshold: 70        # 0-100 (percentage)
```

Match confidence must be ≥ this threshold to recognize as known user.

### Memory Section

```yaml
memory:
  max_conversation_history: 20    # Number of messages to keep
  max_memories_per_user: 100      # Maximum memories per user
```

These limit database storage for long-running systems.

### Database Section

```yaml
database:
  type: "sqlite"
  path: "data/database/cosmo.db"
  enable_wal: true                # Write-Ahead Logging
  foreign_keys: true              # Enforce foreign key constraints
  synchronous: "NORMAL"           # Synchronous mode
```

| Parameter | Values | Notes |
|-----------|--------|-------|
| `path` | File path | Relative or absolute |
| `enable_wal` | `true`/`false` | Allows concurrent read/write |
| `synchronous` | `OFF`, `NORMAL`, `FULL` | Balance speed vs safety |

### Logging Section

```yaml
logging:
  level: "DEBUG"                  # Log level
  console: true                   # Console output
  file: true                      # File output
  file_path: "data/logs/cosmo.log"
  max_file_size_mb: 10            # Log rotation threshold
  backup_count: 5                 # Number of backup logs to keep
```

**Log Levels**:
- `DEBUG` — Detailed debugging information
- `INFO` — General informational messages
- `WARNING` — Warning messages
- `ERROR` — Error messages
- `CRITICAL` — Critical system errors

**Example Output**:
```
[2026-05-30 10:30:00,123] [INFO] [wakeword_manager] Wakeword manager online
[2026-05-30 10:30:05,456] [WARNING] [event_bus] Listener took 5s to execute
[2026-05-30 10:30:10,789] [ERROR] [audio] Microphone error: Permission denied
```

### Scheduler Section

```yaml
scheduler:
  enabled: false
  timezone: "America/Sao_Paulo"
  max_workers: 4
```

**Note**: Not yet implemented.

---

## Configuration Best Practices

### 1. Use Relative Paths for Development

```yaml
database:
  path: "data/database/cosmo.db"    # Relative to project root

logging:
  file_path: "data/logs/cosmo.log"
```

### 2. Customize for Your Environment

```yaml
audio:
  device_index: 2                  # Set to YOUR microphone device

system:
  language: "en-US"              # Change to your language
  timezone: "America/New_York"   # Your timezone
```

### 3. Optimize for Low-End Hardware

```yaml
# For Raspberry Pi or old CPU
audio:
  chunk_size: 2048               # Larger chunks = less processing
  
vad:
  aggressiveness: 0              # Lower sensitivity = less CPU

logging:
  level: "INFO"                  # Less logging overhead
```

### 4. Optimize for Low Latency

```yaml
# For responsive wake-word detection
audio:
  chunk_size: 512                # Smaller chunks = more responsive
  
wakeword:
  confidence_threshold: 0.6      # Slightly lower threshold
```

### 5. Strict Confidence Requirements

```yaml
wakeword:
  confidence_threshold: 0.9       # Very strict
  
stt:
  confidence_threshold: 0.8
```

### 6. Development Configuration

```yaml
system:
  debug: true

logging:
  level: "DEBUG"                 # Detailed logs

database:
  synchronous: "FULL"            # Safer but slower
```

### 7. Production Configuration

```yaml
system:
  debug: false

logging:
  level: "INFO"                  # Less verbose

database:
  synchronous: "NORMAL"          # Balanced
  path: "/var/lib/cosmo/cosmo.db"  # System directory
```

---

## Accessing Configuration in Code

```python
from cosmo.core.config.settings_manager import config

# Simple access
sample_rate = config.get("audio", "sample_rate")

# Nested access
language = config.get("system", "language")

# With default
device_id = config.get("audio", "device_index", default=0)

# Get entire section
audio_config = config.get("audio")
```

---

## Configuration Validation

Current status: ⚠️ No validation

The system does not validate configuration values. Invalid values will cause runtime errors.

**Recommendations**:
- Use valid values from this reference
- Start with default values, change gradually
- Test each configuration change
- Check logs for errors

---

## Troubleshooting Configuration

### "Settings file not found"

**Error**: `FileNotFoundError: cosmo/core/config/settings.yaml`

**Solution**:
1. Check file exists: `ls cosmo/core/config/settings.yaml`
2. Run from project root: `cd /path/to/cosmo && python cosmo/main.py`

### "Invalid YAML syntax"

**Error**: `yaml.YAMLError: ...`

**Solution**:
1. Check YAML syntax (indentation, quotes)
2. Use online YAML validator: https://www.yamllint.com/
3. Fix quotes and indentation

### "Value out of range"

May cause runtime errors. Examples:
- `audio.sample_rate: 8000` (should be 16000)
- `audio.chunk_size: 0` (must be > 0)
- `vad.aggressiveness: 5` (must be 0-3)

### Paths not found

**Error**: `FileNotFoundError: data/database/cosmo.db`

**Solution**:
1. Create directories: `mkdir -p data/database data/logs`
2. Or use absolute paths: `/home/user/cosmo/data/database/cosmo.db`

---

## Version Compatibility

This configuration reference applies to **Cosmo 0.1.1**.

Future versions may introduce new parameters or deprecate old ones.

---

**Last Updated**: May 30, 2026
