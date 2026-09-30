"""Validación de las filas de ventas."""

import pandas as pd  # Librería para trabajar con DataFrames


class ValidationError(Exception):
    """Error que se lanza cuando los datos no tienen la estructura esperada."""


# Columnas que deben existir en el dataset
COLUMNAS_OBLIGATORIAS = ["fecha", "region", "producto", "unidades", "precio_unitario", "cliente_id"]

# Columnas que deben ser numéricas y mayores que VALOR_MINIMO.
# Para añadir una nueva regla basta con añadir la columna a esta lista
COLUMNAS_POSITIVAS = ["unidades", "precio_unitario"]

# Valor a partir del cual una cantidad o un precio se considera válido (estrictamente mayor)
VALOR_MINIMO = 0


def comprobar_columnas(frame: pd.DataFrame) -> None:
    """
    Comprueba que el DataFrame contiene todas las columnas obligatorias.

    Lanza:
      ValidationError si falta alguna columna.
    """
    # Lista de columnas obligatorias que no aparecen en el DataFrame
    faltan = [columna for columna in COLUMNAS_OBLIGATORIAS if columna not in frame.columns]

    if faltan:
        raise ValidationError(f"Faltan columnas obligatorias: {faltan}")


def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa las filas de ventas en válidas e inválidas.

    Una fila es válida si todas las columnas de COLUMNAS_POSITIVAS
    son numéricas y mayores que VALOR_MINIMO.
    A las filas válidas se les añade la columna 'importe'.

    Parámetros:
      frame: DataFrame con los datos de ventas originales.

    Devuelve:
      (validos, errores): DataFrame de filas válidas y DataFrame de filas inválidas.
    """
    # Antes de validar filas se comprueba que la estructura es la correcta
    comprobar_columnas(frame)

    # Copia para no modificar el DataFrame original
    df = frame.copy()

    # Máscara inicial: todas las filas se consideran válidas
    filas_ok = pd.Series(True, index=df.index)

    # Se aplica la regla a cada columna de la lista
    for columna in COLUMNAS_POSITIVAS:
        # Conversión a número: lo que no sea numérico pasa a NaN
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
        # La fila sigue siendo válida solo si además cumple esta columna (NaN > 0 da False)
        filas_ok = filas_ok & (df[columna] > VALOR_MINIMO)

    # Filas válidas (con columnas ya numéricas)
    validos = df[filas_ok].copy()

    # Filas inválidas tal y como venían en los datos originales
    errores = frame[~filas_ok]

    # Columna derivada: importe de cada venta, solo en las filas válidas
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]

    return validos, errores