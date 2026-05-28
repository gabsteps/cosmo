import asyncio

from cosmo.core.logger.logger_manager import logger

from cosmo.core.bootstrap.lifecycle import (
    lifecycle
)

from cosmo.core.events.event_bus import (
    event_bus
)

from cosmo.core.events.event_types import (
    SYSTEM_STARTED,
    SYSTEM_SHUTDOWN
)

from cosmo.core.runtime.async_runtime import (
    async_runtime
)

from cosmo.core.runtime.runtime_manager import (
    runtime_manager
)

from cosmo.audio.wakeword.wakeword_manager import (
    wakeword_manager
)

# =========================
# IMPORTAR LISTENERS
# =========================

from cosmo.core.events.listeners import (
    audio_listener,
    vision_listener,
    system_listener,
    conversation_listener,
    system_async_listener
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

class Bootstrap:

    async def start(self):

        logger.info(
            "Inicializando Zenith Cosmo 42"
        )

        # =========================
        # LIFECYCLE
        # =========================

        lifecycle.start()

        # =========================
        # EVENTO DE STARTUP
        # =========================

        event_bus.emit(
            SYSTEM_STARTED,
            {
                "system": "Zenith Cosmo 42"
            }
        )

        # =========================
        # EVENTO DE STARTUP ASYNC
        # =========================
        await async_event_bus.emit(
            SYSTEM_STARTED,
            {
                "system": "Zenith Cosmo 42"
            }
        )

        # =========================
        # ASYNC RUNTIME
        # =========================

        async_runtime.create_task(
            async_runtime.heartbeat(),
            name="Heartbeat"
        )

        async_runtime.create_task(
            async_event_bus.start(),
            name="AsyncEventBus"
        )



        # =========================
        # THREADS LEGADAS
        # =========================

        runtime_manager.start_thread(
            target=wakeword_manager.start,
            name="WakewordManager"
        )

        logger.info(
            "Zenith Cosmo 42 online"
        )

        # =========================
        # LOOP PRINCIPAL
        # =========================

        await self._main_loop()

    async def _main_loop(self):

        while lifecycle.is_running():

            await asyncio.sleep(1)

    async def shutdown(self):

        logger.info(
            "Encerrando Zenith Cosmo 42"
        )

        lifecycle.stop()

        event_bus.emit(
            SYSTEM_SHUTDOWN
        )

        await async_runtime.shutdown()

        logger.info(
            "Sistema encerrado"
        )


bootstrap = Bootstrap()