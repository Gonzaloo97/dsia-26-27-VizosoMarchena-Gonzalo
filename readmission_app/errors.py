"""Errores de dominio y codigos de salida de la aplicacion."""


class AppError(Exception):
    """Error esperado que puede mostrarse sin traceback ni datos privados."""

    exit_code = 2


class DataError(AppError):
    """Entrada o configuracion invalida."""


class QualityError(AppError):
    """La proporcion de filas rechazadas supera el limite configurado."""

    exit_code = 1


class ModelError(AppError):
    """Modelo inexistente, incompatible o imposible de entrenar."""

    exit_code = 3


class AIClientError(AppError):
    """Fallo permanente de configuracion, contrato o proveedor IA."""

    exit_code = 4


class TransientAIError(AIClientError):
    """Fallo temporal que admite reintentos limitados."""
