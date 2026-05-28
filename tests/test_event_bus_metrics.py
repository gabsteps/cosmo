import asyncio

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.logger.logger_manager import (
    logger
)


TEST_EVENT = "test_event"


async def normal_listener(data):

    await asyncio.sleep(1)


async def timeout_listener(data):

    await asyncio.sleep(10)


async def error_listener(data):

    raise Exception("Erro de teste")


async def flood_events():

    for _ in range(200):

        await async_event_bus.emit(
            TEST_EVENT,
            {"stress": True}
        )


async def run_test():

    async_event_bus.subscribe(
        TEST_EVENT,
        normal_listener
    )

    async_event_bus.subscribe(
        TEST_EVENT,
        timeout_listener
    )

    async_event_bus.subscribe(
        TEST_EVENT,
        error_listener
    )

    asyncio.create_task(
        async_event_bus.start()
    )

    await flood_events()

    await asyncio.sleep(15)

    logger.info(
        f"Metrics finais: "
        f"{async_event_bus.metrics}"
    )


if __name__ == "__main__":

    asyncio.run(
        run_test()
    )