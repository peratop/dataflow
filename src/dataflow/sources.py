"""Sources prontas para uso (out-of-the-box)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .core import Records, Source
from .errors import ConfigurationError
from .registry import SOURCES


@SOURCES.register("memory")
class MemorySource(Source):
    """Lê registros de uma lista já existente em memória."""

    def __init__(self, records: Records) -> None:
        self._records = records

    def read(self) -> Records:
        return [dict(r) for r in self._records]


@SOURCES.register("csv")
class CsvSource(Source):
    """Lê um arquivo CSV com cabeçalho. Todos os valores chegam como texto."""

    def __init__(self, path: str | Path, delimiter: str = ",", encoding: str = "utf-8") -> None:
        self._path = Path(path)
        self._delimiter = delimiter
        self._encoding = encoding

    def read(self) -> Records:
        with self._path.open(newline="", encoding=self._encoding) as f:
            return [dict(row) for row in csv.DictReader(f, delimiter=self._delimiter)]


@SOURCES.register("json")
class JsonSource(Source):
    """Lê um arquivo JSON cujo conteúdo é uma lista de objetos."""

    def __init__(self, path: str | Path, encoding: str = "utf-8") -> None:
        self._path = Path(path)
        self._encoding = encoding

    def read(self) -> Records:
        with self._path.open(encoding=self._encoding) as f:
            data = json.load(f)
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ConfigurationError("O JSON de entrada deve ser uma lista de objetos.")
        return data
