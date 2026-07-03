from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


class SpeakerService:
    """resemblyzer を使った話者識別サービス。

    レジストリが空のときは常に ("unknown", 0.0) を返す。
    登録は /register_speaker エンドポイント経由で行う。
    """

    def __init__(self, registry_path: Path, threshold: float = 0.75) -> None:
        self._registry_path = registry_path
        self._threshold = threshold
        self._encoder = None  # 遅延ロード
        self._registry: dict[str, np.ndarray] = {}
        self._load_registry()

    def _get_encoder(self):
        if self._encoder is None:
            from resemblyzer import VoiceEncoder
            self._encoder = VoiceEncoder()
            logger.info("SpeakerService: VoiceEncoder loaded")
        return self._encoder

    def _load_registry(self) -> None:
        if not self._registry_path.exists():
            return
        try:
            data = json.loads(self._registry_path.read_text(encoding="utf-8"))
            self._registry = {k: np.array(v, dtype=np.float32) for k, v in data.items()}
            logger.info("SpeakerService: loaded %d speakers from %s", len(self._registry), self._registry_path)
        except Exception as e:
            logger.warning("SpeakerService: failed to load registry: %s", e)

    def _save_registry(self) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.tolist() for k, v in self._registry.items()}
        self._registry_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def register(self, speaker_id: str, wav_path: Path) -> None:
        """音声ファイルから話者埋め込みを登録・更新する。

        同一 speaker_id で複数回呼ぶと埋め込みの移動平均になる。
        """
        from resemblyzer import preprocess_wav
        wav = preprocess_wav(str(wav_path))
        embed = self._get_encoder().embed_utterance(wav).astype(np.float32)

        if speaker_id in self._registry:
            # 既存埋め込みと平均を取って正規化
            old = self._registry[speaker_id]
            embed = (old + embed) / 2.0
            norm = np.linalg.norm(embed)
            if norm > 0:
                embed = embed / norm

        self._registry[speaker_id] = embed
        self._save_registry()
        logger.info("SpeakerService: registered speaker '%s' (total: %d)", speaker_id, len(self._registry))

    def identify(self, wav_path: Path) -> tuple[str, float]:
        """音声ファイルから話者を推定する。

        Returns:
            (speaker_id, confidence): レジストリが空または閾値未満なら ("unknown", similarity)
        """
        if not self._registry:
            return "unknown", 0.0

        try:
            from resemblyzer import preprocess_wav
            wav = preprocess_wav(str(wav_path))
            embed = self._get_encoder().embed_utterance(wav).astype(np.float32)
        except Exception as e:
            logger.warning("SpeakerService: identify failed: %s", e)
            return "unknown", 0.0

        best_id, best_sim = "unknown", 0.0
        for name, ref in self._registry.items():
            denom = np.linalg.norm(embed) * np.linalg.norm(ref)
            if denom == 0:
                continue
            sim = float(np.dot(embed, ref) / denom)
            if sim > best_sim:
                best_id, best_sim = name, sim

        if best_sim < self._threshold:
            return "unknown", best_sim
        return best_id, best_sim

    @property
    def registered_speakers(self) -> list[str]:
        return list(self._registry.keys())
