"""Tests unitarios de ventas_app.validator."""

import pandas as pd
import pytest

from ventas_app.validator import ValidationError, validar_ventas


@pytest.fixture
def ventas_mini():
    """
    3 ventas en memoria:
      - fila 0: válida (2 unidades x 10.0)
      - fila 1: inválida (unidades vacías)
      - fila 2: inválida (precio negativo)
    """
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })


def crear_venta(unidades, precio) -> pd.DataFrame:
    """Una sola venta con las unidades y el precio indicados."""
    return pd.DataFrame({
        "fecha": ["2026-01-01"],
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [unidades],
        "precio_unitario": [precio],
        "cliente_id": ["C1"],
    })


def test_validar_ventas_mini_una_valida(ventas_mini):
    validos, _ = validar_ventas(ventas_mini)
    assert len(validos) == 1


def test_validar_ventas_mini_dos_invalidas(ventas_mini):
    _, errores = validar_ventas(ventas_mini)
    assert len(errores) == 2


def test_validar_ventas_importe_es_unidades_por_precio(ventas_mini):
    validos, _ = validar_ventas(ventas_mini)
    assert validos["importe"].iloc[0] == 20.0


def test_validar_ventas_no_modifica_el_original(ventas_mini):
    validar_ventas(ventas_mini)
    assert "importe" not in ventas_mini.columns


@pytest.mark.parametrize("precio, validas_esperadas", [
    (0, 0),   # borde: tiene que ser estrictamente mayor que 0
    (-1, 0),
    (1, 1),
])
def test_validar_ventas_precio_limite(precio, validas_esperadas):
    validos, _ = validar_ventas(crear_venta(unidades=1, precio=precio))
    assert len(validos) == validas_esperadas


def test_validar_ventas_unidades_texto_va_a_errores():
    validos, errores = validar_ventas(crear_venta(unidades="na", precio=10.0))
    assert len(validos) == 0
    assert len(errores) == 1


def test_validar_ventas_sin_columna_obligatoria_lanza_validation_error():
    sin_precio = crear_venta(unidades=1, precio=10.0).drop(columns=["precio_unitario"])
    with pytest.raises(ValidationError):
        validar_ventas(sin_precio)