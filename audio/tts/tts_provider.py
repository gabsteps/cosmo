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

        started_at = time.time()

        try:

            if not text or not text.strip():

                logger.warning(
                    "TTS ignorado: texto vazio"
                )

                return

            text = text.strip()

            logger.info(
                f"TTS iniciado ({len(text)} caracteres)"
            )

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

            synth_started_at = time.time()

            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            _, stderr = await asyncio.wait_for(
                process.communicate(
                    input=text.encode("utf-8")
                ),
                timeout=60
            )

            logger.info(
                f"Piper finalizado em {time.time() - synth_started_at:.2f}s"
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

            file_size = output_file.stat().st_size

            logger.info(
                f"Arquivo TTS gerado: {output_file} ({file_size} bytes)"
            )

            playback_started_at = time.time()

            await asyncio.wait_for(
                asyncio.to_thread(
                    subprocess.run,
                    [
                        "aplay",
                        str(output_file)
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                ),
                timeout=90
            )

            logger.info(
                f"Playback finalizado em {time.time() - playback_started_at:.2f}s"
            )

        except asyncio.TimeoutError:

            logger.exception(
                "Timeout durante TTS ou playback"
            )

            raise

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

            logger.info(
                f"TTS encerrado em {time.time() - started_at:.2f}s"
            )

    async def reset_after_cooldown(self):

        await asyncio.sleep(8.0)

        runtime_state.mode = runtime_state.IDLE


tts_provider = PiperTTSProvider()