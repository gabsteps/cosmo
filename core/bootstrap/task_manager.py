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