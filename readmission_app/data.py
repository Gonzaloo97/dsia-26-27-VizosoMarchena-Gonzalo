"""Adaptador del Proyecto I: una sola implementacion de las reglas de diabetes."""

import math
from pathlib import Path

import pandas as pd

from diabetes_app.loader import DataLoadError, load
from diabetes_app.validator import ValidationError, validar_encuentros
from readmission_app.errors import DataError, QualityError

TARGET = "readmitted"


def read_data(path: Path) -> pd.DataFrame:
    try:
        return load(path)
    except (DataLoadError, OSError, ValueError, pd.errors.ParserError) as exc:
        raise DataError("No se pudo leer el CSV de entrada; comprueba ruta y formato.") from exc


def transform(frame: pd.DataFrame, *, require_target: bool = True):
    """Valida sin I/O; inferencia admite no conocer todavia el reingreso real."""
    if frame.empty:
        raise DataError("El CSV no contiene encuentros.")
    work = frame.copy()
    has_target = TARGET in work.columns
    if require_target and not has_target:
        raise DataError("El entrenamiento necesita la columna readmitted.")
    if not has_target:
        # Solo para reutilizar las reglas de elegibilidad del I, nunca como feature.
        work[TARGET] = "NO"
    try:
        clean, rejected = validar_encuentros(work)
    except ValidationError as exc:
        raise DataError(str(exc)) from exc
    if not has_target:
        clean = clean.drop(columns=TARGET)
        rejected = rejected.drop(columns=TARGET)
    report = {
        "rows_in": len(work), "rows_out": len(clean), "rows_dropped": len(rejected),
        "error_rate": len(rejected) / len(work),
        "rejection_reasons": {str(k): int(v) for k, v in rejected["motivo"].value_counts().items()},
        "target_available": has_target,
    }
    return clean.reset_index(drop=True), rejected.reset_index(drop=True), report


def check_quality(report: dict, max_error_rate: float) -> None:
    if not math.isfinite(max_error_rate) or not 0 <= max_error_rate <= 1:
        raise DataError("max-error-rate debe estar entre 0 y 1.")
    if report["rows_out"] == 0 or report["error_rate"] > max_error_rate:
        raise QualityError("Gate de calidad: demasiadas filas rechazadas o ninguna utilizable.")
