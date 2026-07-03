import os
import subprocess
import uuid
from pathlib import Path

from m5_petit_speech.config import settings


class PiperService:
    def synthesize(
        self,
        text: str,
        speaker: int | None = None,
        length_scale: float | None = None,
        noise_scale: float | None = None,
        noise_w: float | None = None,
        sentence_silence: float | None = None,
    ) -> Path:
        out_path = settings.output_dir / f"{uuid.uuid4().hex}.wav"

        if speaker is None:
            speaker = settings.piper_speaker
        if length_scale is None:
            length_scale = settings.piper_length_scale
        if noise_scale is None:
            noise_scale = settings.piper_noise_scale
        if noise_w is None:
            noise_w = settings.piper_noise_w
        if sentence_silence is None:
            sentence_silence = settings.piper_sentence_silence

        cmd = [
            str(settings.piper_bin),
            "--model",
            str(settings.piper_model_path),
            "--text",
            text,
            "--output_file",
            str(out_path),
            "--speaker",
            str(speaker),
            "--length-scale",
            str(length_scale),
            "--noise-scale",
            str(noise_scale),
            "--noise-w",
            str(noise_w),
            "--sentence-silence",
            str(sentence_silence),
        ]

        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = settings.piper_ld_library_path

        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=True,
            env=env,
        )

        print("stdout:", result.stdout)
        print("stderr:", result.stderr)

        return out_path


piper_service = PiperService()