from __future__ import annotations

import tempfile
from pathlib import Path

import librosa
import numpy as np
from starlette.datastructures import UploadFile


async def save_upload_to_temp(upload_file: UploadFile) -> Path:
    suffix = Path(upload_file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        return Path(tmp.name)


def load_audio_mono_16k(audio_path: Path) -> tuple[np.ndarray, int]:
    waveform, sr = librosa.load(str(audio_path), sr=16000, mono=True)
    return waveform.astype("float32"), sr