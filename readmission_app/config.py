"""Configuracion explicita: leer el entorno solo al crear el cliente."""

import math
import os
from dataclasses import dataclass, field

from readmission_app.errors import DataError


@dataclass(frozen=True)
class AIConfig:
    provider: str = "mock"
    model: str = "gpt-4o-mini"
    api_key: str = field(default="", repr=False)
    timeout: float = 20.0
    max_retries: int = 2

    def __post_init__(self):
        if self.provider not in {"mock", "openai"}:
            raise DataError("Proveedor no soportado: usa mock u openai.")
        if not math.isfinite(self.timeout) or not 0 < self.timeout <= 120:
            raise DataError("AI_TIMEOUT_SECONDS debe estar entre 0 (excluido) y 120.")
        if not 0 <= self.max_retries <= 5:
            raise DataError("AI_MAX_RETRIES debe estar entre 0 y 5.")
        if not self.model.strip():
            raise DataError("El modelo de IA no puede estar vacio.")

    @classmethod
    def from_env(cls, provider: str | None = None, model: str | None = None):
        """Los flags prevalecen sobre las variables de entorno."""
        try:
            return cls(
                provider=provider or os.getenv("AI_PROVIDER", "mock"),
                model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=os.getenv("OPENAI_API_KEY", ""),
                timeout=float(os.getenv("AI_TIMEOUT_SECONDS", "20")),
                max_retries=int(os.getenv("AI_MAX_RETRIES", "2")),
            )
        except ValueError as exc:
            raise DataError("Timeout o numero de reintentos no numerico.") from exc
