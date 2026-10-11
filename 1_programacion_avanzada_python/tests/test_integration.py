"""Tests de integración: cargan y validan el ventas.csv real del curso."""

from pathlib import Path

import pytest

from ventas_app.loader import load
from ventas_app.validator import validar_ventas

RUTA_CSV_CURSO = Path(__file__).parent.parent / "Datos" / "ventas.csv"

# Checkpoint del curso para ventas.csv.
VALIDAS_ESPERADAS = 140
INVALIDAS_ESPERADAS = 10


@pytest.mark.integration
def test_csv_curso_tiene_140_validas():
    validos, _ = validar_ventas(load(RUTA_CSV_CURSO))
    assert len(validos) == VALIDAS_ESPERADAS


@pytest.mark.integration
def test_csv_curso_tiene_10_invalidas():
    _, errores = validar_ventas(load(RUTA_CSV_CURSO))
    assert len(errores) == INVALIDAS_ESPERADAS