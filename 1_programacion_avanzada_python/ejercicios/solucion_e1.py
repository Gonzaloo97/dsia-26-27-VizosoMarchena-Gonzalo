"""
E1 — Procesamiento de datos con pandas.

Flujo: cargar -> diagnosticar -> validar -> agregar -> exportar.
Ejecutar desde la raíz del repositorio o desde cualquier otra carpeta:
    python 1_programacion_avanzada_python/ejercicios/solucion_e1.py
"""

import json
from pathlib import Path

import pandas as pd

# La ruta se construye a partir del propio script para que funcione
# independientemente de la carpeta desde la que se ejecute.
CARPETA_DATOS = Path(__file__).parent.parent / "Datos"

DECIMALES_IMPORTE = 2
NUM_TOP_PRODUCTOS = 3
MIN_COMPRAS_RECURRENTE = 1


# ============================================================
# PARTE 1 - Diagnóstico
# ============================================================

ventas = pd.read_csv(CARPETA_DATOS / "ventas.csv")

print("Shape:", ventas.shape)
print("\nTipos de cada columna:")
print(ventas.dtypes)
print("\nValores nulos por columna:")
print(ventas.isna().sum())

# Observaciones del diagnóstico:
# - 'unidades' se lee como texto (str) porque contiene un valor no numérico ("na"):
#   basta un solo texto para que pandas trate toda la columna como texto.
# - 'unidades' tiene 2 valores vacíos y 'precio_unitario' tiene 1.
#
# Filas inválidas detectadas (índice: motivo):
# - 3:   unidades = 0
# - 41:  precio_unitario = 0
# - 54:  unidades vacía
# - 63:  unidades vacía
# - 66:  precio_unitario vacío
# - 84:  unidades = "na" (texto)
# - 88:  unidades negativas (-2)
# - 109: unidades = 0 y precio_unitario negativo (-1)
# - 134: precio_unitario negativo (-5)
# - 149: precio_unitario negativo (-32)
# Total: 10 inválidas de 150 -> 140 válidas.


# ============================================================
# PARTE 2 - Validación
# ============================================================

def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa las filas de ventas en válidas e inválidas.

    Una fila es válida si 'unidades' y 'precio_unitario' son numéricos y mayores que 0.
    A las filas válidas se les añade la columna 'importe' (unidades * precio_unitario).

    Devuelve:
      (validos, errores): DataFrame de filas válidas y DataFrame de filas inválidas.
    """
    df = frame.copy()

    # errors="coerce" convierte en NaN los valores no numéricos (como "na").
    df["unidades"] = pd.to_numeric(df["unidades"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")

    # Cualquier comparación con NaN da False, así que los vacíos y los textos
    # quedan como inválidos sin necesidad de una regla aparte.
    filas_ok = (df["unidades"] > 0) & (df["precio_unitario"] > 0)

    validos = df[filas_ok].copy()
    # Las filas inválidas se toman del original para conservar los valores tal como venían.
    errores = frame[~filas_ok]

    validos["importe"] = validos["unidades"] * validos["precio_unitario"]
    return validos, errores


validos, errores = validar_ventas(ventas)

print("\nFilas válidas:", len(validos))
print("Filas inválidas:", len(errores))
print("\nDetalle de filas inválidas:")
print(errores)


# ============================================================
# PARTE 3 - Agregaciones
# ============================================================

importe_por_region = validos.groupby("region")["importe"].sum().sort_values(ascending=False)
print("\nImporte total por región:")
print(importe_por_region)

top_productos = (
    validos.groupby("producto")["importe"].sum()
    .sort_values(ascending=False)
    .head(NUM_TOP_PRODUCTOS)
)
print(f"\nTop {NUM_TOP_PRODUCTOS} productos por importe:")
print(top_productos)

compras_por_cliente = validos["cliente_id"].value_counts()
clientes_recurrentes = compras_por_cliente[compras_por_cliente > MIN_COMPRAS_RECURRENTE]
print("\nClientes con más de una compra:")
print(clientes_recurrentes)


# ============================================================
# PARTE 4 - Exportación
# ============================================================

validos.to_csv(CARPETA_DATOS / "ventas_limpias.csv", index=False)

# json no sabe serializar los tipos de numpy, por eso el importe se convierte a float.
calidad = {
    "filas_totales": len(ventas),
    "filas_validas": len(validos),
    "filas_invalidas": len(errores),
    "importe_total": float(round(validos["importe"].sum(), DECIMALES_IMPORTE)),
}

with open(CARPETA_DATOS / "calidad_datos.json", "w", encoding="utf-8") as f:
    json.dump(calidad, f, indent=4)

print("\nArchivos guardados en la carpeta Datos:")
print(calidad)