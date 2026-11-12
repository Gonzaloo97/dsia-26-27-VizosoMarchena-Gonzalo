"""Jobs reutilizables: datos -> sklearn -> resumen agregado IA -> artefactos."""

import hashlib
import json
import time
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from readmission_app.ai_client import CompletionClient
from readmission_app.data import check_quality, read_data, transform
from readmission_app.errors import AppError
from readmission_app.model import evaluate, fit_model, load_model, predict, save_model
from readmission_app.storage import job_logging, protect_inputs, write_csv, write_json, write_text


@contextmanager
def job(output_dir: Path, name: str, generated_files: list[str]):
    """Status es el marcador de publicacion; un error nunca deja un exito antiguo."""
    with job_logging(output_dir, name) as logger:
        start = time.perf_counter()
        write_json(output_dir / "status.json", {"job": name, "status": "running"})
        try:
            # Solo salidas propias de este job, nunca borrado recursivo.
            for filename in generated_files:
                (output_dir / filename).unlink(missing_ok=True)
            logger.info("Inicio job=%s", name)
            yield logger
        except (AppError, OSError) as exc:
            code = getattr(exc, "exit_code", 2)
            message = str(exc) if isinstance(exc, AppError) else "Error de escritura/lectura de archivos."
            logger.error("Fallo job=%s code=%d: %s", name, code, message)
            write_json(output_dir / "status.json", {"job": name, "status": "failed", "exit_code": code, "error": message})
            raise
        else:
            elapsed = round(time.perf_counter() - start, 3)
            write_json(output_dir / "status.json", {
                "job": name, "status": "success", "exit_code": 0,
                "duration_seconds": elapsed,
            })
            logger.info("Finalizado job=%s duration_seconds=%.3f", name, elapsed)


def train_job(source: Path, output_dir: Path, *, seed=42, test_size=0.2, max_error_rate=0.1) -> dict:
    """Genera modelo, holdout separado, predicciones y evidencia reproducible."""
    protect_inputs(output_dir, [source])
    files = ["model.joblib", "training_metrics.json", "quality.json", "holdout.csv", "holdout_predictions.csv"]
    with job(output_dir, "train", files) as logger:
        clean, _, quality = transform(read_data(source))
        write_json(output_dir / "quality.json", quality)
        check_quality(quality, max_error_rate)
        logger.info("Calidad rows_in=%d rows_out=%d rows_dropped=%d",
                    quality["rows_in"], quality["rows_out"], quality["rows_dropped"])
        bundle, holdout, predictions = fit_model(clean, source, seed=seed, test_size=test_size)
        save_model(bundle, output_dir / "model.joblib")
        write_json(output_dir / "training_metrics.json", bundle["metadata"])
        write_csv(output_dir / "holdout.csv", holdout)
        write_csv(output_dir / "holdout_predictions.csv", predictions)
        holdout_metrics = bundle["metadata"]["holdout"]
        logger.info("Holdout rows=%d f1=%.4f roc_auc=%.4f",
                    len(holdout), holdout_metrics["f1"], holdout_metrics["roc_auc"])
        return bundle["metadata"]


def summary_payload(quality: dict, predictions, metadata: dict) -> dict:
    """Lista cerrada de agregados: no enviar filas, IDs, diagnosticos ni texto libre."""
    return {
        "purpose": "demostracion academica; no uso clinico",
        "data_quality": {k: quality[k] for k in ("rows_in", "rows_out", "rows_dropped", "error_rate")},
        "predictions": {
            "mean_score_uncalibrated": float(predictions["score_readmission_30"].mean()),
            "predicted_positive_count": int(predictions["prediction_readmission_30"].sum()),
            "threshold": metadata["threshold"],
        },
        "training_holdout_metrics": metadata["holdout"],
        "baseline_holdout_metrics": metadata["baseline"],
    }


def run_job(source: Path, model_path: Path, output_dir: Path, client: CompletionClient, *, max_error_rate=0.1) -> dict:
    """Carga modelo ya entrenado. No reajusta preprocessing ni usa readmitted como X."""
    protect_inputs(output_dir, [source, model_path])
    files = ["clean.csv", "rejected.csv", "predictions.csv", "metrics.json", "quality.json", "ai_summary.json", "summary.md"]
    with job(output_dir, "inference", files) as logger:
        clean, rejected, quality = transform(read_data(source), require_target=False)
        write_json(output_dir / "quality.json", quality)
        check_quality(quality, max_error_rate)
        bundle = load_model(model_path)
        predictions = predict(bundle, clean)
        overlap = clean["patient_nbr"].astype(str).isin(bundle["train_patient_ids"])
        report = {
            **quality, "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
            "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "training_patient_overlap_rows": int(overlap.sum()),
            "mean_score_uncalibrated": float(predictions["score_readmission_30"].mean()),
            "predicted_positive_count": int(predictions["prediction_readmission_30"].sum()),
            "threshold": bundle["metadata"]["threshold"],
            "evaluation_scope": "batch_descriptive_not_new_holdout" if quality["target_available"] else "unlabeled_inference",
        }
        if quality["target_available"]:
            report["batch_metrics"] = evaluate((clean["readmitted"] == "<30").astype(int), predictions["score_readmission_30"])
        payload = summary_payload(quality, predictions, bundle["metadata"])
        logger.info("Inferencia rows=%d training_overlap_rows=%d", len(predictions), int(overlap.sum()))
        response = client.complete(json.dumps(payload, ensure_ascii=False, allow_nan=False))
        report["ai_provider"] = response.provider
        write_csv(output_dir / "clean.csv", clean)
        write_csv(output_dir / "rejected.csv", rejected)
        write_csv(output_dir / "predictions.csv", predictions)
        write_json(output_dir / "metrics.json", report)
        write_json(output_dir / "ai_summary.json", {**asdict(response), "input_aggregates": payload})
        summary = (
            "# Resumen del lote\n\n"
            f"Proveedor: **{response.provider}**. Modelo: `{response.model}`.\n\n"
            "Texto de IA no validado clinicamente. Las cifras verificables estan en metrics.json.\n\n"
            + response.text + "\n"
        )
        write_text(output_dir / "summary.md", summary)
        logger.info("Resumen completado provider=%s", response.provider)
        return report
