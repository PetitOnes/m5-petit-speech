from __future__ import annotations

import tempfile
from pathlib import Path

import soundfile as sf
from faster_whisper import WhisperModel
from starlette.datastructures import UploadFile

from m5_petit_voice_recognition.config import settings


class WhisperService:
    def __init__(self) -> None:
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            print(
                "DEBUG settings:",
                settings.whisper_model,
                settings.whisper_device,
                settings.whisper_compute_type,
            )
            self._model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
        return self._model

    def transcribe_path(self, audio_path: Path) -> dict:
        info = sf.info(str(audio_path))
        model = self._get_model()
        segments, meta = model.transcribe(str(audio_path), language=settings.whisper_language or None)
        text = "".join(segment.text for segment in segments).strip()

        return {
            "text": text,
            "language": getattr(meta, "language", None),
            "duration_sec": float(info.duration),
        }

    async def transcribe_upload(self, upload_file: UploadFile) -> dict:
        suffix = Path(upload_file.filename or "audio.wav").suffix or ".wav"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await upload_file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            return self.transcribe_path(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)