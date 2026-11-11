"""Smokes E5 explicitos con red, fuera de pytest y de la CI offline."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "proyecto_ii/evidence/open_api_smoke.json")
    args = parser.parse_args(argv)
    cases = [
        ["weather", "--lat", "40.4168", "--lon", "-3.7038"],
        ["country", "--code", "ES"],
        ["fx", "--base", "EUR", "--symbols", "USD,GBP"],
        ["github", "--owner", "dmartincc", "--repo", "dsia-26-27"],
        ["country", "--code", "ZZ"],
    ]
    records = []
    for case in cases:
        command = [sys.executable, "-m", "readmission_app.open_api_client", *case]
        print("Comprobando:", " ".join(case), flush=True)
        try:
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=100)
            record = {"command": "python -m readmission_app.open_api_client " + " ".join(case),
                      "exit_code": run.returncode, "expected_exit_code": 1 if case[-1] == "ZZ" else 0,
                      "response": json.loads(run.stdout) if run.returncode == 0 else None,
                      "error": run.stderr.strip() if run.returncode else None}
        except subprocess.TimeoutExpired:
            record = {"command": " ".join(case), "exit_code": None, "error": "Plazo del smoke agotado."}
        records.append(record)
        print("Resultado:", record["exit_code"], flush=True)
    passed = all(r["exit_code"] == r.get("expected_exit_code") and r["exit_code"] is not None for r in records)
    # Un fallo de red no demuestra el caso negativo del pais inexistente.
    passed = passed and "Pais sin resultados" in (records[-1].get("error") or "")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"checked_at_utc": datetime.now(timezone.utc).isoformat(),
                                      "live_network": True, "all_checks_passed": passed,
                                      "checks": records}, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
