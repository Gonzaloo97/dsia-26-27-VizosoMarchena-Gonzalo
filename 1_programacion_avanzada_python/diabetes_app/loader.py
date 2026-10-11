"""Carga de los encuentros hospitalarios desde fichero (patrón Repository)."""

from pathlib import Path
from typing import Protocol

import pandas as pd

# En el dataset original los valores desconocidos se marcan con "?".
# Además, "None" NO es un nulo: en max_glu_serum y A1Cresult significa
# "prueba no realizada". Por eso se desactivan los nulos por defecto de pandas
# (que convertirían "None" en NaN) y solo se trata "?" como valor ausente.
MARCADORES_NULO = ["?"]


class DataLoadError(Exception):
    """Error que se lanza cuando no se pueden cargar los datos."""


class EncounterRepository(Protocol):
    """Interfaz de cualquier fuente de encuentros hospitalarios."""

    def load(self) -> pd.DataFrame:
        """Devuelve los encuentros como DataFrame."""
        ...


class CsvEncounterRepository:
    """Repositorio que lee los encuentros desde un CSV con el formato del dataset UCI."""

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> pd.DataFrame:
        """Lee el CSV tratando "?" como nulo y conservando "None" como texto."""
        # low_memory=False lee el fichero de una vez y evita avisos de tipos mezclados
        return pd.read_csv(self.path, na_values=MARCADORES_NULO, keep_default_na=False, low_memory=False)


# Para admitir otra fuente basta con crear su repositorio y registrarlo aquí (OCP + DIP).
REPOSITORIOS = {
    ".csv": CsvEncounterRepository,
}


def crear_repositorio(path: str | Path) -> EncounterRepository:
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
    Carga un fichero de encuentros hospitalarios y lo devuelve como DataFrame.

    Lanza:
      DataLoadError si el fichero no existe o su formato no está soportado.
    """
    return crear_repositorio(path).load()