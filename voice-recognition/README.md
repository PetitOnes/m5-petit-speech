# voice-recognition

## [English Page](./README_en.md)

## 概要

このリポジトリは、GPU付きPC上で動作する音声処理サーバーです。

主な機能:
- 音声の文字起こし（Whisper / faster-whisper）
- 環境音の分類（将来的にPANNs/YAMNet）
- 音声特徴量抽出（F0, MFCC, jitter, shimmer, HNRなど）
- FastAPIによるHTTP API提供

想定構成:
- ミニPC（常時ON）: Claude / 制御 / オーケストレーション
- GPU PC（本リポジトリ）: 音声処理専用サーバー

## ディレクトリ構成

```
src/voice_recognition/
  main.py                FastAPIエントリポイント
  config.py              設定（.env読み込み）
  schemas.py             APIレスポンス定義

  api/
    routes.py            エンドポイント定義

  services/
    whisper_service.py   音声認識
    sound_event_service.py  環境音分類（現在はダミー）
    voice_feature_service.py 音声特徴量抽出
    audio_loader.py      音声読み込み

  utils/
    voice_summary.py     Claude向け要約生成
```

## セットアップ

1. uv インストール
    ```
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
    ```

2. 依存関係インストール
    ```
    cd voice-recognition
    uv sync
    ```

3. .env 作成
    ```
    cp .env.example .env
    ```

## 起動方法

```
uv run uvicorn voice_recognition.main:app --host 0.0.0.0 --port 8765
```

## API一覧

GET /health
  ヘルスチェック

GET /help
  API一覧・使用例の表示

POST /transcribe
  音声 → テキスト（話者識別付き）

POST /extract_voice_features
  音声 → 特徴量

POST /analyze_audio
  音声 → まとめて解析（メインAPI、話者識別付き）

POST /analyze_audio_summary
  Claude向けの簡潔な要約（話者識別付き）

POST /register_speaker
  話者の声を登録（フォーム: speaker_id, file）

GET /speakers
  登録済み話者一覧

DELETE /speakers/{speaker_id}
  登録済み話者を削除

## 使用例

```
curl -X POST http://127.0.0.1:8765/analyze_audio \
  -F "file=@sample.wav"
```

## 出力例
```
{
  "transcript": "こんにちは",
  "sound_events": [...],
  "voice_features": {...},
  "summary_for_claude": "環境音: ... 音声特徴: ..."
}
```

## GPU設定

.env
```
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

CPUモード:
```
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
```

## CUDA設定（重要）

必要条件:
- libcublas.so.12
- libcudnn (必要に応じて)

もし認識されない場合:
```
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libcublas/12:$LD_LIBRARY_PATH
```
永続化:
```
echo '/usr/lib/x86_64-linux-gnu/libcublas/12' | sudo tee /etc/ld.so.conf.d/libcublas-12.conf
sudo ldconfig
```
## テスト用音声作成
```
arecord -d 5 -f S16_LE -r 16000 -c 1 sample.wav
```
## 開発メモ

・Whisperは最初CPUで動作確認するのが安全
・GPUは後から有効化
・音声は1回だけロードして各処理に分岐する

## 今後の拡張

・PANNs / YAMNetによる環境音分類
・openSMILE(eGeMAPS)追加
・Claude function call連携
・ROS2ノード化
・リアルタイム処理

## 備考

このサーバーは「音声理解エンジン」として設計されている。
Claudeやロボットと組み合わせて使用する前提。