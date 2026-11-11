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
rm -f "$OUT/LAST_OK.txt"
exec >> "$OUT/cron.log" 2>&1
"$PYTHON" -m readmission_app run \
  --input proyecto_ii/artifacts/holdout.csv --provider mock --output-dir "$OUT"
"$PYTHON" scripts/check_metrics.py --metrics "$OUT/metrics.json" --min-rows-out 100
printf 'PIPELINE_OK %s\n' "$DAY" > "$OUT/LAST_OK.txt"
