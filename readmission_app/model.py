"""Preprocesamiento, entrenamiento, evaluacion y persistencia sklearn."""

import hashlib
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from readmission_app.errors import DataError, ModelError
from readmission_app.storage import atomic_target

NUMERIC = ["time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
           "number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses"]
CATEGORICAL = ["age", "gender", "diag_1", "A1Cresult", "max_glu_serum"]
FEATURES = NUMERIC + CATEGORICAL
SCHEMA_VERSION = 1
THRESHOLD = 0.5


def features(frame: pd.DataFrame) -> pd.DataFrame:
    """Lista cerrada: ni objetivo ni identificadores entran al estimador."""
    missing = set(FEATURES) - set(frame.columns)
    if missing:
        raise DataError(f"Faltan variables del modelo: {sorted(missing)}")
    result = frame[FEATURES].copy()
    for column in NUMERIC:
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if np.isinf(result[column].to_numpy(dtype=float)).any():
            raise DataError(f"La variable {column} contiene infinitos.")
    for column in CATEGORICAL:
        result[column] = result[column].map(lambda v: str(v) if pd.notna(v) else np.nan).astype(object)
    return result


def build_model(seed: int = 42) -> Pipeline:
    """Imputacion y escalado se ajustan EXCLUSIVAMENTE con train."""
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
    ])
    preprocessing = ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)])
    return Pipeline([
        ("preprocess", preprocessing),
        ("classifier", LogisticRegression(class_weight="balanced", solver="liblinear", max_iter=2000, random_state=seed)),
    ])


def grouped_split(frame: pd.DataFrame, seed: int = 42, test_size: float = 0.2):
    """Holdout por patient_nbr: nunca encuentros del mismo paciente a ambos lados."""
    if not 0 < test_size < 1:
        raise DataError("test-size debe estar entre 0 y 1 (excluidos).")
    if not 0 <= seed <= 2**32 - 1:
        raise DataError("seed debe ser un entero entre 0 y 2**32-1.")
    if frame["patient_nbr"].nunique() < 5:
        raise ModelError("Se necesitan al menos 5 pacientes distintos para el holdout.")
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_indices, test_indices = next(splitter.split(frame, groups=frame["patient_nbr"]))
    train, test = frame.iloc[train_indices].copy(), frame.iloc[test_indices].copy()
    for part in (train, test):
        has_both_classes = (part["readmitted"] == "<30").nunique() == 2
        if not has_both_classes:
            raise ModelError("Train y test necesitan ambas clases; aporta mas datos. No se busca un split favorable.")
    return train, test


def evaluate(y_true, probabilities, threshold: float = THRESHOLD) -> dict:
    """AP ayuda a interpretar el desequilibrio; AUC=None si solo hay una clase."""
    y = np.asarray(y_true, dtype=int)
    scores = np.asarray(probabilities, dtype=float)
    predicted = (scores >= threshold).astype(int)
    two_classes = len(np.unique(y)) == 2
    return {
        "rows": len(y), "positive_rate": float(y.mean()), "threshold": threshold,
        "accuracy": float(accuracy_score(y, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)) if two_classes else None,
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "f1": float(f1_score(y, predicted, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, scores)) if two_classes else None,
        "average_precision": float(average_precision_score(y, scores)) if two_classes else None,
        "confusion_matrix": confusion_matrix(y, predicted, labels=[0, 1]).tolist(),
    }


def fit_model(clean: pd.DataFrame, source: Path, *, seed: int = 42, test_size: float = 0.2):
    """Entrena la configuracion fija de build_model y la compara con DummyClassifier."""
    train, test = grouped_split(clean, seed, test_size)
    x_train = features(train)
    x_test = features(test)
    y_train = (train["readmitted"] == "<30").astype(int)
    y_test = (test["readmitted"] == "<30").astype(int)
    estimator = build_model(seed)
    estimator.fit(x_train, y_train)
    baseline = DummyClassifier(strategy="prior").fit(x_train, y_train)
    probabilities = estimator.predict_proba(x_test)[:, 1]
    train_patients = sorted(train["patient_nbr"].astype(str).unique().tolist())
    metadata = {
        "schema_version": SCHEMA_VERSION, "features": FEATURES, "seed": seed,
        "threshold": THRESHOLD, "target": "readmitted == '<30'", "prediction_time": "al alta",
        "estimator": "LogisticRegression(class_weight='balanced', solver='liblinear')",
        "python_version": platform.python_version(), "sklearn_version": sklearn.__version__,
        "pandas_version": pd.__version__, "numpy_version": np.__version__, "joblib_version": joblib.__version__,
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "split": {"strategy": "GroupShuffleSplit", "test_size_groups": test_size,
                  "train_rows": len(train), "test_rows": len(test), "train_patients": len(train_patients),
                  "test_patients": int(test["patient_nbr"].nunique()),
                  "overlap_patients": len(set(train["patient_nbr"]) & set(test["patient_nbr"]))},
        "holdout": evaluate(y_test, probabilities),
        "baseline": evaluate(y_test, baseline.predict_proba(x_test)[:, 1]),
        "limitations": ["Demostracion academica, sin validacion clinica externa.",
                        "Datos historicos de EE. UU.; no representan un hospital actual.",
                        "Scores no calibrados por usar pesos de clase; umbral 0.5 didactico.",
                        "No se ha realizado seleccion de hiperparametros ni ajuste del umbral en test."],
    }
    bundle = {"metadata": metadata, "pipeline": estimator, "train_patient_ids": train_patients}
    test_predictions = test[["encounter_id", "patient_nbr", "readmitted"]].copy()
    test_predictions["score_readmission_30"] = probabilities
    test_predictions["prediction_readmission_30"] = (probabilities >= THRESHOLD).astype(int)
    return bundle, test.reset_index(drop=True), test_predictions


def save_model(bundle: dict, path: Path) -> None:
    with atomic_target(path) as temporary:
        joblib.dump(bundle, temporary)


def load_model(path: Path) -> dict:
    """Solo cargar joblib propios/de confianza: pickle puede ejecutar codigo."""
    if not path.is_file():
        raise ModelError("No existe el modelo. Ejecuta primero el comando train.")
    try:
        bundle = joblib.load(path)
    except Exception as exc:
        # La deserializacion puede fallar con multiples tipos segun version/formato.
        raise ModelError("No se pudo cargar el modelo; vuelve a entrenarlo en este entorno.") from exc
    if not isinstance(bundle, dict) or not isinstance(bundle.get("metadata"), dict):
        raise ModelError("Formato del modelo no reconocido.")
    meta = bundle["metadata"]
    if meta.get("schema_version") != SCHEMA_VERSION or meta.get("features") != FEATURES:
        raise ModelError("Contrato de variables/version del modelo incompatible.")
    if meta.get("sklearn_version") != sklearn.__version__:
        raise ModelError("La version de sklearn difiere del entrenamiento; reentrena el modelo.")
    if (not isinstance(bundle.get("pipeline"), Pipeline)
            or not isinstance(bundle.get("train_patient_ids"), list)
            or meta.get("threshold") != THRESHOLD):
        raise ModelError("Artefacto incompleto o umbral incompatible.")
    return bundle


def predict(bundle: dict, clean: pd.DataFrame) -> pd.DataFrame:
    """Inferencia reutilizable por una futura API; no necesita la etiqueta real."""
    try:
        scores = bundle["pipeline"].predict_proba(features(clean))[:, 1]
    except ValueError as exc:
        raise ModelError("Datos incompatibles con el modelo entrenado.") from exc
    result = clean[["encounter_id", "patient_nbr"]].copy()
    result["score_readmission_30"] = scores
    result["prediction_readmission_30"] = (scores >= bundle["metadata"]["threshold"]).astype(int)
    return result
