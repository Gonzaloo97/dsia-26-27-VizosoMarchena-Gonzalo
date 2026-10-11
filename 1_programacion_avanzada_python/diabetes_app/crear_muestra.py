"""
Genera una muestra reducida del dataset completo para versionarla en el repositorio.

El dataset completo (~100.000 filas, ~18 MB) no se sube a GitHub.
Uso (desde la carpeta 1_programacion_avanzada_python/):
    python -m diabetes_app.crear_muestra --input Datos/diabetic_data.csv --output Datos/diabetic_data_muestra.csv
"""

import argparse

import pandas as pd

FILAS_MUESTRA = 5000

# Semilla fija: la muestra es siempre la misma (reproducible)
SEMILLA = 42


def main() -> None:
    """Lee el CSV completo y guarda una muestra aleatoria reproducible."""
    parser = argparse.ArgumentParser(description="Crea una muestra del dataset de diabetes")
    parser.add_argument("--input", required=True, help="CSV completo descargado de UCI")
    parser.add_argument("--output", required=True, help="Ruta del CSV de muestra")
    parser.add_argument("--filas", type=int, default=FILAS_MUESTRA, help="Número de filas de la muestra")
    args = parser.parse_args()

    # Se lee todo como texto para copiar los valores exactamente como vienen ("?", "None"...)
    completo = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    muestra = completo.sample(n=args.filas, random_state=SEMILLA).sort_index()
    muestra.to_csv(args.output, index=False)
    print(f"Muestra de {len(muestra)} filas guardada en {args.output}")


if __name__ == "__main__":
    main()