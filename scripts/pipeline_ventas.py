"""E4 de data flows sobre ventas, reutilizando los modulos del Proyecto I."""

import argparse
from pathlib import Path

from ventas_app.loader import DataLoadError, load
from ventas_app.validator import ValidationError, validar_ventas
from readmission_app.data import check_quality
from readmission_app.errors import AppError, DataError
from readmission_app.pipeline import job
from readmission_app.storage import protect_inputs, write_csv, write_json


def transform(frame):
    """Etapa pura: filas y agregados, sin escribir ni llamar a servicios."""
    if frame.empty:
        raise DataError("El CSV de ventas no contiene filas.")
    try:
        clean, errors = validar_ventas(frame)
    except ValidationError as exc:
        raise DataError(str(exc)) from exc
    return clean, {
        "rows_in": len(frame), "rows_out": len(clean), "rows_dropped": len(errors),
        "error_rate": len(errors) / len(frame), "importe_total": float(clean["importe"].sum()),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-error-rate", type=float, default=0.1)
    args = parser.parse_args(argv)
    try:
        protect_inputs(args.output_dir, [args.input])
        with job(args.output_dir, "ventas", ["ventas_limpias.csv", "metrics.json"]) as logger:
            try:
                clean, report = transform(load(args.input))
            except (DataLoadError, OSError, ValueError) as exc:
                raise DataError("No se pudo cargar el fichero de ventas.") from exc
            write_json(args.output_dir / "metrics.json", report)
            check_quality(report, args.max_error_rate)
            write_csv(args.output_dir / "ventas_limpias.csv", clean)
            logger.info("rows_in=%d rows_out=%d rows_dropped=%d", report["rows_in"], report["rows_out"], report["rows_dropped"])
    except AppError as exc:
        print(f"ERROR: {exc}")
        return exc.exit_code
    except OSError:
        print("ERROR: no se pudo escribir la salida.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
