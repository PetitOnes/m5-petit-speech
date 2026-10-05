# text-to-speech

## [日本語ページ](./README.md)

A text-to-speech (TTS) server that provides an HTTP API to make a robot like M5 Petit speak. **It runs on a PC without a GPU** (on the same PC as the caller, or on another one).

It's a plain HTTP API rather than MCP because speech synthesis is latency-sensitive, and we want to avoid MCP's overhead.

## Supported engines

- **piper** (piper-plus) — optional. Japanese voice models (e.g. Tsukuyomi-chan). Runs on CPU
- **kokoro** (kokoro-onnx) — lightweight multilingual TTS. Runs on CPU
- **voicevox** — calls a VOICEVOX ENGINE instance over HTTP. The engine can be the CPU build or the GPU build

Switch engines via the `engine` field in the `/speak` request. When omitted: `TTS_DEFAULT_ENGINE`, otherwise piper (if configured), then voicevox.

**The easiest start is voicevox only**: start VOICEVOX ENGINE, then this server (no piper settings needed).

VOICEVOX ENGINE: pick a build from [the releases](https://github.com/VOICEVOX/voicevox_engine/releases) — `linux-cpu-x64` without a GPU, `linux-nvidia` with an NVIDIA GPU — and run `./run --host 127.0.0.1 --port 50021`. This server's settings are the same either way.

## Layout

```
src/text_to_speech/
├── main.py
├── config.py
├── schemas.py
├── api/routes.py
└── services/
    ├── piper_service.py
    ├── kokoro_service.py
    └── voicevox_service.py
```

## Setup

### 1. piper-plus (binary, optional)

```bash
mkdir -p ~/work/piper-bin && cd ~/work/piper-bin
curl -L -o piper.tar.gz https://github.com/ayutaz/piper-plus/releases/latest/download/piper-linux-x64.tar.gz
tar xzf piper.tar.gz
cd piper
LD_LIBRARY_PATH=$PWD/lib ./bin/piper --download-model tsukuyomi
```

Models are saved to `~/.local/share/piper/models/`.

### 2. kokoro / voicevox (optional)

- kokoro: place the model and voices file under `~/.local/share/kokoro/` (override with `KOKORO_MODEL_PATH`/`KOKORO_VOICES_PATH`)
- voicevox: run a [VOICEVOX ENGINE](https://voicevox.hiroshiba.jp/) instance separately and point `VOICEVOX_URL` at it

### 3. Python environment

```bash
uv sync
cp .env.example .env
# edit .env and set PIPER_BIN etc. to their real paths
```

## Running

```bash
uv run uvicorn text_to_speech.main:app --host 0.0.0.0 --port 8766
```

## API

### `GET /help`

Returns the list of supported engines and their parameters.

### `POST /speak`

Generates audio (returns a wav file).

```bash
curl -X POST http://127.0.0.1:8766/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"こんにちは","engine":"piper"}' --output out.wav
```

Example requests per engine:

```jsonc
// piper
{"text": "こんにちは", "engine": "piper", "speaker": 0, "length_scale": 1.0}

// kokoro
{"text": "こんにちは", "engine": "kokoro", "voice": "jf_alpha", "speed": 1.0, "lang": "ja"}

// voicevox
{"text": "こんにちは", "engine": "voicevox", "voicevox_speaker": 3, "speed_scale": 1.0}
```

### `POST /speak_summary`

Same as `/speak` for now (intended to become a lightweight variant that returns only the filename).

## systemd setup

```ini
[Unit]
Description=M5 Petit Speech Server
After=network.target

[Service]
User=<YOUR_USER>
WorkingDirectory=/path/to/m5-petit-speech/text-to-speech
Environment="PYTHONUNBUFFERED=1"
Environment="LD_LIBRARY_PATH=/path/to/piper-bin/piper/lib"
ExecStart=/path/to/.local/bin/uv run uvicorn text_to_speech.main:app --host 0.0.0.0 --port 8766
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now m5_speech
journalctl -u m5_speech -f
```

## Access from another PC

Assumes access over Tailscale:

```bash
curl http://100.xxx.xxx.xxx:8766/help
```

## Common errors

- **No sound**: an error message may have been saved instead of a wav file → check with `file out.wav`
- **libonnxruntime.so error**: `LD_LIBRARY_PATH` needs to be set
- **piper doesn't run**: check the binary path and model path
