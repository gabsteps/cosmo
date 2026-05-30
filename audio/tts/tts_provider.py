import asyncio
import subprocess
from pathlib import Path
import time

from cosmo.core.config.settings_manager import config
from cosmo.core.runtime.runtime_state import (
    runtime_state
)


BASE_DIR = Path(__file__).resolve().parents[2]


class PiperTTSProvider:

    def __init__(self):

        model_name = config.get(
            "tts",
            "model"
        )

        self.speed = config.get(
            "tts",
            "speed"
        )

        self.volume = config.get(
            "tts",
            "volume"
        )

        self.model_path = (
            BASE_DIR
            / "models"
            / "piper"
            / "piper"
            / "piper-voices"
            / config.get("tts", "language")
            / config.get("tts", "locale")
            / f"{config.get('tts', 'model')}.onnx"
        )

        self.output_file = (
            "/tmp/cosmo_tts.wav"
        )

    async def speak(
        self,
        text: str
    ):
        runtime_state.tts_active = True

        try:        
            command = [
                "piper",
                "--model",
                str(self.model_path),
                "--output_file",
                self.output_file
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE
            )

            await process.communicate(
                input=text.encode()
            )

            await asyncio.to_thread(
                subprocess.run,
                [
                    "aplay",
                    self.output_file
                ],
                check=True
            )
        finally:

            runtime_state.mode = (
                runtime_state.COOLDOWN
            )

            runtime_state.ignore_wakeword_until = (
                time.time() + 8.0
            )

            asyncio.create_task(
                self.reset_after_cooldown()
            )

    async def reset_after_cooldown(self):

        await asyncio.sleep(8.0)
        runtime_state.mode = runtime_state.IDLE

tts_provider = PiperTTSProvider()