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

# async def listener_1(data):

#     start = time.time()

#     logger.info("Listener 1 iniciado")

#     await asyncio.sleep(15)

#     end = time.time()

#     logger.info(
#         f"Listener 1 finalizado "
#         f"em {end - start:.2f}s"
#     )

# async def listener_2(data):

#     start = time.time()

#     logger.info("Listener 2 iniciado")

#     await asyncio.sleep(15)

#     end = time.time()

#     logger.info(
#         f"Listener 2 finalizado "
#         f"em {end - start:.2f}s"
#     )


# async_event_bus.subscribe(
#     SYSTEM_STARTED,
#     listener_1
# )

# async_event_bus.subscribe(
#     SYSTEM_STARTED,
#     listener_2
# )

# logger.info(
#     f"Metrics: "
#     f"{async_event_bus.get_metrics()}"
# )