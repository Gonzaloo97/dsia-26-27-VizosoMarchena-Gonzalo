"""
Punto de entrada por línea de comandos.

Uso (desde la carpeta 1_programacion_avanzada_python/):
    python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
"""

import argparse  # Lectura de argumentos de la línea de comandos
import json  # Escritura del informe de calidad en JSON
import logging  # Mensajes de ejecución (sustituye a los print)
import sys  # Permite terminar el programa con un código de error
from pathlib import Path  # Manejo de rutas de archivos

from ventas_app import loader, metrics, validator  # Módulos propios del paquete

# Nombre del fichero del informe de calidad (se guarda junto al CSV de salida)
NOMBRE_INFORME_CALIDAD = "calidad_datos.json"

# Configuración básica del logging: nivel INFO y formato "NIVEL - mensaje"
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

    # 1. Carga y validación. Los errores propios se capturan para
    #    mostrar un mensaje claro y terminar con código de error 1
    try:
        ventas = loader.load(args.input)
        validos, errores = validator.validar_ventas(ventas)
    except (loader.DataLoadError, validator.ValidationError) as error:
        logger.error(error)
        sys.exit(1)

    logger.info("Filas cargadas: %d | válidas: %d | inválidas: %d",
                len(ventas), len(validos), len(errores))

    # 2. Métricas sobre las filas válidas
    logger.info("Importe total por región:\n%s", metrics.importe_por_region(validos))
    logger.info("Top productos por importe:\n%s", metrics.top_productos(validos))
    logger.info("Clientes con más de una compra:\n%s", metrics.clientes_recurrentes(validos))

    # 3. Exportación del CSV limpio
    validos.to_csv(ruta_salida, index=False)
    logger.info("CSV limpio guardado en %s", ruta_salida)

    # 4. Exportación del informe de calidad en la misma carpeta que el CSV
    calidad = metrics.resumen_calidad(ventas, validos, errores)
    ruta_calidad = ruta_salida.with_name(NOMBRE_INFORME_CALIDAD)
    with open(ruta_calidad, "w", encoding="utf-8") as f:
        json.dump(calidad, f, indent=4)
    logger.info("Informe de calidad guardado en %s: %s", ruta_calidad, calidad)


# Solo se ejecuta main() cuando el módulo se lanza directamente (python -m ventas_app.cli),
# no cuando se importa desde otro módulo
if __name__ == "__main__":
    main()