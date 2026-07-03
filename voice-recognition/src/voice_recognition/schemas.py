from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class SoundEvent(BaseModel):
    label: str
    score: float


class TranscribeResponse(BaseModel):
    text: str
    language: str | None = None
    duration_sec: float | None = None
    speaker: str = "unknown"
    speaker_confidence: float = 0.0


class VoiceFeaturesResponse(BaseModel):
    f0_mean_hz: float | None = None
    f0_std_hz: float | None = None
    speech_rate_voiced_segments_per_sec: float | None = None
    pause_ratio: float | None = None
    mean_pause_sec: float | None = None
    jitter_local: float | None = None
    shimmer_local_db: float | None = None
    hnr_db: float | None = None
    mfcc_mean: list[float] = Field(default_factory=list)
    mfcc_std: list[float] = Field(default_factory=list)
    egemaps: dict[str, float] | None = None


class AnalyzeAudioResponse(BaseModel):
    transcript: str
    language: str | None = None
    duration_sec: float | None = None
    sound_events: list[SoundEvent]
    voice_features: VoiceFeaturesResponse
    summary_for_claude: str
    speaker: str = "unknown"
    speaker_confidence: float = 0.0