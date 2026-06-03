# Zenith Cosmo

A Python robot in the making built around an async event bus, wake-word detection, offline speech recognition, LLM-backed response generation, and text-to-speech synthesis.

## Overview

Zenith Cosmo is an intelligent companion that operates entirely locally (with optional cloud LLM integrations). It features:

- **Wake Word Detection**: Continuous microphone monitoring using Vosk wake word recognition
- **Speech Recognition**: Offline transcription via Vosk STT
- **Response Generation**: LLM-powered responses with configurable personality and memory
- **Text-to-Speech**: Local synthesis using Piper TTS
- **Event-Driven Architecture**: Async event bus for efficient task coordination
- **Local Commands**: Built-in command handling for system-level operations
- **Persistent Memory**: SQLite-backed conversation memory and learning
- **Personality System**: Runtime personality controls and customization

The system is written primarily in Brazilian Portuguese and is configured through YAML settings and SQLite persistence.

## Getting Started

*Full for comprehensive documentation soon containig:*

- System architecture and component overview
- Detailed pipeline descriptions (audio, STT, cognition, TTS)
- Event system and runtime state machine
- Configuration, logging, and data persistence
- Development workflow and testing

## Quick Start

```bash
python -m cosmo.main
```

The entry point is `cosmo/main.py`, which initializes the bootstrap sequence and starts the boy.
