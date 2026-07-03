from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import PlainTextResponse

from m5_petit_voice_recognition.config import settings
from m5_petit_voice_recognition.schemas import (
    AnalyzeAudioResponse,
    HealthResponse,
    SoundEvent,
    TranscribeResponse,
    VoiceFeaturesResponse,
)
from m5_petit_voice_recognition.services.audio_loader import (
    load_audio_mono_16k,
    save_upload_to_temp,
)
from m5_petit_voice_recognition.services.sound_event_service import SoundEventService
from m5_petit_voice_recognition.services.speaker_service import SpeakerService
from m5_petit_voice_recognition.services.voice_feature_service import VoiceFeatureService
from m5_petit_voice_recognition.services.whisper_service import WhisperService
from m5_petit_voice_recognition.utils.voice_summary import build_compact_summary, build_voice_summary


router = APIRouter()
whisper_service = WhisperService()
sound_event_service = SoundEventService()
voice_feature_service = VoiceFeatureService()
speaker_service = SpeakerService(
    registry_path=Path(settings.speaker_registry_path),
    threshold=settings.speaker_threshold,
)


@router.get("/help", response_class=PlainTextResponse)
async def help_text() -> str:
    return """m5_petit_voice_recognition API Help

    Available endpoints:
    - GET /health
        Health check

    - GET /help
        Show this help text

    - POST /transcribe
        Transcribe audio file to text (includes speaker identification)

    - POST /extract_voice_features
        Extract voice features from audio file

    - POST /analyze_audio
        Full analysis with detailed output (includes speaker identification)

    - POST /analyze_audio_summary
        Compact summary for Claude or other clients (includes speaker identification)

    - POST /register_speaker
        Register a speaker's voice for identification
        Form fields: speaker_id (str), file (audio)

    - GET /speakers
        List registered speakers

    - DELETE /speakers/{speaker_id}
        Remove a registered speaker

    Examples:

    1) Health check
    curl http://127.0.0.1:8765/health

    2) Transcribe (with speaker ID)
    curl -X POST http://127.0.0.1:8765/transcribe \\
    -F "file=@sample.wav"

    3) Register a speaker
    curl -X POST http://127.0.0.1:8765/register_speaker \\
    -F "speaker_id=user1" -F "file=@user1_voice.wav"

    4) List speakers
    curl http://127.0.0.1:8765/speakers
    """


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    temp_path = await save_upload_to_temp(file)
    try:
        result = whisper_service.transcribe_path(temp_path)
        speaker, confidence = speaker_service.identify(temp_path)
        return TranscribeResponse(
            **result,
            speaker=speaker,
            speaker_confidence=confidence,
        )
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/extract_voice_features", response_model=VoiceFeaturesResponse)
async def extract_voice_features(file: UploadFile = File(...)) -> VoiceFeaturesResponse:
    temp_path = await save_upload_to_temp(file)
    try:
        waveform, sr = load_audio_mono_16k(temp_path)
        result = voice_feature_service.extract(waveform, sr)
        return VoiceFeaturesResponse(
            f0_mean_hz=result.f0_mean_hz,
            f0_std_hz=result.f0_std_hz,
            speech_rate_voiced_segments_per_sec=result.speech_rate_voiced_segments_per_sec,
            pause_ratio=result.pause_ratio,
            mean_pause_sec=result.mean_pause_sec,
            jitter_local=result.jitter_local,
            shimmer_local_db=result.shimmer_local_db,
            hnr_db=result.hnr_db,
            mfcc_mean=result.mfcc_mean,
            mfcc_std=result.mfcc_std,
            egemaps=result.egemaps,
        )
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/analyze_audio", response_model=AnalyzeAudioResponse)
async def analyze_audio(file: UploadFile = File(...)) -> AnalyzeAudioResponse:
    temp_path = await save_upload_to_temp(file)
    try:
        waveform, sr = load_audio_mono_16k(temp_path)

        asr_result = whisper_service.transcribe_path(temp_path)
        sound_events = sound_event_service.classify_waveform(waveform, sr)
        vf = voice_feature_service.extract(waveform, sr)
        speaker, confidence = speaker_service.identify(temp_path)

        voice_features = VoiceFeaturesResponse(
            f0_mean_hz=vf.f0_mean_hz,
            f0_std_hz=vf.f0_std_hz,
            speech_rate_voiced_segments_per_sec=vf.speech_rate_voiced_segments_per_sec,
            pause_ratio=vf.pause_ratio,
            mean_pause_sec=vf.mean_pause_sec,
            jitter_local=vf.jitter_local,
            shimmer_local_db=vf.shimmer_local_db,
            hnr_db=vf.hnr_db,
            mfcc_mean=vf.mfcc_mean,
            mfcc_std=vf.mfcc_std,
            egemaps=vf.egemaps,
        )

        sound_text = ", ".join(
            f"{e['label']}({e['score']:.2f})" for e in sound_events[:3]
        )
        voice_text = build_voice_summary(voice_features)

        return AnalyzeAudioResponse(
            transcript=asr_result["text"],
            language=asr_result.get("language"),
            duration_sec=asr_result.get("duration_sec"),
            sound_events=[SoundEvent(**e) for e in sound_events],
            voice_features=voice_features,
            summary_for_claude=f"環境音: {sound_text}。音声特徴: {voice_text}",
            speaker=speaker,
            speaker_confidence=confidence,
        )
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/analyze_audio_summary")
async def analyze_audio_summary(file: UploadFile = File(...)):
    temp_path = await save_upload_to_temp(file)
    try:
        waveform, sr = load_audio_mono_16k(temp_path)

        asr_result = whisper_service.transcribe_path(temp_path)
        sound_events = sound_event_service.classify_waveform(waveform, sr)
        vf = voice_feature_service.extract(waveform, sr)
        speaker, confidence = speaker_service.identify(temp_path)

        summary = build_compact_summary(
            transcript=asr_result["text"],
            sound_events=sound_events,
            vf=vf,
        )
        summary["speaker"] = speaker
        summary["speaker_confidence"] = round(confidence, 3)

        return summary
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/register_speaker")
async def register_speaker(
    speaker_id: str = Form(...),
    file: UploadFile = File(...),
):
    """話者の声を登録する。同一IDで複数回呼ぶと埋め込みが更新される。

    speaker_id: 任意の文字列（例: "user1", "petit-a"）
    """
    temp_path = await save_upload_to_temp(file)
    try:
        speaker_service.register(speaker_id, temp_path)
        return {
            "ok": True,
            "speaker_id": speaker_id,
            "registered_speakers": speaker_service.registered_speakers,
        }
    finally:
        temp_path.unlink(missing_ok=True)


@router.get("/speakers")
async def list_speakers():
    """登録済み話者の一覧を返す。"""
    return {"speakers": speaker_service.registered_speakers}


@router.delete("/speakers/{speaker_id}")
async def delete_speaker(speaker_id: str):
    """登録済み話者を削除する。"""
    if speaker_id not in speaker_service.registered_speakers:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Speaker '{speaker_id}' not found")
    speaker_service._registry.pop(speaker_id)
    speaker_service._save_registry()
    return {
        "ok": True,
        "deleted": speaker_id,
        "registered_speakers": speaker_service.registered_speakers,
    }
