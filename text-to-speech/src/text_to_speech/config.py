from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8766, alias="PORT")

    # piper は任意。使わないなら未設定でよい(kokoro / voicevox だけで起動できる)
    piper_bin: Path | None = Field(default=None, alias="PIPER_BIN")
    piper_ld_library_path: str = Field(default="", alias="PIPER_LD_LIBRARY_PATH")
    piper_model_path: Path | None = Field(default=None, alias="PIPER_MODEL_PATH")
    # engine を省略したリクエストで使うエンジン。未設定なら、piper が設定されていれば piper、無ければ voicevox
    default_engine: str | None = Field(default=None, alias="TTS_DEFAULT_ENGINE")
    output_dir: Path = Field(default=Path("./outputs"), alias="OUTPUT_DIR")

    kokoro_model_path: Path = Field(
        default=Path.home() / ".local/share/kokoro/kokoro-v1.0.onnx",
        alias="KOKORO_MODEL_PATH",
    )
    kokoro_voices_path: Path = Field(
        default=Path.home() / ".local/share/kokoro/voices-v1.0.bin",
        alias="KOKORO_VOICES_PATH",
    )

    voicevox_url: str = Field(
        default="http://127.0.0.1:50021",
        alias="VOICEVOX_URL",
    )

    piper_speaker: int = Field(default=0, alias="PIPER_SPEAKER")
    piper_length_scale: float = Field(default=1.0, alias="PIPER_LENGTH_SCALE")
    piper_noise_scale: float = Field(default=0.5, alias="PIPER_NOISE_SCALE")
    piper_noise_w: float = Field(default=0.8, alias="PIPER_NOISE_W")
    piper_sentence_silence: float = Field(default=0.2, alias="PIPER_SENTENCE_SILENCE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


    @property
    def piper_configured(self) -> bool:
        return self.piper_bin is not None and self.piper_model_path is not None


settings = Settings()
settings.output_dir.mkdir(parents=True, exist_ok=True)
