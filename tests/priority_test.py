import asyncio
import random

from cosmo.core.events.async_event_bus import (
    async_event_bus,
    AsyncEventBus
)

from cosmo.core.logger.logger_manager import logger


# =========================================================
# LISTENERS
# =========================================================

async def critical_listener(data):

    logger.info(
        f"[TEST] critical_listener -> {data}"
    )

    await asyncio.sleep(0.2)


async def audio_listener(data):

    logger.info(
        f"[TEST] audio_listener -> {data}"
    )

    await asyncio.sleep(0.5)


async def background_listener(data):

    logger.info(
        f"[TEST] background_listener -> {data}"
    )

    await asyncio.sleep(1)


async def slow_listener(data):

    logger.info(
        f"[TEST] slow_listener -> {data}"
    )

    await asyncio.sleep(6)


async def flaky_listener(data):

    logger.info(
        f"[TEST] flaky_listener -> {data}"
    )

    await asyncio.sleep(0.2)

    if random.random() < 0.5:

        raise RuntimeError(
            "Erro aleatório"
        )


# =========================================================
# REGISTER LISTENERS
# =========================================================

async_event_bus.subscribe(
    "critical_event",
    critical_listener
)

async_event_bus.subscribe(
    "audio_event",
    audio_listener
)

async_event_bus.subscribe(
    "background_event",
    background_listener
)

async_event_bus.subscribe(
    "slow_event",
    slow_listener
)

async_event_bus.subscribe(
    "flaky_event",
    flaky_listener
)


# =========================================================
# TEST 1
# PRIORITY ORDER
# =========================================================

async def test_priorities():

    logger.info(
        "[TEST] test_priorities started"
    )

    await async_event_bus.emit(
        "background_event",
        data="BACKGROUND",
        priority=AsyncEventBus.PRIORITY_BACKGROUND
    )

    await async_event_bus.emit(
        "audio_event",
        data="AUDIO",
        priority=AsyncEventBus.PRIORITY_AUDIO
    )

    await async_event_bus.emit(
        "critical_event",
        data="CRITICAL",
        priority=AsyncEventBus.PRIORITY_CRITICAL
    )

    await asyncio.sleep(3)

    logger.info(
        "[TEST] test_priorities finished"
    )


# =========================================================
# TEST 2
# FIFO SAME PRIORITY
# =========================================================

async def test_fifo():

    logger.info(
        "[TEST] test_fifo started"
    )

    for i in range(5):

        await async_event_bus.emit(
            "audio_event",
            data=f"FIFO_{i}",
            priority=AsyncEventBus.PRIORITY_AUDIO
        )

    await asyncio.sleep(5)

    logger.info(
        "[TEST] test_fifo finished"
    )


# =========================================================
# TEST 3
# STARVATION
# =========================================================

async def test_starvation():

    logger.info(
        "[TEST] test_starvation started"
    )

    for i in range(30):

        await async_event_bus.emit(
            "slow_event",
            data=f"SLOW_{i}",
            priority=AsyncEventBus.PRIORITY_BACKGROUND
        )

    await asyncio.sleep(15)

    logger.info(
        "[TEST] test_starvation finished"
    )


# =========================================================
# TEST 4
# QUEUE OVERFLOW
# =========================================================

async def test_queue_overflow():

    logger.info(
        "[TEST] test_queue_overflow started"
    )

    for i in range(500):

        await async_event_bus.emit(
            "background_event",
            data=f"OVERFLOW_{i}",
            priority=AsyncEventBus.PRIORITY_BACKGROUND
        )

    await asyncio.sleep(10)

    logger.info(
        "[TEST] test_queue_overflow finished"
    )


# =========================================================
# TEST 5
# PARTIAL FAILURES
# =========================================================

async def test_partial_failures():

    logger.info(
        "[TEST] test_partial_failures started"
    )

    for i in range(20):

        await async_event_bus.emit(
            "flaky_event",
            data=f"FLAKY_{i}",
            priority=AsyncEventBus.PRIORITY_CONVERSATION
        )

    await asyncio.sleep(5)

    logger.info(
        "[TEST] test_partial_failures finished"
    )


# =========================================================
# TEST 6
# UNHANDLED EVENT
# =========================================================

async def test_unhandled():

    logger.info(
        "[TEST] test_unhandled started"
    )

    await async_event_bus.emit(
        "unknown_event",
        data="NO_LISTENER",
        priority=AsyncEventBus.PRIORITY_BACKGROUND
    )

    await asyncio.sleep(2)

    logger.info(
        "[TEST] test_unhandled finished"
    )


# =========================================================
# METRICS VALIDATION
# =========================================================

async def validate_metrics():

    metrics = (
        async_event_bus.get_metrics()
    )

    logger.info(
        f"[TEST] FINAL METRICS -> {metrics}"
    )

    logger.info(
        "[TEST] validating semantic counters"
    )

    received_ok = (
        metrics["events_received"]
        ==
        (
            metrics["events_emitted"]
            +
            metrics["events_dropped"]
        )
    )

    logger.info(
        f"[TEST] received_consistency -> "
        f"{received_ok}"
    )

    dispatched_ok = (
        metrics["events_dispatched"]
        ==
        (
            metrics["events_completed"]
            +
            metrics["events_failed"]
            +
            metrics["events_partial_failures"]
            +
            metrics["events_unhandled"]
        )
    )

    logger.info(
        f"[TEST] dispatch_consistency -> "
        f"{dispatched_ok}"
    )

    logger.info(
        "[TEST] metrics validation finished"
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    logger.info(
        "[TEST] priority_test started"
    )

    bus_task = asyncio.create_task(
        async_event_bus.start()
    )

    await asyncio.sleep(1)

    await test_priorities()

    await test_fifo()

    await test_partial_failures()

    await test_unhandled()

    await test_starvation()

    await test_queue_overflow()

    await validate_metrics()

    await async_event_bus.shutdown()

    bus_task.cancel()

    logger.info(
        "[TEST] priority_test finished"
    )


if __name__ == "__main__":

    asyncio.run(main())