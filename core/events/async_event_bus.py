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

from cosmo.audio.tts.tts_fallback import (
    tts_fallback
)

from cosmo.data.database.repositories.event_repository import (
    event_repository
)


class AsyncEventBus:

    PRIORITY_CRITICAL = 0
    PRIORITY_AUDIO = 1
    PRIORITY_CONVERSATION = 2
    PRIORITY_COGNITION = 3
    PRIORITY_BACKGROUND = 5

    def __init__(
        self
    ):

        self.listeners = defaultdict(
            list
        )

        self.max_queue_size = 100

        self.queue = asyncio.PriorityQueue(
            maxsize=self.max_queue_size
        )

        self.sequence_lock = asyncio.Lock()

        self.sequence = 0

        self.running = False

        self.listener_timeout = 30

        self.metrics = {
            "events_received": 0,
            "events_emitted": 0,
            "events_dispatched": 0,
            "events_dropped": 0,

            "events_completed": 0,
            "events_failed": 0,
            "events_partial_failures": 0,

            # mantido para compatibilidade
            "events_unhandled": 0,

            # nome mais claro para dashboard/WebUI
            "events_no_listeners": 0,

            "listener_successes": 0,
            "listener_timeouts": 0,
            "listener_errors": 0,

            "queue_peak": 0,
            "current_queue_size": 0,

            "avg_event_processing_time": 0.0,
            "avg_listener_processing_time": 0.0,
            "avg_queue_wait_time": 0.0,
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
        data=None,
        priority=PRIORITY_BACKGROUND
    ):

        self.metrics[
            "events_received"
        ] += 1

        event = {
            "id": str(
                uuid.uuid4()
            ),
            "name": event_name,
            "data": data,
            "priority": priority,
            "created_at": time.time(),
            "dispatched_at": None,
        }

        try:

            async with self.sequence_lock:

                self.sequence += 1
                sequence = self.sequence

            self.queue.put_nowait(
                (
                    priority,
                    sequence,
                    event
                )
            )

            self.metrics[
                "events_emitted"
            ] += 1

            self._persist_event(
                event_name=event_name,
                payload=data
            )

            current_size = self.queue.qsize()

            self.metrics[
                "current_queue_size"
            ] = current_size

            if current_size > self.metrics["queue_peak"]:

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

    def _persist_event(
        self,
        event_name,
        payload
    ) -> None:

        try:

            event_repository.emit_event(
                event_type=event_name,
                payload=payload
            )

        except Exception as error:

            logger.warning(
                f"Falha ao persistir evento no banco: {error}"
            )

    async def start(
        self
    ):

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

            event[
                "dispatched_at"
            ] = time.time()

            queue_wait = (
                event["dispatched_at"]
                - event["created_at"]
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

            self._update_average(
                metric_name="avg_queue_wait_time",
                count=self.metrics["events_dispatched"],
                value=queue_wait
            )

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
                self._dispatch_event(
                    event
                )
            )

            self.queue.task_done()

    async def _dispatch_event(
        self,
        event
    ):

        event_name = event[
            "name"
        ]

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

        event_start = time.perf_counter()

        if not listeners:

            elapsed = (
                time.perf_counter()
                - event_start
            )

            self.metrics[
                "events_unhandled"
            ] += 1

            self.metrics[
                "events_no_listeners"
            ] += 1

            self.metrics[
                "events_completed"
            ] += 1

            self._update_event_processing_average(
                elapsed
            )

            logger.warning(
                f"[TRACE] "
                f"{event['id']} "
                f"no_listeners -> "
                f"{event_name}"
            )

            logger.info(
                f"[TRACE] "
                f"{event['id']} "
                f"event_completed -> "
                f"{event_name} "
                f"(no_listeners)"
            )

            return

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

        success_count = sum(
            results
        )

        failure_count = (
            len(results)
            - success_count
        )

        elapsed = (
            time.perf_counter()
            - event_start
        )

        self._update_event_processing_average(
            elapsed
        )

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

    async def shutdown(
        self
    ):

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
                listener(
                    event["data"]
                ),
                timeout=self.listener_timeout
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            self.metrics[
                "listener_successes"
            ] += 1

            self._update_average(
                metric_name="avg_listener_processing_time",
                count=self.metrics["listener_successes"],
                value=elapsed
            )

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

            if event["name"] in (
                "transcript_ready",
                "audio_captured",
                "response_generated",
            ):

                asyncio.create_task(
                    tts_fallback.speak_timeout_message()
                )

            return False

        except Exception as error:

            self.metrics[
                "listener_errors"
            ] += 1

            logger.exception(
                f"[TRACE] "
                f"{event['id']} "
                f"listener_error -> "
                f"{listener.__name__}: {error}"
            )

            return False

    def _update_event_processing_average(
        self,
        elapsed: float
    ) -> None:

        classified_events = (
            self.metrics["events_completed"]
            + self.metrics["events_failed"]
            + self.metrics["events_partial_failures"]
            + 1
        )

        self._update_average(
            metric_name="avg_event_processing_time",
            count=classified_events,
            value=elapsed
        )

    def _update_average(
        self,
        metric_name: str,
        count: int,
        value: float
    ) -> None:

        if count <= 0:

            self.metrics[
                metric_name
            ] = value

            return

        current_avg = self.metrics[
            metric_name
        ]

        self.metrics[
            metric_name
        ] = (
            (
                current_avg
                * (count - 1)
            )
            + value
        ) / count

    def get_metrics(
        self
    ):

        self.metrics[
            "current_queue_size"
        ] = self.queue.qsize()

        return self.metrics.copy()


async_event_bus = AsyncEventBus()