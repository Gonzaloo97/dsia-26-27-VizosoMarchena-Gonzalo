"""Tests del paquete diabetes_app (Parte B del Proyecto I)."""

from pathlib import Path

import pandas as pd
import pytest

from diabetes_app import metrics
from diabetes_app.loader import DataLoadError, load
from diabetes_app.validator import ValidationError, validar_encuentros

RUTA_MUESTRA = Path(__file__).parent.parent / "Datos" / "diabetic_data_muestra.csv"
VALIDOS_MUESTRA = 4867
INVALIDOS_MUESTRA = 133


def crear_encuentro(**cambios) -> dict:
    """Devuelve un encuentro válido; los argumentos permiten modificar cualquier campo."""
    encuentro = {
        "encounter_id": 1, "patient_nbr": 100, "gender": "Female", "age": "[60-70)",
        "time_in_hospital": 3, "num_lab_procedures": 40, "num_procedures": 1,
        "num_medications": 12, "number_outpatient": 0, "number_emergency": 0,
        "number_inpatient": 0, "number_diagnoses": 7, "diag_1": "428",
        "discharge_disposition_id": 1, "A1Cresult": "None", "max_glu_serum": "None",
        "readmitted": "NO",
    }
    encuentro.update(cambios)
    return encuentro


@pytest.fixture
def encuentros_mini():
    """
    4 encuentros:
      - 0: válido
      - 1: válido (mismo paciente que el 0, reingreso <30)
      - 2: inválido (paciente fallecido, código de alta 11)
      - 3: inválido (sexo "Unknown/Invalid")
    """
    return pd.DataFrame([
        crear_encuentro(encounter_id=1, patient_nbr=100, readmitted="<30", time_in_hospital=5),
        crear_encuentro(encounter_id=2, patient_nbr=100, readmitted="NO", time_in_hospital=3),
        crear_encuentro(encounter_id=3, patient_nbr=200, discharge_disposition_id=11),
        crear_encuentro(encounter_id=4, patient_nbr=300, gender="Unknown/Invalid"),
    ])


def test_validar_mini_dos_validos_dos_invalidos(encuentros_mini):
    validos, errores = validar_encuentros(encuentros_mini)
    assert len(validos) == 2
    assert len(errores) == 2


def test_errores_incluyen_motivo(encuentros_mini):
    _, errores = validar_encuentros(encuentros_mini)
    assert "motivo" in errores.columns
    assert errores["motivo"].str.contains("fallecido").any()


@pytest.mark.parametrize("dias, validos_esperados", [
    (0, 0),   # por debajo del mínimo
    (1, 1),   # límite inferior
    (14, 1),  # límite superior
    (15, 0),  # por encima del máximo
])
def test_time_in_hospital_limites(dias, validos_esperados):
    validos, _ = validar_encuentros(pd.DataFrame([crear_encuentro(time_in_hospital=dias)]))
    assert len(validos) == validos_esperados


@pytest.mark.parametrize("codigo_alta, validos_esperados", [
    (1, 1),    # alta a casa: válido
    (11, 0),   # fallecido
    (13, 0),   # hospicio en casa
    (14, 0),   # hospicio en centro médico
])
def test_alta_fallecimiento_y_hospicio_se_excluyen(codigo_alta, validos_esperados):
    validos, _ = validar_encuentros(pd.DataFrame([crear_encuentro(discharge_disposition_id=codigo_alta)]))
    assert len(validos) == validos_esperados


def test_readmitted_no_permitido_es_invalido():
    validos, _ = validar_encuentros(pd.DataFrame([crear_encuentro(readmitted="QUIZAS")]))
    assert len(validos) == 0


def test_diagnostico_principal_vacio_es_invalido():
    validos, _ = validar_encuentros(pd.DataFrame([crear_encuentro(diag_1=None)]))
    assert len(validos) == 0


def test_encuentro_duplicado_es_invalido():
    duplicados = pd.DataFrame([crear_encuentro(encounter_id=7), crear_encuentro(encounter_id=7)])
    validos, errores = validar_encuentros(duplicados)
    assert len(validos) == 1
    assert errores["motivo"].iloc[0] == "encounter_id duplicado"


def test_faltan_columnas_lanza_validation_error():
    sin_objetivo = pd.DataFrame([crear_encuentro()]).drop(columns=["readmitted"])
    with pytest.raises(ValidationError):
        validar_encuentros(sin_objetivo)


def test_load_path_no_existe_lanza_error():
    with pytest.raises(DataLoadError):
        load("no_existe.csv")


def test_load_interpreta_interrogacion_como_nulo_y_none_como_texto(tmp_path):
    """"?" debe leerse como nulo, pero "None" (prueba no realizada) debe seguir siendo texto."""
    fichero = tmp_path / "mini.csv"
    fichero.write_text("race,A1Cresult\n?,None\n")
    datos = load(fichero)
    assert pd.isna(datos["race"].iloc[0])
    assert datos["A1Cresult"].iloc[0] == "None"


def test_distribucion_reingreso_suma_100(encuentros_mini):
    validos, _ = validar_encuentros(encuentros_mini)
    assert metrics.distribucion_reingreso(validos).sum() == pytest.approx(100)


def test_pacientes_recurrentes(encuentros_mini):
    validos, _ = validar_encuentros(encuentros_mini)
    recurrentes = metrics.pacientes_recurrentes(validos)
    assert list(recurrentes.index) == [100]
    assert recurrentes.loc[100] == 2


def test_estancia_media_por_reingreso(encuentros_mini):
    validos, _ = validar_encuentros(encuentros_mini)
    estancia = metrics.estancia_media_por_reingreso(validos)
    assert estancia["<30"] == 5
    assert estancia["NO"] == 3


def test_codigos_desconocidos_cuentan_como_nulos_encubiertos():
    encuentros = pd.DataFrame([
        crear_encuentro(encounter_id=1, admission_type_id=1),
        crear_encuentro(encounter_id=2, admission_type_id=6),   # 6 = NULL en IDS_mapping
        crear_encuentro(encounter_id=3, admission_type_id=8),   # 8 = Not Mapped
        crear_encuentro(encounter_id=4, admission_type_id=2),
    ])
    resultado = metrics.porcentaje_codigos_desconocidos(encuentros)
    assert resultado["admission_type_id"] == 50.0
    assert resultado["discharge_disposition_id"] == 0.0


def test_codigo_desconocido_no_invalida_la_fila():
    validos, _ = validar_encuentros(pd.DataFrame([crear_encuentro(admission_type_id=6)]))
    assert len(validos) == 1


@pytest.mark.integration
def test_muestra_diabetes_validos_e_invalidos():
    validos, errores = validar_encuentros(load(RUTA_MUESTRA))
    assert len(validos) == VALIDOS_MUESTRA
    assert len(errores) == INVALIDOS_MUESTRA