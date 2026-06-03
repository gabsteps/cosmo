import asyncio
import time

from cosmo.core.events.listeners.tts_listener import (
    on_response_generated
)


async def main():

    started_at = time.time()

    await on_response_generated(
        {
            "text": (
                "Teste de fala em background. "
                "Se isso estiver correto, o listener retorna antes do áudio terminar."
            )
        }
    )

    elapsed = time.time() - started_at

    print(
        f"on_response_generated retornou em {elapsed:.3f}s"
    )

    # Mantém o event loop vivo para a task de TTS terminar.
    await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())