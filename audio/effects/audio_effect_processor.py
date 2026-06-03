# cosmo/audio/effects/audio_effect_processor.py

import asyncio
from pathlib import Path

from cosmo.core.logger.logger_manager import (
    logger
)


class AudioEffectProcessor:

    async def apply_robot_voice(
        self,
        input_file: Path,
        output_file: Path
    ) -> Path:

        if not input_file.exists():
            raise FileNotFoundError(
                f"Arquivo de entrada não encontrado: {input_file}"
            )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_file),

            # Cadeia de efeitos:
            # asetrate/aresample: abaixa pitch levemente
            # equalizer: enfatiza médios/agudos de rádio
            # compand: compressão dinâmica
            # acrusher: leve bitcrush, dá textura sintética
            # volume: ganho final controlado
            "-af",
            (
                "asetrate=22050*0.86,"
                "aresample=22050,"
                "highpass=f=300,"
                "lowpass=f=2800,"
                "equalizer=f=1000:t=q:w=1:g=7,"
                "equalizer=f=2200:t=q:w=1:g=5,"
                "equalizer=f=250:t=q:w=1:g=-8,"
                "compand=attacks=0.01:decays=0.12:points=-80/-80|-45/-24|-20/-8|0/-4,"
                "acrusher=level_in=1.4:level_out=0.85:bits=7:mode=log:aa=0,"
                "tremolo=f=18:d=0.12,"
                "volume=1.35"
            ),

            str(output_file)
        ]

        logger.info(
            f"Aplicando efeito de voz robótica: {input_file} -> {output_file}"
        )

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:

            error_text = stderr.decode(
                "utf-8",
                errors="ignore"
            ).strip()

            raise RuntimeError(
                f"FFmpeg falhou ao processar voz robótica: {error_text}"
            )

        if (
            not output_file.exists()
            or output_file.stat().st_size < 1000
        ):
            raise RuntimeError(
                f"Arquivo de voz processada inválido: {output_file}"
            )

        return output_file


audio_effect_processor = AudioEffectProcessor()