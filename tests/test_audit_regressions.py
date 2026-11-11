"""Regresiones de los fallos reproducidos en la auditoria del 11/11."""

import json
from unittest.mock import Mock

import pytest

from readmission_app.ai_client import MockClient
from readmission_app.cli import main
from readmission_app.data import transform
from readmission_app.errors import AIClientError


@pytest.mark.parametrize("failure,expected", [("key", 4), ("env", 2), ("timeout", 2)])
def test_run_configuration_failure_invalidates_success(csv_path, trained, tmp_path, monkeypatch, failure, expected):
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "output"
    args = ["run", "--input", str(csv_path), "--model-path", str(trained[0]), "--output-dir", str(output)]
    assert main(args + ["--provider", "mock"]) == 0
    if failure == "timeout":
        monkeypatch.setenv("AI_TIMEOUT_SECONDS", "invalid")
    suffix = ["--provider", "openai"] if failure == "key" else ["--provider", "mock"]
    if failure == "env":
        suffix += ["--env-file", str(tmp_path / "missing.env")]
    assert main(args + suffix) == expected
    state = json.loads((output / "status.json").read_text())
    assert state["status"] == "failed"
    assert state["exit_code"] == expected
    assert not (output / "predictions.csv").exists()
    assert not (output / "summary.md").exists()


@pytest.mark.parametrize("failure", ["key", "input", "mid_batch"])
def test_failed_batch_does_not_leave_previous_jsonl(tmp_path, monkeypatch, failure):
    monkeypatch.chdir(tmp_path)
    source, output = tmp_path / "prompts.txt", tmp_path / "responses.jsonl"
    source.write_text("uno\ndos\ntres\n", encoding="utf-8")
    args = ["ai", "--batch", str(source), "--output", str(output)]
    assert main(args + ["--provider", "mock"]) == 0
    if failure == "input":
        source.unlink()
    if failure == "mid_batch":
        client = Mock()
        client.complete.side_effect = [MockClient().complete("uno"), AIClientError("simulado")]
        monkeypatch.setattr("readmission_app.cli.configured_client", lambda args: client)
    code = main(args + ["--provider", "openai" if failure == "key" else "mock"])
    assert code == (2 if failure == "input" else 4)
    assert not output.exists()


def test_batch_preserves_prompts_and_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "prompts.txt"
    source.write_text("uno\n", encoding="utf-8")
    for output in (source, tmp_path / ".env"):
        if output != source:
            output.write_text("AI_PROVIDER=mock\n", encoding="utf-8")
        before = output.read_bytes()
        assert main(["ai", "--provider", "mock", "--batch", str(source), "--output", str(output)]) == 2
        assert output.read_bytes() == before


@pytest.mark.parametrize("column", ["num_medications", "patient_nbr", "encounter_id"])
@pytest.mark.parametrize("value", [str(2**63), "100000000000000000000"])
def test_unrepresentable_integer_is_rejected(encounters, column, value):
    encounters[column] = encounters[column].astype(object)
    encounters.loc[0, column] = value
    clean, rejected, report = transform(encounters)
    assert len(rejected) == 1
    assert report["rows_dropped"] == 1
    assert len(clean) == len(encounters) - 1


def test_largest_int64_is_representable(encounters):
    encounters.loc[0, "num_medications"] = 2**63 - 1
    clean, rejected, _ = transform(encounters)
    assert rejected.empty
    assert clean.loc[0, "num_medications"] == 2**63 - 1


def test_huge_csv_stops_at_quality_gate(encounters, tmp_path, capsys):
    encounters["num_medications"] = "100000000000000000000"
    source, output = tmp_path / "huge.csv", tmp_path / "output"
    encounters.to_csv(source, index=False)
    assert main(["train", "--input", str(source), "--output-dir", str(output)]) == 1
    assert json.loads((output / "status.json").read_text())["status"] == "failed"
    assert "Traceback" not in capsys.readouterr().err
