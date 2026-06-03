import asyncio
import subprocess
from pathlib import Path
import time
from uuid import uuid4

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.audio.tts.providers.base_tts_provider import (
    BaseTTSProvider
)


class EspeakTTSProvider(BaseTTSProvider):

    def __init__(self):

        self.language = config.get(
            "tts",
            "language"
        ) or "pt"

        self.voice = config.get(
            "tts",
            "voice"
        ) or "pt-br"

        self.speed = config.get(
            "tts",
            "speed"
        ) or 145

        self.pitch = config.get(
            "tts",
            "pitch"
        ) or 35

        self.volume = config.get(
            "tts",
            "volume"
        ) or 120

        self.output_dir = Path(
            "/tmp"
        )

    async def speak(
        self,
        text: str
    ) -> None:

        output_file = (
            self.output_dir /
            f"cosmo_espeak_{uuid4().hex}.wav"
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
                f"eSpeak TTS iniciado ({len(text)} caracteres)"
            )

            command = [
                "espeak-ng",
                "-v",
                str(self.voice),
                "-s",
                str(self.speed),
                "-p",
                str(self.pitch),
                "-a",
                str(self.volume),
                "-w",
                str(output_file),
                text
            ]

            synth_started_at = time.time()

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:

                _, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30
                )

            except asyncio.TimeoutError:

                process.kill()

                await process.wait()

                raise RuntimeError(
                    "Timeout durante síntese eSpeak"
                )

            logger.info(
                f"eSpeak finalizado em {time.time() - synth_started_at:.2f}s"
            )

            if process.returncode != 0:

                error_text = stderr.decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                raise RuntimeError(
                    f"eSpeak falhou: {error_text}"
                )

            if (
                not output_file.exists()
                or output_file.stat().st_size < 1000
            ):

                raise RuntimeError(
                    f"Arquivo eSpeak inválido: {output_file}"
                )

            file_size = output_file.stat().st_size

            logger.info(
                f"Arquivo eSpeak gerado: {output_file} ({file_size} bytes)"
            )

            playback_started_at = time.time()

            try:

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

            except asyncio.TimeoutError:

                raise RuntimeError(
                    "Timeout durante playback do áudio eSpeak"
                )

            except subprocess.CalledProcessError as error:

                stderr_text = ""

                if error.stderr:
                    stderr_text = error.stderr.decode(
                        "utf-8",
                        errors="ignore"
                    ).strip()

                raise RuntimeError(
                    f"aplay falhou no eSpeak: {stderr_text}"
                ) from error

            logger.info(
                f"Playback eSpeak finalizado em {time.time() - playback_started_at:.2f}s"
            )

        finally:

            try:

                if output_file.exists():

                    output_file.unlink()

            except Exception as error:

                logger.warning(
                    f"Falha ao remover áudio temporário eSpeak: {error}"
                )

            logger.info(
                f"eSpeak TTS encerrado em {time.time() - started_at:.2f}s"
            )