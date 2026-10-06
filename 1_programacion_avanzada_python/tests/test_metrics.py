"""Tests unitarios de ventas_app.metrics."""

import pandas as pd
import pytest

from ventas_app import metrics


@pytest.fixture
def validos_mini():
    """Ventas ya validadas (con 'importe'): C1 compra dos veces."""
    return pd.DataFrame({
        "region": ["Norte", "Sur", "Norte", "Este"],
        "producto": ["A", "B", "A", "C"],
        "cliente_id": ["C1", "C2", "C1", "C3"],
        "importe": [100.0, 50.0, 30.0, 10.0],
    })


def test_importe_por_region_suma_y_ordena_de_mayor_a_menor(validos_mini):
    resultado = metrics.importe_por_region(validos_mini)
    assert list(resultado.index) == ["Norte", "Sur", "Este"]
    assert resultado["Norte"] == 130.0


def test_top_productos_devuelve_como_maximo_el_numero_configurado(validos_mini):
    resultado = metrics.top_productos(validos_mini)
    assert len(resultado) <= metrics.NUM_TOP_PRODUCTOS
    assert resultado.index[0] == "A"


def test_clientes_recurrentes_solo_incluye_mas_de_una_compra(validos_mini):
    resultado = metrics.clientes_recurrentes(validos_mini)
    assert list(resultado.index) == ["C1"]
    assert resultado["C1"] == 2


def test_resumen_calidad_cuenta_filas_y_suma_importe(validos_mini):
    total = pd.concat([validos_mini, validos_mini.head(1)])
    errores = validos_mini.head(1)
    resumen = metrics.resumen_calidad(total, validos_mini, errores)
    assert resumen == {
        "filas_totales": 5,
        "filas_validas": 4,
        "filas_invalidas": 1,
        "importe_total": 190.0,
    }