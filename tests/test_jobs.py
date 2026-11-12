import json
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from readmission_app.ai_client import MockClient
from readmission_app.cli import main
from readmission_app.errors import AIClientError, DataError, QualityError
from readmission_app.pipeline import run_job, train_job

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "1_programacion_avanzada_python/Datos/diabetic_data_muestra.csv"


def test_train_and_run_jobs(csv_path, tmp_path):
    artifacts, output = tmp_path / "artifacts", tmp_path / "output"
    training = train_job(csv_path, artifacts)
    report = run_job(artifacts / "holdout.csv", artifacts / "model.joblib", output, MockClient())
    assert report["training_patient_overlap_rows"] == 0
    assert report["batch_metrics"] == training["holdout"]
    assert json.loads((output / "status.json").read_text())["status"] == "success"
    assert len(pd.read_csv(output / "predictions.csv")) == training["split"]["test_rows"]
    assert "provider=mock" in (output / "run.log").read_text()


def test_run_idempotence_and_failure_invalidate_old_outputs(csv_path, trained, tmp_path):
    model_path, _, _, _ = trained
    output = tmp_path / "output"
    first = run_job(csv_path, model_path, output, MockClient())
    prediction_bytes = (output / "predictions.csv").read_bytes()
    second = run_job(csv_path, model_path, output, MockClient())
    assert first == second
    assert prediction_bytes == (output / "predictions.csv").read_bytes()
    failing = Mock()
    failing.complete.side_effect = AIClientError("fallo simulado")
    with pytest.raises(AIClientError):
        run_job(csv_path, model_path, output, failing)
    assert not (output / "predictions.csv").exists()
    assert not (output / "summary.md").exists()
    assert json.loads((output / "status.json").read_text())["status"] == "failed"


def test_quality_gate_prevents_ai(encounters, trained, tmp_path):
    path, _, _, _ = trained
    encounters.loc[0, "time_in_hospital"] = 0
    source = tmp_path / "invalid.csv"
    encounters.to_csv(source, index=False)
    client = Mock()
    with pytest.raises(QualityError):
        run_job(source, path, tmp_path / "output", client, max_error_rate=0)
    client.complete.assert_not_called()
    assert not (tmp_path / "output/predictions.csv").exists()
    assert json.loads((tmp_path / "output/quality.json").read_text())["rows_dropped"] == 1


def test_unlabeled_run_and_overlap(encounters, trained, tmp_path):
    model_path, _, _, _ = trained
    source = tmp_path / "new.csv"
    encounters.drop(columns="readmitted").to_csv(source, index=False)
    report = run_job(source, model_path, tmp_path / "output", MockClient())
    assert report["evaluation_scope"] == "unlabeled_inference"
    assert "batch_metrics" not in report
    assert report["training_patient_overlap_rows"] > 0


def test_do_not_overwrite_input(csv_path):
    original = csv_path.read_bytes()
    with pytest.raises(DataError):
        train_job(csv_path, csv_path.parent)
    assert csv_path.read_bytes() == original


def test_cli_exits_and_batch(csv_path, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["train", "--input", "absent.csv", "--output-dir", "fail"]) == 2
    assert main([
        "run", "--input", str(csv_path), "--model-path", "absent.joblib",
        "--output-dir", "output", "--provider", "mock",
    ]) == 3
    assert main(["ai", "--provider", "openai", "--prompt", "test"]) == 4
    assert main(["ai", "--provider", "mock", "--prompt", "test", "--env-file", "absent.env"]) == 2
    prompts = tmp_path / "prompts.txt"
    prompts.write_text("uno\ndos\ntres\ncuatro\ncinco\n", encoding="utf-8")
    output = tmp_path / "responses.jsonl"
    assert main(["ai", "--provider", "mock", "--batch", str(prompts), "--output", str(output), "--fail-once"]) == 0
    records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 5
    assert all(record["provider"] == "mock" for record in records)
    assert main(["ai", "--batch", str(prompts)]) == 2
    assert main(["ai", "--batch", str(prompts), "--output", str(prompts)]) == 2


@pytest.mark.integration
def test_real_sample_training_and_inference(tmp_path):
    artifacts = tmp_path / "artifacts"
    metadata = train_job(SAMPLE, artifacts)
    quality = json.loads((artifacts / "quality.json").read_text())
    assert quality["rows_in"] == 5000
    assert quality["rows_out"] == 4867
    assert metadata["split"]["overlap_patients"] == 0
    output = tmp_path / "output"
    result = run_job(artifacts / "holdout.csv", artifacts / "model.joblib", output, MockClient())
    assert result["batch_metrics"]["roc_auc"] == pytest.approx(metadata["holdout"]["roc_auc"])
    assert 0 <= result["mean_score_uncalibrated"] <= 1


def test_cli_training_and_quality_exit(csv_path, tmp_path):
    assert main(["train", "--input", str(csv_path), "--output-dir", str(tmp_path / "trained")]) == 0
    frame = pd.read_csv(csv_path, keep_default_na=False)
    frame.loc[0, "age"] = "invalid"
    frame.to_csv(csv_path, index=False)
    assert main(["train", "--input", str(csv_path), "--output-dir", str(tmp_path / "failed"), "--max-error-rate", "0"]) == 1
