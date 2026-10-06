"""Tests unitarios de ventas_app.loader."""

import pytest

from ventas_app.loader import (
    CsvSalesRepository,
    DataLoadError,
    JsonSalesRepository,
    crear_repositorio,
    load,
)


def test_load_path_inexistente_lanza_data_load_error():
    with pytest.raises(DataLoadError):
        load("no_existe.csv")


def test_load_formato_no_soportado_lanza_data_load_error(tmp_path):
    # tmp_path: carpeta temporal de pytest que se borra al terminar el test.
    fichero = tmp_path / "ventas.txt"
    fichero.write_text("contenido")
    with pytest.raises(DataLoadError):
        load(fichero)


def test_load_csv_devuelve_todas_las_filas(tmp_path):
    fichero = tmp_path / "ventas.csv"
    fichero.write_text("region,unidades\nNorte,2\nSur,3\n")
    assert len(load(fichero)) == 2


def test_load_json_devuelve_todas_las_filas(tmp_path):
    fichero = tmp_path / "ventas.json"
    fichero.write_text('[{"region": "Norte", "unidades": 2}, {"region": "Sur", "unidades": 3}]')
    assert len(load(fichero)) == 2


def test_crear_repositorio_elige_clase_segun_extension(tmp_path):
    csv = tmp_path / "ventas.csv"
    csv.write_text("region\nNorte\n")
    json_ = tmp_path / "ventas.json"
    json_.write_text('[{"region": "Norte"}]')

    assert isinstance(crear_repositorio(csv), CsvSalesRepository)
    assert isinstance(crear_repositorio(json_), JsonSalesRepository)