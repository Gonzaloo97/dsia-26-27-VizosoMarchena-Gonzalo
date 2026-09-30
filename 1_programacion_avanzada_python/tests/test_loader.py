"""Tests unitarios del módulo loader."""

import pytest  # Framework de testing

from ventas_app.loader import DataLoadError, load  # Código que se prueba


def test_load_path_no_existe_lanza_error():
    """Cargar un fichero que no existe lanza DataLoadError."""
    with pytest.raises(DataLoadError):
        load("no_existe.csv")


def test_load_formato_no_soportado_lanza_error(tmp_path):
    """
    Cargar un fichero con una extensión no soportada lanza DataLoadError.

    tmp_path es una fixture de pytest que crea una carpeta temporal
    que se borra sola al terminar el test.
    """
    fichero = tmp_path / "ventas.txt"
    fichero.write_text("contenido")
    with pytest.raises(DataLoadError):
        load(fichero)


def test_load_csv_devuelve_dataframe(tmp_path):
    """Un CSV correcto se carga con el número de filas esperado."""
    fichero = tmp_path / "ventas.csv"
    fichero.write_text("region,unidades\nNorte,2\nSur,3\n")
    datos = load(fichero)
    assert len(datos) == 2