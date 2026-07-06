# M5 Petit Speech

## [日本語ページ](README.md)

A repository of speech-processing servers for M5 Petit, running on a GPU-equipped PC.

The idea is that an always-on lightweight PC (Claude / control logic) offloads only the heavy speech processing to this GPU PC over HTTP. It's a plain HTTP API rather than MCP because both speech synthesis and speech recognition are latency-sensitive, and we want to avoid MCP's overhead.

## Subprojects

- **[text-to-speech](./text-to-speech/)** — Speech synthesis (TTS). Supports three engines: piper / kokoro / voicevox

Speech recognition (Whisper, speaker identification, voice features) has moved to its own repository: [m5-petit-voice-recognition](https://github.com/PetitOnes/m5-petit-voice-recognition).

## Architecture

```
[Always-on mini PC]
- Claude / control logic / user interaction
- Sends HTTP API requests to the GPU PC

[GPU-equipped PC]
- text-to-speech (port 8766) = this repository
- voice-recognition (port 8767) = m5-petit-voice-recognition
```

Communication is over HTTP, with access from other PCs expected via Tailscale.

## Planned features

- Face recognition / expression estimation
- Image analysis
- A multimodal API integrating voice, image, and environmental data