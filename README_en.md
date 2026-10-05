# M5 Petit Speech

## [日本語ページ](README.md)

A repository of speech-processing servers for M5 Petit. **It runs on a PC without a GPU.** You can run everything on one PC (the same one as Claude), or move only the speech services to another PC (e.g. one with a GPU).

The caller (m5-petit-mcp) only chooses the destination with `VOICE_API_HOST`: `localhost` for the same PC, or the other PC's hostname. It's a plain HTTP API rather than MCP because speech is latency-sensitive and we want to avoid MCP's overhead.

## Subprojects

- **[text-to-speech](./text-to-speech/)** — Speech synthesis (TTS). Supports three engines: piper / kokoro / voicevox

Speech recognition (Whisper, speaker identification, voice features) has moved to its own repository: [m5-petit-voice-recognition](https://github.com/PetitOnes/m5-petit-voice-recognition).

## Architecture

**One PC (no GPU needed)**

```
[one PC]
- Claude / control logic
- text-to-speech (port 8766) = this repository
- voice-recognition (port 8767) = m5-petit-voice-recognition
  → the caller sets VOICE_API_HOST=localhost
```

**Speech on a separate PC (e.g. with a GPU)**

```
[always-on mini PC]                 [speech PC]
- Claude / control logic    HTTP    - text-to-speech (8766)
- VOICE_API_HOST=<speech PC> ───→   - voice-recognition (8767)
```

Communication is plain HTTP (e.g. over Tailscale when on another PC).

## Do I need a GPU?

| | Without GPU | With GPU |
|---|---|---|
| text-to-speech | Works. piper and kokoro run on CPU. For voicevox, start the **CPU build of VOICEVOX ENGINE** | Use the **GPU build of VOICEVOX ENGINE** for faster synthesis (this repository's settings stay the same) |
| voice-recognition | Works (`WHISPER_DEVICE=cpu`); speed depends on model size | `WHISPER_DEVICE=cuda` |

This repository itself has no GPU setting. The only difference is which VOICEVOX ENGINE you start.

## Planned features

- Face recognition / expression estimation
- Image analysis
- A multimodal API integrating voice, image, and environmental data