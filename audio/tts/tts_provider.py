import asyncio
import subprocess
from pathlib import Path
import time
from uuid import uuid4

from cosmo.core.config.settings_manager import config
from cosmo.core.runtime.runtime_state import (
    runtime_state
)
from cosmo.core.logger.logger_manager import (
    logger
)


BASE_DIR = Path(__file__).resolve().parents[2]


class PiperTTSProvider:

    def __init__(self):

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

        self.output_dir = Path(
            "/tmp"
        )

    async def speak(
        self,
        text: str
    ):

        runtime_state.tts_active = True

        output_file = (
            self.output_dir /
            f"cosmo_tts_{uuid4().hex}.wav"
        )

        try:

            if not text or not text.strip():

                logger.warning(
                    "TTS ignorado: texto vazio"
                )

                return

            if not self.model_path.exists():

                raise FileNotFoundError(
                    f"Modelo Piper não encontrado: {self.model_path}"
                )

            command = [
                "piper",
                "--model",
                str(self.model_path),
                "--output_file",
                str(output_file)
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            _, stderr = await process.communicate(
                input=text.encode("utf-8")
            )

            if process.returncode != 0:

                error_text = stderr.decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                raise RuntimeError(
                    f"Piper falhou: {error_text}"
                )

            if (
                not output_file.exists() or
                output_file.stat().st_size < 1000
            ):

                raise RuntimeError(
                    f"Arquivo TTS inválido: {output_file}"
                )

            await asyncio.to_thread(
                subprocess.run,
                [
                    "aplay",
                    str(output_file)
                ],
                check=True
            )

        finally:

            try:

                if output_file.exists():

                    output_file.unlink()

            except Exception as error:

                logger.warning(
                    f"Falha ao remover TTS temporário: {error}"
                )

            runtime_state.tts_active = False

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