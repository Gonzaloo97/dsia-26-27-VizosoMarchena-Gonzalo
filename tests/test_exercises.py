import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sales_transform_in_memory():
    frame = pd.DataFrame({"fecha": ["2026-01-01"] * 3, "region": ["Norte"] * 3,
                          "producto": ["A"] * 3, "cliente_id": ["C1"] * 3,
                          "unidades": [2, None, 5], "precio_unitario": [10, 20, -1]})
    clean, report = script("pipeline_ventas").transform(frame)
    assert len(clean) == 1
    assert report["rows_dropped"] == 2
    assert report["importe_total"] == 20


@pytest.mark.integration
def test_sales_e4_real_checkpoint_gate_and_rerun(tmp_path):
    main = script("pipeline_ventas").main
    args = ["--input", str(ROOT / "1_programacion_avanzada_python/Datos/ventas.csv"), "--output-dir", str(tmp_path / "output")]
    assert main(args) == 0
    first = (tmp_path / "output/ventas_limpias.csv").read_bytes()
    assert main(args) == 0
    assert (tmp_path / "output/ventas_limpias.csv").read_bytes() == first
    metrics = json.loads((tmp_path / "output/metrics.json").read_text())
    assert (metrics["rows_out"], metrics["rows_dropped"]) == (140, 10)
    assert main(args + ["--max-error-rate", "0.05"]) == 1
    assert not (tmp_path / "output/ventas_limpias.csv").exists()
    assert main(["--input", "missing.csv", "--output-dir", str(tmp_path / "bad")]) == 2


def test_check_metrics_pass_fail_malformed(tmp_path):
    main = script("check_metrics").main
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps({"rows_out": 140, "error_rate": 10 / 150}))
    assert main(["--metrics", str(path), "--min-rows-out", "100"]) == 0
    assert main(["--metrics", str(path), "--min-rows-out", "999"]) == 1
    path.write_text('{"rows_out": "bad"}')
    assert main(["--metrics", str(path)]) == 2


@pytest.mark.parametrize("codes,expected_calls,expected_exit", [([1], 1, 1), ([0, 1], 2, 1), ([0, 0], 2, 0)])
def test_chain_stops_and_only_marks_success(codes, expected_calls, expected_exit, tmp_path, monkeypatch):
    wrapper = script("run_pipeline")
    runner = Mock(side_effect=[Mock(returncode=code) for code in codes])
    monkeypatch.setattr(wrapper.subprocess, "run", runner)
    marker = tmp_path / "LAST_OK.txt"
    marker.write_text("old success")
    assert wrapper.main(["--output-dir", str(tmp_path)]) == expected_exit
    assert runner.call_count == expected_calls
    assert marker.exists() == (expected_exit == 0)
