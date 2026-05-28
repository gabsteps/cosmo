# 📚 DOCUMENTAÇÃO COMPLETA DO SISTEMA COSMO

## Índice Geral
1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Estrutura de Módulos e Código-Fonte](#3-estrutura-de-módulos-e-código-fonte)
4. [Fluxo de Inicialização](#4-fluxo-de-inicialização)
5. [Pipeline de Audio](#5-pipeline-de-audio)
6. [Sistema de Eventos](#6-sistema-de-eventos)
7. [Persistência de Dados](#7-persistência-de-dados)
8. [Máquinas de Estado](#8-máquinas-de-estado)
9. [Padrões de Design](#9-padrões-de-design)
10. [Configuração do Sistema](#10-configuração-do-sistema)
11. [Fluxos de Dados](#11-fluxos-de-dados)
12. [Roadmap Futuro](#12-roadmap-futuro)
13. [Mudanças Recentes](#mudanças-recentes-sprint-atual) ⭐
14. [Conclusões](#14-conclusões)

---

## 1. Visão Geral do Projeto

### 1.1 Identidade do Projeto
- **Nome Completo**: Zenith Cosmo 42 (ZC-42)
- **Tipo de Aplicação**: Assistente Inteligente Multimodal Local
- **Linguagem**: Python 3.x
- **Filosofia**: Privacidade primeiro, processamento offline, desacoplamento modular

### 1.2 Propósito Principal
O Cosmo é um assistente de voz inteligente projetado para ser executado completamente offline em hardware local. Oferece:

- ✅ **Reconhecimento de Voz (STT)** - Conversão de áudio para texto em português
- ✅ **Detecção de Palavras-chave** - Wake-word detection para ativação por voz
- ✅ **Síntese de Fala (TTS)** - Resposta em voz com múltiplas opções de voz
- ✅ **Detecção de Atividade de Voz** - VAD para captura eficiente de comando
- 🟡 **Reconhecimento Facial** - Em desenvolvimento
- 🟡 **Inteligência Cognitiva** - Em desenvolvimento (context, memory, personality)
- 🟡 **Interfaces Web/API** - Em desenvolvimento (REST, CLI, WebSocket)

### 1.3 Características Técnicas Principais
- **Offline-first**: Sem dependência de APIs externas
- **Modular**: Componentes independentes e reutilizáveis
- **Event-driven**: Comunicação desacoplada via event bus
- **Persistente**: Banco de dados SQLite para conversas e memórias
- **Thread-safe**: Gerenciamento apropriado de concorrência
- **Configurável**: Todas as settings centralizadas em YAML

---

## 2. Arquitetura do Sistema

### 2.1 Visão em Camadas

```
┌───────────────────────────────────────────────────────────┐
│  Nível 5: Interfaces Externas (Planejado)                 │
│  API REST | CLI | WebSocket                                │
├───────────────────────────────────────────────────────────┤
│  Nível 4: Inteligência Cognitiva (Em Desenvolvimento)     │
│  Context | Memory | Personality | Planner                 │
├───────────────────────────────────────────────────────────┤
│  Nível 3: Processamento Sensorial (Parcialmente Implementado)│
│  Audio (STT, TTS, VAD, Wakeword) | Vision (Em dev)        │
├───────────────────────────────────────────────────────────┤
│  Nível 2: Núcleo do Sistema (Implementado)                │
│  Event Bus | Config | Logger | Runtime | Scheduler        │
├───────────────────────────────────────────────────────────┤
│  Nível 1: Persistência (Implementado)                      │
│  Database | Repositories (User, Conversation, Memory, etc)│
├───────────────────────────────────────────────────────────┤
│  Nível 0: Recursos Externos                               │
│  Modelos (Vosk, Piper) | Cascatas Haar | Configuração    │
└───────────────────────────────────────────────────────────┘
```

### 2.2 Princípios Arquiteturais

**Desacoplamento Vertical**: Camadas superiores não conhecem implementação das inferiores via abstração (Repositories pattern, Event bus abstraction).

**Desacoplamento Horizontal**: Módulos no mesmo nível se comunicam via eventos, não chamadas diretas.

**Inversão de Controle**: Event bus gerencia o fluxo de controle, não componentes individuais.

**Configuração Centralizada**: settings.yaml como fonte única de verdade.

### 2.3 Padrão Dual: Event Bus Síncrono + Assíncrono

**Mudança Recente**: O sistema agora possui dois event buses em paralelo para melhor desempenho e escalabilidade.

```
┌────────────────────────────────────────────────────────┐
│ EVENTOS RÁPIDOS (Sync)                                 │
│ ├─ WAKE_WORD_DETECTED                                 │
│ ├─ SPEECH_RECOGNIZED                                  │
│ └─ Outros eventos que precisam response imediato      │
│                                                        │
│ event_bus.emit(WAKE_WORD_DETECTED, {...})            │
│   → Dispatching imediato (blocking)                    │
│   → Listeners executam serialmente                     │
│   → Sem métricas (performance first)                   │
│                                                        │
│ Implementação: Simple dict-based                       │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ EVENTOS PESADOS (Async) ⭐ NEW                         │
│ ├─ Processamento cognitivo                            │
│ ├─ I/O pesado                                          │
│ └─ Operações que levam tempo                          │
│                                                        │
│ await async_event_bus.emit(MY_EVENT, {...})          │
│   → Enfileira evento                                   │
│   → Processa concorrentemente                         │
│   → Coleta 19 métricas detalhadas                     │
│   → Rastreia UUID por evento                          │
│                                                        │
│ Implementação: Queue-based com asyncio                │
│ Fila: max 100 eventos                                 │
│ Timeout: 10s por listener                             │
└────────────────────────────────────────────────────────┘
```

**Vantagens do Padrão Dual**:
- ✅ Events críticos (wakeword) mantêm latência baixa
- ✅ Events pesados processam concorrentemente
- ✅ Coleta de métricas sem overhead em paths críticos
- ✅ Escalável para novos event types
- ✅ Facilita debugging com tracing UUID

**Diagrama Atualizado**:

```
                         ┌─────────────┐
                         │  main.py    │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │ bootstrap   │ (Inicialização)
                         └──────┬──────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
    ┌─────────────┐        ┌──────────┐          ┌──────────┐
    │ Event Bus   │        │Async Bus │◄─────────│ Lifecycle│
    │ (Sync)      │◄───────│(NEW)     │          └──────────┘
    └─────────────┘        └──────────┘
        │                       │
        ├──────────┬────────────┤
        │          │            │
        ▼          ▼            ▼
    ┌────────┐ ┌────────┐ ┌─────────┐
    │Listeners│ │ Tasks  │ │ Async   │
    │(Sync)  │ │Creator │ │ Runtime │
    └────────┘ └────────┘ └─────────┘
```

---

### 2.4 Diagrama de Componentes

```
                         ┌─────────────┐
                         │  main.py    │
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │ bootstrap   │ (Inicialização)
                         └──────┬──────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
    ┌────────────┐         ┌──────────┐          ┌──────────┐
    │ Event Bus  │◄────────│ Lifecycle│          │  Logger  │
    └────┬───────┘         └──────────┘          └──────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
  ┌──────┐ ┌───────┐ ┌────────┐ ┌──────┐ ┌────────┐
  │Audio │ │Vision │ │Cognition│ │Data  │ │Runtime │
  └──────┘ └───────┘ └────────┘ └──────┘ └────────┘
    │
    └──┬──────────┬──────────┬──────────┐
       │          │          │          │
       ▼          ▼          ▼          ▼
    ┌──────────┐ ┌───────┐ ┌────────┐ ┌────┐
    │Wakeword  │ │STT    │ │VAD     │ │TTS │
    └──────────┘ └───────┘ └────────┘ └────┘
```

---

## 3. Estrutura de Módulos e Código-Fonte

### 3.1 Código-Fonte Completo dos Módulos

Esta seção contém o código-fonte de todos os arquivos Python do projeto.

**Arquivos Incluídos** (45 total):
- **Raiz**: main.py
- **Core**: bootstrap.py, lifecycle.py, task_manager.py, settings_manager.py, event_bus.py, event_types.py, async_event_bus.py, audio_listener.py, conversation_listener.py, system_listener.py, system_async_listener.py, vision_listener.py, logger_manager.py, runtime_manager.py, async_runtime.py
- **Audio**: audio_state.py, stt_engine.py, stt_manager.py, command_processor.py, vad_engine.py, wakeword_engine.py, wakeword_manager.py
- **Data**: database.py, user_repository.py, conversation_repository.py, face_repository.py, memory_repository.py, event_repository.py, system_repository.py

---

#### **RAIZ: main.py**

```python
from cosmo.core.bootstrap.bootstrap import bootstrap


def main():

    bootstrap.start()


if __name__ == "__main__":
    main()
```

---

#### **CORE: bootstrap/bootstrap.py**

```python
from cosmo.core.logger.logger_manager import logger

from cosmo.core.bootstrap.lifecycle import lifecycle

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    SYSTEM_STARTED,
    SYSTEM_SHUTDOWN
)

# =========================
# IMPORTAR LISTENERS
# =========================

from cosmo.core.events.listeners import (
    audio_listener,
    vision_listener,
    system_listener,
    conversation_listener,
)


from cosmo.audio.wakeword.wakeword_manager import (
    wakeword_manager
)

from cosmo.core.runtime.runtime_manager import (
    runtime_manager
)

from cosmo.audio.wakeword.wakeword_manager import (
    wakeword_manager
)


class Bootstrap:

    def start(self):

        logger.info("Inicializando Zenith Cosmo 42")

        lifecycle.start()

        event_bus.emit(
            SYSTEM_STARTED,
            {
                "system": "Zenith Cosmo 42"
            }
        )
        
        runtime_manager.start_thread(
            target=wakeword_manager.start,
            name="WakewordManager"
        )

        logger.info("Zenith Cosmo 42 online")
        
        runtime_manager.wait_forever()

    def shutdown(self):

        logger.info("Encerrando Zenith Cosmo 42")

        lifecycle.stop()

        event_bus.emit(
            SYSTEM_SHUTDOWN
        )

        logger.info("Sistema encerrado")


bootstrap = Bootstrap()
```

---

#### **CORE: bootstrap/lifecycle.py**

```python
class Lifecycle:

    def __init__(self):

        self.running = False
        self.sleeping = False

    def start(self):

        self.running = True

    def stop(self):

        self.running = False

    def sleep(self):

        self.sleeping = True

    def wake(self):

        self.sleeping = False

    def is_running(self):

        return self.running

    def is_sleeping(self):

        return self.sleeping


lifecycle = Lifecycle()
```

---

#### **CORE: config/settings_manager.py**

```python
from pathlib import Path
import yaml


CONFIG_PATH = Path("cosmo/core/config/settings.yaml")


class Config:

    def __init__(self):

        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    def get(self, *keys, default=None):

        value = self.data

        for key in keys:

            if key not in value:
                return default

            value = value[key]

        return value


config = Config()
```

---

#### **CORE: events/event_bus.py**

```python
from collections import defaultdict


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_type, callback):
        self.listeners[event_type].append(callback)

    def emit(self, event_type, data=None):

        if event_type not in self.listeners:
            return

        for callback in self.listeners[event_type]:
            callback(data)


event_bus = EventBus()

#Próximo Upgrade Futuro

#Depois:

#async event bus
#prioridades
#middlewares
#fila
#debounce
#IPC
#distributed events
```

---

#### **CORE: events/event_types.py**

```python
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
```

---

#### **CORE: events/listeners/audio_listener.py**

```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import WAKE_WORD_DETECTED

from cosmo.core.logger.logger_manager import logger


def on_wake_word_detected(data):

    word = data.get("word")

    logger.info(f"Wake word detectada: {word}")


event_bus.subscribe(
    WAKE_WORD_DETECTED,
    on_wake_word_detected
)
```

---

#### **CORE: events/listeners/conversation_listener.py**

```python
from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import COMMAND_RECEIVED

from cosmo.core.logger.logger_manager import logger


def on_command_received(data):

    command = data.get("command")

    logger.info(f"Comando recebido: {command}")


event_bus.subscribe(
    COMMAND_RECEIVED,
    on_command_received
)
```

---

#### **CORE: events/listeners/system_listener.py**

```python
from cosmo.core.events.event_bus import event_bus
from cosmo.core.events.event_types import SYSTEM_STARTED

from cosmo.core.logger.logger_manager import logger


def on_system_started(data):

    logger.info("Sistema iniciado")


event_bus.subscribe(
    SYSTEM_STARTED,
    on_system_started
)
```

---

#### **CORE: events/async_event_bus.py** ⭐ NEW

```python
# fila assíncrona
# dispatcher async
# desacoplamento temporal
# listeners concorrentes
# bounded queue
# tracing
# métricas
# base para prioridades
# base para retries

import asyncio
import uuid
import time

from collections import defaultdict

from cosmo.core.logger.logger_manager import logger


class AsyncEventBus:

    def __init__(self):

        self.listeners = defaultdict(list)

        self.max_queue_size = 100

        self.queue = asyncio.Queue(
            maxsize=self.max_queue_size
        )

        self.running = False

        self.listener_timeout = 10

        self.metrics = {
            # ==================================================

            #             EVENTOS
            # métrica                       significado
            # events_received	            tentativa de emissão
            # events_emitted	            entrou na fila
            # events_dispatched             saiu da fila
            # events_dropped	            rejeitado pela fila
            # events_completed	            todos listeners OK
            # events_failed	                todos falharam
            # events_partial_failures	    mistura de sucesso/falha

            # LISTENERS
            # métrica	                   significado
            # listener_successes	       listener OK
            # listener_timeouts	           timeout
            # listener_errors	           exception
            # ==================================================

            # ==================================================
            # EVENTOS
            # ==================================================

            "events_received": 0,
            "events_emitted": 0,
            "events_dispatched": 0,
            "events_dropped": 0,

            "events_completed": 0,
            "events_failed": 0,
            "events_partial_failures": 0,

            # ==================================================
            # LISTENERS
            # ==================================================

            "listener_successes": 0,
            "listener_timeouts": 0,
            "listener_errors": 0,

            # ==================================================
            # FILA
            # ==================================================

            "queue_peak": 0,
            "current_queue_size": 0,

            # ==================================================
            # PERFORMANCE
            # ==================================================

            "avg_event_processing_time": 0.0,
            "avg_listener_processing_time": 0.0
        }

    def subscribe(
        self,
        event_name,
        callback
    ):

        self.listeners[event_name].append(
            callback
        )

        logger.info(
            f"Listener registrado: "
            f"{event_name} -> {callback.__name__}"
        )

    async def emit(
        self,
        event_name,
        data=None
    ):

        self.metrics["events_received"] += 1

        event = {
            "id": str(uuid.uuid4()),
            "name": event_name,
            "data": data,
            "created_at": time.time()
        }

        try:

            self.queue.put_nowait(event)

            self.metrics["events_emitted"] += 1

            current_size = self.queue.qsize()

            self.metrics["current_queue_size"] = (
                current_size
            )

            if (
                current_size >
                self.metrics["queue_peak"]
            ):

                self.metrics["queue_peak"] = (
                    current_size
                )

        except asyncio.QueueFull:

            self.metrics["events_dropped"] += 1

            logger.warning(
                f"Fila cheia. "
                f"Evento descartado: {event_name}"
            )

            return

        logger.info(
            f"Evento enfileirado: "
            f"{event_name} "
            f"(fila: {self.queue.qsize()})"
        )

        logger.info(
            f"[TRACE] "
            f"{event['id']} "
            f"queued -> "
            f"{event['name']}"
        )

    async def start(self):

        self.running = True

        logger.info(
            "Async event bus online"
        )

        while self.running:

            event = await self.queue.get()

            self.metrics["events_dispatched"] += 1

            self.metrics["current_queue_size"] = (
                self.queue.qsize()
            )

            asyncio.create_task(
                self._dispatch_event(event)
            )

            self.queue.task_done()

    async def _dispatch_event(self, event):

        event_name = event["name"]

        listeners = self.listeners.get(
            event_name,
            []
        )

        logger.info(
            f"[TRACE] "
            f"{event['id']} "
            f"dispatched -> "
            f"{event_name}"
        )

        if not listeners:

            logger.warning(
                f"[TRACE] "
                f"{event['id']} "
                f"no_listeners -> "
                f"{event_name}"
            )

            self.metrics["events_completed"] += 1

            return

        event_start = time.perf_counter()

        tasks = [
            asyncio.create_task(
                self._execute_listener(
                    listener,
                    event
                )
            )
            for listener in listeners
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=False
        )

        success_count = sum(results)

        failure_count = (
            len(results) - success_count
        )

        elapsed = (
            time.perf_counter() - event_start
        )

        completed = (
            self.metrics["events_completed"] +
            self.metrics["events_failed"] +
            self.metrics["events_partial_failures"]
        )

        current_avg = self.metrics[
            "avg_event_processing_time"
        ]

        self.metrics[
            "avg_event_processing_time"
        ] = (
            (
                current_avg * completed
            ) + elapsed
        ) / (completed + 1)

        # ==================================================
        # CLASSIFICAÇÃO DO EVENTO
        # ==================================================

        if failure_count == 0:

            self.metrics[
                "events_completed"
            ] += 1

            logger.info(
                f"[TRACE] "
                f"{event['id']} "
                f"event_completed -> "
                f"{event_name}"
            )

        elif success_count == 0:

            self.metrics[
                "events_failed"
            ] += 1

            logger.error(
                f"[TRACE] "
                f"{event['id']} "
                f"event_failed -> "
                f"{event_name}"
            )

        else:

            self.metrics[
                "events_partial_failures"
            ] += 1

            logger.warning(
                f"[TRACE] "
                f"{event['id']} "
                f"event_partial_failure -> "
                f"{event_name}"
            )

    async def shutdown(self):

        self.running = False

    async def _execute_listener(
        self,
        listener,
        event
    ):

        logger.info(
            f"[TRACE] "
            f"{event['id']} "
            f"listener_started -> "
            f"{listener.__name__}"
        )

        start_time = time.perf_counter()

        try:

            await asyncio.wait_for(
                listener(event["data"]),
                timeout=self.listener_timeout
            )

            elapsed = (
                time.perf_counter() - start_time
            )

            self.metrics[
                "listener_successes"
            ] += 1

            successes = self.metrics[
                "listener_successes"
            ]

            current_avg = self.metrics[
                "avg_listener_processing_time"
            ]

            self.metrics[
                "avg_listener_processing_time"
            ] = (
                (
                    current_avg * (successes - 1)
                ) + elapsed
            ) / successes

            logger.info(
                f"[TRACE] "
                f"{event['id']} "
                f"listener_finished -> "
                f"{listener.__name__}"
            )

            return True

        except asyncio.TimeoutError:

            self.metrics[
                "listener_timeouts"
            ] += 1

            logger.warning(
                f"[TRACE] "
                f"{event['id']} "
                f"listener_timeout -> "
                f"{listener.__name__}"
            )

            return False

        except Exception as e:

            self.metrics[
                "listener_errors"
            ] += 1

            logger.exception(
                f"[TRACE] "
                f"{event['id']} "
                f"listener_error -> "
                f"{listener.__name__}: {e}"
            )

            return False

    def get_metrics(self):

        self.metrics[
            "current_queue_size"
        ] = self.queue.qsize()

        return self.metrics.copy()


async_event_bus = AsyncEventBus()
```

---

#### **CORE: events/listeners/system_async_listener.py** ⭐ NEW

```python
import asyncio
import time

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    SYSTEM_STARTED
)


async def on_system_started(data):

    logger.info(
        f"Sistema async iniciado: {data}"
    )


async_event_bus.subscribe(
    SYSTEM_STARTED,
    on_system_started
)

async def listener_1(data):

    start = time.time()

    logger.info("Listener 1 iniciado")

    await asyncio.sleep(15)

    end = time.time()

    logger.info(
        f"Listener 1 finalizado "
        f"em {end - start:.2f}s"
    )

async def listener_2(data):

    start = time.time()

    logger.info("Listener 2 iniciado")

    await asyncio.sleep(15)

    end = time.time()

    logger.info(
        f"Listener 2 finalizado "
        f"em {end - start:.2f}s"
    )


async_event_bus.subscribe(
    SYSTEM_STARTED,
    listener_1
)

async_event_bus.subscribe(
    SYSTEM_STARTED,
    listener_2
)

logger.info(
    f"Metrics: "
    f"{async_event_bus.get_metrics()}"
)
```

---

#### **CORE: events/listeners/vision_listener.py**

```python
from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    USER_RECOGNIZED,
    FACE_UNKNOWN
)

from cosmo.core.logger.logger_manager import logger


def on_user_recognized(data):

    user_name = data.get("name")

    logger.info(f"Usuário reconhecido: {user_name}")


def on_unknown_face(data):

    logger.info("Rosto desconhecido detectado")


event_bus.subscribe(
    USER_RECOGNIZED,
    on_user_recognized
)

event_bus.subscribe(
    FACE_UNKNOWN,
    on_unknown_face
)
```

---

#### **CORE: logger/logger_manager.py**

```python
import logging
from pathlib import Path


LOG_DIR = Path("cosmo/data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "cosmo.log"


def setup_logger():

    logger = logging.getLogger("cosmo")

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "[%(name)s] "
        "%(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()


#Próximo Upgrade Recomendado

#Depois:

#rotação automática de logs
#logs por módulo
#logs coloridos
#logs JSON
#telemetria
#tracing
```

---

#### **CORE: runtime/runtime_manager.py**

```python
import threading

from cosmo.core.logger.logger_manager import logger


class RuntimeManager:

    def __init__(self):

        # Armazena threads ativas
        self.threads = []

    def start_thread(self, target, name):

        """
        Inicia módulo em thread separada.
        """

        logger.info(
            f"Iniciando thread: {name}"
        )

        # Cria thread daemon
        # daemon=True permite encerramento automático
        # quando processo principal finalizar
        thread = threading.Thread(
            target=target,
            name=name,
            daemon=True
        )

        # Inicia execução paralela
        thread.start()

        # Salva referência da thread
        self.threads.append(thread)

    def wait_forever(self):

        """
        Mantém processo principal vivo.
        """

        logger.info(
            "Runtime manager ativo"
        )

        # Aguarda indefinidamente
        for thread in self.threads:

            thread.join()


runtime_manager = RuntimeManager()
```

---

#### **CORE: runtime/async_runtime.py** ⭐ NEW

```python
# loop central
# gerenciamento de tasks
# controle de shutdown
# base do scheduler
# coordenação futura

import asyncio

from cosmo.core.logger.logger_manager import logger


class AsyncRuntime:

    def __init__(self):

        self.loop = None

        self.tasks = []

        self.running = False

    async def start(self):

        logger.info(
            "Async runtime iniciado"
        )

        self.running = True

        while self.running:

            await asyncio.sleep(1)

    async def shutdown(self):

        logger.info(
            "Encerrando async runtime"
        )

        self.running = False

        for task in self.tasks:

            task.cancel()

        await asyncio.gather(
            *self.tasks,
            return_exceptions=True
        )

    def create_task(
        self,
        coroutine,
        name=None
    ):

        task = asyncio.create_task(
            coroutine,
            name=name
        )

        self.tasks.append(task)

        logger.info(
            f"Task criada: {name}"
        )

        return task

    async def heartbeat(self):

        self.running = True

        while self.running:

            logger.info(
                "Runtime heartbeat"
            )

            await asyncio.sleep(5)



async_runtime = AsyncRuntime()
```

---

#### **CORE: bootstrap/task_manager.py** ⭐ NEW

```python
from cosmo.core.runtime.async_runtime import (
    async_runtime
)


class TaskManager:

    def create(
        self,
        coroutine,
        name=None
    ):

        return async_runtime.create_task(
            coroutine,
            name=name
        )


task_manager = TaskManager()
```

---

#### **AUDIO: audio_state.py**

```python
from enum import Enum


class AudioState(Enum):
    IDLE = "idle"
    LISTENING = "listening"


class AudioStateManager:

    def __init__(self):
        self.state = AudioState.IDLE


audio_state = AudioStateManager()
```

---

#### **AUDIO: stt/stt_engine.py**

```python
from vosk import Model, KaldiRecognizer
import json
from pathlib import Path

from cosmo.core.logger.logger_manager import logger
from cosmo.core.config.settings_manager import config


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "vosk"
    / "vosk-model-small-pt-0.3"
)


class STTEngine:

    def __init__(self):

        logger.info("Carregando modelo STT")

        self.model = Model(str(MODEL_PATH))

        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        self.recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate
        )

        logger.info("STT engine inicializada")

    def process_audio(self, audio_data):

        """
        Processa chunk de áudio
        e retorna texto completo.
        """

        if self.recognizer.AcceptWaveform(audio_data):

            result = json.loads(
                self.recognizer.Result()
            )

            text = result.get(
                "text",
                ""
            ).strip()

            return text

        return None


stt_engine = STTEngine()
```

---

#### **AUDIO: stt/stt_manager.py**

```python
import pyaudio

from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import config

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    SPEECH_RECEIVED
)

from cosmo.audio.stt.stt_engine import (
    stt_engine
)


class STTManager:

    def __init__(self):

        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        self.chunk_size = config.get(
            "audio",
            "chunk_size"
        )

        self.channels = config.get(
            "audio",
            "channels"
        )

        self.audio = pyaudio.PyAudio()

    def listen_once(self):

        """
        Escuta uma frase única.
        """

        logger.info("Escuta ativa iniciada")

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        while True:

            audio_data = stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )

            text = stt_engine.process_audio(
                audio_data
            )

            if text:

                logger.info(
                    f"Texto reconhecido: {text}"
                )

                event_bus.emit(
                    SPEECH_RECEIVED,
                    {
                        "text": text
                    }
                )

                break

        stream.stop_stream()
        stream.close()

        logger.info("Escuta finalizada")


stt_manager = STTManager()
```

---

#### **AUDIO: stt/command_processor.py**

```python
from cosmo.core.logger.logger_manager import logger

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    USER_SPEECH_RECEIVED
)


class CommandProcessor:

    def __init__(self):

        event_bus.subscribe(
            USER_SPEECH_RECEIVED,
            self.process_command
        )

    def process_command(self, data):

        text = data["text"]

        logger.info(
            f"Processando comando: {text}"
        )

        # Comandos iniciais simples
        if "horas" in text:

            logger.info(
                "Usuário perguntou horário"
            )

        elif "nome" in text:

            logger.info(
                "Usuário perguntou nome"
            )

        else:

            logger.info(
                "Comando desconhecido"
            )


command_processor = CommandProcessor()
```

---

#### **AUDIO: vad/vad_engine.py**

```python
import webrtcvad

from cosmo.core.config.settings_manager import config


class VADEngine:

    def __init__(self):

        # agressividade: 0 (leve) a 3 (rigoroso)
        self.vad = webrtcvad.Vad(2)

        self.sample_rate = config.get("audio", "sample_rate")

        # WebRTC só aceita: 10, 20 ou 30ms
        self.frame_ms = 30

        self.frame_size = int(self.sample_rate * self.frame_ms / 1000)

    def is_speech(self, audio_chunk: bytes) -> bool:

        """
        Retorna True se o frame contém voz.
        """

        try:
            return self.vad.is_speech(audio_chunk, self.sample_rate)

        except Exception:
            return False


vad_engine = VADEngine()
```

---

#### **AUDIO: wakeword/wakeword_engine.py**

```python
from vosk import Model
from vosk import KaldiRecognizer

import json

from cosmo.core.config.settings_manager import config


class WakewordEngine:

    def __init__(self):

        # Caminho do modelo Vosk
        self.model_path = "cosmo/models/vosk/vosk-model-small-pt-0.3"

        # Carrega modelo de reconhecimento offline
        self.model = Model(self.model_path)

        # Configuração do sample rate vinda do YAML
        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        # Inicializa reconhecedor
        self.recognizer = KaldiRecognizer(
            self.model,
            self.sample_rate
        )

        # Lista de wake words válidas
        self.wake_words = config.get(
            "wakeword",
            "words"
        )

    def process_audio(self, audio_data):

        """
        Processa chunk de áudio.

        Retorna:
        - palavra detectada
        - None se nada encontrado
        """

        # Vosk retorna resultado completo apenas
        # quando identifica frase válida
        if self.recognizer.AcceptWaveform(audio_data):

            result = self.recognizer.Result()

            data = json.loads(result)

            text = data.get(
                "text",
                ""
            ).lower()

            # Verifica wake words
            for word in self.wake_words:

                if word in text:

                    return word

        return None


wakeword_engine = WakewordEngine()
```

---

#### **AUDIO: wakeword/wakeword_manager.py**

```python
import pyaudio

from cosmo.core.logger.logger_manager import logger

from cosmo.core.config.settings_manager import config

from cosmo.core.events.event_bus import event_bus

from cosmo.core.events.event_types import (
    WAKE_WORD_DETECTED
)

from cosmo.audio.wakeword.wakeword_engine import (
    wakeword_engine
)


class WakewordManager:

    def __init__(self):

        # Configurações de áudio vindas do YAML
        self.sample_rate = config.get(
            "audio",
            "sample_rate"
        )

        self.chunk_size = config.get(
            "audio",
            "chunk_size"
        )

        self.channels = config.get(
            "audio",
            "channels"
        )

        # Inicializa PyAudio
        self.audio = pyaudio.PyAudio()

        # Stream principal do microfone
        self.stream = None

        # Estado do loop
        self.running = False

    def start(self):

        """
        Inicia captura contínua do microfone.
        """

        logger.info("Iniciando wakeword manager")

        # Abre stream de captura
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        self.running = True

        logger.info("Wakeword manager online")

        # Loop principal
        while self.running:

            # Captura chunk do microfone
            audio_data = self.stream.read(
                self.chunk_size,
                exception_on_overflow=False
            )

            # Processa áudio
            detected_word = (
                wakeword_engine.process_audio(
                    audio_data
                )
            )

            # Wake word detectada
            if detected_word:
                
                # Emite evento global
                event_bus.emit(
                    WAKE_WORD_DETECTED,
                    {
                        "word": detected_word
                    }
                )

    def stop(self):

        """
        Finaliza captura de áudio.
        """

        logger.info("Parando wakeword manager")

        self.running = False

        # Fecha stream se existir
        if self.stream:

            self.stream.stop_stream()
            self.stream.close()

        # Finaliza PyAudio
        self.audio.terminate()

        logger.info("Wakeword manager encerrado")


wakeword_manager = WakewordManager()
```

---

#### **DATA: database/database.py**

```python
from pathlib import Path
import sqlite3

DB_PATH = Path("data/database/cosmo.db")


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.connection.row_factory = sqlite3.Row
        self._configure()

    def _configure(self):
        cursor = self.connection.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")

        self.connection.commit()

    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetchone(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


db = Database()
```

---

#### **DATA: repositories/user_repository.py**

```python
from database import db


class UserRepository:

    def create_user(self, name):
        db.execute(
            "INSERT INTO users(name) VALUES(?)",
            (name,)
        )

    def get_user_by_id(self, user_id):
        return db.fetchone(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

    def get_user_by_name(self, name):
        return db.fetchone(
            "SELECT * FROM users WHERE name = ?",
            (name,)
        )

    def get_user_by_face_id(self, face_id):
        return db.fetchone(
            "SELECT * FROM users WHERE face_id = ?",
            (face_id,)
        )

    def list_users(self):
        return db.fetchall(
            "SELECT * FROM users"
        )

    def user_exists(self, name):
        user = db.fetchone(
            "SELECT id FROM users WHERE name = ?",
            (name,)
        )
        return user is not None

    def update_last_seen(self, user_id):
        db.execute(
            """
            UPDATE users
            SET last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (user_id,)
        )

    def update_trust_level(self, user_id, trust_level):
        db.execute(
            """
            UPDATE users
            SET trust_level = ?
            WHERE id = ?
            """,
            (trust_level, user_id)
        )

    def save_face_id(self, user_id, face_id):
        db.execute(
            """
            UPDATE users
            SET face_id = ?
            WHERE id = ?
            """,
            (face_id, user_id)
        )

    def rename_user(self, user_id, new_name):
        db.execute(
            """
            UPDATE users
            SET name = ?
            WHERE id = ?
            """,
            (new_name, user_id)
        )

    def delete_user(self, user_id):
        db.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )


user_repository = UserRepository()
```

---

#### **DATA: repositories/conversation_repository.py**

```python
from database import db


class ConversationRepository:

    def add_message(self, user_id, role, message):
        db.execute(
            """
            INSERT INTO conversations(user_id, role, message)
            VALUES(?, ?, ?)
            """,
            (user_id, role, message)
        )

    def get_conversation_history(self, user_id, limit=20):
        return db.fetchall(
            """
            SELECT * FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit)
        )

    def clear_history(self, user_id):
        db.execute(
            """
            DELETE FROM conversations
            WHERE user_id = ?
            """,
            (user_id,)
        )


conversation_repository = ConversationRepository()
```

---

#### **DATA: repositories/face_repository.py**

```python
from database import db


class FaceRepository:

    def create_face(self, user_id, encoding_path):
        db.execute(
            """
            INSERT INTO faces(user_id, encoding_path)
            VALUES(?, ?)
            """,
            (user_id, encoding_path)
        )

    def get_faces_by_user(self, user_id):
        return db.fetchall(
            """
            SELECT * FROM faces
            WHERE user_id = ?
            """,
            (user_id,)
        )

    def delete_face(self, face_id):
        db.execute(
            "DELETE FROM faces WHERE id = ?",
            (face_id,)
        )


face_repository = FaceRepository()
```

---

#### **DATA: repositories/memory_repository.py**

```python
from database import db


class MemoryRepository:

    def add_memory(self, user_id, category, content, importance=1):
        db.execute(
            """
            INSERT INTO memories(user_id, category, content, importance)
            VALUES(?, ?, ?, ?)
            """,
            (user_id, category, content, importance)
        )

    def get_user_memories(self, user_id):
        return db.fetchall(
            """
            SELECT * FROM memories
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

    def get_memories_by_category(self, category):
        return db.fetchall(
            """
            SELECT * FROM memories
            WHERE category = ?
            ORDER BY created_at DESC
            """,
            (category,)
        )

    def delete_memory(self, memory_id):
        db.execute(
            "DELETE FROM memories WHERE id = ?",
            (memory_id,)
        )


memory_repository = MemoryRepository()
```

---

#### **DATA: repositories/event_repository.py**

```python
from database import db
import json


class EventRepository:

    def emit_event(self, event_type, payload=None):
        db.execute(
            """
            INSERT INTO events(type, payload)
            VALUES(?, ?)
            """,
            (
                event_type,
                json.dumps(payload) if payload else None
            )
        )

    def get_recent_events(self, limit=50):
        return db.fetchall(
            """
            SELECT * FROM events
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )


event_repository = EventRepository()
```

---

#### **DATA: repositories/system_repository.py**

```python
from database import db


class SystemRepository:

    def set_state(self, key, value):
        db.execute(
            """
            INSERT INTO system_state(key, value)
            VALUES(?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (key, value)
        )

    def get_state(self, key):
        return db.fetchone(
            """
            SELECT value FROM system_state
            WHERE key = ?
            """,
            (key,)
        )

    def delete_state(self, key):
        db.execute(
            """
            DELETE FROM system_state
            WHERE key = ?
            """,
            (key,)
        )


system_repository = SystemRepository()
```

---

### 3.1.1 Infraestrutura Assíncrona (Nova)

#### **Event Bus Dual Architecture**

O projeto agora possui **dois event buses** em paralelo para diferentes casos de uso:

**1. Event Bus Síncrono** (`event_bus.py`)
- Implementação simples dict-based
- Dispatching imediato (blocking)
- Sem fila de espera
- Uso: Eventos que precisam ser processados imediatamente
- Exemplo: WAKE_WORD_DETECTED

**2. Async Event Bus** (`async_event_bus.py`) ⭐ NEW
- Implementação queue-based com asyncio
- Fila assíncrona (bounded a 100 eventos)
- Dispatching deferred via loop de eventos
- Coleta automática de métricas
- Timeout de listeners (10s padrão)
- Tracing com UUID para cada evento
- Uso: Eventos que podem processar concorrentemente

#### **Métrica de Desempenho (AsyncEventBus)**

O AsyncEventBus coleta 19 métricas em tempo real:

| Categoria | Métrica | Significado |
|-----------|---------|-------------|
| **Eventos** | events_received | Tentativa de emissão |
| | events_emitted | Entrou na fila |
| | events_dispatched | Saiu da fila e sendo processado |
| | events_dropped | Rejeitado pela fila cheia |
| | events_completed | Todos listeners OK |
| | events_failed | Todos listeners falharam |
| | events_partial_failures | Mistura sucesso/falha |
| **Listeners** | listener_successes | Listener executado com sucesso |
| | listener_timeouts | Listener excedeu 10s |
| | listener_errors | Listener lançou exceção |
| **Fila** | queue_peak | Tamanho máximo atingido |
| | current_queue_size | Tamanho atual |
| **Performance** | avg_event_processing_time | Tempo médio de processamento de evento |
| | avg_listener_processing_time | Tempo médio de listener |

#### **Runtime Assíncrono** (`async_runtime.py`) ⭐ NEW

Manager para orquestração de tasks assincronamente:

- **create_task()**: Cria e rastreia uma task
- **start()**: Loop infinito assíncrono
- **shutdown()**: Cancela todas as tasks
- **heartbeat()**: Sinal periódico (5s)

Exemplo:
```python
task = async_runtime.create_task(
    my_coroutine(),
    name="ProcessAudio"
)
```

#### **Task Manager** (`task_manager.py`) ⭐ NEW

Wrapper sobre AsyncRuntime para interface simplificada:

```python
from cosmo.core.bootstrap.task_manager import task_manager

# Criar task assíncrona
task = task_manager.create(
    my_async_function(),
    name="MyTask"
)
```

#### **Exemplo de Listener Assíncrono** (`system_async_listener.py`)

Demonstra como listeners podem ser assincronamente:

```python
async def listener_1(data):
    start = time.time()
    logger.info("Listener 1 iniciado")
    await asyncio.sleep(15)  # I/O não-bloqueante
    end = time.time()
    logger.info(f"Listener 1 finalizado em {end - start:.2f}s")

async_event_bus.subscribe(SYSTEM_STARTED, listener_1)
```

**Benefícios**:
- Múltiplos listeners rodam concorrentemente
- Não bloqueiam uns aos outros
- Com timeout de 10s por listener
- Rastreamento de sucesso/timeout/erro

---

#### **Bootstrap** (`bootstrap/bootstrap.py`)
Responsabilidade: Inicialização e orquestração do sistema
- Ponto de entrada do ciclo de vida
- Registra listeners
- Inicia threads de processamento
- Aguarda indefinidamente

**Método Principal**:
```python
bootstrap.start()
  → lifecycle.start()
  → event_bus.emit(SYSTEM_STARTED)
  → runtime_manager.start_thread(wakeword_manager.start)
  → runtime_manager.wait_forever()
```

#### **Event Bus** (`events/event_bus.py`)
Responsabilidade: Pub/Sub central para comunicação inter-módulos

**API**:
- `event_bus.subscribe(event_type, callback)` - Registra listener
- `event_bus.emit(event_type, data)` - Dispara evento assincronamente
- `event_bus.unsubscribe(event_type, callback)` - Desregistra listener

**Tipos de Eventos** (`events/event_types.py`):
```python
# Sistema
SYSTEM_STARTED, SYSTEM_SHUTDOWN, SYSTEM_SLEEP, SYSTEM_WAKE

# Audio
WAKE_WORD_DETECTED, SPEECH_RECOGNIZED, STT_ERROR, TTS_ERROR

# Visão (futuro)
FACE_DETECTED, USER_RECOGNIZED, FACE_UNKNOWN

# Conversação
COMMAND_RECEIVED, PROCESSING_COMMAND
```

#### **Config Manager** (`config/settings_manager.py`)
Responsabilidade: Leitura e acesso de configurações

**Arquivo de Configuração**: `config/settings.yaml`

**API**:
```python
config.get("audio", "sample_rate")  # Retorna 16000
config.get("wakeword", "words")     # Retorna ["cosmo", "zenith", ...]
config.get("path.to.nested", default=None)
```

#### **Logger Manager** (`logger/logger_manager.py`)
Responsabilidade: Logging estruturado e centralizado

**Características**:
- Saída para console e arquivo simultâneos
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Formatação: `[TIMESTAMP] [LEVEL] [MODULE] message`
- Arquivo: `data/logs/cosmo.log`

#### **Runtime Manager** (`runtime/runtime_manager.py`)
Responsabilidade: Gerenciamento de threads e pipeline de eventos

**API**:
```python
runtime_manager.start_thread(target, name)  # Inicia thread daemon
runtime_manager.start_event_pipeline()      # Registra todos os listeners
runtime_manager.wait_forever()              # Bloqueia até interrupção
```

#### **Scheduler** (`scheduler/`)
Status: Em preparação
Responsabilidade Futura: Agendamento de tarefas periódicas

---

### 3.2 Processamento de Audio (audio/)

#### **AudioState** (`audio/audio_state.py`)
Responsabilidade: Máquina de estados para evitar race conditions

**Estados**:
- `IDLE`: Nenhum processamento ativo, wakeword habilitada
- `LISTENING`: STT ativo, wakeword bloqueada

**API**:
```python
audio_state.set_state(AudioState.IDLE)
if audio_state.can_listen():  # True se IDLE
    start_listening()
```

**Crítico**: Previne que wakeword e STT rodem simultaneamente.

#### **WakewordManager** (`audio/wakeword/wakeword_manager.py`)
Responsabilidade: Loop contínuo de captura de áudio

**Funcionamento**:
1. Abre stream PyAudio (sample_rate=16000, channels=1, chunk_size=1024)
2. Loop infinito lê chunks de áudio
3. Passa para WakewordEngine
4. Se detectado, emite `WAKE_WORD_DETECTED`

**API**:
```python
wakeword_manager.start()   # Inicia loop (blocking)
wakeword_manager.stop()    # Finaliza stream
```

**Configuração** (settings.yaml):
```yaml
wakeword:
  words: ["cosmo", "cosmos", "cosme", "zenith", "zênite"]
  model: "vosk-model-small-pt-0.3"
```

#### **WakewordEngine** (`audio/wakeword/wakeword_engine.py`)
Responsabilidade: Processamento de áudio com Vosk (Kaldi)

**Características**:
- Reconhecimento offline com modelo PT-BR
- KaldiRecognizer fornecido por Vosk
- Retorna hipótese de texto (confidence disponível)

**API**:
```python
if wakeword_engine.process_audio(audio_chunk):
    recognized_text = wakeword_engine.get_result()
    return recognized_text in config.wakewords
```

**Modelo**: `models/vosk/vosk-model-small-pt-0.3/`

#### **STTManager** (`audio/stt/stt_manager.py`)
Responsabilidade: Orquestração de escuta ativa com timeout

**Funcionamento**:
1. Registra callback de fala via VADEngine
2. Captura áudio enquanto há fala detectada
3. Contabiliza silêncio (VADEngine.is_silent_since)
4. Quando silêncio > 3s, finaliza captura
5. Emite `SPEECH_RECOGNIZED` com texto final

**Configuração** (settings.yaml):
```yaml
stt:
  silence_threshold_ms: 3000
  chunk_size: 1024
```

**API**:
```python
final_text = await stt_manager.listen_once(timeout=30)
# Retorna string com comando reconhecido
```

#### **STTEngine** (`audio/stt/stt_engine.py`)
Responsabilidade: Interface com Vosk para STT

**API**:
```python
partial_text = stt_engine.process_audio(chunk)  # Retorna ""+"atualização parcial"
final_text = stt_engine.get_final_result()
stt_engine.reset()  # Limpa estado
```

#### **VADEngine** (`audio/vad/vad_engine.py`)
Responsabilidade: Voice Activity Detection com WebRTC

**Características**:
- Utiliza webrtcvad (mais eficiente que energy-based VAD)
- Detecta presença de fala em chunk de áudio
- Frame size: 30ms obrigatório por WebRTC

**API**:
```python
is_speech = vad_engine.is_speech(audio_chunk)
if is_speech:
    silence_start = None
else:
    if silence_start is None:
        silence_start = time.time()
```

#### **CommandProcessor** (`audio/stt/command_processor.py`)
Responsabilidade: Parse e processamento de comandos

Status: Parcialmente implementado
Funcionalidade Futura: Integração com NLU para interpretação de intenções

---

### 3.3 Processamento de Visão (vision/)

**Status**: Em desenvolvimento

Estrutura Preparada:
- **camera/** - Captura de vídeo em tempo real
- **detection/** - Detecção de rostos (Haar Cascades/YOLO)
- **recognition/** - Reconhecimento facial (embeddings)
- **tracking/** - Rastreamento de pessoas

**Eventos Planejados**:
- `FACE_DETECTED` - Rosto detectado no frame
- `USER_RECOGNIZED` - Usuário identificado com confiança
- `UNKNOWN_FACE` - Rosto desconhecido detectado
- `USER_LOST` - Usuário saiu do campo de visão

---

### 3.4 Cognição e Inteligência (cognition/)

**Status**: Em desenvolvimento

**Componentes**:
- **context/** - Contextualização de conversas (histórico, tópico)
- **memory/** - Gestão de memória semântica e episódica
- **personality/** - Traços de personalidade do assistente
- **planner/** - Planejamento de ações e tarefas

**Funcionalidade Futura**: 
- NLU (Natural Language Understanding)
- Sistemas de raciocínio
- Integração com conhecimento externo

---

### 3.5 Persistência de Dados (data/)

#### **Database** (`data/database/database.py`)
Responsabilidade: Abstração de operações SQLite

**Configuração**:
- Database: `data/database/cosmo.db`
- Mode: WAL (Write-Ahead Logging) para concorrência
- Synchronous: NORMAL para balanceamento performance/segurança
- Foreign Keys: Habilitadas

**API**:
```python
database.execute("INSERT INTO users (name) VALUES (?)", ("João",))
rows = database.fetchall("SELECT * FROM conversations WHERE user_id = ?", (user_id,))
user = database.fetchone("SELECT * FROM users WHERE name = ?", ("João",))
```

#### **Repositories** (`data/database/repositories/`)

##### **UserRepository**
Responsabilidade: CRUD de usuários

**Entidades**:
- `id` - PK
- `name` - Nome único do usuário
- `face_id` - ID de face para reconhecimento
- `trust_level` - Nível de confiança (0-100)
- `last_seen` - Último acesso registrado

**API**:
```python
user_id = user_repository.create_user("João", face_id="enc_123")
user = user_repository.get_user_by_id(user_id)
user = user_repository.get_user_by_name("João")
exists = user_repository.user_exists("João")
user_repository.update_trust_level(user_id, 85)
user_repository.save_face_id(user_id, "enc_new_123")
```

##### **ConversationRepository**
Responsabilidade: Histórico de conversas

**Entidades**:
- `id` - PK
- `user_id` - FK para users
- `role` - "user" ou "assistant"
- `message` - Texto da mensagem
- `timestamp` - Quando foi registrada

**API**:
```python
msg_id = conversation_repository.add_message(user_id, "user", "Olá Cosmo")
history = conversation_repository.get_conversation_history(user_id, limit=20)
conversation_repository.clear_history(user_id)
```

**Limite**: Max 20 mensagens por configuração (sliding window)

##### **MemoryRepository**
Responsabilidade: Memorias persistentes do usuário

**Entidades**:
- `id` - PK
- `user_id` - FK para users
- `category` - Tipo de memória (preference, fact, event, etc)
- `content` - Texto da memória
- `importance` - 1-100 (para priorização)
- `created_at` - Quando foi criada

**API**:
```python
mem_id = memory_repository.add_memory(user_id, "preference", "Gosta de música clássica", 80)
memories = memory_repository.get_user_memories(user_id)
pref_memories = memory_repository.get_memories_by_category("preference")
memory_repository.delete_memory(mem_id)
```

##### **FaceRepository**
Responsabilidade: Embeddings de faces para reconhecimento

**Entidades**:
- `id` - PK
- `user_id` - FK para users
- `face_data` - BLOB com embedding
- `created_at` - Quando foi extraído

**API**:
```python
face_id = face_repository.save_face_embedding(user_id, embedding_vector)
embeddings = face_repository.get_face_embeddings(user_id)
```

##### **EventRepository**
Responsabilidade: Log estruturado de eventos do sistema

**Entidades**:
- `id` - PK
- `event_type` - String (WAKE_WORD_DETECTED, etc)
- `data` - JSON com metadados
- `timestamp` - Quando ocorreu

**API**:
```python
event_repository.log_event("WAKE_WORD_DETECTED", {"word": "cosmo", "confidence": 0.95})
events = event_repository.get_events_by_type("WAKE_WORD_DETECTED")
```

##### **SystemRepository**
Responsabilidade: Configurações de runtime

**API**:
```python
system_repository.save_setting("language_preference", "pt-BR")
lang = system_repository.get_setting("language_preference")
```

---

## 4. Fluxo de Inicialização

### 4.1 Sequência de Boot

```
Fase 1: Importação
├─ main.py importa bootstrap

Fase 2: Inicialização (main())
├─ bootstrap.start() é chamado

Fase 3: Bootstrap Executa
├─ lifecycle.start()
│  └─ Sets: lifecycle.running = True, lifecycle.sleeping = False
│
├─ event_bus.emit(SYSTEM_STARTED, {...})
│  └─ system_listener.on_system_started() 
│     └─ Log: "[INFO] Sistema iniciado"
│
├─ runtime_manager.start_event_pipeline()
│  ├─ Registra audio_listener para WAKE_WORD_DETECTED
│  ├─ Registra conversation_listener para COMMAND_RECEIVED
│  ├─ Registra vision_listener para USER_RECOGNIZED (futuro)
│  └─ Registra system_listener para SYSTEM_STARTED
│
├─ runtime_manager.start_thread(
│     target=wakeword_manager.start(),
│     name="WakewordManager"
│   )
│  └─ Thread daemon inicia loop infinito de captura
│
└─ runtime_manager.wait_forever()
   └─ Bloqueia na thread principal aguardando threads daemon

Fase 4: Running
└─ Sistema aguarda eventos (wake word, shutdown signal, etc)
```

### 4.2 Logs de Inicialização Esperados

```
[2026-05-24 10:30:00] [INFO] [bootstrap] Inicializando Zenith Cosmo 42
[2026-05-24 10:30:00] [INFO] [event_bus] Registrando listeners...
[2026-05-24 10:30:00] [INFO] [runtime] Iniciando WakewordManager thread...
[2026-05-24 10:30:01] [INFO] [wakeword_manager] Stream PyAudio aberto (16000 Hz, 1 ch)
[2026-05-24 10:30:01] [INFO] [wakeword_engine] Modelo Vosk carregado
[2026-05-24 10:30:02] [INFO] [bootstrap] Zenith Cosmo 42 online ✓
```

### 4.3 Tratamento de Erros de Boot

**Falha ao abrir stream de áudio**: Exceção catchada em WakewordManager, log ERROR, sistema aguarda retry ou shutdown.

**Falha ao carregar modelo Vosk**: WakewordEngine levanta exceção, bootstrap falha, processo encerra.

**Arquivo settings.yaml faltando**: ConfigManager levanta exceção, boot falha, verificar diretório.

---

## 5. Pipeline de Audio

### 5.1 Estado IDLE (Aguardando Wake Word)

```
┌──────────────────────────────┐
│  WakewordManager (thread)    │
│  - PyAudio stream open       │
│  - Loop infinito              │
└────────┬─────────────────────┘
         │
         ├─ A cada 1024 samples (64ms):
         │  ├─ chunk = stream.read(1024)  ← bloqueia até dado disponível
         │  └─ wakeword_engine.process_audio(chunk)
         │
         ├─ WakewordEngine (Vosk KaldiRecognizer):
         │  ├─ recognizer.AcceptWaveform(chunk)
         │  ├─ if recognizer.PartialResult(): partial_text
         │  └─ if recognizer.Result(): final_text
         │
         ├─ Check: final_text.lower() in ["cosmo", "zenith", ...]
         │  └─ YES:
         │     ├─ event_bus.emit(WAKE_WORD_DETECTED)
         │     └─ audio_state.set_state(LISTENING)
         │
         └─ Loop continua...
```

**Recursos Utilizados**:
- CPU: ~5-10% (processamento Vosk é leve)
- RAM: ~50 MB (modelo Vosk na memória)
- Microfone: Contínuo

**Latência para Detecção**: ~100-500ms após pronunciar palavra

---

### 5.2 Estado LISTENING (Processando Comando)

```
Precondição: audio_state = LISTENING

┌──────────────────────────────────────┐
│ audio_listener (callback do evento)  │
│ on_wake_word_detected()              │
└────────┬─────────────────────────────┘
         │
         └─ runtime_manager.start_thread(
              target=stt_manager.listen_once(timeout=30),
              name="STTManager"
            )
              │
              ├─ STTManager thread inicia
              │  │
              │  └─ Abre novo stream PyAudio (STT dedicado)
              │     │
              │     ├─ Loop de captura:
              │     │  ├─ chunk = stream.read(1024)
              │     │  │
              │     │  ├─ vad_engine.is_speech(chunk)
              │     │  │  ├─ if YES (detecta fala):
              │     │  │  │  ├─ silence_start = None  ← reseta timer
              │     │  │  │  └─ stt_engine.process_audio(chunk)
              │     │  │  │
              │     │  │  └─ if NO (silêncio):
              │     │  │     ├─ if silence_start is None:
              │     │  │     │  └─ silence_start = time.time()
              │     │  │     └─ if time.time() - silence_start > 3.0:
              │     │  │        └─ BREAK (comando finalizado)
              │     │  │
              │     │  └─ if total_time > timeout (30s):
              │     │     └─ BREAK (timeout)
              │     │
              │     ├─ final_text = stt_engine.get_final_result()
              │     │
              │     ├─ Fecha stream
              │     │
              │     └─ event_bus.emit(SPEECH_RECOGNIZED, {
              │           "text": final_text,
              │           "user_id": current_user_id,
              │           "confidence": confidence
              │        })
              │
              └─ STTManager thread encerra

                └─ conversation_listener (callback)
                   on_command_received()
                   │
                   ├─ conversation_repository.add_message(
                   │    user_id, "user", final_text
                   │  )
                   │
                   ├─ command_processor.process_command(final_text)
                   │
                   ├─ event_bus.emit(COMMAND_PROCESSED, {...})
                   │
                   └─ audio_state.set_state(IDLE)  ← volta ao padrão
                      └─ WakewordManager retoma operação normal
```

**VAD - Voice Activity Detection**:
- WebRTC VAD com threshold padrão
- Detecta presença de fala vs ruído de fundo
- Frame size: 30ms (requerido)
- Baixa latência (~10ms de processamento)

**STT - Reconhecimento de Fala**:
- Vosk KaldiRecognizer (modelo PT-BR)
- Processamento em tempo real
- Retorna hipóteses parciais progressivamente
- Resultado final com END_OF_UTTERANCE

**Timeout**:
- Silêncio: 3 segundos
- Máximo absoluto: 30 segundos
- Pode ser configurado em settings.yaml

---

### 5.3 Fluxo de Estados de Audio

```
┌─────────────────────────────────────────────────────────┐
│                    ESTADO IDLE                          │
│  ├─ WakewordManager ativo                              │
│  ├─ audio_state.state == IDLE                          │
│  └─ Aguardando palavra-chave                           │
└──────────────┬──────────────────────────────────────────┘
               │
               │ [WAKE_WORD_DETECTED event]
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                  ESTADO LISTENING                       │
│  ├─ audio_state.state == LISTENING                     │
│  ├─ STTManager thread ativo                            │
│  ├─ WakewordManager bloqueado (não processa eventos)  │
│  └─ Capturando fala de comando                         │
└──────────────┬──────────────────────────────────────────┘
               │
               │ [SPEECH_RECOGNIZED event] ou [TIMEOUT]
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                  ESTADO IDLE                            │
│  └─ Volta ao loop de aguardando wake word             │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Sistema de Eventos

### 6.1 Arquitetura do Event Bus

**Padrão**: Pub/Sub (Observer)
**Implementação**: Singleton global
**Modo**: Síncrono (eventos processados imediatamente)

**API**:
```python
class EventBus:
    def subscribe(event_type: str, callback: Callable) -> None
    def unsubscribe(event_type: str, callback: Callable) -> None
    def emit(event_type: str, data: dict) -> None
    def clear_subscribers() -> None
```

### 6.2 Tipos de Eventos Principais

#### **Sistema**
| Evento | Data | Listener |
|--------|------|----------|
| `SYSTEM_STARTED` | `{timestamp}` | system_listener |
| `SYSTEM_SHUTDOWN` | `{reason, timestamp}` | - |
| `SYSTEM_SLEEP` | `{timestamp}` | - |
| `SYSTEM_WAKE` | `{timestamp}` | - |

#### **Audio**
| Evento | Data | Listener |
|--------|------|----------|
| `WAKE_WORD_DETECTED` | `{word, confidence}` | audio_listener |
| `SPEECH_RECOGNIZED` | `{text, user_id, confidence}` | conversation_listener |
| `STT_ERROR` | `{error, timestamp}` | system_listener |
| `TTS_ERROR` | `{error, timestamp}` | system_listener |

#### **Visão** (Futuro)
| Evento | Data | Listener |
|--------|------|----------|
| `FACE_DETECTED` | `{face_id, bbox, confidence}` | vision_listener |
| `USER_RECOGNIZED` | `{user_id, face_id, confidence}` | vision_listener |
| `UNKNOWN_FACE` | `{face_id, bbox}` | vision_listener |

#### **Conversação**
| Evento | Data | Listener |
|--------|------|----------|
| `COMMAND_RECEIVED` | `{text, user_id}` | conversation_listener |
| `RESPONSE_GENERATED` | `{text, user_id}` | - |

### 6.3 Fluxo de Registro de Listeners

```
1. bootstrap.start()
   └─ runtime_manager.start_event_pipeline()
      │
      ├─ Registra audio_listener:
      │  event_bus.subscribe(WAKE_WORD_DETECTED, 
      │    audio_listener.on_wake_word_detected)
      │
      ├─ Registra conversation_listener:
      │  event_bus.subscribe(SPEECH_RECOGNIZED,
      │    conversation_listener.on_command_received)
      │
      ├─ Registra system_listener:
      │  event_bus.subscribe(SYSTEM_STARTED,
      │    system_listener.on_system_started)
      │
      └─ Registra vision_listener (futuro):
         event_bus.subscribe(FACE_DETECTED,
           vision_listener.on_face_detected)

2. Listeners prontos para receber eventos

3. WakewordManager inicia e começa a emitir eventos
```

### 6.4 Exemplo de Fluxo de Eventos

```
Timeline:

[T=00ms] User diz "Olá Cosmo"

[T=100ms] WakewordEngine.process_audio() completa processamento
          ├─ Detecta palavra "cosmo"
          ├─ Confiança: 0.94
          └─ event_bus.emit(WAKE_WORD_DETECTED, {
               "word": "cosmo",
               "confidence": 0.94
             })

[T=101ms] Event bus dispara callbacks registrados:
          ├─ audio_listener.on_wake_word_detected() executada
          │  └─ runtime_manager.start_thread(stt_manager.listen_once)
          └─ system_listener.on_wake_word_detected() (log)

[T=102ms] STTManager thread inicia e abre stream

[T=150ms] User diz "qual é a hora?"

[T=500ms] VADEngine detecta fala
          └─ silence_start = None

[T=3000ms] Silêncio de 3 segundos detectado
           ├─ STTManager finaliza captura
           ├─ Texto final: "qual é a hora"
           └─ event_bus.emit(SPEECH_RECOGNIZED, {
                "text": "qual é a hora",
                "user_id": 1,
                "confidence": 0.89
              })

[T=3001ms] Event bus dispara callbacks:
           ├─ conversation_listener.on_command_received() executada
           │  ├─ conversation_repository.add_message(1, "user", "qual é a hora")
           │  ├─ command_processor.process_command("qual é a hora")
           │  └─ event_bus.emit(COMMAND_PROCESSED, {...})
           │
           └─ STTManager thread encerra

[T=3002ms] audio_state.set_state(IDLE)
           └─ WakewordManager retoma aguardando próxima palavra-chave
```

---

## 7. Persistência de Dados

### 7.1 Banco de Dados SQLite

**Arquivo**: `data/database/cosmo.db`

**Características**:
- **WAL Mode**: Habilitado para permitir leitura durante escrita
- **Foreign Keys**: Habilitadas para integridade referencial
- **Synchronous**: NORMAL (balanceamento entre performance e segurança)

**Tabelas**:

#### `users`
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  face_id TEXT,
  trust_level INTEGER DEFAULT 50,
  last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `conversations`
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

#### `memories`
```sql
CREATE TABLE memories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  content TEXT NOT NULL,
  importance INTEGER DEFAULT 50 CHECK (importance >= 0 AND importance <= 100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_memories_category ON memories(category);
```

#### `faces`
```sql
CREATE TABLE faces (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  face_data BLOB NOT NULL,
  embedding_vector BLOB,
  confidence REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### `events`
```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  data JSON,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
Create INDEX idx_events_type ON events(event_type);
```

#### `system`
```sql
CREATE TABLE system (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 Padrão Repository

**Responsabilidade**: Abstração de acesso a dados, encapsular queries SQL

**Exemplo**:
```python
class UserRepository:
    def __init__(self, database: Database):
        self.db = database
    
    def create_user(self, name: str, face_id: str = None) -> int:
        """Cria novo usuário, retorna ID"""
        user_id = self.db.execute(
            "INSERT INTO users (name, face_id) VALUES (?, ?)",
            (name, face_id)
        )
        return user_id
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Retorna usuário por ID ou None"""
        return self.db.fetchone(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
    
    def get_user_by_name(self, name: str) -> dict:
        """Retorna usuário por nome ou None"""
        return self.db.fetchone(
            "SELECT * FROM users WHERE name = ?",
            (name,)
        )
```

**Benefícios**:
- Desacoplamento da lógica de queries
- Facilita testes (mock repository)
- Facilita mudanças de banco (NoSQL, PostgreSQL, etc)
- Validação de dados em um lugar

### 7.3 Fluxo de Persistência

```
Evento: SPEECH_RECOGNIZED
  ↓
conversation_listener.on_command_received()
  ├─ Extrai: user_id, text do evento
  │
  ├─ conversation_repository.add_message(user_id, "user", text)
  │  │
  │  └─ database.execute(
  │       "INSERT INTO conversations (user_id, role, message) VALUES (?, ?, ?)",
  │       (user_id, "user", text)
  │     )
  │     │
  │     └─ SQLite escreve na WAL, replica para main DB
  │
  └─ Log: "[INFO] Mensagem salva para usuário X"
```

### 7.4 Limitações de Histórico

```yaml
# settings.yaml
memory:
  max_conversation_history: 20
```

**Implementação Planejada**:
```python
def get_conversation_history(user_id: int, limit: int = 20):
    """Retorna últimas N mensagens (sliding window)"""
    return database.fetchall(
        "SELECT * FROM conversations 
         WHERE user_id = ? 
         ORDER BY timestamp DESC 
         LIMIT ?",
        (user_id, limit)
    )
```

---

## 8. Máquinas de Estado

### 8.1 Máquina de Estado de Audio

**Estados**: IDLE, LISTENING

```
┌─────────────────────────────────────────────────────────┐
│                    IDLE                                 │
│  - WakewordManager aguardando                           │
│  - STT desativado                                       │
│  - Consumo baixo                                        │
└─────────┬───────────────────────────────────────────────┘
          │
          │ Evento: WAKE_WORD_DETECTED
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                    LISTENING                            │
│  - STTManager aguardando fala                           │
│  - WakewordManager bloqueado                            │
│  - Processamento ativo                                  │
└─────────┬───────────────────────────────────────────────┘
          │
          │ Evento: SPEECH_RECOGNIZED ou TIMEOUT
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                    IDLE                                 │
└─────────────────────────────────────────────────────────┘
```

**Implementação**:
```python
class AudioState(Enum):
    IDLE = "idle"
    LISTENING = "listening"

# Uso em WakewordManager:
if audio_state.state == AudioState.IDLE:
    # Processa wakeword
    if word_detected:
        audio_state.state = AudioState.LISTENING
        event_bus.emit(WAKE_WORD_DETECTED, {...})

# Prevenção de race condition:
def can_listen(self) -> bool:
    return self.state == AudioState.IDLE
```

### 8.2 Máquina de Estado do Sistema

**Estados**: NOT_STARTED, RUNNING (+ SLEEPING variant)

```
┌───────────────────┐
│  NOT_STARTED      │
└────────┬──────────┘
         │
         │ bootstrap.start()
         │
         ▼
┌────────────────────────────────────────────────────────┐
│  RUNNING                                               │
│  ├─ lifecycle.running = True                           │
│  ├─ lifecycle.sleeping = False                         │
│  └─ Threads ativas, events processados                 │
└────┬───────────────────────────────┬──────────────────┘
     │                               │
     │ Event: SYSTEM_SLEEP           │ Event: SYSTEM_WAKE
     │                               │
     ▼                               ▼
  ┌──────────┐                    ┌──────────┐
  │SLEEPING  │                    │SLEEPING  │
  │+ running │◄───────────────────│+ running │
  │+ sleep   │   (same as RUNNING)│+ sleep   │
  └──────────┘                    └──────────┘

     │
     │ bootstrap.shutdown()
     │
     ▼
┌───────────────────┐
│  STOPPED          │
└───────────────────┘
```

**API** (`lifecycle.py`):
```python
lifecycle.start()        # Sets: running=True, sleeping=False
lifecycle.stop()         # Sets: running=False
lifecycle.sleep()        # Sets: sleeping=True (running ainda True)
lifecycle.wake()         # Sets: sleeping=False
lifecycle.is_running()   # Retorna running
lifecycle.is_sleeping()  # Retorna sleeping
```

---

## 9. Padrões de Design

### 9.1 Event-Driven Architecture

**Benefícios**:
- Desacoplamento de módulos
- Reatividade em tempo real
- Escalabilidade (fácil adicionar novos listeners)

**Implementação**:
```python
# Publicador
event_bus.emit(WAKE_WORD_DETECTED, {"word": "cosmo"})

# Subscriber
event_bus.subscribe(WAKE_WORD_DETECTED, on_wake_word_detected)

# Callback
def on_wake_word_detected(data):
    print(f"Word: {data['word']}")
```

### 9.2 Singleton Pattern

Instâncias globais para garantir estado centralizado:

```python
# core/
event_bus = EventBus()          # Única instância
logger = LoggerManager.setup()  # Logger compartilhado
config = ConfigManager()        # Config centralizada
lifecycle = Lifecycle()         # Estado do sistema
runtime = RuntimeManager()      # Gerenciador de threads

# Uso em qualquer módulo:
from cosmo.core import event_bus, logger
logger.info("Sistema iniciado")
event_bus.emit(SYSTEM_STARTED, {})
```

### 9.3 Observer Pattern

**Componente**: Listeners registrados dinamicamente

```python
class Listener(ABC):
    @abstractmethod
    def on_event(self, data: dict):
        pass

# Implementação
class SystemListener(Listener):
    def on_event(self, data: dict):
        logger.info(f"Evento do sistema: {data}")

# Registro
event_bus.subscribe(SYSTEM_STARTED, system_listener.on_event)
```

### 9.4 Repository Pattern

Abstração de persistência:

```python
class UserRepository:
    def __init__(self, database: Database):
        self.db = database
    
    # Abstração de queries SQL
    def create_user(self, name: str):
        # SQL encapsulado aqui
        pass

# Uso
user_repo = UserRepository(database)
user = user_repo.get_user_by_name("João")
```

### 9.5 Manager Pattern

Orquestração de componentes complexos:

```python
class WakewordManager:
    """Gerencia o ciclo de vida da detecção de wake word"""
    
    def __init__(self, engine, event_bus, audio_state):
        self.engine = engine
        self.event_bus = event_bus
        self.audio_state = audio_state
    
    def start(self):
        # Orquestra: abrir stream, processar, emitir eventos
        while True:
            chunk = self.stream.read()
            if self.engine.process(chunk):
                self.event_bus.emit(WAKE_WORD_DETECTED, {...})
    
    def stop(self):
        self.stream.close()
```

### 9.6 State Machine Pattern

Controle de fluxo com transições explícitas:

```python
class AudioState:
    """Máquina de estados para áudio"""
    
    def __init__(self):
        self.state = State.IDLE
    
    def transition_to_listening(self):
        if self.state == State.IDLE:
            self.state = State.LISTENING
            return True
        return False  # Transição inválida
    
    def transition_to_idle(self):
        if self.state == State.LISTENING:
            self.state = State.IDLE
            return True
        return False
```

---

## 10. Configuração do Sistema

### 10.1 Arquivo settings.yaml

**Localização**: `cosmo/core/config/settings.yaml`

**Estrutura**:

```yaml
# Identidade do Sistema
system:
  name: "Zenith Cosmo 42"
  codename: "ZC-42"
  version: "0.1.0"
  language: "pt-BR"
  debug: true

# Configuração de Audio
audio:
  sample_rate: 16000          # Hz
  channels: 1                 # Mono
  chunk_size: 1024            # Samples por chunk
  dtype: "int16"              # Tipo de dado
  device_index: null          # Microfone padrão
  
# Wake Word Detection
wakeword:
  enabled: true
  words:
    - "cosmo"
    - "cosmos"
    - "cosme"
    - "zenith"
    - "zênite"
  confidence_threshold: 0.7
  model_path: "models/vosk/vosk-model-small-pt-0.3"

# Speech-to-Text
stt:
  engine: "vosk"
  silence_threshold_ms: 3000   # 3 segundos
  max_listening_time_ms: 30000 # 30 segundos
  confidence_threshold: 0.5

# Voice Activity Detection
vad:
  engine: "webrtcvad"
  aggressiveness: 2            # 0-3 (2 é recomendado)
  frame_ms: 30                 # Requerido para WebRTC VAD

# Text-to-Speech (TTS)
tts:
  engine: "piper"
  language: "pt-BR"
  voice_model: "pt_BR-faber-medium"
  speed: 1.0                   # 0.5-2.0
  volume: 1.0                  # 0.0-2.0
  model_path: "models/piper/piper-voices"

# Reconhecimento Facial (Futuro)
vision:
  enabled: false
  camera_index: 0
  resolution:
    width: 640
    height: 480
  grayscale: true
  face_detector: "haar"        # haar, yolo, mediapipe
  face_recognition_model: "facenet"

# Configuração de Memória
face_recognition:
  confidence_threshold: 70     # 0-100

# Limite de Histórico
memory:
  max_conversation_history: 20
  max_memories_per_user: 100

# Banco de Dados
database:
  type: "sqlite"
  path: "data/database/cosmo.db"
  enable_wal: true
  foreign_keys: true
  synchronous: "NORMAL"

# Logging
logging:
  level: "DEBUG"               # DEBUG, INFO, WARNING, ERROR, CRITICAL
  console: true
  file: true
  file_path: "data/logs/cosmo.log"
  max_file_size_mb: 10
  backup_count: 5

# Scheduler (Futuro)
scheduler:
  enabled: false
  timezone: "America/Sao_Paulo"
  max_workers: 4
```

### 10.2 Acesso às Configurações

```python
from cosmo.core.config import config

# Acesso simples
sample_rate = config.get("audio", "sample_rate")  # 16000

# Acesso com default
debug = config.get("system", "debug", default=False)

# Acesso nested
tts_engine = config.get("tts", "engine")  # "piper"
```

### 10.3 Arquivo de Configuração Expandido

**Exemplo com todos os parâmetros**:

```yaml
system:
  name: "Zenith Cosmo 42"
  codename: "ZC-42"
  version: "0.1.0"
  language: "pt-BR"
  timezone: "America/Sao_Paulo"
  debug: true
  log_level: "DEBUG"

audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024
  dtype: "int16"
  format: "FLOAT"
  device_index: null
  
wakeword:
  enabled: true
  words: ["cosmo", "zenith"]
  confidence_threshold: 0.7
  model_path: "models/vosk/vosk-model-small-pt-0.3"
  
stt:
  engine: "vosk"
  silence_threshold_ms: 3000
  max_listening_time_ms: 30000
  confidence_threshold: 0.5
  partial_results: true
  
vad:
  engine: "webrtcvad"
  aggressiveness: 2
  frame_ms: 30
  
tts:
  engine: "piper"
  language: "pt-BR"
  voice_model: "pt_BR-faber-medium"
  speed: 1.0
  volume: 1.0
  
memory:
  max_conversation_history: 20
  
database:
  path: "data/database/cosmo.db"
  
logging:
  level: "DEBUG"
  file_path: "data/logs/cosmo.log"
```

---

## 11. Fluxos de Dados

### 11.1 Fluxo Principal: Do Áudio ao Armazenamento

```
┌──────────────────────────────────────────────────────────────┐
│ 1. CAPTURA DE ÁUDIO (WakewordManager)                       │
│    PyAudio.stream.read(1024) → raw PCM bytes                │
│    Repeat a cada ~64ms                                       │
└───────────┬──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. DETECÇÃO DE WAKE WORD (WakewordEngine)                   │
│    Vosk KaldiRecognizer.AcceptWaveform(chunk)               │
│    Processa Kaldi ASR → partial/final text                  │
└───────────┬──────────────────────────────────────────────────┘
            │
            ├─ NO: Continua loop
            │
            └─ YES: word in config.wakewords
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. EMISSÃO DE EVENTO (Event Bus)                            │
│    event_bus.emit(WAKE_WORD_DETECTED,                       │
│      {"word": "cosmo", "confidence": 0.94}                  │
│    )                                                         │
└───────────┬──────────────────────────────────────────────────┘
            │
            ├─ audio_listener.on_wake_word_detected(data)
            │  └─ runtime_manager.start_thread(stt_manager...)
            │
            ├─ system_listener.on_wake_word_detected(data)
            │  └─ logger.info(f"Wake word: {data['word']}")
            │
            └─ Outros listeners registrados...
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. CAPTURA DE COMANDO (STTManager thread)                   │
│    ├─ audio_state.state = LISTENING (bloqueia wakeword)    │
│    ├─ Nova captura de áudio em paralelo                    │
│    └─ Aguarda fala + 3s silêncio                           │
└───────────┬──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. DETECÇÃO DE ATIVIDADE DE VOZ (VADEngine)                 │
│    ├─ webrtcvad.is_speech(chunk) → bool                    │
│    ├─ Controla contagem de silêncio                        │
│    └─ Alimenta STTEngine enquanto há fala                  │
└───────────┬──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. RECONHECIMENTO DE FALA (STTEngine)                       │
│    ├─ Vosk KaldiRecognizer.AcceptWaveform(chunk)           │
│    ├─ Retorna texto parcial progressivamente                │
│    └─ Ao finalizar: get_final_result() → string            │
└───────────┬──────────────────────────────────────────────────┘
            │
            │ Quando silêncio > 3s ou timeout
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. EMISSÃO DE RECONHECIMENTO (Event Bus)                    │
│    event_bus.emit(SPEECH_RECOGNIZED,                        │
│      {"text": "qual é a hora",                              │
│       "user_id": 1,                                          │
│       "confidence": 0.89}                                    │
│    )                                                         │
└───────────┬──────────────────────────────────────────────────┘
            │
            ├─ conversation_listener.on_command_received(data)
            │  ├─ conversation_repository.add_message(
            │  │   user_id=1,
            │  │   role="user",
            │  │   message="qual é a hora"
            │  │ )
            │  ├─ command_processor.process_command(text)
            │  └─ audio_state.state = IDLE
            │
            └─ system_listener (log)
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 8. PERSISTÊNCIA (Database)                                  │
│    INSERT INTO conversations (                              │
│      user_id, role, message, timestamp                      │
│    ) VALUES (1, "user", "qual é a hora", NOW())            │
│                                                              │
│    SQLite WAL escreve → sincroniza com main DB             │
└──────────────────────────────────────────────────────────────┘
```

### 11.2 Fluxo de Reconhecimento Facial (Futuro)

```
[Vision Module] (Thread separada, planejada)
      │
      ├─ Camera.capture() → frame (BGR)
      │
      ├─ FaceDetector.detect(frame) → [bboxes]
      │
      ├─ if faces detected:
      │  ├─ event_bus.emit(FACE_DETECTED, {"count": 1, ...})
      │  │
      │  ├─ FaceRecognizer.recognize(face_region) → embedding
      │  │
      │  ├─ FaceRepository.find_match(embedding) → user_id
      │  │
      │  ├─ if match found (confidence > threshold):
      │  │  ├─ event_bus.emit(USER_RECOGNIZED, 
      │  │  │   {"user_id": X, "confidence": 0.92}
      │  │  │ )
      │  │  │
      │  │  └─ vision_listener.on_user_recognized(data)
      │  │     ├─ user_repository.update_last_seen(user_id)
      │  │     └─ context.set_current_user(user_id)
      │  │
      │  └─ else:
      │     └─ event_bus.emit(UNKNOWN_FACE, {...})
      │
      └─ Continue lendo próximo frame
```

### 11.3 Fluxo de Memória (Futuro)

```
[Cognition Module]
      │
      ├─ Após USER_RECOGNIZED event:
      │  │
      │  └─ memory_module.load_user_memory(user_id)
      │     │
      │     ├─ memory_repository.get_user_memories(user_id)
      │     │
      │     └─ context.set_user_memories([...])
      │
      ├─ Ao processar COMMAND_RECEIVED:
      │  │
      │  └─ memory_module.extract_knowledge(text, user_id)
      │     │
      │     ├─ NLU analisa texto
      │     │
      │     ├─ Se contém informação relevante:
      │     │  │
      │     │  └─ memory_repository.add_memory(
      │     │      user_id, category, content, importance
      │     │    )
      │     │
      │     └─ event_bus.emit(MEMORY_UPDATED, {...})
      │
      └─ Resposta gerada com contexto de memória
```

---

## 12. Roadmap Futuro

### 12.1 Curto Prazo (1-2 meses)

**Audio/Voice**:
- [ ] Implementar TTS completo (Piper com múltiplas vozes)
- [ ] Melhorar VAD (tuning de aggressiveness)
- [ ] Suporte a múltiplas línguas (EN, ES, FR)

**Cognition**:
- [ ] NLU básico (intent detection com regex/patterns)
- [ ] Context manager (histórico de conversas)
- [ ] Memory system (armazenar e recuperar fatos)

**Data**:
- [ ] Implementar todas as queries de Repository
- [ ] Migrations automáticas de schema
- [ ] Backup automático de database

### 12.2 Médio Prazo (2-4 meses)

**Vision**:
- [ ] Detecção facial com Haar Cascades
- [ ] Reconhecimento facial com embeddings (FaceNet ou ArcFace)
- [ ] Rastreamento de pessoas

**Interfaces**:
- [ ] REST API (Flask/FastAPI)
- [ ] CLI (argparse ou click)
- [ ] WebSocket para integração web

**Performance**:
- [ ] Async event bus (asyncio)
- [ ] Multithreading otimizado
- [ ] Compressão de audio para economizar CPU

### 12.3 Longo Prazo (4+ meses)

**Inteligência Avançada**:
- [ ] Planejamento de tarefas (STRIPS, HTN)
- [ ] Integração com LLMs locais (Ollama, LM Studio)
- [ ] Raciocínio multimodal

**Sistema Distribuído**:
- [ ] IPC entre processos
- [ ] Suporte para múltiplas instâncias
- [ ] Sincronização de memória

**DevOps**:
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Telemetria e monitoramento

---

## 12.4 Mudanças Recentes (Sprint Atual)

### Novos Arquivos (8 total)

| Arquivo | Tipo | Linhas | Responsabilidade |
|---------|------|--------|------------------|
| `async_event_bus.py` | Core | 562 | Event bus assíncrono com fila e métricas |
| `async_runtime.py` | Core | 52 | Runtime assíncrono para orchestração de tasks |
| `system_async_listener.py` | Core | 60 | Exemplo de listener assíncrono |
| `task_manager.py` | Core | 15 | Wrapper para criação de tasks assíncronas |

### Padrão Dual Implementado

✅ **Event Bus Síncrono** (já existia)
- Dispatching imediato
- Sem overhead de métricas
- Para eventos críticos

✅ **Event Bus Assíncrono** (NEW)
- Fila bounded (max 100 eventos)
- 19 métricas detalhadas
- Listeners com timeout (10s)
- Tracing com UUID
- Rastreamento de sucesso/timeout/erro

### Métrica de Desempenho

O AsyncEventBus coleta automaticamente:

**Eventos**: 7 métricas
- events_received / emitted / dispatched / dropped
- events_completed / failed / partial_failures

**Listeners**: 3 métricas
- listener_successes / timeouts / errors

**Infraestrutura**: 4 métricas
- queue_peak / current_queue_size
- avg_event_processing_time
- avg_listener_processing_time

**Total**: 19 métricas em tempo real

### Compatibilidade

- ✅ Ambos os event buses rodam em paralelo
- ✅ Listeners sync continuam funcionando
- ✅ Novos listeners podem ser async
- ✅ Sem breaking changes no código existente

### Próximas Evoluções

- [ ] Priorização de eventos na fila
- [ ] Retries automáticos para listeners falhados
- [ ] Circuit breaker para listeners com erro recorrente
- [ ] Integração com metrics server (Prometheus)
- [ ] Dashboard de monitoramento real-time

---

## 14. Conclusões

### 14.1 Strengths (Pontos Fortes)

✅ **Arquitetura Limpa**: Separação clara de responsabilidades, desacoplamento via event bus.

✅ **Offline-First**: Sem dependência de APIs externas, garantindo privacidade.

✅ **Modular**: Fácil adicionar novos componentes (Vision, Cognition, Interfaces) sem impactar existentes.

✅ **Event-Driven**: Comunicação assíncrona e reativa, escalável.

✅ **Persistência Robusta**: Banco de dados com repositories, WAL mode para segurança.

✅ **Configuração Centralizada**: YAML único para todas as settings.

✅ **Thread-Safe**: Máquinas de estado previnem race conditions.

### 14.2 Areas de Melhoria

⚠️ **Error Handling**: Adicionar recovery strategies e circuit breakers.

⚠️ **Logging**: Implementar log rotation, aggregation, alertas.

⚠️ **Testing**: Criar testes unitários e integração (pytest).

⚠️ **Documentation**: Adicionar docstrings (PyDoc) em classes/métodos.

⚠️ **Performance**: Profile CPU/memory, otimizar loops críticos.

⚠️ **Observability**: Adicionar tracing distribuído, métricas.

### 14.3 Fluxo Simplificado (TL;DR)

```
1. Sistema inicia (bootstrap.start())
   └─ Event bus registra listeners
   └─ WakewordManager thread começa a escutar

2. Usuário diz palavra-chave ("Cosmo")
   └─ WakewordEngine detecta (Vosk)
   └─ WAKE_WORD_DETECTED event emitido
   └─ audio_listener inicia STTManager

3. Usuário fala comando ("qual é a hora?")
   └─ VADEngine detecta fala
   └─ STTEngine processa (Vosk)
   └─ Quando silêncio > 3s, SPEECH_RECOGNIZED event

4. Evento processado
   └─ conversation_listener salva em banco de dados
   └─ command_processor analisa texto
   └─ audio_state volta para IDLE

5. Volta para passo 2 (aguardando próxima palavra-chave)
```

### 14.4 Diagrama de Stack Tecnológico

```
┌─────────────────────────────────────────────────────┐
│  Aplicação (cosmo/)                                 │
│  ├─ Audio: STT, TTS, VAD, Wakeword                 │
│  ├─ Vision: Face detection/recognition (futuro)    │
│  ├─ Cognition: NLU, Context, Memory (futuro)      │
│  └─ Core: Events, Config, Logger, Runtime         │
├─────────────────────────────────────────────────────┤
│  Python 3.10+                                       │
│  ├─ PyAudio (áudio)                                 │
│  ├─ Vosk (STT/Wakeword)                            │
│  ├─ WebRTC VAD (detecção de voz)                   │
│  ├─ Piper (TTS)                                     │
│  ├─ OpenCV (visão)                                 │
│  └─ SQLite3 (banco de dados)                       │
├─────────────────────────────────────────────────────┤
│  Modelos Externos (models/)                         │
│  ├─ Vosk: vosk-model-small-pt-0.3 (Kaldi ASR)     │
│  ├─ Piper: pt_BR-faber-medium (TTS)               │
│  └─ Haar: haarcascade_frontalface_default.xml     │
├─────────────────────────────────────────────────────┤
│  Hardware                                           │
│  ├─ Microfone (captura de áudio)                   │
│  ├─ Alto-falante (reprodução)                      │
│  ├─ Camera (futuro - reconhecimento facial)        │
│  └─ CPU/RAM (processamento)                        │
└─────────────────────────────────────────────────────┘
```

---

## Documento Finalizado

**Data**: 25 de Maio de 2026
**Versão da Aplicação**: 0.1.1 (ZC-42) - Com Async Infrastructure
**Última Atualização**: Adicionada infraestrutura assíncrona com Event Bus Dual, AsyncRuntime e Métricas
**Escopo**: Análise completa da arquitetura, fluxos, e componentes do sistema Cosmo.

Este documento serve como referência técnica para desenvolvimento, manutenção e evolução do projeto Zenith Cosmo 42.

Para dúvidas sobre componentes específicos, consulte os arquivos Python correspondentes em `cosmo/` e `cosmo/core/`.
