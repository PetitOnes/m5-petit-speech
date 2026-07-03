# text-to-speech

GPU PC上で動作する音声合成(TTS)サーバー。M5 Petitのようなロボットの発話を、常時ONの軽量PCから呼び出すためのHTTP APIとして提供する。

MCP経由ではなく素のHTTP APIにしているのは、音声合成は応答速度が重要なため、MCPのオーバーヘッドを避けたいから。

## 対応エンジン

- **piper** (piper-plus) — デフォルト。日本語話者モデル(つくよみちゃん等)
- **kokoro** (kokoro-onnx) — 軽量な多言語TTS
- **voicevox** — VOICEVOX ENGINEをHTTPで呼び出し

`/speak`リクエストの`engine`で切り替える。

## 構成

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

## セットアップ

### 1. piper-plus (バイナリ)

```bash
mkdir -p ~/work/piper-bin && cd ~/work/piper-bin
curl -L -o piper.tar.gz https://github.com/ayutaz/piper-plus/releases/latest/download/piper-linux-x64.tar.gz
tar xzf piper.tar.gz
cd piper
LD_LIBRARY_PATH=$PWD/lib ./bin/piper --download-model tsukuyomi
```

モデルは `~/.local/share/piper/models/` に保存される。

### 2. kokoro / voicevox（任意）

- kokoro: モデルとvoicesファイルを`~/.local/share/kokoro/`に配置（`KOKORO_MODEL_PATH`/`KOKORO_VOICES_PATH`で変更可）
- voicevox: [VOICEVOX ENGINE](https://voicevox.hiroshiba.jp/)を別途起動し、`VOICEVOX_URL`で接続先を指定

### 3. Python環境

```bash
uv sync
cp .env.example .env
# .env を編集してPIPER_BIN等のパスを実際の値に
```

## 起動

```bash
uv run uvicorn text_to_speech.main:app --host 0.0.0.0 --port 8766
```

## API

### `GET /help`

対応エンジンとパラメータ一覧を返す。

### `POST /speak`

音声生成(wav返却)。

```bash
curl -X POST http://127.0.0.1:8766/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"こんにちは","engine":"piper"}' --output out.wav
```

エンジンごとのリクエスト例:

```jsonc
// piper
{"text": "こんにちは", "engine": "piper", "speaker": 0, "length_scale": 1.0}

// kokoro
{"text": "こんにちは", "engine": "kokoro", "voice": "jf_alpha", "speed": 1.0, "lang": "ja"}

// voicevox
{"text": "こんにちは", "engine": "voicevox", "voicevox_speaker": 3, "speed_scale": 1.0}
```

### `POST /speak_summary`

`/speak`と同じ(将来的にファイル名のみ返す軽量版にする想定)。

## systemd化

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

## 別PCからアクセス

Tailscale経由を想定:

```bash
curl http://100.xxx.xxx.xxx:8766/help
```

## よくあるエラー

- **音が出ない**: wavではなくエラーメッセージが保存されている場合がある → `file out.wav`で確認
- **libonnxruntime.so エラー**: `LD_LIBRARY_PATH`が必要
- **piperが動かない**: バイナリパス・モデルパスを確認
