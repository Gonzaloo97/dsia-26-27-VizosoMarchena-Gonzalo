"""
Validación de los encuentros hospitalarios.

Cada fila del dataset es un encuentro (ingreso) de un paciente diabético.
Una fila es válida para el análisis de reingresos si cumple todas las reglas
definidas en este módulo. Las filas inválidas se devuelven aparte con el motivo.
"""

import pandas as pd


class ValidationError(Exception):
    """Error que se lanza cuando el dataset no tiene la estructura esperada."""


COLUMNAS_OBLIGATORIAS = [
    "encounter_id", "patient_nbr", "gender", "age", "time_in_hospital",
    "num_lab_procedures", "num_procedures", "num_medications",
    "number_outpatient", "number_emergency", "number_inpatient",
    "number_diagnoses", "diag_1", "discharge_disposition_id",
    "A1Cresult", "max_glu_serum", "readmitted",
]

# Columnas que no pueden estar vacías (identificadores, datos demográficos básicos,
# diagnóstico principal y variable objetivo)
COLUMNAS_SIN_NULOS = ["encounter_id", "patient_nbr", "gender", "age", "diag_1", "readmitted"]

# Columnas numéricas con su rango válido (mínimo, máximo), ambos incluidos.
# None significa "sin límite superior"
RANGOS_NUMERICOS = {
    "time_in_hospital": (1, 14),     # días de estancia: el dataset solo incluye ingresos de 1 a 14 días
    "number_diagnoses": (1, 16),
    "num_lab_procedures": (0, None),
    "num_procedures": (0, None),
    "num_medications": (0, None),
    "number_outpatient": (0, None),
    "number_emergency": (0, None),
    "number_inpatient": (0, None),
}

GRUPOS_EDAD = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
               "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
VALORES_PERMITIDOS = {
    "gender": {"Female", "Male"},                       # "Unknown/Invalid" no es válido
    "age": set(GRUPOS_EDAD),
    "readmitted": {"NO", ">30", "<30"},
    "A1Cresult": {"None", "Norm", ">7", ">8"},          # "None" = prueba no realizada
    "max_glu_serum": {"None", "Norm", ">200", ">300"},
}

# Códigos de alta que indican fallecimiento del paciente (según IDS_mapping.csv).
# Un paciente fallecido no puede reingresar, por lo que esos encuentros
# quedan fuera del análisis de reingresos
CODIGOS_ALTA_FALLECIMIENTO = {11, 19, 20, 21}

# Alta a hospicio (cuidados paliativos, según IDS_mapping.csv). No implica fallecimiento,
# pero es un contexto clínico muy distinto al resto; se excluye por coherencia con la
# literatura del dataset (Strack et al., 2014).
CODIGOS_ALTA_HOSPICIO = {13, 14}

# Códigos que en IDS_mapping.csv significan "desconocido" (NULL, Not Available,
# Not Mapped, Unknown/Invalid). pandas los lee como números normales, así que no
# cuentan como nulos: son nulos encubiertos. No invalidan la fila porque estas
# columnas no son necesarias para el análisis de reingresos; se informan en el
# JSON de calidad.
CODIGOS_DESCONOCIDOS = {
    "admission_type_id": {5, 6, 8},
    "discharge_disposition_id": {18, 25, 26},
    "admission_source_id": {9, 15, 17, 20, 21},
}


def comprobar_columnas(frame: pd.DataFrame) -> None:
    """
    Comprueba que el DataFrame contiene todas las columnas obligatorias.

    Lanza:
      ValidationError si falta alguna columna.
    """
    faltan = [columna for columna in COLUMNAS_OBLIGATORIAS if columna not in frame.columns]
    if faltan:
        raise ValidationError(f"Faltan columnas obligatorias: {faltan}")


def construir_reglas(df: pd.DataFrame) -> dict[str, pd.Series]:
    """
    Evalúa todas las reglas sobre el DataFrame.

    Devuelve:
      Diccionario {motivo: máscara}, donde cada máscara vale True
      en las filas que INCUMPLEN esa regla.
    """
    reglas = {}

    for columna in COLUMNAS_SIN_NULOS:
        reglas[f"{columna} vacío"] = df[columna].isna()

    for columna, (minimo, maximo) in RANGOS_NUMERICOS.items():
        # El texto pasa a NaN y cuenta como fuera de rango.
        valores = pd.to_numeric(df[columna], errors="coerce")
        fuera_de_rango = valores.isna() | (valores < minimo)
        if maximo is not None:
            fuera_de_rango = fuera_de_rango | (valores > maximo)
        reglas[f"{columna} no numérico o fuera de rango"] = fuera_de_rango

    # Los nulos ya los controla la regla de COLUMNAS_SIN_NULOS; aquí solo se miran los valores presentes.
    for columna, permitidos in VALORES_PERMITIDOS.items():
        reglas[f"{columna} con valor no permitido"] = df[columna].notna() & ~df[columna].isin(permitidos)

    reglas["encounter_id duplicado"] = df["encounter_id"].duplicated(keep="first")

    alta = pd.to_numeric(df["discharge_disposition_id"], errors="coerce")
    reglas["paciente fallecido (fuera del análisis de reingresos)"] = alta.isin(CODIGOS_ALTA_FALLECIMIENTO)
    reglas["alta a hospicio (fuera del análisis de reingresos)"] = alta.isin(CODIGOS_ALTA_HOSPICIO)

    return reglas


def validar_encuentros(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separa los encuentros en válidos e inválidos.

    Parámetros:
      frame: DataFrame con los encuentros originales.

    Devuelve:
      (validos, errores): DataFrame de encuentros válidos y DataFrame de
      encuentros inválidos con una columna 'motivo' (la primera regla incumplida).
    """
    comprobar_columnas(frame)
    df = frame.copy()

    reglas = construir_reglas(df)

    # Motivo de cada fila: la primera regla que incumple (vacío si cumple todas).
    # Se recorren las reglas en orden inverso para que prevalezca la primera
    motivo = pd.Series("", index=df.index)
    for nombre_regla, incumple in reversed(list(reglas.items())):
        motivo[incumple] = nombre_regla

    es_valida = motivo == ""

    validos = df[es_valida].copy()
    errores = df[~es_valida].copy()
    errores["motivo"] = motivo[~es_valida]

    # En las filas válidas ya no hay textos ni nulos en estas columnas: se pueden pasar a entero.
    for columna in RANGOS_NUMERICOS:
        validos[columna] = pd.to_numeric(validos[columna]).astype(int)

    return validos, errores


def contar_incumplimientos(frame: pd.DataFrame) -> dict[str, int]:
    """
    Cuenta cuántas filas incumplen cada regla (una fila puede incumplir varias).

    Solo se incluyen las reglas con al menos un incumplimiento.
    """
    comprobar_columnas(frame)
    reglas = construir_reglas(frame)
    return {nombre: int(incumple.sum()) for nombre, incumple in reglas.items() if incumple.any()}