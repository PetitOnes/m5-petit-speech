import uuid
from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro

from m5_petit_speech.config import settings

KOKORO_VOICES = [
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    "jm_kumo",
]


class KokoroService:
    def __init__(self) -> None:
        self._kokoro: Kokoro | None = None

    def _get_kokoro(self) -> Kokoro:
        if self._kokoro is None:
            self._kokoro = Kokoro(
                str(settings.kokoro_model_path),
                str(settings.kokoro_voices_path),
            )
        return self._kokoro

    def synthesize(
        self,
        text: str,
        voice: str = "jf_alpha",
        speed: float = 1.0,
        lang: str = "ja",
    ) -> Path:
        if voice not in KOKORO_VOICES:
            raise ValueError(f"Unknown voice: {voice}. Available: {KOKORO_VOICES}")

        kokoro = self._get_kokoro()
        samples, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)

        out_path = settings.output_dir / f"{uuid.uuid4().hex}.wav"
        sf.write(str(out_path), samples, sample_rate)
        return out_path


kokoro_service = KokoroService()
