# M5 Petit Speech

## [English Page](./README_en.md)

GPU付きPC上で動作する、M5 Petit向けの音声処理サーバー群のリポジトリ。

常時ONの軽量PC（Claude / 制御ロジック）から、HTTP経由で重い音声処理だけをこのGPU PCに投げる構成を想定している。MCP経由ではなく素のHTTP APIにしているのは、音声合成・音声認識は応答速度が重要で、MCPのオーバーヘッドを避けたいため。

## サブプロジェクト

- **[text-to-speech](./text-to-speech/)** — 音声合成(TTS)。piper / kokoro / voicevoxの3エンジンに対応

音声認識（Whisper・話者識別・音声特徴量）は独立リポジトリ [m5-petit-voice-recognition](https://github.com/PetitOnes/m5-petit-voice-recognition) に移動しました。

## 構成イメージ

```
[常時ONのミニPC]
- Claude / 制御ロジック / ユーザーとの対話
- GPU PCへのHTTP APIリクエスト送信

[GPU付きPC]
- text-to-speech (port 8766) = このリポジトリ
- voice-recognition (port 8767) = m5-petit-voice-recognition
```

通信はHTTP、Tailscale経由での他PCからのアクセスを想定。

## 今後追加したい機能

- 顔認識・表情推定
- 画像解析
- 音声・画像・環境情報を統合するマルチモーダルAPI
