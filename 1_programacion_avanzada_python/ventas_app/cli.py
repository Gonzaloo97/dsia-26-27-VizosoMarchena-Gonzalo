"""
Punto de entrada por línea de comandos.

Uso (desde la carpeta 1_programacion_avanzada_python/):
    python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from ventas_app import loader, metrics, validator

NOMBRE_INFORME_CALIDAD = "calidad_datos.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def leer_argumentos() -> argparse.Namespace:
    """Define y lee los argumentos --input y --output."""
    parser = argparse.ArgumentParser(description="Limpieza y métricas de ventas")
    parser.add_argument("--input", required=True, help="Ruta del fichero de ventas (CSV o JSON)")
    parser.add_argument("--output", required=True, help="Ruta del CSV de ventas limpias")
    return parser.parse_args()


def main() -> None:
    """Orquesta el pipeline: cargar -> validar -> calcular métricas -> exportar."""
    args = leer_argumentos()
    ruta_salida = Path(args.output)

    # Solo se capturan los errores propios: muestran un mensaje claro y terminan
    # con código 1. Cualquier otro error inesperado debe verse completo.
    try:
        ventas = loader.load(args.input)
        validos, errores = validator.validar_ventas(ventas)
    except (loader.DataLoadError, validator.ValidationError) as error:
        logger.error(error)
        sys.exit(1)

    logger.info("Filas cargadas: %d | válidas: %d | inválidas: %d",
                len(ventas), len(validos), len(errores))

    logger.info("Importe total por región:\n%s", metrics.importe_por_region(validos))
    logger.info("Top productos por importe:\n%s", metrics.top_productos(validos))
    logger.info("Clientes con más de una compra:\n%s", metrics.clientes_recurrentes(validos))

    validos.to_csv(ruta_salida, index=False)
    logger.info("CSV limpio guardado en %s", ruta_salida)

    calidad = metrics.resumen_calidad(ventas, validos, errores)
    ruta_calidad = ruta_salida.with_name(NOMBRE_INFORME_CALIDAD)
    with open(ruta_calidad, "w", encoding="utf-8") as f:
        json.dump(calidad, f, indent=4)
    logger.info("Informe de calidad guardado en %s: %s", ruta_calidad, calidad)


if __name__ == "__main__":
    main()