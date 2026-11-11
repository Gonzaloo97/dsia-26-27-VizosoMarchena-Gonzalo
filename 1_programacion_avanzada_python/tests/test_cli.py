"""Cierra la cobertura pendiente de las dos CLI del Proyecto I."""

import json
import sys

import pytest

from diabetes_app import cli as diabetes_cli
from ventas_app import cli as ventas_cli


@pytest.mark.parametrize("cli,source,report,expected", [
    (ventas_cli, "fecha,region,producto,unidades,precio_unitario,cliente_id\n2026-01-01,Norte,A,2,10,C1\n", "calidad_datos.json", 1),
    (diabetes_cli, "encounter_id,patient_nbr,gender,age,time_in_hospital,num_lab_procedures,num_procedures,num_medications,number_outpatient,number_emergency,number_inpatient,number_diagnoses,diag_1,discharge_disposition_id,A1Cresult,max_glu_serum,readmitted\n1,100,Female,[60-70),3,40,1,12,0,0,0,7,428,1,None,None,NO\n", "calidad_diabetes.json", 1),
])
def test_cli_writes_outputs(cli, source, report, expected, tmp_path, monkeypatch):
    input_path = tmp_path / "data.csv"
    input_path.write_text(source, encoding="utf-8")
    output = tmp_path / "nested/clean.csv"
    monkeypatch.setattr(sys, "argv", ["cli", "--input", str(input_path), "--output", str(output)])
    cli.main()
    assert output.exists()
    metrics = json.loads(output.with_name(report).read_text(encoding="utf-8"))
    assert metrics["filas_validas"] == expected


@pytest.mark.parametrize("cli", [ventas_cli, diabetes_cli])
def test_cli_missing_input_exits_one(cli, tmp_path, monkeypatch):
    output = tmp_path / "clean.csv"
    monkeypatch.setattr(sys, "argv", ["cli", "--input", str(tmp_path / "absent.csv"), "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 1
    assert not output.exists()
