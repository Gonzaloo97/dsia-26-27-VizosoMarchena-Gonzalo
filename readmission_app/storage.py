"""Escritura atomica por fichero y manifiesto que indica si un job termino."""

import json
import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

from readmission_app.errors import DataError


@contextmanager
def atomic_target(path: Path):
    """No deja un fichero de destino a medio escribir; sustituye al terminar."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        yield temporary
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, value: dict) -> None:
    """JSON estandar: rechaza NaN e Infinity."""
    with atomic_target(path) as temporary:
        temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    with atomic_target(path) as temporary:
        temporary.write_text(value, encoding="utf-8")


def write_csv(path: Path, frame) -> None:
    with atomic_target(path) as temporary:
        frame.to_csv(temporary, index=False)


def protect_inputs(output_dir: Path, inputs: list[Path]) -> None:
    """Prohibe entradas dentro del directorio que el job puede sobrescribir."""
    destination = output_dir.resolve()
    for source in inputs:
        if source.resolve().is_relative_to(destination):
            raise DataError("La entrada/modelo debe estar fuera del directorio de salida.")


@contextmanager
def job_logging(output_dir: Path, job: str):
    """Un log por ejecucion; cierra handlers para permitir reruns en Windows."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"readmission.{job}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handlers = [logging.StreamHandler(), logging.FileHandler(output_dir / "run.log", mode="w", encoding="utf-8")]
    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    try:
        yield logger
    finally:
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()
