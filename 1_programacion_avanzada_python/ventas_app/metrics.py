"""Agregaciones de negocio sobre las ventas válidas."""

import pandas as pd

NUM_TOP_PRODUCTOS = 3
MIN_COMPRAS_RECURRENTE = 1
DECIMALES_IMPORTE = 2


def importe_por_region(validos: pd.DataFrame) -> pd.Series:
    """Importe total por región, de mayor a menor."""
    return validos.groupby("region")["importe"].sum().sort_values(ascending=False)


def top_productos(validos: pd.DataFrame) -> pd.Series:
    """Los NUM_TOP_PRODUCTOS productos con mayor importe total."""
    importe_por_producto = validos.groupby("producto")["importe"].sum()
    return importe_por_producto.sort_values(ascending=False).head(NUM_TOP_PRODUCTOS)


def clientes_recurrentes(validos: pd.DataFrame) -> pd.Series:
    """Clientes con más de una compra y su número de compras."""
    compras_por_cliente = validos["cliente_id"].value_counts()
    return compras_por_cliente[compras_por_cliente > MIN_COMPRAS_RECURRENTE]


def resumen_calidad(total: pd.DataFrame, validos: pd.DataFrame, errores: pd.DataFrame) -> dict:
    """Informe de calidad: filas totales, válidas, inválidas e importe total."""
    return {
        "filas_totales": len(total),
        "filas_validas": len(validos),
        "filas_invalidas": len(errores),
        # json no sabe serializar los tipos de numpy, por eso se convierte a float.
        "importe_total": float(round(validos["importe"].sum(), DECIMALES_IMPORTE)),
    }