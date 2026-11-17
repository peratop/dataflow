"""Sinks prontos para uso (out-of-the-box)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .core import Records, Sink
from .registry import SINKS


@SINKS.register("memory")
class MemorySink(Sink):
    """Guarda o resultado em ``self.records`` (útil em testes e notebooks)."""

    def __init__(self) -> None:
        self.records: Records = []

    def write(self, records: Records) -> None:
        self.records = [dict(r) for r in records]


@SINKS.register("csv")
class CsvSink(Sink):
    """Grava os registros em CSV. Sem ``fieldnames``, usa a união das chaves na ordem de aparição."""

    def __init__(
        self,
        path: str | Path,
        fieldnames: list[str] | None = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> None:
        self._path = Path(path)
        self._fieldnames = fieldnames
        self._delimiter = delimiter
        self._encoding = encoding

    def write(self, records: Records) -> None:
        fieldnames = self._fieldnames or list(dict.fromkeys(k for r in records for k in r))
        with self._path.open("w", newline="", encoding=self._encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=self._delimiter, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)


@SINKS.register("json")
class JsonSink(Sink):
    """Grava os registros como uma lista JSON."""

    def __init__(self, path: str | Path, indent: int = 2, encoding: str = "utf-8") -> None:
        self._path = Path(path)
        self._indent = indent
        self._encoding = encoding

    def write(self, records: Records) -> None:
        with self._path.open("w", encoding=self._encoding) as f:
            json.dump(records, f, indent=self._indent, ensure_ascii=False)
