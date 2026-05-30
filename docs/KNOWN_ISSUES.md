# Known Issues & Limitations

## Summary

Cosmo is currently in active development (**Version 0.1.1**). While core voice interaction features are functional, several implementation gaps and design issues exist. This document tracks known problems and their recommended workarounds.

---

## Critical Issues 🔴

### 1. Repository Import Path Errors

**Status**: 🔴 CRITICAL - Breaks data access layer

**Files Affected**:
- `cosmo/data/database/repositories/user_repository.py`
- `cosmo/data/database/repositories/conversation_repository.py`
- `cosmo/data/database/repositories/face_repository.py`
- `cosmo/data/database/repositories/event_repository.py`

**Problem**:
```python
# ❌ CURRENT (incorrect)
from database import db

# Should be
from cosmo.data.database.database import db
```

**Impact**: All repository operations fail at runtime with `ModuleNotFoundError`

**Workaround**: Manually fix imports before using database:
```bash
cd cosmo/data/database/repositories
sed -i 's/from database import db/from cosmo.data.database.database import db/g' *.py
```

**Fix ETA**: Next release

---

### 2. No Database Table Initialization

**Status**: 🔴 CRITICAL - Database is non-functional

**File**: `cosmo/data/database/database.py`

**Problem**: No `CREATE TABLE` statements. Database exists but has no schema.

**Impact**: Any attempt to use repositories raises: `sqlite3.OperationalError: no such table`

**Workaround**: Manually create tables:
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

db.execute("""
CREATE TABLE IF NOT EXISTS memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  content TEXT NOT NULL,
  importance INTEGER DEFAULT 50,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS faces (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  face_data BLOB NOT NULL,
  embedding_vector BLOB,
  confidence REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  data JSON,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS system (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

print("Tables created successfully")
EOF
```

**Fix ETA**: Next release (automatic migrations)

---

### 3. Configuration Path Issues

**Status**: 🔴 CRITICAL - System won't start from wrong directory

**Files Affected**:
- `cosmo/core/config/settings_manager.py` — Uses `Path("cosmo/core/config/settings.yaml")`
- `cosmo/data/database/database.py` — Uses `Path("data/database/cosmo.db")`

**Problem**: Hardcoded relative paths fail if running from directory other than project root

**Example Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'cosmo/core/config/settings.yaml'
```

**Workaround**: Always run from project root
```bash
cd /path/to/cosmo
python cosmo/main.py  # Works

cd /path/to/cosmo/cosmo
python main.py  # Fails - wrong directory
```

**Fix ETA**: Next release (use `__file__` for absolute paths)

---

## High Priority Issues ⚠️

### 4. STTManager is Synchronous Only

**Status**: ⚠️ HIGH - Inconsistent with async architecture

**File**: `cosmo/audio/stt/stt_manager.py`

**Problem**:
```python
# ❌ CURRENT - synchronous blocking I/O
def listen_once(self):
    stream.read(self.chunk_size)  # Blocks until data available
```

**Should be**:
```python
# ✅ SHOULD BE - async
async def listen_once(self):
    await asyncio.to_thread(
        self.stream.read,
        self.chunk_size
    )
```

**Impact**:
- Blocks the thread during audio processing
- Cannot be used with async event bus
- Inconsistent with system's async architecture

**Workaround**: Currently functional but not optimal. Consider running in separate thread (already done in bootstrap).

**Fix ETA**: Next release (async conversion)

---

### 5. Mixed Async/Sync Paradigm

**Status**: ⚠️ HIGH - Architecture inconsistency

**Problem**: System uses both:
- Threading approach (RuntimeManager, WakewordManager starting threads)
- Asyncio approach (AsyncEventBus, AsyncRuntime)

**Impact**:
- Confusing for developers
- Suboptimal performance
- Hard to debug concurrency issues

**Recommended Fix**: Consolidate on asyncio-only approach

**Timeline**: 2-4 weeks

---

### 6. No Error Handling in I/O Operations

**Status**: ⚠️ HIGH - Crashes on audio/database errors

**Files Affected**: All audio and database modules

**Examples**:
```python
# ❌ No error handling
audio_data = self.stream.read(chunk_size)  # Can raise OSError
result = stt_engine.process_audio(audio_data)  # Can raise exception
db.execute(query)  # Can raise sqlite3 errors
```

**Should be**:
```python
# ✅ With error handling
try:
    audio_data = self.stream.read(chunk_size)
except OSError as e:
    logger.error(f"Audio read failed: {e}")
    # Handle recovery
```

**Impact**:
- System crashes on microphone disconnection
- Database errors not logged
- No recovery mechanism

**Workaround**: Manually restart system on errors

**Fix ETA**: Next 1-2 releases

---

### 7. Missing Repository Implementations

**Status**: ⚠️ HIGH - Data access incomplete

**Missing Files**:
- `cosmo/data/database/repositories/memory_repository.py` — Documented but missing
- `cosmo/data/database/repositories/system_repository.py` — Documented but missing

**Impact**: Cannot store/retrieve user memories or system state

**Workaround**: Manually implement using ConversationRepository as template

**Fix ETA**: Next release

---

## Medium Priority Issues 📋

### 8. No Input Validation

**Status**: 📋 MEDIUM - Silent failures on bad config

**Problem**: Configuration values are not validated

**Example**:
```yaml
audio:
  chunk_size: 0  # Invalid - should be > 0
  sample_rate: 8000  # Invalid - Vosk requires 16000
```

**Impact**: Vague runtime errors instead of clear config messages

**Workaround**: Follow CONFIGURATION_REFERENCE.md strictly

**Fix ETA**: 1-2 months

---

### 9. Hardcoded Logging Configuration

**Status**: 📋 MEDIUM - Can't change logging level from YAML

**Problem**: Log level hardcoded to DEBUG in logger_manager.py

```python
# ❌ CURRENT
logger.setLevel(logging.DEBUG)  # Hardcoded

# Should be
logger.setLevel(getattr(logging, config.get("logging", "level", "DEBUG")))
```

**Impact**: Cannot reduce verbosity via YAML configuration

**Workaround**: Edit Python code if you need to change log level

**Fix ETA**: Next release

---

### 10. No Database Migrations

**Status**: 📋 MEDIUM - Schema changes break existing data

**Problem**: No migration framework exists

**Impact**: 
- Adding new database columns requires manual migration
- No version tracking
- Data loss risk on schema changes

**Workaround**: Manual database updates using SQL

**Fix ETA**: 2-3 releases

---

### 11. TTS Not Integrated

**Status**: 📋 MEDIUM - Piper configured but not used

**File**: `cosmo/core/config/settings.yaml` (TTS section configured)

**Problem**: Piper voice synthesis is in config but not implemented

**Impact**: System can only receive commands, cannot speak responses

**Current Status**: Configuration ready, implementation pending

**Fix ETA**: Next 1-2 months

---

### 12. Minimal Error Recovery

**Status**: 📋 MEDIUM - No retry logic or circuit breaker

**Problem**: 
- Failed listeners not retried
- No exponential backoff
- No circuit breaker pattern

**Impact**:
- One failed listener can impact others
- Resource leaks possible
- No graceful degradation

**Fix ETA**: 2-3 months

---

## Low Priority Issues 🔵

### 13. No Type Hints

**Status**: 🔵 LOW - Code quality concern

**Problem**: Limited use of Python type hints

**Impact**: Harder to catch bugs, worse IDE support

**Fix ETA**: Ongoing improvement

---

### 14. Deprecated Threading Approach

**Status**: 🔵 LOW - Will be removed in favor of asyncio

**Files**: `cosmo/core/runtime/runtime_manager.py`

**Status**: RuntimeManager uses threading, should use AsyncRuntime

**Timeline**: Will be phased out

---

### 15. No Docstrings in Core Modules

**Status**: 🔵 LOW - Documentation gap

**Problem**: Many functions lack docstrings

**Impact**: Harder to understand code, worse IDE documentation

**Fix ETA**: Ongoing improvement

---

## Limitations (By Design)

### Vision System Not Implemented

**Status**: 🔴 Not Started

- No face detection
- No face recognition
- No person tracking

**ETA**: 2-4 months

---

### Cognition System Not Implemented

**Status**: 🔴 Not Started

- No NLU (natural language understanding)
- No context tracking
- No memory system
- No personality traits

**ETA**: 3-6 months

---

### REST API Not Implemented

**Status**: 🔴 Not Started

**Impact**: No programmatic API access (only voice interaction)

**ETA**: 2-3 months

---

### No LLM Integration

**Status**: 🔴 Not Started

**Impact**: Cannot generate natural responses, only basic command processing

**ETA**: 4-6 months

---

### Portuguese Only (STT)

**Status**: ⚠️ By Design for Now

**Current**: Vosk model supports Portuguese only (PT-BR)

**Future**: Plan multi-language support

**Workaround**: System only works in Portuguese

---

## Workarounds Summary

| Issue | Quick Fix |
|-------|-----------|
| Import errors | Fix imports manually or use symlink |
| Missing tables | Run manual CREATE TABLE script |
| Config path | Run from project root |
| STT sync | Already working, just not async |
| No TTS | Remove from future plans or wait for implementation |
| No error handling | Keep microphone connected, restart on errors |
| No migrations | Manual SQL updates |
| Log level fixed | Edit logger_manager.py |

---

## Reporting Issues

Found a bug not listed here? Please:

1. Check this document
2. Search GitHub issues
3. Reproduce minimally
4. Report with: version, steps to reproduce, error message, environment

---

## Contribution Opportunities

Help wanted in:

1. **Async/Sync Unification** — Convert remaining modules to asyncio
2. **Error Handling** — Add comprehensive error handling
3. **Database Migrations** — Implement migration framework
4. **Vision System** — Implement face detection/recognition
5. **REST API** — Build REST interface
6. **Type Hints** — Add type annotations throughout
7. **Tests** — Expand test coverage

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for contribution guidelines.

---

**Document Version**: 1.0  
**Last Updated**: May 30, 2026  
**Scope**: Known issues, limitations, and workarounds for Cosmo 0.1.1
