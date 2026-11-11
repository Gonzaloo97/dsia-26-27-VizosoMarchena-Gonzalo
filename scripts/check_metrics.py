"""Segundo paso de una cadena: solo continuar si se cumple el contrato de calidad."""

import argparse
import json
import math
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--max-error-rate", type=float, default=0.1)
    parser.add_argument("--min-rows-out", type=int, default=1)
    args = parser.parse_args(argv)
    if not 0 <= args.max_error_rate <= 1 or args.min_rows_out < 1:
        return 2
    try:
        report = json.loads(args.metrics.read_text(encoding="utf-8"))
        error_rate, rows = report["error_rate"], report["rows_out"]
        if not isinstance(error_rate, (int, float)) or not math.isfinite(error_rate) or not 0 <= error_rate <= 1:
            return 2
        if type(rows) is not int or rows < 0:
            return 2
    except (OSError, ValueError, KeyError, TypeError):
        return 2
    return 0 if error_rate <= args.max_error_rate and rows >= args.min_rows_out else 1


if __name__ == "__main__":
    raise SystemExit(main())
