from enum import Enum
from pydantic import BaseModel


class TTSEngine(str, Enum):
    piper = "piper"
    kokoro = "kokoro"
    voicevox = "voicevox"


class SpeakRequest(BaseModel):
    text: str
    engine: TTSEngine = TTSEngine.piper

    # piper options
    speaker: int | None = None
    length_scale: float | None = None
    noise_scale: float | None = None
    noise_w: float | None = None
    sentence_silence: float | None = None

    # kokoro options
    voice: str | None = None
    speed: float | None = None
    lang: str | None = None

    # voicevox options
    voicevox_speaker: int | None = None
    speed_scale: float | None = None
    pitch_scale: float | None = None
    intonation_scale: float | None = None
    volume_scale: float | None = None
    pre_phoneme_length: float | None = None
    post_phoneme_length: float | None = None
