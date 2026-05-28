import asyncio

from cosmo.core.bootstrap.bootstrap import (
    bootstrap
)


async def main():

    try:

        await bootstrap.start()

    except KeyboardInterrupt:

        await bootstrap.shutdown()


if __name__ == "__main__":

    asyncio.run(main())