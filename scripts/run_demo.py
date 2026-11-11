"""Demo completa desde cualquier cwd. Ejecutar con el Python del venv instalado."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        ["train", "--input", "1_programacion_avanzada_python/Datos/diabetic_data_muestra.csv"],
        ["run", "--input", "proyecto_ii/artifacts/holdout.csv", "--provider", "mock"],
        ["ai", "--provider", "mock", "--batch", "proyecto_ii/prompts.txt",
         "--output", "proyecto_ii/output/respuestas.jsonl", "--fail-once"],
    ]
    for args in commands:
        print("Ejecutando:", " ".join(["python -m readmission_app", *args]), flush=True)
        completed = subprocess.run([sys.executable, "-m", "readmission_app", *args], cwd=ROOT, check=False)
        if completed.returncode:
            return completed.returncode
    print("Demo completada. Resultados: proyecto_ii/output; evaluacion: proyecto_ii/artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
