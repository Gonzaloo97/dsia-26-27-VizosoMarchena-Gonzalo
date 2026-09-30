from pathlib import Path  # Manejo de rutas de archivos independiente del sistema operativo
import json  # Lectura y escritura de archivos JSON
import pandas as pd  # Librería para trabajar con tablas de datos (DataFrames)

# ============================================================
# PARTE 1 - Diagnóstico
# ============================================================

# Carpeta en la que se encuentra este script (ejercicios/)
carpeta_script = Path(__file__).parent

# Se sube un nivel (1_programacion_avanzada_python/) y se entra en la carpeta Datos/
carpeta_datos = carpeta_script.parent / "Datos"

# Carga del CSV de ventas en un DataFrame
ventas = pd.read_csv(carpeta_datos / "ventas.csv")

# Número de filas y columnas del dataset
print("Shape:", ventas.shape)

# Tipo de dato de cada columna (numérico, texto, etc.)
print("\nTipos de cada columna:")
print(ventas.dtypes)

# Cantidad de valores vacíos (NaN) en cada columna
print("\nValores nulos por columna:")
print(ventas.isna().sum())

# Observaciones del diagnóstico:
# - La columna 'unidades' se lee como texto (str) en lugar de número porque
#   contiene un valor no numérico ("na"). Por eso hay que convertirla a número
#   antes de validarla.
# - 'unidades' tiene 2 valores vacíos y 'precio_unitario' tiene 1.
#
# Filas inválidas detectadas (índice: motivo):
# - 3:   unidades = 0
# - 41:  precio_unitario = 0
# - 54:  unidades vacía
# - 63:  unidades vacía
# - 66:  precio_unitario vacío
# - 84:  unidades = "na" (texto, no es un número)
# - 88:  unidades negativas (-2)
# - 109: unidades = 0 y precio_unitario negativo (-1)
# - 134: precio_unitario negativo (-5)
# - 149: precio_unitario negativo (-32)
#
# En total 10 filas inválidas de 150, por lo que quedan 140 válidas.


# ============================================================
# PARTE 2 - Validación
# ============================================================

def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa las filas de ventas en válidas e inválidas.

    Una fila es válida si:
      - 'unidades' es un número mayor que 0
      - 'precio_unitario' es un número mayor que 0

    A las filas válidas se les añade la columna 'importe'
    (unidades * precio_unitario).

    Parámetros:
      frame: DataFrame con los datos de ventas originales.

    Devuelve:
      (validos, errores): una tupla con dos DataFrames,
      el primero con las filas válidas y el segundo con las inválidas.
    """
    # Copia del DataFrame para no modificar los datos originales
    df = frame.copy()

    # Conversión de las columnas a número.
    # errors="coerce" convierte en NaN cualquier valor que no sea numérico (por ejemplo "na")
    df["unidades"] = pd.to_numeric(df["unidades"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")

    # Serie de True/False: True si la fila cumple las dos condiciones.
    # Las comparaciones con NaN devuelven False, así que los vacíos quedan como inválidos
    filas_ok = (df["unidades"] > 0) & (df["precio_unitario"] > 0)

    # Filas que cumplen las reglas (ya con columnas numéricas)
    validos = df[filas_ok].copy()

    # Filas que no cumplen las reglas (~ invierte True/False).
    # Se toman del DataFrame original para conservar los valores tal y como venían
    errores = frame[~filas_ok]

    # Columna derivada: importe de cada venta, calculado solo en las filas válidas
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]

    return validos, errores


# Aplicación de la validación al dataset de ventas
validos, errores = validar_ventas(ventas)

# Resumen del número de filas válidas e inválidas
print("\nFilas válidas:", len(validos))
print("Filas inválidas:", len(errores))

# Detalle de las filas descartadas
print("\nFilas inválidas:")
print(errores)


# ============================================================
# PARTE 3 - Agregaciones
# ============================================================

# 1. Importe total por región, ordenado de mayor a menor.
# groupby agrupa las filas por región, sum suma el importe de cada grupo
# y sort_values ordena el resultado de forma descendente
importe_region = validos.groupby("region")["importe"].sum().sort_values(ascending=False)
print("\nImporte total por región:")
print(importe_region)

# 2. Top 3 productos con mayor importe total.
# Mismo procedimiento que por región, quedándose con los 3 primeros con head(3)
top_productos = validos.groupby("producto")["importe"].sum().sort_values(ascending=False).head(3)
print("\nTop 3 productos:")
print(top_productos)

# 3. Clientes con más de una compra.
# value_counts cuenta cuántas filas (compras) tiene cada cliente
compras_cliente = validos["cliente_id"].value_counts()

# Filtro para quedarse solo con los clientes que tienen más de 1 compra
clientes_repetidos = compras_cliente[compras_cliente > 1]
print("\nClientes con más de una compra:")
print(clientes_repetidos)


# ============================================================
# PARTE 4 - Exportación
# ============================================================

# Guardado de las ventas válidas en un nuevo CSV.
# index=False evita que se guarde la columna con el número de fila
validos.to_csv(carpeta_datos / "ventas_limpias.csv", index=False)

# Diccionario con el resumen de calidad de los datos
calidad = {
    "filas_totales": len(ventas),  # Filas del CSV original
    "filas_validas": len(validos),  # Filas que pasan la validación
    "filas_invalidas": len(errores),  # Filas descartadas
    "importe_total": float(round(validos["importe"].sum(), 2)),  # Suma de importes redondeada a 2 decimales
}

# Guardado del resumen en un archivo JSON.
# "w" abre el archivo en modo escritura (lo crea si no existe)
# indent=4 da formato legible al JSON
with open(carpeta_datos / "calidad_datos.json", "w", encoding="utf-8") as f:
    json.dump(calidad, f, indent=4)

# Confirmación por pantalla
print("\nArchivos guardados en la carpeta Datos")
print(calidad)