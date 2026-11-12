#!/usr/bin/env bash
# Wrapper cron-ready: requiere venv y modelo entrenado. No instala un cron.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
PYTHON="$REPO/.venv/bin/python"
# Permite verificar el mismo wrapper con Git Bash en Windows.
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$REPO/.venv/Scripts/python.exe"
fi
DAY="$(date +%F)"
OUT="$REPO/proyecto_ii/output_daily/$DAY"
mkdir -p "$OUT"
exec >> "$OUT/cron.log" 2>&1
# Reutiliza la misma cadena que PowerShell y la ejecucion directa en Python.
"$PYTHON" scripts/run_pipeline.py "$@"
