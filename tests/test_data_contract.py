import pandas as pd
import pytest

from readmission_app.data import check_quality, read_data, transform
from readmission_app.errors import DataError, QualityError


def test_transform_is_pure_and_counts(encounters):
    original = encounters.copy(deep=True)
    encounters.loc[0, "time_in_hospital"] = 0
    before = encounters.copy(deep=True)
    clean, rejected, report = transform(encounters)
    assert len(clean) == len(original) - 1
    assert len(rejected) == 1
    assert report["error_rate"] == pytest.approx(1 / len(original))
    pd.testing.assert_frame_equal(encounters, before)


@pytest.mark.parametrize("column,value", [
    ("num_medications", float("inf")), ("num_medications", 1.5),
    ("diag_1", "  "), ("patient_nbr", ""), ("patient_nbr", "abc"),
    ("discharge_disposition_id", "x"), ("time_in_hospital", -1),
    ("discharge_disposition_id", 21), ("discharge_disposition_id", 14),
])
def test_invalid_rows_are_rejected_not_crashes(encounters, column, value):
    encounters[column] = encounters[column].astype(object)
    encounters.loc[0, column] = value
    clean, rejected, _ = transform(encounters)
    assert len(rejected) == 1
    assert len(clean) == len(encounters) - 1


def test_unlabeled_inference_does_not_fabricate_target(encounters):
    clean, _, report = transform(encounters.drop(columns="readmitted"), require_target=False)
    assert "readmitted" not in clean
    assert not report["target_available"]
    with pytest.raises(DataError):
        transform(clean)


def test_empty_and_missing_columns(encounters):
    with pytest.raises(DataError):
        transform(encounters.iloc[:0])
    with pytest.raises(DataError, match="columnas"):
        transform(encounters.drop(columns="age"))


@pytest.mark.parametrize("threshold", [-1, 2, float("nan")])
def test_invalid_gate_configuration(threshold):
    with pytest.raises(DataError):
        check_quality({"rows_out": 2, "error_rate": 0.1}, threshold)


def test_gate_boundary_and_zero_valid():
    check_quality({"rows_out": 2, "error_rate": 0.1}, 0.1)
    with pytest.raises(QualityError):
        check_quality({"rows_out": 2, "error_rate": 0.11}, 0.1)
    with pytest.raises(QualityError):
        check_quality({"rows_out": 0, "error_rate": 1}, 1)


def test_read_errors_and_none_category(tmp_path):
    with pytest.raises(DataError):
        read_data(tmp_path / "missing.csv")
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(DataError):
        read_data(path)
    path.write_text("A1Cresult,diag_1\nNone,\n", encoding="utf-8")
    result = read_data(path)
    assert result.loc[0, "A1Cresult"] == "None"
    assert pd.isna(result.loc[0, "diag_1"])
