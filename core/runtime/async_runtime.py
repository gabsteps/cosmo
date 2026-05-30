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

            # logger.info(
            #     "Runtime heartbeat"
            # )

            await asyncio.sleep(5)



async_runtime = AsyncRuntime()