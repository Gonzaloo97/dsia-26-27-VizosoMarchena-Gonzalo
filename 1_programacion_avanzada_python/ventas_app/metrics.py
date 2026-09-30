"""Agregaciones y métricas sobre las ventas válidas."""

import pandas as pd  # Librería para trabajar con DataFrames

# Número de productos que se muestran en el ranking
NUM_TOP_PRODUCTOS = 3

# Un cliente es recurrente si tiene más compras que este valor
MIN_COMPRAS_RECURRENTE = 1


def importe_por_region(validos: pd.DataFrame) -> pd.Series:
    """Devuelve el importe total por región, ordenado de mayor a menor."""
    return validos.groupby("region")["importe"].sum().sort_values(ascending=False)


def top_productos(validos: pd.DataFrame) -> pd.Series:
    """Devuelve los NUM_TOP_PRODUCTOS productos con mayor importe total."""
    importe_producto = validos.groupby("producto")["importe"].sum()
    return importe_producto.sort_values(ascending=False).head(NUM_TOP_PRODUCTOS)


def clientes_recurrentes(validos: pd.DataFrame) -> pd.Series:
    """Devuelve los clientes con más de una compra y su número de compras."""
    # Número de compras (filas) de cada cliente
    compras_cliente = validos["cliente_id"].value_counts()
    # Filtro de los clientes que superan el mínimo
    return compras_cliente[compras_cliente > MIN_COMPRAS_RECURRENTE]


def resumen_calidad(total: pd.DataFrame, validos: pd.DataFrame, errores: pd.DataFrame) -> dict:
    """
    Construye el informe de calidad de los datos.

    Devuelve:
      Diccionario con filas totales, válidas, inválidas e importe total.
    """
    return {
        "filas_totales": len(total),
        "filas_validas": len(validos),
        "filas_invalidas": len(errores),
        "importe_total": float(round(validos["importe"].sum(), 2)),
    }