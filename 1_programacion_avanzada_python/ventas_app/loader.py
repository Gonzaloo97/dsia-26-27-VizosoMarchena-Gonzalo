"""Carga de los datos de ventas desde fichero."""

from pathlib import Path  # Manejo de rutas de archivos
import pandas as pd  # Librería para trabajar con DataFrames


class DataLoadError(Exception):
    """Error que se lanza cuando no se pueden cargar los datos."""


def load(path: str | Path) -> pd.DataFrame:
    """
    Carga un fichero de ventas y lo devuelve como DataFrame.

    Formatos admitidos:
      - .csv
      - .json (lista de registros: [{"fecha": ..., "region": ...}, ...])

    Parámetros:
      path: ruta del fichero a cargar.

    Devuelve:
      DataFrame con los datos del fichero.

    Lanza:
      DataLoadError si el fichero no existe o su formato no está soportado.
    """
    # Conversión a Path para poder usar sus métodos (exists, suffix...)
    ruta = Path(path)

    # Si el fichero no existe se lanza un error propio con un mensaje claro
    if not ruta.exists():
        raise DataLoadError(f"No existe el fichero: {ruta}")

    # Elección del lector según la extensión del fichero
    if ruta.suffix == ".csv":
        return pd.read_csv(ruta)
    if ruta.suffix == ".json":
        return pd.read_json(ruta)

    # Cualquier otra extensión no está soportada
    raise DataLoadError(f"Formato no soportado: {ruta.suffix}")