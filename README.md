# m5-petit-speech

GPU付きPC上で動作する、M5 Petit向けの音声処理サーバー群のリポジトリ。

常時ONの軽量PC（Claude / 制御ロジック）から、HTTP経由で重い音声処理だけをこのGPU PCに投げる構成を想定している。MCP経由ではなく素のHTTP APIにしているのは、音声合成・音声認識は応答速度が重要で、MCPのオーバーヘッドを避けたいため。

## サブプロジェクト

- **[m5_petit_speech](./m5_petit_speech/)** — 音声合成(TTS)。piper / kokoro / voicevoxの3エンジンに対応
- **[m5_petit_voice_recognition](./m5_petit_voice_recognition/)** — 音声認識(Whisper)・環境音分類・音声特徴量抽出・話者識別

各サブプロジェクトは独立したuvプロジェクトで、個別に起動・テストできる。詳細は各ディレクトリのREADMEを参照。

## 構成イメージ

```
[常時ONのミニPC]
- Claude / 制御ロジック / ユーザーとの対話
- GPU PCへのHTTP APIリクエスト送信

[GPU付きPC = このリポジトリ]
- m5_petit_speech            (port 8766)
- m5_petit_voice_recognition (port 8765)
```

通信はHTTP、Tailscale経由での他PCからのアクセスを想定。

## 今後追加したい機能

- 顔認識・表情推定
- 画像解析
- 音声・画像・環境情報を統合するマルチモーダルAPI
