# voice-recognition

## [日本語ページ](./README.md)

## Overview

This is a speech-processing server that runs on a GPU-equipped PC.

Main features:
- Speech-to-text transcription (Whisper / faster-whisper)
- Sound event classification (PANNs/YAMNet planned)
- Voice feature extraction (F0, MFCC, jitter, shimmer, HNR, etc.)
- HTTP API via FastAPI

Assumed setup:
- Mini PC (always on): Claude / control / orchestration
- GPU PC (this repository): dedicated speech-processing server

## Directory layout

```
src/voice_recognition/
  main.py                FastAPI entry point
  config.py              Settings (.env loading)
  schemas.py             API response definitions

  api/
    routes.py            Endpoint definitions

  services/
    whisper_service.py       Speech recognition
    sound_event_service.py   Sound event classification (currently a stub)
    voice_feature_service.py Voice feature extraction
    audio_loader.py           Audio loading

  utils/
    voice_summary.py     Builds a summary for Claude
```

## Setup

1. Install uv
    ```
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
    ```

2. Install dependencies
    ```
    cd voice-recognition
    uv sync
    ```

3. Create .env
    ```
    cp .env.example .env
    ```

## Running

```
uv run uvicorn voice_recognition.main:app --host 0.0.0.0 --port 8765
```

## API list

GET /health
  Health check

GET /help
  Shows the API list and usage examples

POST /transcribe
  Audio → text (includes speaker identification)

POST /extract_voice_features
  Audio → voice features

POST /analyze_audio
  Audio → full analysis (main API, includes speaker identification)

POST /analyze_audio_summary
  Compact summary for Claude (includes speaker identification)

POST /register_speaker
  Register a speaker's voice (form fields: speaker_id, file)

GET /speakers
  List registered speakers

DELETE /speakers/{speaker_id}
  Remove a registered speaker

## Example usage

```
curl -X POST http://127.0.0.1:8765/analyze_audio \
  -F "file=@sample.wav"
```

## Example output
```
{
  "transcript": "こんにちは",
  "sound_events": [...],
  "voice_features": {...},
  "summary_for_claude": "環境音: ... 音声特徴: ..."
}
```

## GPU configuration

.env
```
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

CPU mode:
```
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
```

## CUDA configuration (important)

Requirements:
- libcublas.so.12
- libcudnn (if needed)

If it isn't detected:
```
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libcublas/12:$LD_LIBRARY_PATH
```
To persist it:
```
echo '/usr/lib/x86_64-linux-gnu/libcublas/12' | sudo tee /etc/ld.so.conf.d/libcublas-12.conf
sudo ldconfig
```

## Creating a test audio file
```
arecord -d 5 -f S16_LE -r 16000 -c 1 sample.wav
```

## Development notes

- It's safest to verify Whisper on CPU first
- Enable GPU afterward
- Audio is loaded once and then branched out to each processing step

## Planned extensions

- Sound event classification via PANNs / YAMNet
- Add openSMILE (eGeMAPS)
- Claude function-call integration
- ROS2 node
- Real-time processing

## Notes

This server is designed as a "voice understanding engine", intended to be used together with Claude or a robot.
