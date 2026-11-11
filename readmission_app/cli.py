"""CLI ligera: configuracion y codigos de salida; el nucleo no depende de argparse."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from readmission_app.ai_client import DeferredClient, create_client
from readmission_app.config import AIConfig
from readmission_app.errors import AppError, DataError
from readmission_app.pipeline import run_job, train_job
from readmission_app.storage import write_text


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Proyecto II: reingresos, sklearn e IA")
    commands = root.add_subparsers(dest="command", required=True)
    train = commands.add_parser("train", help="Entrenar y evaluar por pacientes separados")
    train.add_argument("--input", type=Path, required=True)
    train.add_argument("--output-dir", type=Path, default=Path("proyecto_ii/artifacts"))
    train.add_argument("--seed", type=int, default=42)
    train.add_argument("--test-size", type=float, default=0.2)
    train.add_argument("--max-error-rate", type=float, default=0.1)
    run = commands.add_parser("run", help="Inferencia con modelo persistido y resumen IA")
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--model-path", type=Path, default=Path("proyecto_ii/artifacts/model.joblib"))
    run.add_argument("--output-dir", type=Path, default=Path("proyecto_ii/output"))
    run.add_argument("--max-error-rate", type=float, default=0.1)
    ai = commands.add_parser("ai", help="Ejercicio E5: prompt o batch JSONL")
    inputs = ai.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--prompt")
    inputs.add_argument("--batch", type=Path)
    ai.add_argument("--output", type=Path)
    for subparser in (run, ai):
        subparser.add_argument("--provider", choices=["mock", "openai"])
        subparser.add_argument("--model", help="Nombre de modelo del proveedor IA")
        subparser.add_argument("--env-file", type=Path, help="Archivo .env explicito; por defecto .env del directorio actual")
        subparser.add_argument("--fail-once", action="store_true", help="Simular un fallo transitorio (E5)")
    return root


def ai_job(args, client) -> int:
    if args.batch:
        if not args.output:
            raise DataError("--batch requiere --output para el JSONL.")
        if args.batch.resolve() == args.output.resolve():
            raise DataError("El JSONL de salida no puede sobrescribir los prompts.")
    if args.output:
        env_path = args.env_file or Path(".env")
        if args.output.resolve() == env_path.resolve():
            raise DataError("La salida no puede sobrescribir el archivo de entorno.")
        # El destino representa este intento, no el ultimo batch que tuvo exito.
        args.output.unlink(missing_ok=True)
    if args.batch:
        prompts = [line.strip() for line in args.batch.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not prompts:
            raise DataError("El batch no contiene prompts.")
    else:
        prompts = [args.prompt]
    records = [{"prompt": prompt, **asdict(client.complete(prompt))} for prompt in prompts]
    serialized = "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n"
    if args.output:
        write_text(args.output, serialized)
    else:
        print(serialized, end="")
    return 0


def configured_client(args):
    env_path = args.env_file or Path(".env")
    if args.env_file and not env_path.is_file():
        raise DataError("No existe el --env-file indicado.")
    load_dotenv(env_path, override=False)
    return create_client(AIConfig.from_env(args.provider, args.model), fail_once=args.fail_once)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "train":
            train_job(args.input, args.output_dir, seed=args.seed, test_size=args.test_size, max_error_rate=args.max_error_rate)
        else:
            client = DeferredClient(lambda: configured_client(args))
            if args.command == "run":
                run_job(args.input, args.model_path, args.output_dir, client, max_error_rate=args.max_error_rate)
            else:
                return ai_job(args, client)
    except AppError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return exc.exit_code
    except (OSError, UnicodeError):
        print("ERROR: no se pudo leer o escribir un archivo; comprueba rutas, permisos y UTF-8.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
