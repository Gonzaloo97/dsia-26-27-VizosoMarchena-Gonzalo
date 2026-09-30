"""Tests de integración: usan el ventas.csv real del curso."""

from pathlib import Path  # Manejo de rutas de archivos

import pytest  # Framework de testing

from ventas_app.loader import load  # Carga de datos
from ventas_app.validator import validar_ventas  # Validación

# Ruta al CSV real: se sube de tests/ a 1_programacion_avanzada_python/ y se entra en Datos/
RUTA_CSV_CURSO = Path(__file__).parent.parent / "Datos" / "ventas.csv"

# Resultados esperados con el CSV del curso (checkpoint de la E1)
VALIDAS_ESPERADAS = 140
INVALIDAS_ESPERADAS = 10


@pytest.mark.integration
def test_csv_curso_tiene_140_validas():
    """El pipeline completo (cargar + validar) sobre el CSV real da 140 filas válidas."""
    validos, _ = validar_ventas(load(RUTA_CSV_CURSO))
    assert len(validos) == VALIDAS_ESPERADAS


@pytest.mark.integration
def test_csv_curso_tiene_10_invalidas():
    """El pipeline completo (cargar + validar) sobre el CSV real da 10 filas inválidas."""
    _, errores = validar_ventas(load(RUTA_CSV_CURSO))
    assert len(errores) == INVALIDAS_ESPERADAS