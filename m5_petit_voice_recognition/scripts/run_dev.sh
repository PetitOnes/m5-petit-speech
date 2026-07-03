#!/usr/bin/env bash
set -eu
uv run uvicorn m5_petit_voice_recognition.main:app --host 0.0.0.0 --port 8000 --reload