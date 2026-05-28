# fila assíncrona
# dispatcher async
# desacoplamento temporal
# listeners concorrentes
# bounded queue
# tracing
# métricas
# prioridades
# base para retries

import asyncio
import uuid
import time

from collections import defaultdict

from cosmo.core.logger.logger_manager import logger


class AsyncEventBus:

    # ==================================================
    # PRIORIDADES
    # ==================================================

    PRIORITY_CRITICAL = 0
    PRIORITY_AUDIO = 1
    PRIORITY_CONVERSATION = 2
    PRIORITY_COGNITION = 3
    PRIORITY_BACKGROUND = 5

    def __init__(self):

        self.listeners = defaultdict(list)

        self.max_queue_size = 100

        # ==================================================
        # PRIORITY QUEUE
        # ==================================================

        self.queue = asyncio.PriorityQueue(
            maxsize=self.max_queue_size
        )

        # ==================================================
        # SEQUENCE COUNTER
        # evita comparação de dicts
        # quando prioridades forem iguais
        # ==================================================

        self.sequence_lock = asyncio.Lock()

        self.sequence = 0

        self.running = False

        self.listener_timeout = 10

        self.metrics = {

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
            "events_unhandled": 0,

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
            "avg_listener_processing_time": 0.0,
            "avg_queue_wait_time": 0.0
        }

    # ==================================================
    # SUBSCRIBE
    # ==================================================

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

    # ==================================================
    # EMIT
    # ==================================================

    async def emit(
        self,
        event_name,
        data=None,
        priority=PRIORITY_BACKGROUND
    ):

        self.metrics["events_received"] += 1

        event = {
            "id": str(uuid.uuid4()),
            "name": event_name,
            "data": data,
            "priority": priority,
            "created_at": time.time(),
            "dispatched_at": None
        }

        try:

            # ==================================================
            # SEQUENCE
            # ==================================================

            async with self.sequence_lock:
                self.sequence += 1
                sequence = self.sequence

            # ==================================================
            # PRIORITY INSERT
            # ==================================================

            self.queue.put_nowait(
                (
                    priority,
                    sequence,
                    event
                )
            )

            self.metrics["events_emitted"] += 1

            current_size = self.queue.qsize()

            self.metrics[
                "current_queue_size"
            ] = current_size

            if (
                current_size >
                self.metrics["queue_peak"]
            ):

                self.metrics[
                    "queue_peak"
                ] = current_size

        except asyncio.QueueFull:

            self.metrics[
                "events_dropped"
            ] += 1

            logger.warning(
                f"Fila cheia. "
                f"Evento descartado: "
                f"{event_name}"
            )

            return

        logger.info(
            f"Evento enfileirado: "
            f"{event_name} "
            f"(priority={priority}) "
            f"(fila={self.queue.qsize()})"
        )

        logger.info(
            f"[TRACE] "
            f"{event['id']} "
            f"queued -> "
            f"{event['name']} "
            f"(priority={priority})"
        )

    # ==================================================
    # START
    # ==================================================

    async def start(self):

        self.running = True

        logger.info(
            "Async event bus online"
        )

        while self.running:

            (
                priority,
                sequence,
                event
            ) = await self.queue.get()

            # ==================================================
            # DISPATCH TIMESTAMP
            # ==================================================

            event["dispatched_at"] = time.time()

            queue_wait = (
                event["dispatched_at"] -
                event["created_at"]
            )
            logger.info(
                f"[TRACE] "
                f"{event['id']} "
                f"queue_wait -> "
                f"{queue_wait:.4f}s"
            )

            self.metrics[
                "events_dispatched"
            ] += 1

            # ==================================================
            # QUEUE LATENCY METRICS
            # ==================================================

            dispatched = self.metrics[
                "events_dispatched"
            ]

            current_avg = self.metrics[
                "avg_queue_wait_time"
            ]

            self.metrics[
                "avg_queue_wait_time"
            ] = (
                (
                    current_avg * (dispatched - 1)
                ) + queue_wait
            ) / dispatched

            # ==================================================
            # STARVATION WARNING
            # ==================================================

            if queue_wait > 5:

                logger.warning(
                    f"[TRACE] "
                    f"{event['id']} "
                    f"high_queue_latency -> "
                    f"{queue_wait:.2f}s"
                )

            self.metrics[
                "current_queue_size"
            ] = self.queue.qsize()

            asyncio.create_task(
                self._dispatch_event(event)
            )

            self.queue.task_done()
            
    # ==================================================
    # DISPATCH
    # ==================================================

    async def _dispatch_event(
        self,
        event
    ):

        event_name = event["name"]

        listeners = self.listeners.get(
            event_name,
            []
        )

        logger.info(
            f"[TRACE] "
            f"{event['id']} "
            f"dispatched -> "
            f"{event_name} "
            f"(priority={event['priority']})"
        )

        # ==================================================
        # NO LISTENERS
        # ==================================================

        if not listeners:

            logger.warning(
                f"[TRACE] "
                f"{event['id']} "
                f"no_listeners -> "
                f"{event_name}"
            )

            self.metrics[
                "events_unhandled"
            ] += 1
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

        classified_events = (
            self.metrics["events_completed"] +
            self.metrics["events_failed"] +
            self.metrics[
                "events_partial_failures"
            ]
        )

        current_avg = self.metrics[
            "avg_event_processing_time"
        ]

        self.metrics[
            "avg_event_processing_time"
        ] = (
            (
                current_avg *
                classified_events
            ) + elapsed
        ) / (classified_events + 1)

        # ==================================================
        # EVENT CLASSIFICATION
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

    # ==================================================
    # SHUTDOWN
    # ==================================================

    async def shutdown(self):

        self.running = False

    # ==================================================
    # LISTENER EXECUTION
    # ==================================================

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
                time.perf_counter() -
                start_time
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
                    current_avg *
                    (successes - 1)
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

    # ==================================================
    # METRICS
    # ==================================================

    def get_metrics(self):

        self.metrics[
            "current_queue_size"
        ] = self.queue.qsize()

        return self.metrics.copy()


async_event_bus = AsyncEventBus()
