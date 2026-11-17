"""Steps (transformações) prontos para uso (out-of-the-box)."""
from __future__ import annotations

from typing import Any, Callable, Iterable

from .core import Record, Records, Step
from .registry import STEPS


@STEPS.register("filter")
class FilterStep(Step):
    """Mantém apenas os registros para os quais ``predicate(record)`` é verdadeiro."""

    def __init__(self, predicate: Callable[[Record], bool]) -> None:
        self._predicate = predicate

    def process(self, records: Records) -> Records:
        return [r for r in records if self._predicate(r)]


@STEPS.register("map")
class MapStep(Step):
    """Aplica ``func(record) -> record`` a cada registro."""

    def __init__(self, func: Callable[[Record], Record]) -> None:
        self._func = func

    def process(self, records: Records) -> Records:
        return [self._func(dict(r)) for r in records]


@STEPS.register("rename")
class RenameStep(Step):
    """Renomeia campos conforme ``mapping`` ({nome_antigo: nome_novo})."""

    def __init__(self, mapping: dict[str, str]) -> None:
        self._mapping = mapping

    def process(self, records: Records) -> Records:
        return [{self._mapping.get(k, k): v for k, v in r.items()} for r in records]


@STEPS.register("select")
class SelectStep(Step):
    """Mantém somente os campos listados (campos ausentes no registro são ignorados)."""

    def __init__(self, fields: Iterable[str]) -> None:
        self._fields = list(fields)

    def process(self, records: Records) -> Records:
        return [{f: r[f] for f in self._fields if f in r} for r in records]


@STEPS.register("drop")
class DropStep(Step):
    """Remove os campos listados."""

    def __init__(self, fields: Iterable[str]) -> None:
        self._fields = set(fields)

    def process(self, records: Records) -> Records:
        return [{k: v for k, v in r.items() if k not in self._fields} for r in records]


@STEPS.register("cast")
class CastStep(Step):
    """Converte tipos: ``CastStep({"idade": int, "salario": float})``."""

    def __init__(self, types: dict[str, Callable[[Any], Any]]) -> None:
        self._types = types

    def process(self, records: Records) -> Records:
        result: Records = []
        for r in records:
            new = dict(r)
            for field, converter in self._types.items():
                if field in new:
                    new[field] = converter(new[field])
            result.append(new)
        return result


@STEPS.register("deduplicate")
class DeduplicateStep(Step):
    """Remove duplicados, mantendo a primeira ocorrência. Sem ``key_fields``, compara o registro inteiro."""

    def __init__(self, key_fields: Iterable[str] | None = None) -> None:
        self._key_fields = list(key_fields) if key_fields is not None else None

    def process(self, records: Records) -> Records:
        seen: set[tuple] = set()
        result: Records = []
        for r in records:
            fields = self._key_fields if self._key_fields is not None else sorted(r)
            key = tuple((f, repr(r.get(f))) for f in fields)
            if key not in seen:
                seen.add(key)
                result.append(r)
        return result


@STEPS.register("sort")
class SortStep(Step):
    """Ordena por um campo (str) ou por uma função-chave."""

    def __init__(self, key: str | Callable[[Record], Any], reverse: bool = False) -> None:
        self._key = (lambda r: r[key]) if isinstance(key, str) else key
        self._reverse = reverse

    def process(self, records: Records) -> Records:
        return sorted(records, key=self._key, reverse=self._reverse)
