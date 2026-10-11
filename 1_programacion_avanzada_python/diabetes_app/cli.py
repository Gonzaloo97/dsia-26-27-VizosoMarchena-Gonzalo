"""
Punto de entrada por línea de comandos.

Uso (desde la carpeta 1_programacion_avanzada_python/):
    python -m diabetes_app.cli --input Datos/diabetic_data_muestra.csv --output Datos/diabetes_limpio.csv
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from diabetes_app import loader, metrics, validator

NOMBRE_INFORME_CALIDAD = "calidad_diabetes.json"

NUM_PACIENTES_MOSTRADOS = 5

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def leer_argumentos() -> argparse.Namespace:
    """Define y lee los argumentos --input y --output."""
    parser = argparse.ArgumentParser(description="Limpieza y métricas de ingresos de pacientes diabéticos")
    parser.add_argument("--input", required=True, help="Ruta del CSV de encuentros (formato UCI)")
    parser.add_argument("--output", required=True, help="Ruta del CSV de encuentros válidos")
    return parser.parse_args()


def main() -> None:
    """Orquesta el pipeline: cargar -> validar -> calcular métricas -> exportar."""
    args = leer_argumentos()
    ruta_salida = Path(args.output)

    # Solo se capturan los errores propios: muestran un mensaje claro y terminan con código 1.
    try:
        encuentros = loader.load(args.input)
        validos, errores = validator.validar_encuentros(encuentros)
        incumplimientos = validator.contar_incumplimientos(encuentros)
    except (loader.DataLoadError, validator.ValidationError) as error:
        logger.error(error)
        sys.exit(1)

    logger.info("Encuentros cargados: %d | válidos: %d | inválidos: %d",
                len(encuentros), len(validos), len(errores))
    logger.info("Motivos de invalidez (primera regla incumplida):\n%s",
                errores["motivo"].value_counts())

    logger.info("Distribución de reingresos (%%):\n%s", metrics.distribucion_reingreso(validos))
    logger.info("Reingreso <30 días por edad (%%):\n%s", metrics.tasa_reingreso_30_por_edad(validos))
    logger.info("Reingreso <30 días según HbA1c (%%):\n%s", metrics.tasa_reingreso_30_por_hba1c(validos))
    logger.info("Estancia media (días) por reingreso:\n%s", metrics.estancia_media_por_reingreso(validos))
    recurrentes = metrics.pacientes_recurrentes(validos)
    logger.info("Pacientes con más de un encuentro: %d (top %d):\n%s",
                len(recurrentes), NUM_PACIENTES_MOSTRADOS, recurrentes.head(NUM_PACIENTES_MOSTRADOS))

    validos.to_csv(ruta_salida, index=False)
    logger.info("CSV limpio guardado en %s", ruta_salida)

    calidad = metrics.resumen_calidad(encuentros, validos, errores, incumplimientos)
    ruta_calidad = ruta_salida.with_name(NOMBRE_INFORME_CALIDAD)
    with open(ruta_calidad, "w", encoding="utf-8") as f:
        json.dump(calidad, f, indent=4, ensure_ascii=False)
    logger.info("Informe de calidad guardado en %s", ruta_calidad)


if __name__ == "__main__":
    main()