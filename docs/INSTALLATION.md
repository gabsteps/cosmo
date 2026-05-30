# Installation & Setup Guide

## System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.10 or higher
- **RAM**: Minimum 2 GB (4 GB recommended for Vosk model)
- **Storage**: 2 GB for models and database
- **Microphone**: USB or integrated audio input device
- **Optional**: USB camera for vision features (future)

## Quick Start (Linux/macOS)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/cosmo.git
cd cosmo
```

### 2. Create Virtual Environment

```bash
python3 -m venv zenith
source zenith/bin/activate  # Linux/macOS
# or on Windows:
# zenith\Scripts\activate
```

### 3. Install Core Dependencies

```bash
pip install --upgrade pip
pip install pyaudio vosk webrtcvad pyyaml
```

### 4. Download Vosk Model (PT-BR)

The Portuguese speech recognition model is already included in `cosmo/models/vosk/`. If missing, download it:

```bash
cd cosmo/models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
rm vosk-model-small-pt-0.3.zip
```

### 5. Create Data Directories

```bash
mkdir -p data/database
mkdir -p data/logs
mkdir -p data/cache/audio
```

### 6. Verify Audio Device

```bash
python3 << 'EOF'
import pyaudio

p = pyaudio.PyAudio()
print(f"Available audio devices: {p.get_device_count()}")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"  [{i}] {info['name']} (in: {info['maxInputChannels']}, out: {info['maxOutputChannels']})")
p.terminate()
EOF
```

If your microphone isn't detected, update `cosmo/core/config/settings.yaml`:

```yaml
audio:
  device_index: <your_device_number>  # e.g., 2
```

### 7. Test Installation

```bash
python cosmo/main.py
```

**Expected output**:
```
[2026-05-30 10:30:00] [INFO] [bootstrap] Initializing Zenith Cosmo 42
[2026-05-30 10:30:01] [INFO] [lifecycle] System started
[2026-05-30 10:30:02] [INFO] [wakeword_manager] Wakeword manager online
[2026-05-30 10:30:02] [INFO] [bootstrap] Zenith Cosmo 42 online ✓
```

Say "Cosmo" to test wake-word detection.

---

## Detailed Installation

### Prerequisites

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.10 python3.10-venv python3.10-dev \
    build-essential \
    libasound2-dev \
    portaudio19-dev
```

#### macOS

```bash
brew install python@3.10 portaudio
```

#### Windows (WSL2)

```bash
# In WSL2 terminal
sudo apt-get update
sudo apt-get install -y \
    python3.10 python3.10-venv python3.10-dev \
    build-essential \
    libasound2-dev \
    portaudio19-dev
```

### Dependency Installation

#### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **pyaudio** | ≥0.2.11 | Audio I/O (microphone capture) |
| **vosk** | ≥0.3.45 | Offline speech recognition (Kaldi) |
| **webrtcvad** | ≥2.0.10 | Voice activity detection |
| **pyyaml** | ≥6.0 | Configuration file parsing |

```bash
pip install pyaudio vosk webrtcvad pyyaml
```

#### Optional Dependencies

For development and testing:

```bash
pip install pytest pytest-cov black flake8 mypy
```

### Verify Dependencies

```bash
python3 << 'EOF'
import sys
packages = {
    'pyaudio': 'Audio I/O',
    'vosk': 'Speech Recognition',
    'webrtcvad': 'Voice Activity Detection',
    'yaml': 'Configuration',
}

for pkg, desc in packages.items():
    try:
        __import__(pkg)
        print(f"✓ {pkg:15} - {desc}")
    except ImportError:
        print(f"✗ {pkg:15} - {desc} [MISSING]")
        sys.exit(1)
EOF
```

---

## Configuration

### Initial Setup

1. **Copy configuration template** (if provided):
   ```bash
   cp cosmo/core/config/settings.yaml.example cosmo/core/config/settings.yaml
   ```

2. **Edit settings** for your environment:
   ```bash
   nano cosmo/core/config/settings.yaml
   ```

3. **Key settings to configure**:
   - `audio.device_index` — Your microphone device number
   - `wakeword.words` — Wake words to listen for
   - `stt.silence_threshold_ms` — Silence detection threshold
   - `logging.level` — Log verbosity (DEBUG, INFO, WARNING)

See [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md) for all options.

### Test Configuration

```bash
python3 << 'EOF'
from cosmo.core.config.settings_manager import config

# Test config loading
print("System:", config.get("system", "name"))
print("Language:", config.get("system", "language"))
print("Sample Rate:", config.get("audio", "sample_rate"))
print("Wake Words:", config.get("wakeword", "words"))
EOF
```

---

## Running the System

### Basic Execution

```bash
python cosmo/main.py
```

### With Verbose Logging

The system logs to both console and file. To change log level:

1. Edit `cosmo/core/config/settings.yaml`:
   ```yaml
   logging:
     level: DEBUG  # More verbose
   ```

2. Run the system:
   ```bash
   python cosmo/main.py
   ```

3. View real-time logs:
   ```bash
   tail -f data/logs/cosmo.log
   ```

### Running in Background

```bash
# Using nohup
nohup python cosmo/main.py > data/logs/cosmo.out 2>&1 &

# Using screen
screen -S cosmo
python cosmo/main.py
# Press Ctrl+A then D to detach

# Using tmux
tmux new-session -d -s cosmo 'python cosmo/main.py'
```

### Stopping the System

```bash
# Find process
ps aux | grep "python cosmo/main.py"

# Kill by PID
kill <PID>

# Or send SIGTERM (graceful)
kill -TERM <PID>
```

---

## Troubleshooting

### Audio Device Not Detected

**Problem**: System hangs or reports "No audio device"

**Solution**:
1. List available devices:
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

2. Update `settings.yaml`:
   ```yaml
   audio:
     device_index: <device_number>
   ```

3. Test audio capture:
   ```bash
   python3 -c "import pyaudio; p = pyaudio.PyAudio(); s = p.open(format=8, channels=1, rate=16000, input=True, input_device_index=<N>, frames_per_buffer=1024); data = s.read(1024); print('Audio OK')"
   ```

### "ModuleNotFoundError: No module named 'pyaudio'"

**Solution**: Install with system audio libraries

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev
pip install --no-cache-dir pyaudio
```

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

### "ModuleNotFoundError: No module named 'vosk'"

**Solution**: Install vosk package
```bash
pip install vosk
```

**Note**: Vosk model must also be present in `cosmo/models/vosk/vosk-model-small-pt-0.3/`

### Vosk Model Missing

**Error**: `OSError: [Errno 2] No such file or directory`

**Solution**:
```bash
cd cosmo/models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
```

### "Wake word not detected"

**Debugging**:
1. Check microphone is working: `arecord -d 3 test.wav`
2. Check wake word configuration:
   ```bash
   python3 -c "from cosmo.core.config import config; print(config.get('wakeword', 'words'))"
   ```
3. Try speaking louder and clearer
4. Check if "cosmo" is in the configured words

### Database Errors

**Error**: `sqlite3.OperationalError: no such table: users`

**Solution**: Initialize database tables

```bash
python3 << 'EOF'
from cosmo.data.database.database import db

# Create tables
db.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  face_id TEXT,
  trust_level INTEGER DEFAULT 50,
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  role TEXT CHECK (role IN ('user', 'assistant')),
  message TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

print("Tables created")
EOF
```

### Config File Not Found

**Error**: `FileNotFoundError: cosmo/core/config/settings.yaml`

**Solution**: Ensure YAML file exists and working directory is correct

```bash
pwd  # Should show /path/to/cosmo
ls cosmo/core/config/settings.yaml
```

If running from different directory:

```bash
cd /path/to/cosmo
python cosmo/main.py
```

---

## Development Setup

### Install Development Tools

```bash
pip install pytest black flake8 mypy sphinx
```

### Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (if not exists)
# Then install hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest cosmo/tests/

# Run specific test
pytest cosmo/tests/critical_event_test.py

# With coverage
pytest --cov=cosmo cosmo/tests/
```

### Code Style

```bash
# Format code
black cosmo/

# Check style
flake8 cosmo/

# Type checking
mypy cosmo/
```

---

## Uninstallation

### Remove Virtual Environment

```bash
deactivate
rm -rf zenith/
```

### Remove Application

```bash
rm -rf cosmo/
```

### Clean Data

```bash
rm -rf data/
```

---

## Platform-Specific Notes

### Linux

- **ALSA warnings**: Normal, can be suppressed with: `export ALSA_CARD=default`
- **PulseAudio**: Ensure enabled: `pactl info`
- **Permission denied**: Grant microphone permission if using snap/container

### macOS

- **Microphone permission**: Grant in System Preferences → Security & Privacy → Microphone
- **Python version**: Use `python3`, not `python` (may be Python 2)
- **M1/M2 Macs**: Use `pip install --upgrade` for native ARM builds

### Windows (WSL2)

- **Audio passthrough**: Must configure PulseAudio or ALSA
- **Microphone**: May need additional configuration in Windows Sound settings
- **Path separators**: Code is Python (uses `/`), should work fine

---

## Next Steps

1. **Configure Wake Words**: Edit `settings.yaml` to customize wake words
2. **Test Voice Commands**: Say "Cosmo" then speak a simple command
3. **Monitor Logs**: `tail -f data/logs/cosmo.log`
4. **Read Documentation**: See README.md and other docs in `docs/` folder
5. **Extend System**: Add custom commands or components

---

## Support

If you encounter issues:

1. Check [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for known problems
2. Review logs: `data/logs/cosmo.log`
3. Enable DEBUG logging in settings.yaml
4. Test components individually (see DEVELOPER_GUIDE.md)

---

**Last Updated**: May 30, 2026  
**Version**: 1.0
