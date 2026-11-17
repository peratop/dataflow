"""Exceções públicas da biblioteca."""
from __future__ import annotations


class DataFlowError(Exception):
    """Classe base de todos os erros da DataFlow."""


class ConfigurationError(DataFlowError):
    """Pipeline ou etapa configurados de forma inválida."""


class RegistryError(DataFlowError):
    """Erro ao registrar ou localizar um componente no registro."""


class StageExecutionError(DataFlowError):
    """Uma etapa (source, step ou sink) falhou durante a execução."""

    def __init__(self, stage: str, original: Exception) -> None:
        super().__init__(f"Falha na etapa '{stage}': {original}")
        self.stage = stage
        self.original = original
