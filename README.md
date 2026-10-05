# M5 Petit Speech

## [English Page](./README_en.md)

M5 Petit向けの音声処理サーバー群のリポジトリ。**GPUなしのPCでも動く**。1台(Claudeと同じPC)でも、音声だけ別のPC(GPU付きなど)に分けてもよい。

呼ぶ側(m5-petit-mcp)は `VOICE_API_HOST` で行き先を決めるだけなので、同じPCなら `localhost`、別のPCならそのホスト名を指定する。MCP経由ではなく素のHTTP APIにしているのは、音声は応答速度が大事で、MCPのオーバーヘッドを避けたいから。

## サブプロジェクト

- **[text-to-speech](./text-to-speech/)** — 音声合成(TTS)。piper / kokoro / voicevoxの3エンジンに対応

音声認識（Whisper・話者識別・音声特徴量）は独立リポジトリ [m5-petit-voice-recognition](https://github.com/PetitOnes/m5-petit-voice-recognition) に移動しました。

## 構成イメージ

**1台で動かす(GPUなしでよい)**

```
[1台のPC]
- Claude / 制御ロジック
- text-to-speech (port 8766) = このリポジトリ
- voice-recognition (port 8767) = m5-petit-voice-recognition
  → 呼ぶ側は VOICE_API_HOST=localhost
```

**音声だけ別のPCに分ける(GPU付きPCなど)**

```
[常時ONのミニPC]                    [音声用のPC]
- Claude / 制御ロジック     HTTP    - text-to-speech (8766)
- VOICE_API_HOST=<音声用PC>  ───→   - voice-recognition (8767)
```

通信はHTTP。別PCの場合はTailscale経由などを想定。

## GPUは要る?

| | GPUなし | GPUあり |
|---|---|---|
| text-to-speech | 動く。piper・kokoroはCPU実行。voicevoxは **CPU版のVOICEVOX ENGINE** を起動しておく | voicevoxを **GPU版のVOICEVOX ENGINE** にすると合成が速くなる(このリポジトリの設定は同じ) |
| voice-recognition | 動く(`WHISPER_DEVICE=cpu`)。速さはモデルの大きさしだい | `WHISPER_DEVICE=cuda` |

このリポジトリ自体にGPUの設定はない。違いは「どのVOICEVOX ENGINEを起動するか」だけ。

## 今後追加したい機能

- 顔認識・表情推定
- 画像解析
- 音声・画像・環境情報を統合するマルチモーダルAPI
