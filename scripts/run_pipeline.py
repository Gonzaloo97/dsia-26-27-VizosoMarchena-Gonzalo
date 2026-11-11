"""Cadena portable: inferencia -> check_metrics -> marcador local, sin instalar tareas."""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "proyecto_ii/output_daily" / date.today().isoformat())
    parser.add_argument("--min-rows-out", type=int, default=100)
    args = parser.parse_args(argv)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    marker = output / "LAST_OK.txt"
    marker.unlink(missing_ok=True)
    commands = [
        ["-m", "readmission_app", "run", "--input", "proyecto_ii/artifacts/holdout.csv",
         "--provider", "mock", "--output-dir", str(output)],
        ["scripts/check_metrics.py", "--metrics", str(output / "metrics.json"),
         "--min-rows-out", str(args.min_rows_out)],
    ]
    for args_list in commands:
        result = subprocess.run([sys.executable, *args_list], cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    marker.write_text(f"PIPELINE_OK {date.today().isoformat()}\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
