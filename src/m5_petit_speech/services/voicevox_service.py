import uuid
from pathlib import Path

import httpx

from m5_petit_speech.config import settings


class VoicevoxService:
    def synthesize(
        self,
        text: str,
        speaker: int = 0,
        speed_scale: float = 1.0,
        pitch_scale: float | None = None,
        intonation_scale: float | None = None,
        volume_scale: float | None = None,
        pre_phoneme_length: float | None = None,
        post_phoneme_length: float | None = None,
    ) -> Path:
        base = settings.voicevox_url

        query_resp = httpx.post(
            f"{base}/audio_query",
            params={"text": text, "speaker": speaker},
            timeout=30.0,
        )
        query_resp.raise_for_status()
        audio_query = query_resp.json()

        audio_query["speedScale"] = speed_scale
        if pitch_scale is not None:
            audio_query["pitchScale"] = pitch_scale
        if intonation_scale is not None:
            audio_query["intonationScale"] = intonation_scale
        if volume_scale is not None:
            audio_query["volumeScale"] = volume_scale
        if pre_phoneme_length is not None:
            audio_query["prePhonemeLength"] = pre_phoneme_length
        if post_phoneme_length is not None:
            audio_query["postPhonemeLength"] = post_phoneme_length

        synth_resp = httpx.post(
            f"{base}/synthesis",
            params={"speaker": speaker},
            json=audio_query,
            timeout=60.0,
        )
        synth_resp.raise_for_status()

        out_path = settings.output_dir / f"{uuid.uuid4().hex}.wav"
        out_path.write_bytes(synth_resp.content)
        return out_path


voicevox_service = VoicevoxService()
