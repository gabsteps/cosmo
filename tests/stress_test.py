import asyncio
import random
import time

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.logger.logger_manager import logger


TOTAL_EVENTS = 5000


# ==================================================
# FAST LISTENER
# ==================================================

async def fast_listener(data):

    await asyncio.sleep(0.01)


# ==================================================
# SLOW LISTENER
# ==================================================

async def slow_listener(data):

    await asyncio.sleep(0.25)


# ==================================================
# ERROR LISTENER
# ==================================================

async def error_listener(data):

    if random.randint(1, 100) <= 5:
        raise RuntimeError(
            "simulated listener failure"
        )

    await asyncio.sleep(0.02)


# ==================================================
# REGISTER
# ==================================================

async_event_bus.subscribe(
    "fast_event",
    fast_listener
)

async_event_bus.subscribe(
    "slow_event",
    slow_listener
)

async_event_bus.subscribe(
    "error_event",
    error_listener
)


# ==================================================
# EVENT PRODUCER
# ==================================================

async def produce_events():

    logger.info(
        f"[STRESS] generating "
        f"{TOTAL_EVENTS} events"
    )

    start = time.perf_counter()

    for i in range(TOTAL_EVENTS):

        r = random.randint(1, 100)

        if r <= 10:

            await async_event_bus.emit(
                "fast_event",
                {"index": i},
                priority=async_event_bus.PRIORITY_CRITICAL
            )

        elif r <= 60:

            await async_event_bus.emit(
                "fast_event",
                {"index": i},
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

        elif r <= 90:

            await async_event_bus.emit(
                "slow_event",
                {"index": i},
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

        else:

            await async_event_bus.emit(
                "error_event",
                {"index": i},
                priority=async_event_bus.PRIORITY_BACKGROUND
            )

    elapsed = (
        time.perf_counter() - start
    )

    logger.info(
        f"[STRESS] enqueue finished "
        f"in {elapsed:.2f}s"
    )


# ==================================================
# WAIT UNTIL IDLE
# ==================================================

async def wait_completion():

    logger.info(
        "[STRESS] waiting completion"
    )

    while True:

        metrics = (
            async_event_bus.get_metrics()
        )

        classified = (
            metrics["events_completed"]
            + metrics["events_failed"]
            + metrics["events_partial_failures"]
            + metrics.get(
                "events_unhandled",
                0
            )
        )

        if (
            classified
            >= metrics["events_dispatched"]
            and
            metrics["current_queue_size"]
            == 0
        ):
            break

        await asyncio.sleep(1)


# ==================================================
# MAIN
# ==================================================

async def main():

    logger.info(
        "[STRESS] starting bus"
    )

    bus_task = asyncio.create_task(
        async_event_bus.start()
    )

    await asyncio.sleep(1)

    global_start = time.perf_counter()

    await produce_events()

    await wait_completion()

    total_elapsed = (
        time.perf_counter() - global_start
    )

    logger.info(
        f"[STRESS] total runtime "
        f"{total_elapsed:.2f}s"
    )

    logger.info(
        f"[STRESS] metrics -> "
        f"{async_event_bus.get_metrics()}"
    )

    await async_event_bus.shutdown()

    bus_task.cancel()

    logger.info(
        "[STRESS] finished"
    )


if __name__ == "__main__":

    asyncio.run(main())