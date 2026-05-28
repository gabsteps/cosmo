import asyncio

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
        f"[CRITICAL_LISTENER] START -> {data}"
    )

    await asyncio.sleep(0.5)

    logger.info(
        f"[CRITICAL_LISTENER] END -> {data}"
    )


async def background_listener(data):

    logger.info(
        f"[BACKGROUND_LISTENER] START -> {data}"
    )

    await asyncio.sleep(2)

    logger.info(
        f"[BACKGROUND_LISTENER] END -> {data}"
    )


# =========================================================
# SUBSCRIPTIONS
# =========================================================

async_event_bus.subscribe(
    "critical_event",
    critical_listener
)

async_event_bus.subscribe(
    "background_event",
    background_listener
)


# =========================================================
# TEST
# =========================================================

async def test_critical_priority():

    logger.info(
        "[TEST] critical priority test started"
    )

    # =====================================================
    # FLOOD BACKGROUND
    # =====================================================

    for i in range(10):

        await async_event_bus.emit(
            "background_event",
            data=f"BACKGROUND_{i}",
            priority=AsyncEventBus.PRIORITY_BACKGROUND
        )

    # =====================================================
    # EMIT CRITICAL
    # =====================================================

    await async_event_bus.emit(
        "critical_event",
        data="CRITICAL_EVENT",
        priority=AsyncEventBus.PRIORITY_CRITICAL
    )

    # =====================================================
    # MORE BACKGROUND
    # =====================================================

    for i in range(10, 20):

        await async_event_bus.emit(
            "background_event",
            data=f"BACKGROUND_{i}",
            priority=AsyncEventBus.PRIORITY_BACKGROUND
        )

    # =====================================================
    # WAIT
    # =====================================================

    await asyncio.sleep(10)

    logger.info(
        "[TEST] critical priority test finished"
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    logger.info(
        "[TEST] starting event bus"
    )

    bus_task = asyncio.create_task(
        async_event_bus.start()
    )

    await asyncio.sleep(1)

    await test_critical_priority()

    metrics = (
        async_event_bus.get_metrics()
    )

    logger.info(
        f"[TEST] FINAL METRICS -> {metrics}"
    )

    await async_event_bus.shutdown()

    bus_task.cancel()

    logger.info(
        "[TEST] shutdown complete"
    )


if __name__ == "__main__":

    asyncio.run(main())