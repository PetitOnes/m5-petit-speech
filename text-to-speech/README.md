# text-to-speech

## [English Page](./README_en.md)

音声合成(TTS)サーバー。M5 Petitのようなロボットの発話を、HTTP APIとして提供する。**GPUなしのPCでも動く**(同じPCで動かしても、別のPCに置いてもよい)。

MCP経由ではなく素のHTTP APIにしているのは、音声合成は応答速度が重要なため、MCPのオーバーヘッドを避けたいから。

## 対応エンジン

- **piper** (piper-plus) — 任意。日本語話者モデル(つくよみちゃん等)。CPU実行
- **kokoro** (kokoro-onnx) — 軽量な多言語TTS。CPU実行
- **voicevox** — VOICEVOX ENGINEをHTTPで呼び出し。エンジンはCPU版・GPU版のどちらでもよい

`/speak`リクエストの`engine`で切り替える。省略したときは `TTS_DEFAULT_ENGINE`、無ければ piper(設定済みのとき)→ voicevox の順。

**いちばん簡単な始め方は voicevox だけ**: VOICEVOX ENGINE を起動して、このサーバーを起動する(piperの設定は要らない)。

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

### 1. VOICEVOX ENGINE(おすすめ)

[VOICEVOX ENGINE](https://github.com/VOICEVOX/voicevox_engine/releases) から、PCに合うものを選んで起動する。

- GPUなし: `linux-cpu-x64`(Windows / macOS はそれぞれのCPU版)
- NVIDIAのGPUあり: `linux-nvidia`(合成が速くなる)

```bash
./run --host 127.0.0.1 --port 50021
```

このサーバーは `VOICEVOX_URL`(既定 `http://127.0.0.1:50021`)に頼むだけなので、CPU版でもGPU版でも設定は同じ。

### 2. piper-plus (バイナリ、任意)

```bash
mkdir -p ~/work/piper-bin && cd ~/work/piper-bin
curl -L -o piper.tar.gz https://github.com/ayutaz/piper-plus/releases/latest/download/piper-linux-x64.tar.gz
tar xzf piper.tar.gz
cd piper
LD_LIBRARY_PATH=$PWD/lib ./bin/piper --download-model tsukuyomi
```

モデルは `~/.local/share/piper/models/` に保存される。

### 3. kokoro（任意）

モデルとvoicesファイルを`~/.local/share/kokoro/`に配置（`KOKORO_MODEL_PATH`/`KOKORO_VOICES_PATH`で変更可）

### 4. Python環境

```bash
uv sync
cp .env.example .env
# piper を使うときだけ、.env の PIPER_BIN 等のコメントを外して実際のパスに
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
  -d '{"text":"こんにちは","engine":"voicevox","voicevox_speaker":3}' --output out.wav
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

## 別PCからアクセス(分けて動かす場合)

Tailscale経由を想定:

```bash
curl http://100.xxx.xxx.xxx:8766/help
```

## よくあるエラー

- **音が出ない**: wavではなくエラーメッセージが保存されている場合がある → `file out.wav`で確認
- **libonnxruntime.so エラー**: `LD_LIBRARY_PATH`が必要
- **piperが動かない**: バイナリパス・モデルパスを確認
- **503 piper は設定されていません**: `engine` に `voicevox` か `kokoro` を指定するか、`.env` に piper の設定を書く
