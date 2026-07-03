from __future__ import annotations

import numpy as np

from m5_petit_voice_recognition.config import settings


class SoundEventService:
    def classify_waveform(self, waveform: np.ndarray, sample_rate: int) -> list[dict]:
        # ここをあとで YAMNet か PANNs 実装に差し替える
        # まずはAPI疎通確認用の仮実装
        return [
            {"label": "Speech", "score": 0.90},
            {"label": "Inside, small room", "score": 0.55},
        ][: settings.sound_top_k]