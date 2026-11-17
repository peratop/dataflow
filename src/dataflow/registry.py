"""Registro de componentes (Factory Method baseado em registro).

Permite criar componentes pelo nome ("csv", "rename"...) e que o cliente
registre os seus próprios com um decorator, sem alterar o código da lib.
"""
from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

from .core import Sink, Source, Step
from .errors import RegistryError

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self, kind: str, base_class: type[T]) -> None:
        self._kind = kind
        self._base_class = base_class
        self._items: dict[str, type[T]] = {}

    def register(self, name: str, *, overwrite: bool = False) -> Callable[[type[T]], type[T]]:
        """Decorator: ``@STEPS.register("meu_step")``."""

        def decorator(cls: type[T]) -> type[T]:
            self.add(name, cls, overwrite=overwrite)
            return cls

        return decorator

    def add(self, name: str, cls: type[T], *, overwrite: bool = False) -> None:
        if not (isinstance(cls, type) and issubclass(cls, self._base_class)):
            raise RegistryError(
                f"'{cls}' deve herdar de {self._base_class.__name__} para ser registrado como {self._kind}."
            )
        key = name.strip().lower()
        if not key:
            raise RegistryError("O nome do componente não pode ser vazio.")
        if key in self._items and not overwrite:
            raise RegistryError(f"Já existe {self._kind} registrado com o nome '{key}'.")
        self._items[key] = cls

    def create(self, name: str, **options: Any) -> T:
        """Instancia o componente registrado sob ``name`` com as opções dadas."""
        key = name.strip().lower()
        try:
            cls = self._items[key]
        except KeyError:
            disponiveis = ", ".join(self.names()) or "nenhum"
            raise RegistryError(
                f"{self._kind} '{name}' não encontrado. Disponíveis: {disponiveis}."
            ) from None
        return cls(**options)

    def names(self) -> list[str]:
        return sorted(self._items)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name.strip().lower() in self._items


SOURCES: Registry[Source] = Registry("source", Source)
STEPS: Registry[Step] = Registry("step", Step)
SINKS: Registry[Sink] = Registry("sink", Sink)
