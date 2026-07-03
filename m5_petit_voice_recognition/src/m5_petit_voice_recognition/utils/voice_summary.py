from __future__ import annotations

from m5_petit_voice_recognition.schemas import VoiceFeaturesResponse


def build_voice_summary(features: VoiceFeaturesResponse) -> str:
    parts: list[str] = []

    if features.f0_mean_hz is not None:
        parts.append(f"平均F0は {features.f0_mean_hz:.1f} Hz")
    if features.f0_std_hz is not None:
        parts.append(f"F0変動は {features.f0_std_hz:.1f} Hz")
    if features.speech_rate_voiced_segments_per_sec is not None:
        parts.append(f"話速指標は {features.speech_rate_voiced_segments_per_sec:.2f}")
    if features.mean_pause_sec is not None:
        parts.append(f"平均ポーズ長は {features.mean_pause_sec:.2f} 秒")
    if features.jitter_local is not None:
        parts.append(f"jitter は {features.jitter_local:.4f}")
    if features.shimmer_local_db is not None:
        parts.append(f"shimmer は {features.shimmer_local_db:.3f} dB")
    if features.hnr_db is not None:
        parts.append(f"HNR は {features.hnr_db:.2f} dB")

    if not parts:
        return "音声特徴量は十分に安定して抽出できませんでした。"

    return "、".join(parts) + "。"

def build_compact_summary(transcript: str, sound_events: list, vf) -> dict:
    # ===== 環境 =====
    env_labels = [e["label"] for e in sound_events[:2]]

    if any("Speech" in l for l in env_labels):
        environment = "speech"
    else:
        environment = ", ".join(env_labels) if env_labels else "unknown"

    if any("Inside" in l for l in env_labels):
        environment += ", indoor"

    # ===== ピッチ =====
    pitch = None
    if vf.f0_mean_hz:
        if vf.f0_mean_hz < 150:
            pitch = "low"
        elif vf.f0_mean_hz > 220:
            pitch = "high"
        else:
            pitch = "normal"

    # ===== 話速 =====
    speed = None
    if vf.speech_rate_voiced_segments_per_sec:
        if vf.speech_rate_voiced_segments_per_sec < 1.0:
            speed = "slow"
        elif vf.speech_rate_voiced_segments_per_sec > 2.5:
            speed = "fast"
        else:
            speed = "normal"

    # ===== 安定性 / 疲れ =====
    stability = "normal"
    if vf.jitter_local and vf.hnr_db:
        if vf.jitter_local > 0.01 or vf.hnr_db < 10:
            stability = "slightly_unstable"

    # ===== 総合 =====
    voice_state_parts = []

    if pitch:
        voice_state_parts.append(pitch)
    if speed:
        voice_state_parts.append(speed)
    if stability != "normal":
        voice_state_parts.append("tired")

    voice_state = ", ".join(voice_state_parts) if voice_state_parts else "unknown"

    return {
        "transcript": transcript,
        "environment": environment,
        "voice_state": voice_state,
    }