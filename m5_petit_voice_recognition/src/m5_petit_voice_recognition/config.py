from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    whisper_model: str = Field(default="small", alias="WHISPER_MODEL")
    whisper_device: str = Field(default="cpu", alias="WHISPER_DEVICE")
    whisper_compute_type: str = Field(default="int8", alias="WHISPER_COMPUTE_TYPE")
    whisper_language: str = Field(default="ja", alias="WHISPER_LANGUAGE")

    sound_model: str = Field(default="panns", alias="SOUND_MODEL")
    sound_top_k: int = Field(default=5, alias="SOUND_TOP_K")
    sound_min_score: float = Field(default=0.2, alias="SOUND_MIN_SCORE")

    voice_frame_length: int = Field(default=2048, alias="VOICE_FRAME_LENGTH")
    voice_hop_length: int = Field(default=256, alias="VOICE_HOP_LENGTH")
    voice_fmin: float = Field(default=65.0, alias="VOICE_FMIN")
    voice_fmax: float = Field(default=400.0, alias="VOICE_FMAX")
    voice_mfcc_n: int = Field(default=13, alias="VOICE_MFCC_N")
    voice_pause_db_threshold: float = Field(default=25.0, alias="VOICE_PAUSE_DB_THRESHOLD")
    voice_min_pause_sec: float = Field(default=0.20, alias="VOICE_MIN_PAUSE_SEC")
    enable_opensmile: bool = Field(default=False, alias="ENABLE_OPENSMILE")

    speaker_registry_path: str = Field(default="speaker_registry.json", alias="SPEAKER_REGISTRY_PATH")
    speaker_threshold: float = Field(default=0.75, alias="SPEAKER_THRESHOLD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


settings = Settings()