"""Carga de los datos de ventas (patrón Repository)."""

from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar los datos de origen."""


class SalesRepository(Protocol):
    """
    Interfaz de cualquier fuente de datos de ventas.

    Cualquier clase con un método load() que devuelva un DataFrame cumple
    esta interfaz sin necesidad de heredar de ella (duck typing).
    """

    def load(self) -> pd.DataFrame:
        """Devuelve las ventas como DataFrame."""
        ...


class CsvSalesRepository:
    """Lee las ventas desde un fichero CSV."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.path)


class JsonSalesRepository:
    """Lee las ventas desde un fichero JSON con una lista de registros."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> pd.DataFrame:
        return pd.read_json(self.path)


# Para admitir un formato nuevo basta con crear su repositorio y registrarlo aquí:
# el resto del código no cambia (OCP + DIP).
REPOSITORIOS = {
    ".csv": CsvSalesRepository,
    ".json": JsonSalesRepository,
}


def crear_repositorio(path: str | Path) -> SalesRepository:
    """
    Devuelve el repositorio adecuado según la extensión del fichero.

    Lanza:
      DataLoadError si el fichero no existe o su formato no está soportado.
    """
    ruta = Path(path)
    if not ruta.exists():
        raise DataLoadError(f"No existe el fichero: {ruta}")

    clase_repositorio = REPOSITORIOS.get(ruta.suffix)
    if clase_repositorio is None:
        raise DataLoadError(f"Formato no soportado: {ruta.suffix}")

    return clase_repositorio(ruta)


def load(path: str | Path) -> pd.DataFrame:
    """
    Carga un fichero de ventas (CSV o JSON) y lo devuelve como DataFrame.

    Lanza:
      DataLoadError si el fichero no existe o su formato no está soportado.
    """
    return crear_repositorio(path).load()