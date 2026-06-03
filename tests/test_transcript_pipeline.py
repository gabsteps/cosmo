import asyncio
import time

from cosmo.core.events.listeners.transcript_listener import (
    on_transcript_ready
)


async def main():

    started_at = time.time()

    await on_transcript_ready(
        {
            "text": "faça uma piada curta"
        }
    )

    elapsed = time.time() - started_at

    print(
        f"on_transcript_ready retornou em {elapsed:.3f}s"
    )

    await asyncio.sleep(45)


asyncio.run(main())