import joblib
import numpy as np
import pandas as pd
import pytest

from readmission_app.errors import DataError, ModelError
from readmission_app.model import (FEATURES, NUMERIC, build_model, evaluate, features,
                                  grouped_split, load_model, predict)


def test_split_disjoint_reproducible_and_no_id_features(encounters):
    train, test = grouped_split(encounters)
    train2, test2 = grouped_split(encounters)
    assert set(train.patient_nbr).isdisjoint(test.patient_nbr)
    pd.testing.assert_frame_equal(test, test2)
    pd.testing.assert_frame_equal(train, train2)
    assert set(FEATURES).isdisjoint({"readmitted", "patient_nbr", "encounter_id"})
    assert len(train) + len(test) == len(encounters)


def test_preprocessing_fitted_only_on_train(encounters):
    train, test = grouped_split(encounters)
    train.loc[:, "num_medications"] = 2
    test.loc[:, "num_medications"] = 99999
    estimator = build_model().fit(features(train), (train.readmitted == "<30").astype(int))
    scaler = estimator.named_steps["preprocess"].named_transformers_["numeric"].named_steps["scale"]
    assert scaler.mean_[NUMERIC.index("num_medications")] == 2
    before = scaler.mean_.copy()
    estimator.predict_proba(features(test))
    np.testing.assert_array_equal(scaler.mean_, before)


def test_model_roundtrip_and_unseen_category(trained):
    path, original, holdout, expected = trained
    loaded = load_model(path)
    result = predict(loaded, holdout.drop(columns="readmitted"))
    np.testing.assert_allclose(result.score_readmission_30, expected.score_readmission_30)
    changed_target = holdout.assign(readmitted="NO")
    np.testing.assert_allclose(predict(loaded, changed_target).score_readmission_30, result.score_readmission_30)
    holdout.loc[:, "diag_1"] = "NEW_CATEGORY"
    assert predict(loaded, holdout).score_readmission_30.between(0, 1).all()
    assert original["metadata"]["split"]["overlap_patients"] == 0


def test_bad_models_and_version(tmp_path, trained):
    with pytest.raises(ModelError, match="train"):
        load_model(tmp_path / "missing.joblib")
    path = tmp_path / "bad.joblib"
    path.write_bytes(b"not a pickle")
    with pytest.raises(ModelError):
        load_model(path)
    joblib.dump({}, path)
    with pytest.raises(ModelError):
        load_model(path)
    _, bundle, _, _ = trained
    bundle["metadata"]["sklearn_version"] = "incompatible"
    joblib.dump(bundle, path)
    with pytest.raises(ModelError, match="version"):
        load_model(path)


def test_split_insufficient_or_single_class(encounters):
    with pytest.raises(ModelError):
        grouped_split(encounters.iloc[:2])
    with pytest.raises(ModelError):
        grouped_split(encounters.assign(readmitted="NO"))
    with pytest.raises(DataError):
        grouped_split(encounters, test_size=1)
    with pytest.raises(DataError):
        grouped_split(encounters, seed=-1)


def test_known_metrics_and_one_class():
    metrics = evaluate([0, 0, 1, 1], [0.1, 0.8, 0.9, 0.7])
    assert metrics["confusion_matrix"] == [[1, 1], [0, 2]]
    assert metrics["recall"] == 1
    assert metrics["precision"] == pytest.approx(2 / 3)
    assert metrics["f1"] == pytest.approx(0.8)
    assert evaluate([0, 0], [0.1, 0.2])["roc_auc"] is None


def test_missing_feature(encounters):
    with pytest.raises(DataError, match="variables"):
        features(encounters.drop(columns="age"))
