"""Validación de las filas de ventas."""

import numpy as np
import pandas as pd


class ValidationError(Exception):
    """Los datos no tienen la estructura esperada."""


COLUMNAS_OBLIGATORIAS = ["fecha", "region", "producto", "unidades", "precio_unitario", "cliente_id"]

# Columnas que deben ser numéricas y mayores que VALOR_MINIMO.
# Añadir una columna a esta lista amplía la validación sin tocar la función (OCP).
COLUMNAS_POSITIVAS = ["unidades", "precio_unitario"]
VALOR_MINIMO = 0


def comprobar_columnas(frame: pd.DataFrame) -> None:
    """
    Comprueba que el DataFrame contiene todas las columnas obligatorias.

    Lanza:
      ValidationError si falta alguna columna.
    """
    faltan = [columna for columna in COLUMNAS_OBLIGATORIAS if columna not in frame.columns]
    if faltan:
        raise ValidationError(f"Faltan columnas obligatorias: {faltan}")


def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa las filas de ventas en válidas e inválidas.

    Una fila es válida si todas las columnas de COLUMNAS_POSITIVAS son numéricas
    y mayores que VALOR_MINIMO. A las válidas se les añade la columna 'importe'.

    Devuelve:
      (validos, errores): DataFrame de filas válidas y DataFrame de filas inválidas.

    Lanza:
      ValidationError si faltan columnas obligatorias.
    """
    comprobar_columnas(frame)
    df = frame.copy()

    filas_ok = pd.Series(True, index=df.index)
    for columna in COLUMNAS_POSITIVAS:
        # Los valores no numéricos pasan a NaN, y NaN > 0 es False:
        # los vacíos y los textos quedan como inválidos.
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
        filas_ok = filas_ok & np.isfinite(df[columna]) & (df[columna] > VALOR_MINIMO)

    # float evita tambien el desbordamiento silencioso de multiplicaciones int64.
    with np.errstate(over="ignore", invalid="ignore"):
        importes = df["unidades"].astype(float) * df["precio_unitario"].astype(float)
    filas_ok = filas_ok & np.isfinite(importes)
    validos = df[filas_ok].copy()
    # Las filas inválidas se devuelven tal como venían, para poder revisarlas.
    errores = frame[~filas_ok]

    validos["importe"] = importes[filas_ok]
    return validos, errores
