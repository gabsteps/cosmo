# 📚 DOCUMENTAÇÃO COMPLETA DO SISTEMA COSMO

**Versão**: 0.1.1 (ZC-42 com Infraestrutura Assíncrona)  
**Data**: 30 de Maio de 2026  
**Língua**: Português (Brasil)  
**Status**: Desenvolvimento Ativo

---

## ⚡ INÍCIO RÁPIDO

### Instalação Mínima

```bash
python3 -m venv zenith && source zenith/bin/activate
pip install pyaudio vosk webrtcvad pyyaml
mkdir -p data/{database,logs,cache/audio}
python cosmo/main.py
```

Diga "Cosmo" para ativar o sistema.

**Para documentação completa de instalação**: Ver [INSTALLATION.md](docs/INSTALLATION.md)

---

## 📖 GUIA DE DOCUMENTAÇÃO

Este projeto possui documentação estruturada em múltiplos documentos:

| Documento | Tipo | Audiência | Conteúdo |
|-----------|------|-----------|----------|
| **[README.md](README.md)** | Visão geral | Todos | Features, quick start, tecnologia |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Design | Arquitetos/Devs | Arquitetura em camadas, fluxos, padrões |
| **[INSTALLATION.md](docs/INSTALLATION.md)** | Setup | DevOps/Usuários | Instalação, dependências, troubleshooting |
| **[CONFIGURATION_REFERENCE.md](docs/CONFIGURATION_REFERENCE.md)** | Referência | Operadores | Todos os parâmetros de configuração |
| **[API_REFERENCE.md](docs/API_REFERENCE.md)** | Técnico | Desenvolvedores | Tipos de eventos, APIs públicas |
| **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** | Como fazer | Contribuidores | Workflow, testes, extensibilidade |
| **[KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)** | Referência | Todos | Bugs conhecidos, limitações, workarounds |
| **[DOCUMENTACAO_SISTEMA.md](DOCUMENTACAO_SISTEMA.md)** | Completo | Tecnical Deep Dive | Este arquivo - análise técnica profunda |

---

## 🎯 ÍNDICE DO SISTEMA

Este documento cobre:

1. [Identidade do Projeto](#1-identidade-do-projeto)
2. [Arquitetura em Camadas](#2-arquitetura-em-camadas)
3. [Estrutura de Módulos](#3-estrutura-de-módulos)
4. [Ciclo de Vida & Bootstrap](#4-ciclo-de-vida--bootstrap)
5. [Pipeline de Áudio](#5-pipeline-de-áudio)
6. [Sistema de Eventos](#6-sistema-de-eventos)
7. [Persistência de Dados](#7-persistência-de-dados)
8. [Máquinas de Estado](#8-máquinas-de-estado)
9. [Padrões de Design](#9-padrões-de-design)
10. [Configuração do Sistema](#10-configuração-do-sistema)
11. [Fluxos de Dados](#11-fluxos-de-dados)
12. [Mudanças Recentes](#12-mudanças-recentes)
13. [Roadmap Futuro](#13-roadmap-futuro)
14. [Limitações & Problemas Conhecidos](#14-limitações--problemas-conhecidos)

---

## 1. Identidade do Projeto

### Conceito

**Cosmo** (Zenith Cosmo 42, ou ZC-42) é um assistente de voz inteligente multimodal executado localmente, com processamento offline, sem dependência de APIs externas, com ênfase em privacidade e responsividade.

### Objetivo Principal

Criar uma plataforma de interação de voz em tempo real que:
- ✅ Funciona completamente offline
- ✅ Detecta palavras-chave ("cosmo", "zenith")
- ✅ Reconhece comandos em português (STT via Vosk)
- ✅ Persiste dados do usuário (memórias, histórico)
- ⚠️ Integra visão (futuro - facial recognition)
- ⚠️ Oferece inteligência cognitiva (futuro - NLU, planejamento)
- ⚠️ Expõe APIs externas (futuro - REST, CLI, WebSocket)

### Stack Técnico

```
Python 3.10+
├─ PyAudio (I/O de áudio)
├─ Vosk + Kaldi (STT offline, Wakeword)
├─ WebRTC VAD (Detecção de atividade de voz)
├─ Piper (TTS - não integrado)
├─ OpenCV (Visão - não integrado)
├─ SQLite3 (Persistência)
├─ asyncio (Runtime assíncrono)
└─ YAML (Configuração)
```

### Filosofia de Design

1. **Offline First** — Sem cloud, sem APIs, sem internet
2. **Privacy by Default** — Todos os dados locais
3. **Modular Decoupling** — Componentes independentes via eventos
4. **Event-Driven** — Comunicação assíncrona via pub/sub
5. **State Safety** — Máquinas de estado explícitas

---

## 2. Arquitetura em Camadas

### Modelo de Camadas

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 5: Interfaces Externas (Planejadas)             │
│  REST API | CLI | WebSocket                             │
├─────────────────────────────────────────────────────────┤
│  CAMADA 4: Inteligência Cognitiva (Em Desenvolvimento)  │
│  Contexto | Memória | Personalidade | Planejador       │
├─────────────────────────────────────────────────────────┤
│  CAMADA 3: Processamento Sensorial (Parcial)           │
│  Audio (STT, TTS, VAD, Wakeword) | Visão (Em dev)      │
├─────────────────────────────────────────────────────────┤
│  CAMADA 2: Núcleo do Sistema (Implementado)            │
│  Event Bus | Config | Logger | Runtime | Scheduler     │
├─────────────────────────────────────────────────────────┤
│  CAMADA 1: Persistência (Parcial)                      │
│  Database | Repositories                                │
├─────────────────────────────────────────────────────────┤
│  CAMADA 0: Recursos Externos                            │
│  Modelos (Vosk, Piper) | Haar Cascades | Configuração │
└─────────────────────────────────────────────────────────┘
```

### Princípios Arquiteturais

**Desacoplamento Vertical**:
- Camadas superiores não dependem de implementações inferiores
- Uso de abstrações (repositories, event bus, interfaces)
- Injeção de dependência onde apropriado

**Desacoplamento Horizontal**:
- Módulos da mesma camada comunicam via eventos
- Não há chamadas diretas entre componentes
- Event bus coordena todas as interações

**Inversão de Controle**:
- Event bus controla o fluxo
- Componentes reagem a eventos
- Sem hierarquia síncrona de chamadas

### Padrão Dual: Event Bus Síncrono + Assíncrono

```
SINCRONIZADO (crítico)
├─ Dispatching imediato (blocking)
├─ Sem overhead de métricas
└─ Uso: WAKE_WORD_DETECTED, eventos de sistema

ASSÍNCRONO (background)
├─ Fila bounded (max 100 eventos)
├─ Dispatching deferred via asyncio
├─ 19 métricas em tempo real
├─ UUID tracing por evento
└─ Uso: Processamento pesado, I/O, database
```

---

## 3. Estrutura de Módulos

### Organização Geral

```
cosmo/
├── core/                        # Núcleo (implementado ✅)
│   ├── bootstrap/              # Inicialização & lifecycle
│   ├── config/                 # Gerenciamento de configuração
│   ├── events/                 # Event bus (sync + async)
│   ├── logger/                 # Sistema de logging
│   ├── runtime/                # Gerenciamento de threads/async
│   └── scheduler/              # Agendamento (futuro)
│
├── audio/                      # Pipeline de áudio (parcial ⚠️)
│   ├── wakeword/              # Detecção de palavra-chave
│   ├── stt/                   # Speech-to-text
│   ├── vad/                   # Voice activity detection
│   ├── tts/                   # Text-to-speech (não integrado)
│   └── audio_state.py         # Máquina de estados
│
├── vision/                     # Visão (não implementado 🔴)
│   ├── camera/
│   ├── detection/
│   ├── recognition/
│   └── tracking/
│
├── cognition/                  # Cognição (não implementado 🔴)
│   ├── context/
│   ├── memory/
│   ├── personality/
│   └── planner/
│
├── data/                       # Persistência (parcial ⚠️)
│   ├── database/              # SQLite + driver
│   ├── repositories/          # Acesso a dados (padrão Repository)
│   └── cache/                 # Cache de áudio/dados
│
├── interfaces/                 # APIs externas (não implementado 🔴)
│   ├── api/                   # REST API
│   ├── cli/                   # CLI interface
│   └── websocket/             # WebSocket server
│
├── models/                     # Modelos ML
│   ├── vosk/                  # Modelo de reconhecimento (PT-BR)
│   ├── piper/                 # Modelos TTS
│   └── embeddings/            # Face embeddings
│
├── tests/                      # Suite de testes
│   ├── critical_event_test.py
│   ├── priority_test.py
│   ├── stress_test.py
│   └── test_event_bus_metrics.py
│
├── docs/                       # Documentação
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── CONFIGURATION_REFERENCE.md
│   ├── API_REFERENCE.md
│   ├── DEVELOPER_GUIDE.md
│   └── KNOWN_ISSUES.md
│
├── main.py                     # Ponto de entrada
├── README.md                   # Visão geral (inglês)
└── DOCUMENTACAO_SISTEMA.md    # Este arquivo (português)
```

### Responsabilidades por Módulo

| Módulo | Responsabilidade | Status |
|--------|------------------|--------|
| `bootstrap` | Inicialização e sequência de startup | ✅ |
| `event_bus` | Dispatch sincronizado de eventos | ✅ |
| `async_event_bus` | Dispatch assíncrono com fila e métricas | ✅ |
| `config` | Carregamento e acesso à configuração | ✅ |
| `logger` | Logging para console e arquivo | ✅ |
| `runtime` | Gerenciamento de threads e tasks | ⚠️ |
| `wakeword_manager` | Loop de captura e detecção de wakeword | ✅ |
| `stt_manager` | Escuta de comando e STT | ⚠️ |
| `vad_engine` | Detecção de atividade de voz | ✅ |
| `database` | Conexão e pragmas SQLite | ⚠️ |
| `repositories` | Acesso a dados (CRUD) | ⚠️ |

---

## 4. Ciclo de Vida & Bootstrap

### Sequência de Inicialização

```
┌─ main.py
│   └─ bootstrap.start()
│       ├─ lifecycle.start()
│       │  └─ lifecycle.running = True
│       │
│       ├─ event_bus.emit(SYSTEM_STARTED, {})
│       │  └─ system_listener invocado
│       │     └─ Log: "Sistema iniciado"
│       │
│       ├─ runtime_manager.start_event_pipeline()
│       │  ├─ Register audio_listener
│       │  ├─ Register conversation_listener
│       │  ├─ Register vision_listener
│       │  └─ Register system_listener
│       │
│       ├─ runtime_manager.start_thread(
│       │   target=wakeword_manager.start,
│       │   name="WakewordManager"
│       │ )
│       │  └─ Thread daemon criada
│       │
│       └─ runtime_manager.wait_forever()
│          └─ Bloqueia esperando threads filhas
│
└─ Sistema aguardando wake word
```

### Logs Esperados

```
[2026-05-30 10:30:00] [INFO] [bootstrap] Inicializando Zenith Cosmo 42
[2026-05-30 10:30:00] [INFO] [lifecycle] Sistema iniciado
[2026-05-30 10:30:01] [INFO] [wakeword_manager] Wakeword manager online
[2026-05-30 10:30:01] [INFO] [bootstrap] Zenith Cosmo 42 online ✓
```

### Estados do Ciclo de Vida

```
NOT_STARTED
    ↓
RUNNING (lifecycle.running = True)
    ├─ AWAKE (lifecycle.sleeping = False)
    ├─ SLEEPING (lifecycle.sleeping = True)
    │   ↓
    │ [SYSTEM_WAKE event]
    │   ↓
    └─ AWAKE
    ↓
STOPPING (bootstrap.shutdown() chamado)
    ↓
STOPPED
```

---

## 5. Pipeline de Áudio

### Fluxo de Captura

```
WakewordManager (thread daemon)
├─ PyAudio.open(
│   format=paInt16,
│   channels=1,
│   rate=16000,
│   input=True,
│   frames_per_buffer=1024
│ )
│
├─ Loop infinito:
│   ├─ audio_data = stream.read(1024)  [~64ms de áudio]
│   ├─ wakeword_engine.process_audio(audio_data)
│   ├─ if word_detected:
│   │  ├─ audio_state.state = LISTENING
│   │  └─ event_bus.emit(WAKE_WORD_DETECTED, {word, confidence})
│   │     └─ audio_listener invocado
│   │        └─ runtime_manager.start_thread(stt_manager.listen_once)
│   │
│   └─ else: continua looping
│
└─ loop continua até stop()
```

### Captura de Comando (STT)

```
STTManager (thread criada por audio_listener)
├─ PyAudio.open(...)  [nova stream]
│
├─ Loop até timeout ou silêncio:
│   ├─ audio_data = stream.read(1024)
│   │
│   ├─ vad_engine.is_speech(audio_data)
│   │  ├─ if SIM:
│   │  │  ├─ silence_start = None
│   │  │  └─ stt_engine.process_audio(audio_data)
│   │  │
│   │  └─ if NÃO:
│   │     ├─ if silence_start is None:
│   │     │  └─ silence_start = time.time()
│   │     │
│   │     └─ if time.time() - silence_start > 3.0:
│   │        └─ BREAK
│   │
│   └─ if total_time > 30.0:
│       └─ BREAK
│
├─ final_text = stt_engine.get_final_result()
│
├─ stream.close()
│
├─ event_bus.emit(SPEECH_RECOGNIZED, {
│   text: "qual é a hora",
│   confidence: 0.89
│  })
│  └─ conversation_listener invocado
│     ├─ conversation_repository.add_message(user_id, "user", text)
│     └─ command_processor.process_command(text)
│
├─ audio_state.state = IDLE
│
└─ thread encerra
```

### Máquina de Estados de Áudio

```
        ┌─────────────────────┐
        │       IDLE          │
        │ WakewordManager on  │
        │ STT off             │
        └────────┬────────────┘
                 │
      [WAKE_WORD_DETECTED]
                 │
                 ▼
        ┌─────────────────────┐
        │    LISTENING        │
        │ STT ativo           │
        │ VAD detectando      │
        └────────┬────────────┘
                 │
    [SPEECH_RECOGNIZED ou TIMEOUT]
                 │
                 ▼
        ┌─────────────────────┐
        │       IDLE          │
        └─────────────────────┘
```

### Timing de Áudio

```
Sample Rate:     16000 Hz (16 mil amostras por segundo)
Chunk Size:      1024 amostras
Chunk Duration:  1024 / 16000 = 64 ms

VAD Frame:       30 ms (requerido por WebRTC)

Silence Timeout: 3000 ms (3 segundos padrão)
Max Listen:      30000 ms (30 segundos máximo)

Wakeword Latency: 100-500 ms
STT Latency:     Real-time (streaming)
```

---

## 6. Sistema de Eventos

### Tipos de Eventos Implementados

#### 6.1 Eventos de Áudio

| Evento | Emitente | Dados | Listeners |
|--------|----------|-------|-----------|
| `WAKE_WORD_DETECTED` | WakewordEngine | `{word, confidence}` | audio_listener |
| `SPEECH_RECOGNIZED` | STTManager | `{text, confidence}` | conversation_listener |
| `VOICE_ACTIVITY_STARTED` | VADEngine | `{timestamp}` | Nenhum |
| `VOICE_ACTIVITY_ENDED` | VADEngine | `{timestamp}` | Nenhum |

#### 6.2 Eventos de Sistema

| Evento | Emitente | Dados | Listeners |
|--------|----------|-------|-----------|
| `SYSTEM_STARTED` | Bootstrap | `{system, version}` | system_listener |
| `SYSTEM_SHUTDOWN` | Bootstrap | `{reason, timestamp}` | Nenhum |
| `SYSTEM_SLEEP` | - | `{timestamp}` | Nenhum |
| `SYSTEM_WAKE` | - | `{timestamp}` | Nenhum |

#### 6.3 Eventos de Visão (Planejados)

| Evento | Emitente | Dados | Listeners |
|--------|----------|-------|-----------|
| `FACE_DETECTED` | FaceDetector | `{count, faces: []}` | vision_listener |
| `USER_RECOGNIZED` | FaceRecognizer | `{user_id, confidence}` | vision_listener |
| `UNKNOWN_FACE` | FaceRecognizer | `{face_id, bbox}` | vision_listener |

#### 6.4 Eventos de Conversação

| Evento | Emitente | Dados | Listeners |
|--------|----------|-------|-----------|
| `COMMAND_RECEIVED` | App | `{command, user_id}` | Processador |
| `CONVERSATION_STARTED` | App | `{user_id, timestamp}` | Nenhum |
| `CONVERSATION_FINISHED` | App | `{user_id, duration}` | Nenhum |

### Infraestrutura Assíncrona (Nova ⭐)

#### 6.5 Event Bus Assíncrono

Implementado em `async_event_bus.py`:

```python
class AsyncEventBus:
    def __init__(self):
        self.listeners = defaultdict(list)
        self.max_queue_size = 100
        self.queue = asyncio.Queue(maxsize=100)
        self.running = False
        self.listener_timeout = 10
        
    async def emit(self, event_name, data=None, priority=None):
        """Enfileira evento para processamento assíncrono"""
        event = {
            "id": uuid.uuid4(),      # Rastreamento único
            "name": event_name,
            "data": data,
            "created_at": time.time()
        }
        self.queue.put_nowait(event)  # Enfileira
        
    async def start(self):
        """Loop principal de processamento de eventos"""
        while self.running:
            event = await self.queue.get()
            asyncio.create_task(self._dispatch_event(event))
            self.queue.task_done()
            
    async def _dispatch_event(self, event):
        """Executa listeners com timeout e rastreamento"""
        listeners = self.listeners.get(event["name"], [])
        
        tasks = [
            asyncio.create_task(
                asyncio.wait_for(
                    listener(event["data"]),
                    timeout=10  # 10 segundos por listener
                )
            )
            for listener in listeners
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Métricas coletadas automaticamente
```

#### 6.6 Métricas Colhidas (19 no Total)

**Eventos** (7 métricas):
- `events_received` — Tentativa de emissão
- `events_emitted` — Entrou na fila
- `events_dispatched` — Saiu da fila
- `events_dropped` — Rejeitado (fila cheia)
- `events_completed` — Todos listeners OK
- `events_failed` — Todos listeners falharam
- `events_partial_failures` — Alguns falharam

**Listeners** (3 métricas):
- `listener_successes` — Execução OK
- `listener_timeouts` — Excedeu 10s
- `listener_errors` — Exceção lançada

**Fila** (2 métricas):
- `queue_peak` — Tamanho máximo atingido
- `current_queue_size` — Tamanho atual

**Performance** (2 métricas):
- `avg_event_processing_time` — Tempo médio evento
- `avg_listener_processing_time` — Tempo médio listener

**UUID Tracing**:
Cada evento possui UUID para rastreamento completo:
```
[TRACE] 550e8400-e29b-41d4-a716-446655440000 queued → WAKE_WORD_DETECTED
[TRACE] 550e8400-e29b-41d4-a716-446655440000 dispatched → WAKE_WORD_DETECTED
[TRACE] 550e8400-e29b-41d4-a716-446655440000 listener_started → audio_listener
[TRACE] 550e8400-e29b-41d4-a716-446655440000 listener_finished → audio_listener
[TRACE] 550e8400-e29b-41d4-a716-446655440000 event_completed → WAKE_WORD_DETECTED
```

---

## 7. Persistência de Dados

### Banco de Dados SQLite

**Arquivo**: `data/database/cosmo.db`

**Configuração**:
```python
PRAGMA foreign_keys = ON;        # Integridade referencial
PRAGMA journal_mode = WAL;       # Write-Ahead Logging (concorrência)
PRAGMA synchronous = NORMAL;     # Balanceamento segurança/performance
```

### Schema de Tabelas

#### Tabela: users

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  face_id TEXT,
  trust_level INTEGER DEFAULT 50,    -- 0-100
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: conversations

```sql
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  role TEXT CHECK (role IN ('user', 'assistant')),
  message TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

#### Tabela: memories

```sql
CREATE TABLE memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  category TEXT NOT NULL,           -- preference, fact, event, etc
  content TEXT NOT NULL,
  importance INTEGER DEFAULT 50,    -- 0-100
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
Create INDEX idx_memories_category ON memories(category);
```

#### Tabela: faces

```sql
CREATE TABLE faces (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  face_data BLOB NOT NULL,          -- Encoding de face
  embedding_vector BLOB,             -- Embeddings numéricos
  confidence REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Tabela: events

```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,         -- WAKE_WORD_DETECTED, etc
  data JSON,                         -- Metadados do evento
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_events_type ON events(event_type);
```

#### Tabela: system

```sql
CREATE TABLE system (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Padrão Repository

Cada entidade tem um Repository para acesso:

```python
# Exemplo: UserRepository
class UserRepository:
    def create_user(self, name: str) -> int:
        """Cria novo usuário"""
        
    def get_user_by_id(self, user_id: int) -> dict:
        """Busca usuário por ID"""
        
    def get_user_by_name(self, name: str) -> dict:
        """Busca usuário por nome"""
        
    def update_trust_level(self, user_id: int, level: int):
        """Atualiza nível de confiança"""
        
    def list_users(self) -> list:
        """Lista todos os usuários"""
```

**Status**: ⚠️ Import errors em repositories (usar full path)

---

## 8. Máquinas de Estado

### Audio State Machine

```
Estado: IDLE
├─ WakewordManager ativo
├─ STT inativo
└─ Aguardando palavra-chave

Evento: WAKE_WORD_DETECTED
  └─ audio_state.state = LISTENING

Estado: LISTENING
├─ STTManager ativo
├─ WakewordManager bloqueado
└─ Aguardando fim da fala

Evento: SPEECH_RECOGNIZED ou TIMEOUT
  └─ audio_state.state = IDLE
     └─ Volta ao início
```

### System Lifecycle State Machine

```
Estado: NOT_STARTED
  └─ bootstrap.start() chamado

Estado: RUNNING
├─ lifecycle.running = True
├─ Threads ativas
└─ Eventos processados

Sub-estado: AWAKE
├─ lifecycle.sleeping = False
└─ Sistema processando normalmente

Sub-estado: SLEEPING
├─ lifecycle.sleeping = True
└─ Sistema em modo sleep (futuro)

Evento: SYSTEM_SHUTDOWN
  └─ bootstrap.shutdown() chamado

Estado: STOPPED
  └─ Todas as threads encerradas
```

---

## 9. Padrões de Design

### 9.1 Pub/Sub (Observer Pattern)

**Implementação**: Event Bus

```python
# Publicador
event_bus.emit(WAKE_WORD_DETECTED, {"word": "cosmo"})

# Subscriber
event_bus.subscribe(WAKE_WORD_DETECTED, callback)

# Callback
def callback(data):
    print(f"Wake word: {data['word']}")
```

**Vantagens**:
- Desacoplamento total entre publicador e subscribers
- Fácil adicionar novos listeners
- Testável (mock do event bus)

### 9.2 Singleton Pattern

**Componentes Globais**:
```python
from cosmo.core.events.event_bus import event_bus           # Única instância
from cosmo.core.logger.logger_manager import logger         # Única instância
from cosmo.core.config.settings_manager import config       # Única instância
from cosmo.data.database.database import db                 # Única instância
```

**Vantagens**:
- Estado centralizado
- Acesso fácil de qualquer lugar
- Previne múltiplas instâncias conflitantes

### 9.3 Repository Pattern

**Implementação**: Data Access Layer

```python
class UserRepository:
    def get_user_by_id(self, id): ...
    def create_user(self, name): ...
    def update_user(self, id, data): ...

# Uso
user = user_repository.get_user_by_id(1)
```

**Vantagens**:
- Abstração de SQL
- Fácil trocar banco de dados
- Lógica de negócio separada de persistência

### 9.4 Manager Pattern

**Responsabilidade**: Orquestração de componentes complexos

```python
class WakewordManager:
    def __init__(self, engine, event_bus, audio_state):
        self.engine = engine
        self.event_bus = event_bus
        self.audio_state = audio_state
    
    def start(self):
        # Orquestra: abrir stream, processar, emitir
```

### 9.5 State Machine Pattern

**Responsabilidade**: Controle de fluxo com transições explícitas

```python
class AudioState(Enum):
    IDLE = "idle"
    LISTENING = "listening"

# Uso
audio_state.state = AudioState.LISTENING
if audio_state.state == AudioState.IDLE:
    # Processar wakeword
```

---

## 10. Configuração do Sistema

### Arquivo: settings.yaml

**Localização**: `cosmo/core/config/settings.yaml`

**Estrutura Completa**:

```yaml
system:
  name: "Zenith Cosmo 42"
  codename: "ZC-42"
  version: "0.1.1"
  language: "pt-BR"
  timezone: "America/Sao_Paulo"
  debug: true

audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024
  device_index: null

wakeword:
  enabled: true
  words:
    - cosmo
    - zenith
  confidence_threshold: 0.7

stt:
  engine: vosk
  silence_threshold_ms: 3000
  max_listening_time_ms: 30000

vad:
  engine: webrtcvad
  aggressiveness: 2
  frame_ms: 30

tts:
  engine: piper
  voice_model: pt_BR-faber-medium
  speed: 1.0

database:
  path: data/database/cosmo.db
  enable_wal: true

logging:
  level: DEBUG
  file_path: data/logs/cosmo.log
```

**Acesso em Código**:

```python
from cosmo.core.config.settings_manager import config

sample_rate = config.get("audio", "sample_rate")        # 16000
wake_words = config.get("wakeword", "words")            # ["cosmo", "zenith", ...]
silence_ms = config.get("stt", "silence_threshold_ms")  # 3000
```

---

## 11. Fluxos de Dados

### Fluxo Completo: Wakeword → Comando → Persistência

```
[T=00ms] User diz "Cosmo qual é a hora"

[T=100ms] WakewordEngine detecta "cosmo"
          ├─ Confiança: 0.94
          └─ event_bus.emit(WAKE_WORD_DETECTED, {word: "cosmo", confidence: 0.94})

[T=101ms] audio_listener invocado
          └─ runtime_manager.start_thread(stt_manager.listen_once)
          └─ audio_state.state = LISTENING

[T=150ms] STTManager thread iniciada
          ├─ Abre novo stream PyAudio
          └─ Aguarda fala

[T=200ms] User continua: "qual é a hora"
          └─ VADEngine detecta voice activity

[T=1500ms] Reconhecimento em progresso
          └─ stt_engine acumula texto parcial

[T=3000ms] Silêncio detectado (3 segundos)
          ├─ stt_engine retorna texto final: "qual é a hora"
          ├─ stream.close()
          └─ event_bus.emit(SPEECH_RECOGNIZED, {
               text: "qual é a hora",
               confidence: 0.89
             })

[T=3001ms] conversation_listener invocado
          ├─ conversation_repository.add_message(1, "user", "qual é a hora")
          │  └─ INSERT INTO conversations (user_id, role, message) VALUES (1, "user", "qual é a hora")
          │
          ├─ command_processor.process_command("qual é a hora")
          │  └─ Identifica intenção
          │
          └─ audio_state.state = IDLE

[T=3002ms] WakewordManager retoma aguardando próxima palavra-chave

[T=3100ms] Database escreveu mensagem em data/database/cosmo.db
```

### Timeline de Eventos

```
E1: WAKE_WORD_DETECTED
    └─ Dispara audio_listener (síncrono)

E2: SPEECH_RECOGNIZED
    └─ Dispara conversation_listener (síncrono)

E3: CONVERSATION_FINISHED (futuro)
    └─ Dispara async listeners (fila)

E4: MEMORY_CREATED (futuro)
    └─ Persiste em database (async)
```

---

## 12. Mudanças Recentes

### Sprint Atual: Infraestrutura Assíncrona ⭐

**Novos Componentes**:

1. **async_event_bus.py** (562 linhas)
   - Fila assíncrona bounded (max 100)
   - 19 métricas em tempo real
   - UUID tracing por evento
   - Timeout de 10s por listener
   - Rastreamento de sucesso/timeout/erro

2. **async_runtime.py** (52 linhas)
   - AsyncRuntime para orquestração de tasks
   - create_task(), start(), shutdown()
   - Heartbeat periódico (5s)

3. **system_async_listener.py** (60 linhas)
   - Exemplo de async listener
   - Demonstra wait_for() com timeout
   - Rastreamento de sucesso

4. **task_manager.py** (15 linhas)
   - Wrapper para create_task()
   - Interface simplificada

**Padrão Dual Implementado**:

✅ Event Bus Síncrono (já existia)
- Dispatching imediato
- Sem overhead de métricas
- Para eventos críticos

✅ Event Bus Assíncrono (NEW)
- Fila bounded
- 19 métricas detalhadas
- Listeners com timeout
- UUID tracing
- Rastreamento de erros

**Benefícios**:
- ✅ Eventos críticos (wakeword) mantêm baixa latência
- ✅ Eventos pesados processam concorrentemente
- ✅ Coleta de métricas sem overhead em críticos
- ✅ Escalável para novos tipos de evento
- ✅ Facilita debugging com UUID tracing

---

## 13. Roadmap Futuro

### Curto Prazo (1-2 meses)

**Audio/Voice**:
- [ ] Integrar TTS (Piper)
- [ ] Melhorar VAD (tuning de agressiveness)
- [ ] Suporte a múltiplas línguas

**Core**:
- [ ] Converter STTManager para async
- [ ] Unificar async/sync (remover threading)
- [ ] Implementar Database migrations

**Data**:
- [ ] Implementar repositories faltantes
- [ ] Implementar table creation automática

### Médio Prazo (2-4 meses)

**Vision**:
- [ ] Detecção facial (Haar Cascades)
- [ ] Reconhecimento facial (embeddings)
- [ ] Rastreamento de pessoas

**Cognition**:
- [ ] NLU básico (intent detection)
- [ ] Context manager
- [ ] Memory system

**Interfaces**:
- [ ] REST API (FastAPI ou Flask)
- [ ] CLI (argparse ou click)
- [ ] WebSocket server

### Longo Prazo (4+ meses)

**Inteligência Avançada**:
- [ ] Integração com LLM local (Ollama)
- [ ] Planejamento de tarefas
- [ ] Raciocínio multimodal

**DevOps**:
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Telemetria e monitoramento

---

## 14. Limitações & Problemas Conhecidos

### Críticos 🔴

1. **Import errors em repositories** — Quebra data layer
2. **Sem table creation** — Database não funcional
3. **Config paths relativos** — Falha se não executar do root

Ver [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) para workarounds.

### Altos ⚠️

4. **STTManager síncrono** — Não usa async
5. **Paradigma misto** — Threading + asyncio juntos
6. **Sem error handling** — Crashes em erros I/O

### Médios 📋

7. **Sem validação** — Config values não validados
8. **Sem migrations** — Schema changes manuais
9. **TTS não integrado** — Piper configurado mas não usado
10. **Sem recovery** — Listeners falhados não reentam

Ver [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) para lista completa.

---

## 📚 Referências

- **Vosk API**: https://github.com/alphacep/vosk-api
- **PyAudio**: https://people.csail.mit.edu/hubert/pyaudio/
- **WebRTC VAD**: https://github.com/wiseman/py-webrtcvad
- **Piper TTS**: https://github.com/rhasspy/piper
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html

---

## 📝 Informações do Documento

| Campo | Valor |
|-------|-------|
| **Título** | Documentação Completa do Sistema Cosmo |
| **Versão** | 1.0 |
| **Data** | 30 de Maio de 2026 |
| **Escopo** | Análise técnica profunda completa |
| **Público-Alvo** | Arquitetos, desenvolvedores, contribuidores |
| **Idioma** | Português (Brasil) |
| **Status** | Documento de Referência - Atualizado |

---

**Fim do Documento**

Para detalhes específicos, consulte os documentos temáticos:
- Setup: [INSTALLATION.md](docs/INSTALLATION.md)
- Arquitetura: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- APIs: [API_REFERENCE.md](docs/API_REFERENCE.md)
- Configuração: [CONFIGURATION_REFERENCE.md](docs/CONFIGURATION_REFERENCE.md)
- Desenvolvimento: [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- Problemas: [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)
