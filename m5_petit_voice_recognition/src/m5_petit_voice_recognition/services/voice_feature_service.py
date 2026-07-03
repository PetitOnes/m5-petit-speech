from __future__ import annotations

from dataclasses import dataclass

import librosa
import numpy as np
import parselmouth

from m5_petit_voice_recognition.config import settings


@dataclass
class VoiceFeatureResult:
    f0_mean_hz: float | None
    f0_std_hz: float | None
    speech_rate_voiced_segments_per_sec: float | None
    pause_ratio: float | None
    mean_pause_sec: float | None
    jitter_local: float | None
    shimmer_local_db: float | None
    hnr_db: float | None
    mfcc_mean: list[float]
    mfcc_std: list[float]
    egemaps: dict[str, float] | None = None


class VoiceFeatureService:
    def extract(self, waveform: np.ndarray, sr: int) -> VoiceFeatureResult:
        duration_sec = len(waveform) / sr if sr > 0 else 0.0

        f0, voiced_flag, _ = librosa.pyin(
            waveform,
            fmin=librosa.note_to_hz("C2") if settings.voice_fmin <= 0 else settings.voice_fmin,
            fmax=settings.voice_fmax,
            frame_length=settings.voice_frame_length,
            hop_length=settings.voice_hop_length,
        )

        valid_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        f0_mean = float(np.mean(valid_f0)) if valid_f0.size else None
        f0_std = float(np.std(valid_f0)) if valid_f0.size else None

        mfcc = librosa.feature.mfcc(
            y=waveform,
            sr=sr,
            n_mfcc=settings.voice_mfcc_n,
        )
        mfcc_mean = np.mean(mfcc, axis=1).tolist()
        mfcc_std = np.std(mfcc, axis=1).tolist()

        speech_rate, pause_ratio, mean_pause_sec = self._estimate_timing(
            waveform=waveform,
            sr=sr,
            voiced_flag=voiced_flag,
            duration_sec=duration_sec,
        )

        jitter_local, shimmer_local_db, hnr_db = self._extract_parselmouth_features(
            waveform=waveform,
            sr=sr,
        )

        return VoiceFeatureResult(
            f0_mean_hz=f0_mean,
            f0_std_hz=f0_std,
            speech_rate_voiced_segments_per_sec=speech_rate,
            pause_ratio=pause_ratio,
            mean_pause_sec=mean_pause_sec,
            jitter_local=jitter_local,
            shimmer_local_db=shimmer_local_db,
            hnr_db=hnr_db,
            mfcc_mean=mfcc_mean,
            mfcc_std=mfcc_std,
            egemaps=None,
        )

    def _estimate_timing(
        self,
        waveform: np.ndarray,
        sr: int,
        voiced_flag: np.ndarray | None,
        duration_sec: float,
    ) -> tuple[float | None, float | None, float | None]:
        if duration_sec <= 0:
            return None, None, None

        if voiced_flag is not None:
            voiced_flag = np.nan_to_num(voiced_flag.astype(float)).astype(bool)
            segments = self._count_segments(voiced_flag)
            speech_rate = segments / duration_sec
        else:
            speech_rate = None

        rms = librosa.feature.rms(y=waveform, frame_length=settings.voice_frame_length,
                                  hop_length=settings.voice_hop_length)[0]
        db = librosa.amplitude_to_db(rms, ref=np.max)
        silent = db < (-settings.voice_pause_db_threshold)

        pause_lengths = self._segment_lengths(
            silent,
            hop_length=settings.voice_hop_length,
            sr=sr,
        )
        pause_lengths = [p for p in pause_lengths if p >= settings.voice_min_pause_sec]

        total_pause = float(sum(pause_lengths))
        pause_ratio = total_pause / duration_sec if duration_sec > 0 else None
        mean_pause_sec = float(np.mean(pause_lengths)) if pause_lengths else 0.0

        return speech_rate, pause_ratio, mean_pause_sec

    def _extract_parselmouth_features(
        self,
        waveform: np.ndarray,
        sr: int,
    ) -> tuple[float | None, float | None, float | None]:
        snd = parselmouth.Sound(waveform, sampling_frequency=sr)

        pitch = snd.to_pitch()
        point_process = parselmouth.praat.call(
            [snd, pitch],
            "To PointProcess (cc)",
        )
        jitter_local = parselmouth.praat.call(
            point_process,
            "Get jitter (local)",
            0,
            0,
            0.0001,
            0.02,
            1.3,
        )
        shimmer_local = parselmouth.praat.call(
            [snd, point_process],
            "Get shimmer (local_dB)",
            0,
            0,
            0.0001,
            0.02,
            1.3,
            1.6,
        )
        harmonicity = snd.to_harmonicity_cc()
        hnr = parselmouth.praat.call(
            harmonicity,
            "Get mean",
            0,
            0,
        )

        return (
            float(jitter_local) if jitter_local == jitter_local else None,
            float(shimmer_local) if shimmer_local == shimmer_local else None,
            float(hnr) if hnr == hnr else None,
        )

    def _count_segments(self, mask: np.ndarray) -> int:
        if len(mask) == 0:
            return 0
        changes = np.diff(mask.astype(int), prepend=0)
        return int(np.sum(changes == 1))

    def _segment_lengths(self, mask: np.ndarray, hop_length: int, sr: int) -> list[float]:
        lengths = []
        count = 0
        for v in mask:
            if v:
                count += 1
            elif count > 0:
                lengths.append(count * hop_length / sr)
                count = 0
        if count > 0:
            lengths.append(count * hop_length / sr)
        return lengths