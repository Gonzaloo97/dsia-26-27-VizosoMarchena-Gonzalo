"""Fixtures pequenas, sinteticas y sin red."""

import pandas as pd
import pytest

from readmission_app.data import transform
from readmission_app.model import fit_model, save_model


@pytest.fixture
def encounters():
    """80 pacientes x 2 encuentros; ambas clases en cada paciente (solo test)."""
    rows = []
    for patient in range(80):
        for label in range(2):
            rows.append({
                "encounter_id": patient * 2 + label + 1, "patient_nbr": patient + 100,
                "gender": "Male" if patient % 2 else "Female", "age": "[60-70)",
                "time_in_hospital": 2 + label, "num_lab_procedures": 20 + patient % 15,
                "num_procedures": 1, "num_medications": 8, "number_outpatient": 0,
                "number_emergency": 0, "number_inpatient": label, "number_diagnoses": 5,
                "diag_1": "250", "discharge_disposition_id": 1, "A1Cresult": "None",
                "max_glu_serum": "None", "readmitted": "<30" if label else "NO",
            })
    return pd.DataFrame(rows)


@pytest.fixture
def csv_path(encounters, tmp_path):
    path = tmp_path / "encounters.csv"
    encounters.to_csv(path, index=False)
    return path


@pytest.fixture
def trained(encounters, csv_path, tmp_path):
    clean, _, _ = transform(encounters)
    bundle, holdout, predictions = fit_model(clean, csv_path)
    path = tmp_path / "artifacts" / "model.joblib"
    save_model(bundle, path)
    return path, bundle, holdout, predictions


@pytest.fixture(autouse=True)
def offline_configuration(monkeypatch):
    """Ningun test hereda claves/configuracion real del usuario."""
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("AI_MAX_RETRIES", "2")
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "20")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
