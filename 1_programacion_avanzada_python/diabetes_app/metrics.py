"""Métricas sobre los encuentros hospitalarios válidos."""

import pandas as pd

from diabetes_app.validator import CODIGOS_DESCONOCIDOS, GRUPOS_EDAD

# Valor de 'readmitted' que indica reingreso en menos de 30 días
# (el indicador de calidad hospitalaria más habitual)
REINGRESO_30_DIAS = "<30"

MIN_ENCUENTROS_RECURRENTE = 1

UMBRAL_COLUMNA_CASI_VACIA = 50.0

DECIMALES = 2


def distribucion_reingreso(validos: pd.DataFrame) -> pd.Series:
    """Porcentaje de encuentros en cada categoría de reingreso (NO, >30, <30)."""
    return (validos["readmitted"].value_counts(normalize=True) * 100).round(DECIMALES)


def tasa_reingreso_30_por_edad(validos: pd.DataFrame) -> pd.Series:
    """Porcentaje de reingresos en menos de 30 días por grupo de edad, en orden de edad."""
    es_reingreso_30 = validos["readmitted"] == REINGRESO_30_DIAS
    tasa = es_reingreso_30.groupby(validos["age"]).mean() * 100
    # reindex ordena por edad; los grupos sin datos se eliminan con dropna
    return tasa.reindex(GRUPOS_EDAD).dropna().round(DECIMALES)


def tasa_reingreso_30_por_hba1c(validos: pd.DataFrame) -> pd.Series:
    """
    Porcentaje de reingresos en menos de 30 días según el resultado de HbA1c.

    Permite comparar pacientes a los que se midió la HbA1c ("Norm", ">7", ">8")
    con los que no ("None").
    """
    es_reingreso_30 = validos["readmitted"] == REINGRESO_30_DIAS
    tasa = es_reingreso_30.groupby(validos["A1Cresult"]).mean() * 100
    return tasa.sort_values(ascending=False).round(DECIMALES)


def estancia_media_por_reingreso(validos: pd.DataFrame) -> pd.Series:
    """Días medios de estancia hospitalaria según la categoría de reingreso."""
    return validos.groupby("readmitted")["time_in_hospital"].mean().round(DECIMALES)


def pacientes_recurrentes(validos: pd.DataFrame) -> pd.Series:
    """Pacientes con más de un encuentro y su número de encuentros, de más a menos."""
    encuentros_paciente = validos["patient_nbr"].value_counts()
    return encuentros_paciente[encuentros_paciente > MIN_ENCUENTROS_RECURRENTE]


def porcentaje_nulos(frame: pd.DataFrame) -> dict[str, float]:
    """Porcentaje de nulos de cada columna que tiene alguno, de mayor a menor."""
    nulos = (frame.isna().mean() * 100).round(DECIMALES)
    return nulos[nulos > 0].sort_values(ascending=False).to_dict()


def porcentaje_codigos_desconocidos(frame: pd.DataFrame) -> dict[str, float]:
    """Porcentaje de filas con un código "desconocido" (nulo encubierto) en cada columna de IDs."""
    return {
        columna: round(float(frame[columna].isin(codigos).mean() * 100), DECIMALES)
        for columna, codigos in CODIGOS_DESCONOCIDOS.items()
        if columna in frame.columns
    }


def resumen_calidad(total: pd.DataFrame, validos: pd.DataFrame, errores: pd.DataFrame,
                    incumplimientos: dict[str, int]) -> dict:
    """
    Construye el informe de calidad de los datos.

    Parámetros:
      total: DataFrame original.
      validos, errores: resultado de la validación.
      incumplimientos: número de filas que incumplen cada regla.
    """
    nulos = porcentaje_nulos(total)
    return {
        "filas_totales": len(total),
        "filas_validas": len(validos),
        "filas_invalidas": len(errores),
        "incumplimientos_por_regla": incumplimientos,
        "porcentaje_nulos_por_columna": nulos,
        "columnas_casi_vacias": [col for col, pct in nulos.items() if pct > UMBRAL_COLUMNA_CASI_VACIA],
        "porcentaje_nulos_encubiertos": porcentaje_codigos_desconocidos(total),
        "pacientes_unicos": int(validos["patient_nbr"].nunique()),
        "tasa_reingreso_30_global": float(round((validos["readmitted"] == REINGRESO_30_DIAS).mean() * 100, DECIMALES)),
    }