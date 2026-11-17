"""Contratos (interfaces) que o desenvolvedor-cliente pode implementar.

Source, Step e Sink são as três "estratégias" intercambiáveis de um pipeline.
Para estender a biblioteca basta herdar de uma delas; nenhum código da lib muda.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

Record = dict[str, Any]
Records = list[Record]


class Source(ABC):
    """Origem dos dados: lê registros de algum lugar (arquivo, memória, API...)."""

    @abstractmethod
    def read(self) -> Records:
        """Devolve a lista de registros lidos."""


class Step(ABC):
    """Etapa de transformação. Recebe registros e devolve novos registros.

    Implementações não devem modificar a lista de entrada.
    """

    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def process(self, records: Records) -> Records:
        """Transforma os registros e devolve o resultado."""


class Sink(ABC):
    """Destino dos dados: grava registros em algum lugar."""

    @abstractmethod
    def write(self, records: Records) -> None:
        """Persiste os registros recebidos."""
