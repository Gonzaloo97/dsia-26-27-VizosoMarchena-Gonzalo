"""Tests unitarios del módulo validator."""

import pandas as pd  # Librería para trabajar con DataFrames
import pytest  # Framework de testing

from ventas_app.validator import ValidationError, validar_ventas  # Código que se prueba


# ------------------------------------------------------------
# Fixture: datos de prueba en memoria
# ------------------------------------------------------------

@pytest.fixture
def ventas_mini():
    """
    DataFrame pequeño con 3 ventas:
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
    """Crea un DataFrame con una sola venta, con las unidades y el precio indicados."""
    return pd.DataFrame({
        "fecha": ["2026-01-01"],
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [unidades],
        "precio_unitario": [precio],
        "cliente_id": ["C1"],
    })


# ------------------------------------------------------------
# Parte 1 - Tests con la fixture
# ------------------------------------------------------------

def test_mini_tiene_una_fila_valida(ventas_mini):
    """Solo la primera fila cumple las reglas."""
    validos, _ = validar_ventas(ventas_mini)
    assert len(validos) == 1


def test_mini_tiene_dos_filas_invalidas(ventas_mini):
    """La fila con unidades vacías y la fila con precio negativo son inválidas."""
    _, errores = validar_ventas(ventas_mini)
    assert len(errores) == 2


def test_importe_se_calcula_en_filas_validas(ventas_mini):
    """El importe de la fila válida es unidades * precio_unitario = 2 * 10.0."""
    validos, _ = validar_ventas(ventas_mini)
    assert validos["importe"].iloc[0] == 20.0


def test_validacion_no_modifica_el_dataframe_original(ventas_mini):
    """validar_ventas trabaja sobre una copia: el original no gana la columna 'importe'."""
    validar_ventas(ventas_mini)
    assert "importe" not in ventas_mini.columns


# ------------------------------------------------------------
# Parte 2 - Casos borde y errores
# ------------------------------------------------------------

# El mismo test se ejecuta 3 veces, una por cada pareja (precio, filas válidas esperadas)
@pytest.mark.parametrize("precio, validas_esperadas", [
    (0, 0),   # precio 0: inválido (tiene que ser > 0)
    (-1, 0),  # precio negativo: inválido
    (1, 1),   # precio positivo: válido
])
def test_precio_limite(precio, validas_esperadas):
    """Solo los precios estrictamente mayores que 0 son válidos."""
    validos, _ = validar_ventas(crear_venta(unidades=1, precio=precio))
    assert len(validos) == validas_esperadas


def test_unidades_texto_es_invalida():
    """Un texto en 'unidades' (por ejemplo "na") se convierte en NaN y la fila es inválida."""
    validos, errores = validar_ventas(crear_venta(unidades="na", precio=10.0))
    assert len(validos) == 0
    assert len(errores) == 1


def test_faltan_columnas_lanza_validation_error():
    """Si falta una columna obligatoria se lanza ValidationError."""
    sin_precio = crear_venta(unidades=1, precio=10.0).drop(columns=["precio_unitario"])
    with pytest.raises(ValidationError):
        validar_ventas(sin_precio)