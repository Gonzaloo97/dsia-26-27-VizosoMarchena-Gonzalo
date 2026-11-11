"""E5: borde HTTP abierto, adaptado al contrato del ejemplo de dmartincc/dsia-26-27.

No se usa para inferir riesgos hospitalarios; es una practica independiente.
"""

import argparse
import json
import math
import re
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any

import httpx


class OpenAPIError(Exception):
    """Fallo permanente de parametros, HTTP o formato."""


class TransientOpenAPIError(OpenAPIError):
    """Timeout, conexion, 408, 429 o 5xx: admite repeticion acotada."""


@dataclass(frozen=True)
class APIResult:
    source: str
    data: dict[str, Any]


class OpenAPIClient:
    def __init__(self, *, get=None, timeout=15, max_retries=2, sleep=time.sleep):
        if not math.isfinite(timeout) or not 0 < timeout <= 120 or not 0 <= max_retries <= 5:
            raise OpenAPIError("Timeout o numero de reintentos fuera de rango.")
        self.get = get or httpx.get
        self.timeout, self.max_retries, self.sleep = timeout, max_retries, sleep

    def _request(self, url, params):
        try:
            response = self.get(url, params=params, timeout=self.timeout,
                                headers={"Accept": "application/json", "User-Agent": "dsia-proyecto-ii/0.2"},
                                follow_redirects=True)
        except httpx.TransportError as exc:
            raise TransientOpenAPIError("Timeout o fallo de conexion con la API abierta.") from exc
        status = response.status_code
        if status in {408, 429} or 500 <= status <= 599:
            raise TransientOpenAPIError(f"API abierta temporalmente no disponible (HTTP {status}).")
        if not 200 <= status < 300:
            raise OpenAPIError(f"API abierta rechazo la solicitud (HTTP {status}).")
        try:
            return response.json()
        except ValueError as exc:
            raise OpenAPIError("La API abierta no devolvio JSON valido.") from exc

    def _get_json(self, url, params=None):
        for attempt in range(self.max_retries + 1):
            try:
                return self._request(url, params)
            except TransientOpenAPIError:
                if attempt == self.max_retries:
                    raise
                self.sleep(0.2 * 2**attempt)

    def weather(self, lat=40.4168, lon=-3.7038):
        if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise OpenAPIError("Latitud o longitud fuera de rango.")
        payload = self._get_json("https://api.open-meteo.com/v1/forecast", {
            "latitude": lat, "longitude": lon, "current": "temperature_2m,wind_speed_10m", "timezone": "auto"})
        try:
            current = payload["current"]
            return APIResult("open-meteo", {"lat": lat, "lon": lon, "time": current["time"],
                                          "temperature_c": current["temperature_2m"], "wind_kmh": current["wind_speed_10m"]})
        except (KeyError, TypeError) as exc:
            raise OpenAPIError("Formato inesperado de Open-Meteo.") from exc

    def country(self, code):
        code = code.strip().upper()
        if not re.fullmatch(r"[A-Z]{2,3}", code):
            raise OpenAPIError("Usa un codigo ISO de pais de 2 o 3 letras.")
        payload = self._get_json(f"https://api.worldbank.org/v2/country/{code}", {"format": "json"})
        try:
            item = payload[1][0]
            return APIResult("worldbank", {"id": item["id"], "iso2": item["iso2Code"],
                                         "name": item["name"], "capital": item["capitalCity"]})
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenAPIError("Pais sin resultados o formato inesperado de World Bank.") from exc

    def fx(self, base="EUR", symbols="USD,GBP"):
        base, symbols = base.strip().upper(), symbols.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", base) or not re.fullmatch(r"[A-Z]{3}(,[A-Z]{3})*", symbols):
            raise OpenAPIError("Usa monedas ISO de tres letras, separadas por comas.")
        payload = self._get_json("https://api.frankfurter.app/latest", {"from": base, "to": symbols})
        try:
            rates = payload["rates"]
            if not isinstance(rates, dict) or not rates:
                raise OpenAPIError("La API no devolvio tipos de cambio.")
            return APIResult("frankfurter", {"base": payload["base"], "date": payload["date"], "rates": rates})
        except (KeyError, TypeError) as exc:
            raise OpenAPIError("Formato inesperado de Frankfurter.") from exc

    def github(self, owner, repo):
        if any(not re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in (owner, repo)):
            raise OpenAPIError("Nombre de propietario o repositorio invalido.")
        payload = self._get_json(f"https://api.github.com/repos/{owner}/{repo}")
        try:
            return APIResult("github", {"full_name": payload["full_name"], "html_url": payload["html_url"],
                                      "language": payload["language"], "stars": payload["stargazers_count"]})
        except (KeyError, TypeError) as exc:
            raise OpenAPIError("Formato inesperado de GitHub.") from exc


def main(argv=None, *, client=None):
    parser = argparse.ArgumentParser(description="E5: APIs abiertas sin claves")
    sub = parser.add_subparsers(dest="command", required=True)
    weather = sub.add_parser("weather")
    weather.add_argument("--lat", type=float, default=40.4168)
    weather.add_argument("--lon", type=float, default=-3.7038)
    country = sub.add_parser("country")
    country.add_argument("--code", required=True)
    fx = sub.add_parser("fx")
    fx.add_argument("--base", default="EUR")
    fx.add_argument("--symbols", default="USD,GBP")
    github = sub.add_parser("github")
    github.add_argument("--owner", required=True)
    github.add_argument("--repo", required=True)
    args = vars(parser.parse_args(argv))
    command = args.pop("command")
    try:
        result = getattr(client or OpenAPIClient(), command)(**args)
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2, allow_nan=False))
    except (OpenAPIError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
