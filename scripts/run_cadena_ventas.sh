#!/usr/bin/env bash
# E4: limpiar -> validar metricas -> publicar copias y marcador local.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
PYTHON="$REPO/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$REPO/.venv/Scripts/python.exe"
fi
OUT="${1:-$REPO/proyecto_ii/output_ventas_diario/$(date +%F)}"
GATE="${2:-0.1}"
MIN_ROWS="${3:-100}"
mkdir -p "$OUT"
rm -f "$OUT/LAST_OK.txt" "$OUT/publicado/ventas_limpias.csv" "$OUT/publicado/metrics.json"
"$PYTHON" scripts/pipeline_ventas.py \
  --input "$REPO/1_programacion_avanzada_python/Datos/ventas.csv" \
  --output-dir "$OUT" --max-error-rate "$GATE"
"$PYTHON" scripts/check_metrics.py --metrics "$OUT/metrics.json" --min-rows-out "$MIN_ROWS"
mkdir -p "$OUT/publicado"
cp "$OUT/ventas_limpias.csv" "$OUT/metrics.json" "$OUT/publicado/"
printf 'PIPELINE_OK %s\n' "$(date +%F)" > "$OUT/LAST_OK.txt"
