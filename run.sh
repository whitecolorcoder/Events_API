#!/bin/bash

set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
APP_MODULE="${APP_MODULE:-src.core.wsgi.main:app}"

if command -v uv >/dev/null 2>&1; then
	exec uv run python -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}"
elif [ -x "./venv_events/bin/python" ]; then
	exec ./venv_events/bin/python -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}"
elif [ -x "./venv_events/Scripts/python.exe" ]; then
	exec ./venv_events/Scripts/python.exe -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}"
elif command -v python3 >/dev/null 2>&1; then
	exec python3 -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}"
else
	exec python -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}"
fi